import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync } from "node:fs";
import { mkdir, readFile } from "node:fs/promises";
import { resolve } from "node:path";

const { version: releaseVersion } = JSON.parse(readFileSync(new URL("../package.json", import.meta.url), "utf8")) as { version: string };

async function load(page: Page, n = 5) {
  await page.goto("/#market");
  const panel = page.getByTestId("market-workbench");
  await panel.getByLabel("Marktfall", { exact: true }).selectOption("bafin");
  await panel.getByLabel("Marktperioden", { exact: true }).selectOption(String(n));
  const reply = page.waitForResponse(r => r.url().endsWith("/api/market/reference-case"));
  await panel.getByRole("button", { name: "Modellmarkt laden", exact: true }).click();
  const body = await (await reply).json();
  expect(body.valid).toBe(true);
  await expect(panel.getByTestId("bafin-reference")).toContainText("Schreibfreies Demooriginal");
  return { panel, bundle: body.source_bundle };
}
async function calculate(page: Page) {
  const response = page.waitForResponse(r => r.url().endsWith("/api/market/calculate"));
  await page.getByRole("button", { name: "Gemeinsamen Markt berechnen", exact: true }).click();
  const reply = await response;
  expect(reply.status()).toBe(200);
  const result = await reply.json();
  expect(result.valid).toBe(true);
  await expect(page.getByTestId("market-results")).toBeVisible();
  return result;
}

test("AP6: Original, frische Quellenbindung, Einzel-VU-Dateien und Offline-Wiederaufnahme", async ({ page }) => {
  const external: string[] = [];
  await page.route("**/*", route => {
    const url = new URL(route.request().url());
    if (!new Set(["127.0.0.1", "localhost"]).has(url.hostname)) { external.push(url.hostname); return route.abort(); }
    return route.continue();
  });
  const { panel, bundle } = await load(page);
  await expect(panel.getByLabel("Workshop-Anteil motor", { exact: true })).toBeDisabled();
  await expect(panel.getByTestId("bafin-denominators")).toContainText("267.483,206");
  await expect(panel.getByTestId("bafin-rest")).toContainText("13.213,167");
  await expect(panel.getByTestId("bafin-rest")).toContainText("23.433,600");
  const result = await calculate(page);
  expect(result.source_bundle).toEqual(bundle);
  expect(result.source_input.insurers).toHaveLength(40);
  expect(result.reference.german_direct_selection_verified).toBe(false);
  await panel.getByText("40 Gruppen, Gewichte und Modellbasis zeigen", { exact: true }).click();
  await expect(panel.getByRole("region", { name: "BaFin Gruppen und Quellengewichte", exact: true }).locator("tbody tr")).toHaveCount(40);
  const aid = result.source_input.insurers[0].insurer_id;
  const excelResponse = page.waitForResponse(r => r.url().endsWith("/api/market/export.xlsx"));
  const excel = page.waitForEvent("download");
  await panel.getByRole("button", { name: `Einzel-VU ${aid} in Excel`, exact: true }).click();
  expect((await excelResponse).status()).toBe(200);
  expect((await excel).suggestedFilename()).toContain(`VU${aid}`);
  const saved = page.waitForEvent("download");
  await panel.getByRole("button", { name: "Marktquelle als JSON sichern", exact: true }).click();
  const path = (await (await saved).path())!;
  expect(JSON.parse(await readFile(path, "utf8"))).toEqual(bundle);
  await page.reload();
  await page.getByLabel("Marktdatei öffnen", { exact: true }).setInputFiles(path);
  await expect(page.getByTestId("market-results")).toContainText(result.content_digest);
  await expect(page.getByTestId("bafin-reference")).toContainText("Eigene bearbeitbare Sitzung");
  expect(external).toEqual([]);
  const help = await page.context().newPage();
  await help.goto("/api/seminar/handbook/market_ap6.html");
  await expect(help.getByRole("heading", { level: 1 })).toContainText("BaFin");
  await expect(help.locator("body")).toContainText("7.997,8640");
  await help.close();
});

test("AP6: Mix, Quellen-Override, stabile Identitäten und entwertete Ergebnisse", async ({ page }) => {
  const { panel, bundle } = await load(page);
  await calculate(page);
  await panel.getByRole("button", { name: "Als eigene Sitzung übernehmen", exact: true }).click();
  await panel.getByLabel("Workshop-Anteil motor", { exact: true }).fill("50");
  await panel.getByLabel("Workshop-Anteil property_liability", { exact: true }).fill("30");
  await expect(panel.getByTestId("market-results")).toHaveCount(0);
  await expect(panel.getByRole("button", { name: "Gemeinsamen Markt berechnen", exact: true })).toBeDisabled();
  await panel.getByRole("button", { name: "Spartenmix neu abbilden", exact: true }).click();
  await expect(panel.getByRole("button", { name: "Gemeinsamen Markt berechnen", exact: true })).toBeEnabled();
  const edited = await calculate(page);
  expect(edited.source_bundle.workshop.nonlife_mix).toEqual({ motor: "0.5", property_liability: "0.3", unmodeled: "0.2" });
  expect(edited.source_bundle.source_catalog).toEqual(bundle.source_catalog);
  const entity = bundle.source_catalog.entities.find((r: any) => r.group_assertion === "Itzehoer" && r.source_sector === "Schaden/Unfall");
  const stable = bundle.source_catalog.groups.find((g: any) => g.name === "Itzehoer").insurer_id;
  await panel.getByText("Quellenwerte und bearbeitete Annahmen", { exact: true }).click();
  await panel.getByLabel("BaFin Quellenzeile", { exact: true }).selectOption(String(entity.workbook_row));
  await panel.getByLabel("BaFin angenommener Beitrag", { exact: true }).fill("1000");
  await panel.getByLabel("BaFin Override Begründung", { exact: true }).fill("Handfall, keine recherchierte Änderung");
  await panel.getByRole("button", { name: "Annahme übernehmen und Auswahl neu abbilden", exact: true }).click();
  await expect(panel.getByTestId("market-results")).toHaveCount(0);
  await expect(panel.getByText("Workshop-Override Zeile", { exact: false })).toBeVisible();
  const changed = await calculate(page);
  expect(changed.source_input.insurers.find((a: any) => a.name === "Itzehoer").insurer_id).toBe(stable);
  expect(changed.source_input.insurers.some((a: any) => a.name === "Münchener Verein")).toBe(false);
  expect(changed.source_bundle.source_catalog).toEqual(bundle.source_catalog);
  expect(changed.content_digest).not.toBe(edited.content_digest);
  await panel.getByLabel("Workshop-Anteil motor", { exact: true }).fill("80");
  await panel.getByRole("button", { name: "Spartenmix neu abbilden", exact: true }).click();
  await expect(panel.getByRole("alert")).toContainText("zusammen 1");
  await expect(panel.getByTestId("market-results")).toHaveCount(0);
});

test("AP6: tatsächlicher 40er-100-Perioden-Lauf und angezeigte API-Summen", async ({ page }, info) => {
  test.setTimeout(240_000);
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  const { panel } = await load(page, 100);
  let result: any;
  await page.route("**/api/market/calculate", async route => {
    const response = await route.fetch({ timeout: 180_000 });
    result = await response.json();
    expect(response.status()).toBe(200);
    await route.fulfill({ response });
  });
  await panel.getByRole("button", { name: "Gemeinsamen Markt berechnen", exact: true }).click();
  await expect(panel.getByTestId("market-results")).toBeVisible({ timeout: 180_000 });
  expect(result.source_input.insurers).toHaveLength(40);
  expect(result.period_count).toBe(100);
  await panel.getByLabel("Markt Ergebnisperiode", { exact: true }).selectOption("100");
  const table = result.sides.variant.market_rows;
  const rows = table.rows.map((v: any[]) => Object.fromEntries(table.columns.map((key: string, i: number) => [key, v[i]])));
  const total = rows.find((r: any) => r.period === 100 && r.sector_id === "total");
  const expected = Number(total.closing_equity).toLocaleString("de-DE", { minimumFractionDigits: 4, maximumFractionDigits: 4 }).replace("-", "−");
  await expect(panel.getByTestId("market-equity")).toHaveText(expected);
  await expect(panel.getByTestId("market-grand-total")).toContainText(expected);
  await expect(page.locator(".sidebar")).toContainText(`Release ${releaseVersion}`);
  expect(result.reference.model_binding).toBe("preset_mapping");
  expect(errors).toEqual([]);
  await info.attach("AP6 40×100", { body: JSON.stringify({ content_digest: result.content_digest, total, source_count: result.source_bundle.source_catalog.entities.length, model_binding: result.reference.model_binding }), contentType: "application/json" });
  await panel.getByTestId("market-results").scrollIntoViewIfNeeded();
  const directory = process.env.IMS_AP6_CAPTURE === "1" ? resolve("../docs/handbook/images") : info.outputDir;
  await mkdir(directory, { recursive: true });
  await page.screenshot({ path: resolve(directory, "ap6_result_100_light_1440x900.png") });
});

for (const viewport of [{ width: 1440, height: 900 }, { width: 1024, height: 768 }, { width: 390, height: 844 }]) for (const theme of ["light", "dark"] as const) {
  test(`AP6 ${viewport.width}×${viewport.height} ${theme}: Quellen, Kontrast und Tastatur`, async ({ page }, info) => {
    await page.setViewportSize(viewport);
    await page.addInitScript(value => localStorage.setItem("ims.theme", value), theme);
    const { panel } = await load(page);
    await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
    await panel.getByRole("button", { name: "Als eigene Sitzung übernehmen", exact: true }).click();
    await panel.getByText("Quellenwerte und bearbeitete Annahmen", { exact: true }).click();
    await panel.getByRole("button", { name: "Spartenmix neu abbilden", exact: true }).focus();
    await page.keyboard.press("Tab");
    expect(await page.evaluate(() => document.activeElement?.tagName)).not.toBe("BODY");
    const report = await new AxeBuilder({ page }).include('[data-testid="market-workbench"]').withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
    expect(report.violations).toEqual([]);
    const ratios = report.passes.filter(v => v.id === "color-contrast").flatMap(v => v.nodes.flatMap(n => n.any.map(c => (c.data as { contrastRatio?: number } | null)?.contrastRatio).filter((r): r is number => typeof r === "number")));
    expect(ratios.length).toBeGreaterThan(0); expect(Math.min(...ratios)).toBeGreaterThanOrEqual(4.5);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
    const directory = process.env.IMS_AP6_CAPTURE === "1" ? resolve("../docs/handbook/images") : info.outputDir;
    await mkdir(directory, { recursive: true });
    await panel.getByTestId("bafin-reference").scrollIntoViewIfNeeded();
    await page.screenshot({ path: resolve(directory, `ap6_reference_${theme}_${viewport.width}x${viewport.height}.png`) });
    await info.attach("AP6 Kontrast", { body: JSON.stringify({ viewport, theme, minimumContrast: Math.min(...ratios), checkedTextNodes: ratios.length }), contentType: "application/json" });
  });
}
