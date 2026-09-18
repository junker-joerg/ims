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
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, acceptDownloads: true });
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto(`${baseUrl}#capital`, { waitUntil: "domcontentloaded" });
  const balance = page.getByTestId("model-balance-workbench");
  const life = page.getByTestId("life-workbench");
  const health = page.getByTestId("health-workbench");
  const four = page.getByTestId("four-sector-workbench");
  const capital = page.getByTestId("capital-workbench");
  await capital.waitFor();
  assert.match(await capital.innerText(), /Zuerst die Vier-Sparten-Gesamtbilanz prüfen/);

  await balance.getByRole("button", { name: "Bilanz berechnen" }).click();
  await balance.getByTestId("model-balance-results").waitFor();
  await life.getByRole("button", { name: "Beide Fälle berechnen" }).click();
  await life.getByTestId("life-results").waitFor();
  await health.locator(".health-top-controls select").selectOption("2");
  await health.getByRole("button", { name: "Beide Fälle berechnen" }).click();
  await health.getByTestId("health-results").waitFor();
  await four.locator(".four-sector-confirm input").check();
  await four.getByRole("button", { name: "Gesamtbilanz berechnen" }).click();
  await four.getByTestId("four-sector-results").waitFor();
  assert.match(await capital.innerText(), /Bilanzquelle/);
  const sourceDigest = await four.locator(".four-sector-digest").getAttribute("title");

  await capital.getByRole("textbox", { name: "Kfz-Anlagen Teilbetrag" }).fill("1");
  await capital.getByRole("textbox", { name: "Kfz-Anlagen Stresssatz" }).fill("0,25");
  await capital.getByRole("textbox", { name: "Maximaler Nettoverlust" }).fill("1");
  await capital.locator(".capital-confirm input").check();
  const responseEvent = page.waitForResponse((response) => response.url().endsWith(
    "/api/accounting/solvency-capital-readiness") && response.request().method() === "POST");
  await capital.getByRole("button", { name: "Kapitalwirkung berechnen" }).click();
  const response = await responseEvent;
  assert.equal(response.status(), 200);
  const report = await response.json();
  assert.equal(report.valid, true);
  assert.equal(report.management_evaluation.net_model_stress_loss, "0.2500");
  assert.equal(report.regulatory_metrics.scr, null);
  await capital.getByTestId("capital-results").waitFor();
  assert.match(await capital.getByTestId("capital-results").innerText(), /0,2500/);
  assert.match(await capital.getByTestId("capital-regulatory").innerText(), /SCR.*nicht berechnet/s);
  assert.equal(report.compliance_decision_enabled, false);

  const jsonDownload = page.waitForEvent("download");
  await capital.getByRole("button", { name: "JSON" }).click();
  const json = await jsonDownload;
  assert.match(json.suggestedFilename(), /^ims-kapital-modell-vu-1-p-1\.json$/);
  const jsonPath = await json.path();
  const { readFileSync } = await import("node:fs");
  const exported = JSON.parse(readFileSync(jsonPath, "utf8"));
  assert.equal(exported.four_sector_content_digest, sourceDigest);
  assert.equal(exported.capital_readiness.content_digest, report.content_digest);
  assert.equal(exported.capital_readiness.regulatory_metrics.scr, null);

  await page.route("**/api/accounting/solvency-capital-readiness.xlsx", async (route) => {
    const upstream = await route.fetch();
    await route.fulfill({ response: upstream, headers: { ...upstream.headers(), etag: '"wrong"' } });
  });
  await capital.getByRole("button", { name: "XLSX" }).click();
  await capital.getByRole("alert").waitFor();
  assert.match(await capital.getByRole("alert").innerText(), /XLSX-Nachweis/);
  await page.unroute("**/api/accounting/solvency-capital-readiness.xlsx");
  const xlsxDownload = page.waitForEvent("download");
  await capital.getByRole("button", { name: "XLSX" }).click();
  const xlsx = await xlsxDownload;
  assert.match(xlsx.suggestedFilename(), /^ims-kapital-modell-vu-1-p-1\.xlsx$/);
  assert.ok((await xlsx.path()).length > 0);

  await capital.scrollIntoViewIfNeeded();
  await capital.screenshot({ path: resolve(images, "windows_capital_pr178_wide_2026-09-18.png") });
  await page.setViewportSize({ width: 390, height: 844 });
  await capital.screenshot({ path: resolve(images, "windows_capital_pr178_narrow_2026-09-18.png") });
  const widths = await page.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth }));
  assert.ok(widths.document <= widths.viewport + 1, `Seitenueberlauf: ${JSON.stringify(widths)}`);

  await capital.getByRole("textbox", { name: "Kfz-Anlagen Teilbetrag" }).fill("999999");
  assert.equal(await capital.getByTestId("capital-results").count(), 0);
  assert.equal(await capital.getByRole("button", { name: "Kapitalwirkung berechnen" }).isDisabled(), true);
  await capital.locator(".capital-confirm input").check();
  await capital.getByRole("button", { name: "Kapitalwirkung berechnen" }).click();
  await capital.getByRole("alert").waitFor();
  assert.match(await capital.getByRole("alert").innerText(), /Teilposition|zugeordnet|uebersteigt/i);
  assert.equal(await capital.getByTestId("capital-results").count(), 0);
  await life.locator(".life-top-controls input[type=number]").fill("2");
  assert.match(await capital.innerText(), /Zuerst die Vier-Sparten-Gesamtbilanz prüfen/);
  assert.equal(await capital.getByRole("button", { name: "XLSX" }).count(), 0);
  assert.deepEqual(errors, []);
  console.log("PR178 browser smoke passed: source chain, model/regulatory split, downloads, wide/narrow and invalid input");
} finally {
  await browser.close();
}
