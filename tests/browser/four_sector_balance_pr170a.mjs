import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(new URL("../../frontend/package.json", import.meta.url));
const { chromium } = require(process.env.IMS_PLAYWRIGHT_PATH || "playwright");
const root = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const images = process.env.IMS_SCREENSHOT_DIR || resolve(root, "docs/handbook/images");
const baseUrl = process.env.IMS_BASE_URL || "http://127.0.0.1:8010/";
const browser = await chromium.launch({ headless: true, ...(process.env.IMS_BROWSER_CHANNEL ? { channel: process.env.IMS_BROWSER_CHANNEL } : {}) });

try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  async function show(model) {
    await page.evaluate((hash) => { location.hash = hash; }, model);
    await page.locator(`.model-workspace[data-model="${model}"]`).waitFor();
  }
  const pageErrors = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  await page.goto(`${baseUrl}#four-sector-balance`, { waitUntil: "domcontentloaded" });
  const section = page.getByTestId("four-sector-workbench");
  const balance = page.getByTestId("model-balance-workbench");
  const life = page.getByTestId("life-workbench");
  const health = page.getByTestId("health-workbench");
  await section.waitFor();
  await show("four-sector-balance");
  assert.equal(await section.getByRole("button", { name: "Gesamtbilanz berechnen" }).isDisabled(), true);
  assert.match(await section.innerText(), /Noch nicht geprüft/);

  await show("balance");
  await balance.getByRole("button", { name: "Bilanz berechnen" }).click();
  await balance.getByTestId("model-balance-results").waitFor();
  await show("life");
  await life.getByRole("button", { name: "Beide Fälle berechnen" }).click();
  await life.getByTestId("life-results").waitFor();
  await show("health");
  await health.locator(".health-top-controls select").selectOption("2");
  await show("health");
  await health.getByRole("button", { name: "Beide Fälle berechnen" }).click();
  await health.getByTestId("health-results").waitFor();

  assert.equal(await section.locator(".four-sector-ready-icon").count(), 4);
  await show("four-sector-balance");
  assert.equal(await section.getByRole("button", { name: "Gesamtbilanz berechnen" }).isDisabled(), true);
  await show("four-sector-balance");
  await section.locator(".four-sector-confirm input").check();
  const responseEvent = page.waitForResponse((response) =>
    response.url().endsWith("/api/accounting/four-sector-balance") && response.request().method() === "POST");
  await show("four-sector-balance");
  await section.getByRole("button", { name: "Gesamtbilanz berechnen" }).click();
  const response = await responseEvent;
  assert.equal(response.status(), 200);
  const body = await response.json();
  assert.equal(body.valid, true);
  assert.equal(body.period_count, 2);
  assert.equal(body.sectors.length, 4);
  assert.equal(body.total_rows.length, 2);
  for (const row of body.total_rows) {
    const decimal = (value) => BigInt(value.replace(".", ""));
    assert.equal(decimal(row.closing_assets), decimal(row.closing_liabilities) + decimal(row.closing_equity));
  }
  await section.getByTestId("four-sector-results").waitFor();
  assert.equal(await section.locator(".four-sector-table-wrap tbody tr").count(), 2);
  assert.match(await section.innerText(), /Bilanz je Versicherer/);

  await show("four-sector-balance");
  await section.scrollIntoViewIfNeeded();
  await show("four-sector-balance");
  await section.screenshot({ path: resolve(images, "windows_four_sector_balance_pr170a_wide_2026-09-18.png") });
  await page.setViewportSize({ width: 390, height: 844 });
  await show("four-sector-balance");
  await section.screenshot({ path: resolve(images, "windows_four_sector_balance_pr170a_narrow_2026-09-18.png") });
  const widths = await page.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth }));
  assert.ok(widths.document <= widths.viewport + 1, `Seitenueberlauf: ${JSON.stringify(widths)}`);
  await show("four-sector-balance");
  await section.getByRole("button", { name: "Leben" }).click();
  assert.equal(await section.locator(".four-sector-table-wrap tbody tr").count(), 2);
  await show("four-sector-balance");
  await section.getByRole("button", { name: "Gesamt", exact: true }).click();
  await show("four-sector-balance");
  await section.getByRole("button", { name: "Variante", exact: true }).click();
  await section.getByTestId("four-sector-results").waitFor({ state: "detached" });
  assert.equal(await section.locator(".four-sector-confirm input").isChecked(), false);

  await page.setViewportSize({ width: 1440, height: 900 });
  await show("four-sector-balance");
  await section.locator(".four-sector-confirm input").check();
  await show("four-sector-balance");
  await section.getByRole("button", { name: "Gesamtbilanz berechnen" }).click();
  await section.getByTestId("four-sector-results").waitFor();
  assert.match(await section.getByTestId("four-sector-results").innerText(), /Variante/);

  await show("life");
  await life.locator(".life-top-controls input[type=number]").fill("2");
  await section.getByTestId("four-sector-results").waitFor({ state: "detached" });
  await show("life");
  await life.getByRole("button", { name: "Beide Fälle berechnen" }).click();
  await life.getByTestId("life-results").waitFor();
  assert.match(await section.innerText(), /verschiedene Versicherer-IDs/);
  await show("four-sector-balance");
  assert.equal(await section.getByRole("button", { name: "Gesamtbilanz berechnen" }).isDisabled(), true);
  await show("life");
  await life.locator(".life-top-controls input[type=number]").fill("1");
  await show("life");
  await life.getByRole("button", { name: "Beide Fälle berechnen" }).click();
  await life.getByTestId("life-results").waitFor();

  await show("health");
  await health.locator(".health-top-controls select").selectOption("5");
  await show("health");
  await health.getByRole("button", { name: "Beide Fälle berechnen" }).click();
  await health.getByTestId("health-results").waitFor();
  assert.match(await section.innerText(), /verschiedene Periodenzahlen/);
  await show("four-sector-balance");
  assert.equal(await section.getByRole("button", { name: "Gesamtbilanz berechnen" }).isDisabled(), true);
  await show("health");
  await health.locator(".health-top-controls select").selectOption("2");
  await show("health");
  await health.getByRole("button", { name: "Beide Fälle berechnen" }).click();
  await health.getByTestId("health-results").waitFor();

  await page.route("**/api/accounting/four-sector-balance", async (route) => {
    const request = JSON.parse(route.request().postData());
    request.sectors.health.sources.variant_id = "wrong";
    await route.continue({ postData: JSON.stringify(request) });
  });
  await show("four-sector-balance");
  await section.locator(".four-sector-confirm input").check();
  await show("four-sector-balance");
  await section.getByRole("button", { name: "Gesamtbilanz berechnen" }).click();
  await section.getByRole("alert").last().waitFor();
  assert.equal(await section.getByTestId("four-sector-results").count(), 0);
  assert.match(await section.getByRole("alert").last().innerText(), /Kranken/);
  assert.deepEqual(pageErrors, []);
  console.log("PR170a browser smoke passed: four sources, both sides, reconciliation, wide/narrow, stale and error paths");
} finally {
  await browser.close();
}
