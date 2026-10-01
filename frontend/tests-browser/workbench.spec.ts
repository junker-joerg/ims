import { test, expect, type Page, type TestInfo } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, readFile } from "node:fs/promises";
import { resolve } from "node:path";

const areas = ["overview", "scenario", "balance", "life", "health", "four-sector-balance", "capital", "strategies", "execution", "results", "help"];
async function navigate(page: Page, hash: string) {
  await page.evaluate((value) => { location.hash = value; }, hash);
  await expect(page.locator(".shell")).toHaveAttribute("data-view", ["balance", "life", "health", "four-sector-balance", "capital", "strategies", "execution"].includes(hash) ? "simulation" : hash);
  if (["balance", "life", "health", "four-sector-balance", "capital", "strategies", "execution"].includes(hash)) {
    await expect(page.locator(`.model-workspace[data-model="${hash}"]`).first()).toBeVisible();
  }
}
async function noOverflow(page: Page) {
  const dimensions = await page.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth }));
  expect(dimensions.document, JSON.stringify(dimensions)).toBeLessThanOrEqual(dimensions.viewport);
}
async function accessible(page: Page) {
  const result = await new AxeBuilder({ page }).analyze();
  expect(result.violations.map(({ id, nodes }) => ({ id, targets: nodes.map((node) => node.target), details: nodes.map((node) => node.failureSummary) }))).toEqual([]);
  // AP2 requires 4.5:1 even where WCAG permits 3:1 for large headings.
  const ratios = result.passes.filter((rule) => rule.id === "color-contrast").flatMap((rule) => rule.nodes.flatMap((node) =>
    node.any.map((check) => (check.data as { contrastRatio?: number } | null)?.contrastRatio).filter((ratio): ratio is number => typeof ratio === "number")));
  expect(ratios.length).toBeGreaterThan(0);
  const minimum = Math.min(...ratios);
  expect(minimum, "Textkontrast einschließlich großer Schrift").toBeGreaterThanOrEqual(4.5);
  return { minimumContrast: minimum, checkedTextNodes: ratios.length };
}
async function capture(page: Page, name: string, testInfo: TestInfo) {
  const directory = process.env.IMS_CAPTURE === "1" ? resolve("../docs/handbook/images") : testInfo.outputDir;
  await mkdir(directory, { recursive: true });
  await page.screenshot({ path: resolve(directory, `ap2_after_${name}.png`) });
}

for (const viewport of [{ width: 1440, height: 900 }, { width: 1024, height: 768 }, { width: 390, height: 844 }]) {
  for (const theme of ["light", "dark"] as const) {
    test(`${viewport.width}×${viewport.height} ${theme}: Bereiche, Kontrast, Ziele, Tabellen`, async ({ page }, testInfo) => {
      await page.setViewportSize(viewport);
      await page.addInitScript((value) => localStorage.setItem("ims.theme", value), theme);
      await page.goto("/#overview");
      await page.waitForLoadState("networkidle");
      const errors: string[] = [];
      page.on("pageerror", (error) => errors.push(error.message));
      await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
      const evidence = [];
      for (const area of areas) {
        await navigate(page, area);
        await noOverflow(page);
        const accessibility = await accessible(page);
        evidence.push({ area, viewport, theme, ...accessibility });
        const targets = await page.locator(".area-navigation a, .theme-toggle, .primary-action:visible, .model-navigation a:visible").evaluateAll((elements) => elements.map((element) => {
          const rect = element.getBoundingClientRect(); return { label: element.textContent, width: rect.width, height: rect.height };
        }));
        for (const target of targets) { expect(target.width, target.label || "control").toBeGreaterThanOrEqual(44); expect(target.height, target.label || "control").toBeGreaterThanOrEqual(44); }
        if (area === "overview" || area === "health") await capture(page, `${area}_${theme}_${viewport.width}x${viewport.height}`, testInfo);
      }
      expect(errors).toEqual([]);
      await testInfo.attach("Kontrast und Ansichten", { body: JSON.stringify(evidence, null, 2), contentType: "application/json" });
    });
  }
}

test("Navigation erhält Eingaben, Ergebnis und Freigabe; Fehlerkorrektur und drei Exporte", async ({ page }, testInfo) => {
  await page.goto("/#health");
  const health = page.getByTestId("health-workbench");
  const opening = health.locator(".health-opening input").nth(1);
  await health.locator(".health-top-controls select").selectOption("100");
  await opening.fill("999.00");
  await navigate(page, "overview"); await navigate(page, "health");
  await expect(opening).toHaveValue("999.00");
  await health.getByRole("button", { name: "Beide Fälle berechnen" }).click();
  await expect(health.getByRole("alert").first()).toBeVisible();
  await accessible(page);
  await expect(health.getByTestId("health-results")).toHaveCount(0);
  await expect(health.getByRole("button", { name: "Geprüften Fall speichern" })).toBeDisabled();
  await opening.fill("1000.00");
  await health.getByRole("button", { name: "Beide Fälle berechnen" }).click();
  await expect(health.getByTestId("health-results")).toBeVisible();
  await expect(health.locator(".health-table tbody tr")).toHaveCount(100);
  await health.locator(".health-check input").check();
  await navigate(page, "results");
  await expect(health.getByTestId("health-results")).toBeVisible();
  await expect(health.locator(".health-check input")).toBeChecked();
  await expect(health.locator(".health-opening")).toBeHidden();
  await expect(page.locator(".results-empty")).toBeHidden();
  await health.getByRole("button", { name: "Geprüften Fall speichern" }).click();
  await expect(health.getByText("Gespeichert · VU 1 · Variante · 100 Perioden")).toBeVisible();
  for (const [label, extension] of [["CSV", ".csv"], ["JSON", ".json"], ["Excel", ".xlsx"]]) {
    const event = page.waitForEvent("download"); await health.getByRole("button", { name: label, exact: true }).click();
    const download = await event; expect(download.suggestedFilename()).toContain(extension); expect(await download.failure()).toBeNull();
    expect((await readFile((await download.path())!)).length).toBeGreaterThan(20);
  }
  await accessible(page);
  for (const theme of ["light", "dark"]) {
    if (await page.locator("html").getAttribute("data-theme") !== theme) await page.getByRole("button", { name: "Dunkelmodus", exact: true }).click();
    for (const viewport of [{ width: 1440, height: 900 }, { width: 1024, height: 768 }, { width: 390, height: 844 }]) {
      await page.setViewportSize(viewport); await noOverflow(page); await accessible(page);
      await health.getByTestId("health-results").scrollIntoViewIfNeeded();
      await capture(page, `results_${theme}_${viewport.width}x${viewport.height}`, testInfo);
    }
  }
  await page.setViewportSize({ width: 390, height: 844 }); await noOverflow(page);
  const table = health.locator(".health-table-wrap");
  expect(await table.evaluate((element) => element.scrollWidth > element.clientWidth)).toBe(true);
  await table.focus(); await page.keyboard.press("ArrowRight");
  await expect.poll(() => table.evaluate((element) => element.scrollLeft)).toBeGreaterThan(0);
  await navigate(page, "health"); await opening.fill("999.00");
  await expect(health.locator(".health-check input")).not.toBeChecked();
  await expect(health.getByTestId("health-results")).toHaveCount(0);
  await navigate(page, "results"); await expect(page.locator(".results-empty")).toBeVisible();
});

test("Tastatur, Zurück/Vorwärts, gespeicherter Farbmodus, reduzierte Bewegung und Details", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/#overview");
  await page.keyboard.press("Tab"); await expect(page.getByRole("link", { name: "Zum Inhalt" })).toBeFocused();
  await page.keyboard.press("Enter"); await expect(page.getByRole("heading", { level: 1 })).toBeFocused();
  await page.locator('.area-navigation a[href="#scenario"]').click();
  await expect(page.getByRole("heading", { level: 1 })).toBeFocused();
  const focus = await page.getByRole("heading", { level: 1 }).evaluate((element) => getComputedStyle(element).outlineWidth);
  expect(parseFloat(focus)).toBeGreaterThanOrEqual(3);
  await page.goBack(); await expect(page.locator(".shell")).toHaveAttribute("data-view", "overview");
  await page.goForward(); await expect(page.locator(".shell")).toHaveAttribute("data-view", "scenario");
  await page.getByRole("button", { name: "Dunkelmodus", exact: true }).click();
  const selected = await page.locator("html").getAttribute("data-theme");
  await page.reload(); await expect(page.locator("html")).toHaveAttribute("data-theme", selected!);
  expect(await page.locator("html").evaluate((element) => getComputedStyle(element).scrollBehavior)).toBe("auto");
  await navigate(page, "help");
  await expect(page.locator(".workbench-disclosure[open]")).toHaveCount(0);
  await page.locator(".workbench-disclosure summary:visible").first().click();
  await accessible(page); await noOverflow(page);
  await page.evaluate(() => { location.hash = "validation"; });
  await expect(page.locator("details:has(#validation)")).toHaveAttribute("open", "");
  await expect(page.locator("#validation")).toBeVisible();
});

test("Laden und API-Fehler sind sichtbar und lassen sich ohne Formularverlust beheben", async ({ page }) => {
  let release!: () => void;
  const pending = new Promise<void>((resolve) => { release = resolve; });
  await page.route("**/api/accounting/health-period-chain/preview", async (route) => { await pending; await route.continue(); });
  await page.goto("/#health");
  const health = page.getByTestId("health-workbench");
  await health.getByRole("button", { name: "Beide Fälle berechnen" }).click();
  try { await expect(health.getByRole("button", { name: "Berechnung läuft…" })).toBeDisabled(); }
  finally { release(); }
  await expect(health.getByTestId("health-results")).toBeVisible();
  await page.unroute("**/api/accounting/health-period-chain/preview");
  await page.route("**/api/accounting/health-period-chain/preview", (route) => route.abort());
  await health.getByRole("button", { name: "Beide Fälle berechnen" }).click();
  await expect(health.getByRole("alert").first()).toBeVisible();
  await expect(health.getByRole("button", { name: "Beide Fälle berechnen" })).toBeEnabled();
  await page.unroute("**/api/accounting/health-period-chain/preview");
  await health.getByRole("button", { name: "Beide Fälle berechnen" }).click();
  await expect(health.getByTestId("health-results")).toBeVisible();
});
