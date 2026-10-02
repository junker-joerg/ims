import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, readFile } from "node:fs/promises";
import { resolve } from "node:path";

const formatted = (value: string) => Number(value).toLocaleString("de-DE", { minimumFractionDigits: 4, maximumFractionDigits: 4 }).replace("-", "−");
function rows(table: { columns: string[]; rows: unknown[][]; missing?: Record<string, string[]> }) {
  return table.rows.map((values, i) => Object.fromEntries(table.columns.filter(key => !table.missing?.[i]?.includes(key)).map(key => [key, values[table.columns.indexOf(key)]])));
}
async function load(page: Page, id = "capacity", n = 10, count = 3) {
  await page.goto("/#market");
  const panel = page.getByTestId("market-workbench");
  await panel.getByLabel("Marktfall", { exact: true }).selectOption(id);
  await panel.getByLabel("Marktperioden", { exact: true }).selectOption(String(n));
  if (id === "market") await panel.getByLabel("Anzahl Modellanbieter", { exact: true }).selectOption(String(count));
  await panel.getByRole("button", { name: "Modellmarkt laden", exact: true }).click();
  await expect(panel.getByRole("button", { name: "Gemeinsamen Markt berechnen", exact: true })).toBeEnabled();
  return panel;
}
async function calculate(page: Page) {
  const response = page.waitForResponse(r => r.url().endsWith("/api/market/calculate") && r.request().method() === "POST");
  await page.getByTestId("market-workbench").getByRole("button", { name: "Gemeinsamen Markt berechnen", exact: true }).click();
  const reply = await response, body = await reply.json();
  expect(reply.status()).toBe(200); expect(body.valid).toBe(true);
  expect(reply.headers().etag).toBe(`"${body.content_digest}"`);
  await expect(page.getByTestId("market-results")).toBeVisible();
  return body;
}

test("AP5: Handbuch-Handfall, reale Risikobuchung und ausgewählte VU-Dateien", async ({ page }) => {
  const panel = await load(page, "switch"); const result = await calculate(page);
  await expect(panel.getByTestId("market-grand-total")).toContainText("Eigenkapital 157,0000 · Aktiva 172,0000 · Passiva 15,0000");
  const customer = panel.getByRole("region", { name: "Kunden und Risikobuchung", exact: true }).locator("tbody tr");
  await expect(customer).toHaveCount(1);
  await expect(customer.locator("td").nth(1)).toHaveText("1"); await expect(customer.locator("td").nth(2)).toHaveText("2");
  await expect(customer).toContainText("40,0000");
  await panel.getByLabel("Markt Anbieter", { exact: true }).selectOption("2");
  const exportReply = page.waitForResponse(r => r.url().endsWith("/api/market/export.xlsx"));
  const download = page.waitForEvent("download"); await panel.getByRole("button", { name: "Einzel-VU 2 in Excel", exact: true }).click();
  expect((await exportReply).status()).toBe(200); expect((await download).suggestedFilename()).toContain("VU2");
  const sourceDownload = page.waitForEvent("download"); await panel.getByRole("button", { name: "Marktquelle als JSON sichern", exact: true }).click();
  const sourcePath = (await (await sourceDownload).path())!; const source = JSON.parse(await readFile(sourcePath, "utf8"));
  expect(source).toEqual(result.source_input);
  await panel.getByLabel("Marktdatei öffnen", { exact: true }).setInputFiles(sourcePath);
  await expect(panel.getByTestId("market-results")).toContainText(result.content_digest);
  const help = await page.context().newPage(); await help.goto("/api/seminar/handbook/market_ap5.html");
  await expect(help.getByRole("heading", { level: 1 })).toContainText("Strategiefamilien");
  await expect(help.locator("body")).toContainText("172 = 15 + 157"); await help.close();
});

test("AP5: überlappende Peers, leere Sparte und reine Filter ohne Neuberechnung", async ({ page }) => {
  const panel = await load(page); const result = await calculate(page);
  let calculations = 0; page.on("request", r => { if (r.url().endsWith("/api/market/calculate")) calculations++; });
  await expect(panel.getByTestId("market-equity")).toHaveText("315,0000");
  const customer = panel.getByRole("region", { name: "Kunden und Risikobuchung", exact: true });
  await expect(customer.locator("tbody tr").nth(2)).toContainText("unversichert");
  await expect(customer.locator("tbody tr").nth(2).locator("td").last()).toHaveText("7,0000");
  await panel.getByLabel("Markt Vergleichsgruppe", { exact: true }).selectOption("peer:Vergleich_A");
  await expect(panel.getByTestId("market-equity")).toHaveText("215,0000");
  await panel.getByLabel("Markt Vergleichsgruppe", { exact: true }).selectOption("peer:Vergleich_B");
  await expect(panel.getByTestId("market-equity")).toHaveText("212,0000");
  await expect(panel.getByTestId("market-grand-total")).toContainText("Eigenkapital 315,0000");
  await panel.getByLabel("Markt Vergleichsgruppe", { exact: true }).selectOption("family:Preis_VU1");
  await panel.getByLabel("Markt Sparte", { exact: true }).selectOption("life");
  await expect(panel.getByTestId("market-equity")).toHaveText("0,0000");
  await panel.getByLabel("Markt Sparte", { exact: true }).selectOption("motor");
  await expect(panel.getByTestId("market-equity")).toHaveText("103,0000");
  for (const role of ["ceo", "cio", "coo", "cso_sales"]) await page.getByLabel("Meine Rolle", { exact: true }).selectOption(role);
  await page.evaluate(() => { location.hash = "overview"; }); await page.getByRole("link", { name: "Kunden im Markt verfolgen", exact: true }).click();
  await expect(panel.getByTestId("market-equity")).toHaveText("103,0000");
  await expect(panel.getByTestId("market-results")).toContainText(result.content_digest); expect(calculations).toBe(0);
});

test("AP5: Strategie und Kostenplan werden ausgeführt; ungültige Quellen entwerten den Stand", async ({ page }) => {
  const panel = await load(page, "market", 25); await calculate(page);
  await panel.getByLabel("Markt Strategiefamilie", { exact: true }).selectOption("motor_Festpreis");
  await panel.getByLabel("Markt Familienende", { exact: true }).fill("8");
  await panel.getByRole("button", { name: "Familie für Variante übernehmen", exact: true }).click();
  await expect(panel.getByTestId("market-results")).toHaveCount(0);
  await panel.getByText("Aufnahme mit Kosten und Vorlauf erweitern", { exact: true }).click();
  await panel.getByLabel("Markt Maßnahmenkosten", { exact: true }).fill("4");
  await panel.getByLabel("Markt Vorlauf", { exact: true }).fill("0"); await panel.getByLabel("Markt Wirkdauer", { exact: true }).fill("2");
  await panel.getByRole("button", { name: "Aufnahmeplan für Variante übernehmen", exact: true }).click();
  const result = await calculate(page);
  const records = rows(result.sides.variant.vu_rows).filter(r => r.insurer_id === 1 && r.sector_id === "motor");
  expect(records[5].family_id).toBe("motor_Festpreis"); expect(records[7].family_id).toBe("motor_Festpreis"); expect(records[8].family_id).toBe("motor_Preisantwort");
  expect(records[5].measure_cost).toBe("4.0000"); expect(records[6].measure_cost).toBe("0.0000");
  expect(records.filter(r => (r.active_measures as string[]).length).map(r => r.period)).toEqual([6, 7]);
  await panel.getByText("Quellen und vollständige Eingaben bearbeiten", { exact: true }).click();
  const source = structuredClone(result.source_input); source.insurers[0].sectors.motor.opening.assets = "NaN";
  await panel.getByLabel("Vollständige Marktquelle", { exact: true }).fill(JSON.stringify(source));
  await expect(panel.getByTestId("market-results")).toHaveCount(0);
  await panel.getByRole("button", { name: "Gemeinsamen Markt berechnen", exact: true }).click();
  await expect(panel.getByRole("alert")).toContainText("Dezimalstring"); await expect(panel.getByTestId("market-results")).toHaveCount(0);
  await expect(panel.getByRole("button", { name: /in Excel/ })).toHaveCount(0);
});

test("AP5: vollständiger 41er-Markt, 100 Perioden und Anzeige aus derselben API", async ({ page }, info) => {
  test.setTimeout(180_000); const errors: string[] = []; page.on("pageerror", e => errors.push(e.message));
  const panel = await load(page, "market", 100, 41);
  // Observe the real response once via APIRequestContext: Chromium's inspector
  // cache evicts this 36 MB body although the application's fetch succeeds.
  let result: any;
  await page.route("**/api/market/calculate", async route => {
    const response = await route.fetch({ timeout: 120_000 }); result = await response.json();
    expect(response.status()).toBe(200); expect(response.headers().etag).toBe(`"${result.content_digest}"`);
    await route.fulfill({ response });
  });
  await panel.getByRole("button", { name: "Gemeinsamen Markt berechnen", exact: true }).click();
  await expect(panel.getByTestId("market-results")).toBeVisible({ timeout: 120_000 });
  expect(result.valid).toBe(true);
  expect(rows(result.sides.variant.vu_rows)).toHaveLength(41 * 4 * 100);
  await panel.getByLabel("Markt Ergebnisperiode", { exact: true }).selectOption("100");
  const total = rows(result.sides.variant.market_rows).find(r => r.period === 100 && r.sector_id === "total")!;
  await expect(panel.getByTestId("market-equity")).toHaveText(formatted(total.closing_equity as string));
  await panel.getByText("Exakte Markt-Verlaufstabelle öffnen", { exact: true }).click();
  const table = panel.getByRole("region", { name: "Exakte Markt-Verlaufstabelle", exact: true });
  await expect(table.locator("tbody tr")).toHaveCount(100); await expect(table.locator("tbody tr").last()).toContainText(formatted(total.closing_equity as string));
  await expect(page.locator(".sidebar")).toContainText("2.0.0-alpha.5");
  expect(errors).toEqual([]);
  await info.attach("AP5 41×100", { body: JSON.stringify({ content_digest: result.content_digest, total, rows: 16400 }), contentType: "application/json" });
});

for (const viewport of [{ width: 1440, height: 900 }, { width: 1024, height: 768 }, { width: 390, height: 844 }]) for (const theme of ["light", "dark"] as const) {
  test(`AP5 ${viewport.width}×${viewport.height} ${theme}: Kontrast, Tastatur und echte Tabellen`, async ({ page }, info) => {
    test.setTimeout(150_000); await page.setViewportSize(viewport); await page.addInitScript(value => localStorage.setItem("ims.theme", value), theme);
    const panel = await load(page); const result = await calculate(page);
    await panel.getByText("Exakte Markt-Verlaufstabelle öffnen", { exact: true }).click();
    const table = panel.getByRole("region", { name: "Exakte Markt-Verlaufstabelle", exact: true });
    await expect(table.locator("tbody tr")).toHaveCount(10); await table.focus(); await expect(table).toBeFocused();
    if (viewport.width === 390) { await page.keyboard.press("ArrowRight"); await expect.poll(() => table.evaluate(element => element.scrollLeft)).toBeGreaterThan(0); }
    const report = await new AxeBuilder({ page }).analyze();
    expect(report.violations.map(v => ({ id: v.id, details: v.nodes.map(n => n.failureSummary) }))).toEqual([]);
    const ratios = report.passes.filter(v => v.id === "color-contrast").flatMap(v => v.nodes.flatMap(n => n.any.map(c => (c.data as { contrastRatio?: number } | null)?.contrastRatio).filter((r): r is number => typeof r === "number")));
    expect(ratios.length).toBeGreaterThan(0); expect(Math.min(...ratios)).toBeGreaterThanOrEqual(4.5);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    const directory = process.env.IMS_AP5_CAPTURE === "1" ? resolve("../docs/handbook/images") : info.outputDir; await mkdir(directory, { recursive: true });
    await table.evaluate(element => { element.scrollLeft = 0; });
    await page.getByTestId("market-results").evaluate(element => element.scrollIntoView({ block: "start" }));
    await page.screenshot({ path: resolve(directory, `ap5_market_${theme}_${viewport.width}x${viewport.height}.png`) });
    if (viewport.width === 1440 && theme === "light") await panel.getByRole("region", { name: "Kunden und Risikobuchung", exact: true }).screenshot({ path: resolve(directory, "ap5_capacity_booking.png") });
    await info.attach("AP5 Kontrast", { body: JSON.stringify({ viewport, theme, minimumContrast: Math.min(...ratios), checkedTextNodes: ratios.length, content_digest: result.content_digest }), contentType: "application/json" });
  });
}
