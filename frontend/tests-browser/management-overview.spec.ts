import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, readFile } from "node:fs/promises";
import { resolve } from "node:path";

const formatted = (value: string | number) => Number(value).toLocaleString("de-DE", { minimumFractionDigits: 4, maximumFractionDigits: 4 }).replace("-", "−");
const roles = ["ceo", "cio", "coo", "cso_sales"];
async function overview(page: Page) { await page.evaluate(() => { location.hash = "overview"; }); await expect(page.getByTestId("management-overview")).toBeVisible(); }
async function demo(page: Page, title: string) {
  const response = page.waitForResponse(response => response.url().endsWith("/api/seminar/import-bundle") && response.request().method() === "POST");
  const button = page.getByRole("button", { name: `Demo öffnen: ${title}`, exact: true });
  if (!await button.isVisible()) await page.getByRole("button", { name: "Szenario öffnen", exact: true }).click();
  await button.click();
  const body = await (await response).json();
  await expect(page.getByTestId("management-run-status")).toHaveText("Lauf abgeschlossen");
  return body.results.modern;
}
async function accessible(page: Page) {
  const report = await new AxeBuilder({ page }).analyze();
  expect(report.violations.map(item => ({ id: item.id, targets: item.nodes.map(node => node.target), details: item.nodes.map(node => node.failureSummary) }))).toEqual([]);
  const ratios = report.passes.filter(item => item.id === "color-contrast").flatMap(item => item.nodes.flatMap(node => node.any.map(check => (check.data as { contrastRatio?: number } | null)?.contrastRatio).filter((value): value is number => typeof value === "number")));
  expect(ratios.length).toBeGreaterThan(0); expect(Math.min(...ratios)).toBeGreaterThanOrEqual(4.5);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  return { minimumContrast: Math.min(...ratios), checkedTextNodes: ratios.length };
}

for (const viewport of [{ width: 1440, height: 900 }, { width: 1024, height: 768 }, { width: 390, height: 844 }]) {
  for (const theme of ["light", "dark"] as const) {
    test(`AP4 ${viewport.width}×${viewport.height} ${theme}: echte Kennzahlen, Erklärweg und vier Rollen`, async ({ page }, info) => {
      test.setTimeout(150_000);
      await page.setViewportSize(viewport); await page.addInitScript(value => localStorage.setItem("ims.theme", value), theme);
      const errors: string[] = []; page.on("pageerror", error => errors.push(error.message));
      await page.goto("/#overview");
      await expect(page.getByTestId("kpi-equity")).toHaveCount(0);
      await expect(page.getByTestId("management-run-status")).toContainText("Noch kein Szenario");
      const result = await demo(page, "Preis und Anbieterwechsel");
      await expect(page.getByTestId("kpi-equity")).toHaveText(formatted(result.sides.variant.total_rows[99].closing_equity));
      await expect(page.getByTestId("kpi-profit")).toHaveText(formatted(result.sides.variant.total_rows[99].period_profit));
      await expect(page.getByTestId("kpi-equity-percent")).toContainText("−24,73 %");
      await expect(page.getByTestId("kpi-periods")).toHaveText("100");
      await expect(page.getByTestId("cumulative-premium")).toHaveText("61.500,0000");
      await expect(page.getByTestId("cumulative-advertising")).toHaveText("190,0000");
      await expect(page.getByTestId("cumulative-investment")).toHaveText("1.015,7633");
      await expect(page.getByTestId("profit-reconciliation")).toContainText("−302,0000 × 95 = −28.690,0000");
      await expect(page.getByTestId("decision-explanation")).toContainText("gewählt VU 2");
      for (const item of result.sides.variant.sectors) await expect(page.getByTestId(`sector-equity-${item.sector_id}`)).toHaveText(formatted(item.rows[99].closing_equity));
      let recalculations = 0; page.on("request", request => { if (/\/api\/seminar\/(calculate|import-bundle)$/.test(request.url())) recalculations++; });
      for (const role of roles) {
        await page.getByLabel("Meine Rolle", { exact: true }).selectOption(role);
        await expect(page.getByTestId("kpi-equity")).toHaveText("87.325,7633");
        await expect(page.getByTestId("management-overview")).toContainText(result.content_digest);
      }
      expect(recalculations).toBe(0);
      await page.getByLabel("Meine Rolle", { exact: true }).selectOption("ceo");
      const evidence = await accessible(page);
      const directory = process.env.IMS_AP4_CAPTURE === "1" ? resolve("../docs/handbook/images") : info.outputDir;
      await mkdir(directory, { recursive: true }); await page.screenshot({ path: resolve(directory, `ap4_overview_${theme}_${viewport.width}x${viewport.height}.png`) });
      await page.getByLabel("Übersichtsperiode", { exact: true }).selectOption("6");
      await expect(page.getByTestId("kpi-equity")).toHaveText(formatted(result.sides.variant.total_rows[5].closing_equity));
      await expect(page.getByTestId("explained-premium")).toHaveText("Preis 3,6000 × gedeckte Exposition 0,0000 = Prämie 0,0000.");
      await page.getByRole("group", { name: "Vergleichsseite" }).getByRole("button", { name: "Baseline", exact: true }).click();
      await expect(page.getByTestId("explained-premium")).toHaveText("Preis 3,0000 × gedeckte Exposition 100,0000 = Prämie 300,0000.");
      await expect(page.getByTestId("kpi-equity")).toHaveText(formatted(result.sides.baseline.total_rows[5].closing_equity));
      await page.getByRole("group", { name: "Vergleichsseite" }).getByRole("button", { name: "Variante", exact: true }).click();
      await page.getByLabel("Übersichtsperiode", { exact: true }).selectOption("100");
      await page.getByText("Exakte Verlaufstabelle öffnen", { exact: true }).click();
      const table = page.getByRole("region", { name: "Eigenkapitalverlauf als Tabelle" });
      await expect(table.locator("tbody tr")).toHaveCount(100);
      await expect(table.locator("tbody tr").nth(99)).toContainText(formatted(result.sides.variant.total_rows[99].closing_equity));
      if (viewport.width === 390) { await table.focus(); await page.keyboard.press("ArrowRight"); await expect.poll(() => table.evaluate(element => element.scrollLeft)).toBeGreaterThan(0); }
      await accessible(page);
      await info.attach("AP4 Ansicht und Kontrast", { body: JSON.stringify({ viewport, theme, ...evidence, content_digest: result.content_digest }), contentType: "application/json" });
      if (viewport.width === 1440 && theme === "light") {
        await page.evaluate(() => { location.hash = "seminar"; });
        const download = page.waitForEvent("download"); await page.getByTestId("seminar-workbench").getByRole("button", { name: "Strategie JSON", exact: true }).click();
        const exported = JSON.parse(await readFile((await (await download).path())!, "utf8"));
        expect(exported.content_digest).toBe(result.content_digest);
        expect(exported.sides.variant.total_rows[99].closing_equity).toBe(result.sides.variant.total_rows[99].closing_equity);
        await overview(page);
      }
      expect(errors).toEqual([]);
    });
  }
}

test("AP4: drei Demos ohne JSON, Offlinehilfe und Tastatur", async ({ page }) => {
  test.setTimeout(180_000); await page.goto("/#overview");
  await page.keyboard.press("Tab"); await expect(page.getByRole("link", { name: "Zum Inhalt", exact: true })).toBeFocused();
  await page.keyboard.press("Enter"); await expect(page.getByRole("heading", { level: 1 })).toBeFocused();
  for (const [title, expected, sector] of [["Preis und Anbieterwechsel", "87.325,7633", "motor"], ["Kosten und Beitragsreaktion", "118.865,7633", "health"], ["Lebens-Anlageentscheidung", "117.045,6230", "life"]]) {
    await demo(page, title); await expect(page.getByTestId("kpi-equity")).toHaveText(expected);
    await expect(page.getByLabel("Sparte erklären", { exact: true })).toHaveValue(sector);
  }
  await page.getByLabel("Meine Rolle", { exact: true }).selectOption("cio");
  await page.getByRole("link", { name: "DORA / ICT verstehen", exact: true }).click();
  await expect(page.getByTestId("ict-workbench")).toBeVisible();
  const help = await page.context().newPage();
  await help.goto("/api/seminar/handbook/management_ap4.html");
  await expect(help.getByRole("heading", { level: 1 })).toContainText("Managementlabor");
  await expect(help.getByText("BAV", { exact: true })).toBeVisible();
  await expect.poll(() => help.locator("img").evaluateAll(images => images.every(image => (image as HTMLImageElement).complete && (image as HTMLImageElement).naturalWidth > 0))).toBe(true);
  await help.close();
});

test("AP4: Rollen erhalten editierte Eingaben/Freigaben; veraltete, laufende und fehlerhafte Ergebnisse", async ({ page }) => {
  test.setTimeout(180_000); await page.goto("/#overview"); await demo(page, "Preis und Anbieterwechsel");
  await page.evaluate(() => { location.hash = "seminar"; });
  const seminar = page.getByTestId("seminar-workbench");
  await seminar.getByRole("button", { name: "Als bearbeitbare Sitzung übernehmen", exact: true }).click();
  await seminar.getByLabel("Strategie Preisfaktor", { exact: true }).fill("6");
  await seminar.getByRole("button", { name: "Zuordnung für Variante übernehmen", exact: true }).click();
  await seminar.getByRole("checkbox").check();
  for (const role of roles) { await page.getByLabel("Meine Rolle", { exact: true }).selectOption(role); await expect(seminar.getByRole("checkbox")).toBeChecked(); await expect(seminar.getByLabel("Strategie Preisfaktor", { exact: true })).toHaveValue("6"); }
  await overview(page); await expect(page.getByTestId("management-run-status")).toContainText("Ergebnis veraltet"); await expect(page.getByTestId("kpi-equity")).toHaveCount(0);
  let release!: () => void; const paused = new Promise<void>(resolve => { release = resolve; });
  await page.route("**/api/seminar/import-bundle", async route => { await paused; await route.fulfill({ status: 503, json: { valid: false, issues: [{ message: "AP4 Test: Dienst vorübergehend nicht erreichbar", path: "$" }] } }); });
  await page.getByRole("button", { name: "Demo öffnen: Preis und Anbieterwechsel", exact: true }).click();
  await expect(page.getByTestId("management-run-status")).toContainText("Quellen werden geprüft");
  await expect(page.getByTestId("kpi-equity")).toHaveCount(0); release();
  await expect(page.getByTestId("management-run-status")).toContainText("Prüfung fehlgeschlagen"); await expect(page.getByRole("alert").filter({ hasText: "AP4 Test:" }).first()).toBeVisible();
  await page.unroute("**/api/seminar/import-bundle"); await demo(page, "Preis und Anbieterwechsel");
  await expect(page.getByTestId("kpi-equity")).toHaveText("87.325,7633");
});

test("AP4: tatsächlicher gültiger Lauf mit Null-Baseline und negativem Eigenkapital", async ({ page, request }) => {
  test.setTimeout(180_000);
  const original = await (await request.post("/api/seminar/workshop-case", { data: { case_id: "price", period_count: 100 } })).json();
  const source = original.source_input;
  const initial = await (await request.post("/api/seminar/calculate", { data: source })).json(); expect(initial.valid).toBe(true);
  const offset = Number(initial.sides.baseline.total_rows[99].closing_equity);
  const opening = source.accounting_source.sectors.motor.opening;
  opening.opening_claim_liability = (Number(opening.opening_claim_liability) + offset).toFixed(4);
  opening.opening_equity = (Number(opening.opening_equity) - offset).toFixed(4);
  const response = await (await request.post("/api/seminar/calculate", { data: source })).json();
  expect(response.valid).toBe(true); expect(response.sides.baseline.total_rows[99].closing_equity).toBe("0.0000");
  await page.goto("/#seminar"); const seminar = page.getByTestId("seminar-workbench");
  await seminar.getByRole("button", { name: "Seminarfall laden", exact: true }).click();
  await seminar.getByText("Expertenmodus: vollständige Gruppen, Ziehungen und Quellen", { exact: true }).click();
  await seminar.getByLabel("Moderne Seminarquellen", { exact: true }).fill(JSON.stringify(source));
  await seminar.getByRole("checkbox").check(); await seminar.getByRole("button", { name: "Moderne Kopplung berechnen", exact: true }).click();
  await expect(seminar.getByTestId("seminar-results")).toBeVisible(); await overview(page);
  await expect(page.getByTestId("kpi-equity-percent")).toContainText("Nicht definiert (Baseline 0)");
  await expect(page.getByTestId("kpi-equity")).toHaveText(formatted(response.sides.variant.total_rows[99].closing_equity));
  await accessible(page);
});
