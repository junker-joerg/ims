import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.IMS_PLAYWRIGHT_PATH || "playwright");
const root = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const images = resolve(root, "docs/handbook/images");
const baseUrl = process.env.IMS_BASE_URL || "http://127.0.0.1:8011/";
const browser = await chromium.launch({ channel: "msedge", headless: true });

try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, acceptDownloads: true });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  const section = page.getByTestId("health-workbench");
  await section.waitFor();
  await section.getByText("Gespeicherte Krankenfälle").waitFor();
  const initialHistoryCount = await section.locator(".health-history-list button").count();

  async function capture(locator, filename) {
    await locator.evaluate((element) => element.scrollIntoView({ block: "start", behavior: "instant" }));
    await page.waitForTimeout(150);
    await page.screenshot({ path: resolve(images, filename) });
  }

  await section.locator(".health-top-controls select").selectOption("100");
  await capture(section, "windows_health_workbench_pr169d_wide_inputs_2026-09-17.png");
  await section.getByRole("button", { name: "Beide Fälle berechnen" }).click();
  await section.getByTestId("health-results").waitFor();
  assert.equal(await section.locator(".health-table tbody tr").count(), 100);
  assert.match(await section.getByTestId("health-results").innerText(), /100 Perioden/);
  await section.locator(".health-results-controls select").selectOption("closing_cash");
  await capture(section.getByTestId("health-results"), "windows_health_workbench_pr169d_wide_results_2026-09-17.png");

  await page.setViewportSize({ width: 390, height: 844 });
  await capture(section, "windows_health_workbench_pr169d_narrow_inputs_2026-09-17.png");
  await capture(section.getByTestId("health-results"), "windows_health_workbench_pr169d_narrow_results_2026-09-17.png");
  const width = await page.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth }));
  assert.ok(width.document <= width.viewport + 1, `Horizontale Seitenueberlaeufe: ${JSON.stringify(width)}`);

  await page.setViewportSize({ width: 1440, height: 900 });
  await section.locator(".health-check input").check();
  await section.getByRole("button", { name: "Geprüften Fall speichern" }).click();
  await section.getByText("Gespeichert · VU 1 · Variante · 100 Perioden").waitFor();
  await section.locator(".health-history-list button").nth(initialHistoryCount).waitFor();
  assert.equal(await section.locator(".health-history-list button").count(), initialHistoryCount + 1);
  for (const [label, extension] of [["CSV", ".csv"], ["JSON", ".json"], ["Excel", ".xlsx"]]) {
    const event = page.waitForEvent("download");
    await section.getByRole("button", { name: label, exact: true }).click();
    const download = await event;
    assert.ok(download.suggestedFilename().endsWith(extension));
    assert.equal(await download.failure(), null);
  }
  await section.getByRole("button", { name: "Verlauf aktualisieren" }).click();
  await section.locator(".health-history-list button").first().click();
  await section.getByRole("heading", { name: "Gespeichertes Ergebnis" }).waitFor();
  assert.match(await section.getByTestId("health-results").innerText(), /Gespeichertes Ergebnis/);
  await section.getByRole("button", { name: "Vergleich" }).click();
  await section.getByRole("heading", { name: "Wirkung über die Zeit" }).waitFor();
  assert.match(await section.getByTestId("health-results").innerText(), /Wirkung über die Zeit/);

  await section.locator(".health-opening input").nth(1).fill("999.00");
  await section.getByRole("button", { name: "Beide Fälle berechnen" }).click();
  await section.getByRole("alert").first().waitFor();
  assert.equal(await section.getByTestId("health-results").count(), 0);
  assert.equal(await section.getByRole("button", { name: "Geprüften Fall speichern" }).isDisabled(), true);
  assert.equal(await section.locator(".health-history-list button").count(), initialHistoryCount + 1);
  await section.locator(".health-opening input").nth(1).fill("1000.00");
  await section.locator(".health-editor-block").nth(1).locator("input").first().fill("101");
  await section.getByRole("button", { name: "Beide Fälle berechnen" }).click();
  assert.match(await section.getByRole("alert").first().innerText(), /zwischen Periode 1 und 100/);
  assert.equal(await section.locator(".health-history-list button").count(), initialHistoryCount + 1);
  assert.deepEqual(errors, []);
  await browser.close();
  console.log("PR169d browser smoke passed: 100 periods, four screenshots, storage, history, three downloads, error path");
} finally {
  if (browser.isConnected()) await browser.close();
}
