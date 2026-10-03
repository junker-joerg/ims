import assert from "node:assert/strict";
import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync } from "node:fs";
import { mkdir, readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { amountText, amountUnits } from "../src/seminarPresentation";

const { version: releaseVersion } = JSON.parse(readFileSync(new URL("../package.json", import.meta.url), "utf8")) as { version: string };

type Row = Record<string, any>;
function rows(result: any, side: string, name: string): Row[] {
  const table = result.sides[side][name];
  return table.rows.map((values: any[], i: number) => Object.fromEntries(table.columns.map((key: string, j: number) => [key, values[j]]).filter(([key]: [string, any]) => !table.missing?.[String(i)]?.includes(key))));
}
async function load(page: Page, caseId = "us_hyperscaler_outage", n = 25) {
  await page.goto("/#market");
  await page.getByRole("tab", { name: "Schock bearbeiten", exact: true }).click();
  const panel = page.getByTestId("market-shock-workbench");
  await panel.getByLabel("Schockfall", { exact: true }).selectOption(caseId);
  await panel.getByLabel("Schockperioden", { exact: true }).selectOption(String(n));
  const { reply } = await observePost(page, "shock-case");
  await panel.getByRole("button", { name: "Schockdemo laden", exact: true }).click();
  const { result: source } = await reply;
  assert.equal(source.valid, true);
  await expect(panel.getByTestId("shock-original")).toContainText("Schreibfreies Demooriginal");
  return { panel, source: source.shock_bundle };
}
async function observePost(page: Page, path: string) {
  // Read the real HTTP response before Chromium's small inspector body cache
  // evicts it. This is forwarding the backend response, not a mocked result.
  let resolveReply!: (value: { result: any; etag: string }) => void;
  let rejectReply!: (failure: unknown) => void;
  const response = new Promise<{ result: any; etag: string }>((resolve, reject) => { resolveReply = resolve; rejectReply = reject; });
  await page.route(`**/api/market/${path}`, async route => {
    try {
      const reply = await route.fetch({ timeout: 360_000 });
      assert.equal(reply.status(), 200);
      const result = await reply.json();
      await route.fulfill({ response: reply });
      resolveReply({ result, etag: reply.headers().etag });
    } catch (failure) { rejectReply(failure); await route.abort(); }
  }, { times: 1 });
  return { reply: response };
}
async function calculate(page: Page) {
  const { reply } = await observePost(page, "calculate");
  await page.getByRole("button", { name: "Schockfall frisch berechnen", exact: true }).click();
  const { result, etag } = await reply;
  assert.equal(result.valid, true);
  assert.equal(etag, `"${result.content_digest}"`);
  await expect(page.getByTestId("shock-results")).toBeVisible({ timeout: 60_000 });
  return result;
}
async function capture(page: Page, info: any, name: string) {
  const directory = process.env.IMS_AP7_CAPTURE === "1" ? resolve("../docs/handbook/images") : info.outputDir;
  await mkdir(directory, { recursive: true });
  await page.screenshot({ path: resolve(directory, name) });
}

for (const caseId of ["us_hyperscaler_outage", "google_motor_entry", "life_demand_shock", "dora_2_workshop"]) {
  test(`AP7 ${caseId}: realer 100er-Lauf, Erhaltung, Prefix und sichtbare Wirkung`, async ({ page }, info) => {
    test.setTimeout(480_000);
    const errors: string[] = [], external: string[] = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.route("**/*", route => {
      const url = new URL(route.request().url());
      if (!["127.0.0.1", "localhost"].includes(url.hostname)) { external.push(url.hostname); return route.abort(); }
      return route.continue();
    });
    const { panel, source } = await load(page, caseId, 100);
    const started = Date.now();
    const result = await calculate(page);
    const elapsed = (Date.now() - started) / 1000;
    assert.deepEqual(result.shock_bundle, source);
    assert.equal(result.period_count, 100);
    assert.equal(result.source_input.insurers.length, caseId === "google_motor_entry" ? 41 : 40);
    assert.equal(result.reference.german_direct_selection_verified, false);
    const byteLength = Buffer.byteLength(JSON.stringify(result), "utf8");
    assert.ok(byteLength <= 64 * 1024 * 1024);
    for (const side of ["baseline", "variant"]) {
      const vu = rows(result, side, "vu_rows"), process = rows(result, side, "ict_process_rows");
      const previous = new Map<string, Row>();
      for (const row of vu) {
        const key = `${row.insurer_id}/${row.sector_id}`, before = previous.get(key);
        if (before) for (const stock of ["assets", "liabilities", "equity"]) assert.equal(row[`opening_${stock}`], before[`closing_${stock}`]);
        previous.set(key, row);
      }
      for (const row of vu) assert.equal(amountUnits(row.closing_assets), amountUnits(row.closing_liabilities) + amountUnits(row.closing_equity));
      for (const row of process) assert.equal(row.opening_queue + row.arrivals, row.completed + row.closing_queue);
      for (const row of rows(result, side, "ict_resource_rows")) assert.equal(amountUnits(row.processed_work) <= amountUnits(row.capacity_work), true);
      for (const total of rows(result, side, "market_rows").filter(row => row.sector_id === "total")) {
        for (const key of ["closing_assets", "closing_liabilities", "closing_equity", "premium_income", "operating_expense", "measure_cost"]) assert.equal(vu.filter(row => row.period === total.period).reduce((sum, row) => sum + amountUnits(row[key]), 0n), amountUnits(total[key]));
      }
      for (const name of ["family_rows", "insurance_group_rows"]) for (const period of [21, 100]) {
        const partition = rows(result, side, name).filter(row => row.period === period && row.sector_id === "total");
        const total = rows(result, side, "market_rows").find(row => row.period === period && row.sector_id === "total")!;
        for (const stock of ["assets", "liabilities", "equity"]) assert.equal(partition.reduce((sum, row) => sum + amountUnits(row[`closing_${stock}`]), 0n), amountUnits(total[`closing_${stock}`]));
      }
      const choices = rows(result, side, "customer_decisions");
      for (const row of choices) {
        const cohort = source.model_input.customer_groups.find((item: any) => item.group_id === row.group_id)!;
        assert.equal(amountUnits(row.risk_loss), amountUnits(cohort.risk_periods[row.period - 1].loss));
      }
      for (const period of [21, 100]) for (const sector of ["motor", "property_liability"]) {
        const coveredRisk = choices.filter(row => row.period === period && row.sector_id === sector && row.insured).reduce((sum, row) => sum + amountUnits(row.risk_loss), 0n);
        assert.equal(vu.filter(row => row.period === period && row.sector_id === sector).reduce((sum, row) => sum + amountUnits(row.insurance_expense), 0n), coveredRisk);
      }
      const costs = rows(result, side, "cost_rows"), groups = new Map<string, Row[]>();
      for (const row of costs) { const key = `${row.cost_id}/${row.period}`; groups.set(key, [...(groups.get(key) || []), row]); }
      for (const distributed of groups.values()) assert.equal(distributed.reduce((sum, row) => sum + amountUnits(row.amount), 0n), amountUnits(distributed[0].total_cost));
    }
    const shorter = await page.request.post("/api/market/shock-case", { data: { case_id: caseId, period_count: 25 } });
    const prefix = await page.request.post("/api/market/calculate", { data: (await shorter.json()).shock_bundle, timeout: 180_000 });
    const checked = await prefix.json();
    assert.equal(checked.valid, true);
    for (const side of ["baseline", "variant"]) for (const name of ["vu_rows", "market_rows", "customer_decisions", "ict_process_rows", "life_demand_rows"]) assert.deepEqual(rows(result, side, name).filter(row => row.period <= 25), rows(checked, side, name));
    await panel.getByRole("button", { name: "P100 · Horizont", exact: true }).click();
    const total = (side: string) => rows(result, side, "market_rows").find(row => row.period === 100 && row.sector_id === "total")!;
    await expect(panel.getByTestId("shock-equity-difference")).toHaveText(amountText(amountUnits(total("variant").closing_equity) - amountUnits(total("baseline").closing_equity), true));
    await panel.getByRole("button", { name: "P21 · Schock", exact: true }).click();
    if (caseId === "us_hyperscaler_outage") {
      const base = rows(result, "baseline", "ict_resource_rows").find(row => row.period === 21)!;
      const variant = rows(result, "variant", "ict_resource_rows").find(row => row.period === 21)!;
      assert.equal(base.capacity_work, "0.0000"); assert.equal(variant.capacity_work, "96.0000");
      await expect(panel.getByTestId("shock-dependencies").locator(".failed")).toHaveCount(4);
      await expect(panel.locator(".shock-path-proof")).toContainText("eu-iam");
      await panel.locator(".shock-path-proof").scrollIntoViewIfNeeded();
      await capture(page, info, "ap7_us_path_100_light_1440x900.png");
    } else if (caseId === "life_demand_shock") {
      assert.equal(rows(result, "baseline", "life_demand_rows")[20].willing, 1);
      assert.equal(rows(result, "variant", "life_demand_rows")[20].willing, 2);
      await expect(panel.getByTestId("shock-life-flow")).toContainText("2 kaufwillig");
    } else if (caseId === "google_motor_entry") {
      const extra = rows(result, "variant", "vu_rows").filter(row => row.insurer_id === 1_000_000);
      assert.equal(extra[19].active_in_period, false); assert.equal(extra[20].active_in_period, true);
      assert.equal(extra.reduce((sum, row) => sum + amountUnits(row.capital_contribution), 0n), amountUnits("100000"));
    } else {
      assert.equal(rows(result, "baseline", "ict_resource_rows")[20].capacity_work, "48.0000");
      assert.equal(rows(result, "variant", "ict_resource_rows")[20].capacity_work, "96.0000");
    }
    await panel.locator(".shock-plots").scrollIntoViewIfNeeded();
    await capture(page, info, `ap7_${caseId}_100_light_1440x900.png`);
    await expect(page.locator(".sidebar")).toContainText(`Release ${releaseVersion}`);
    assert.deepEqual(errors, []); assert.deepEqual(external, []);
    await info.attach("AP7 real 100", { body: JSON.stringify({ caseId, elapsed_seconds: elapsed, wire_bytes: byteLength, digest: result.content_digest, prefix_25: "passed", conservation: "passed", risk_and_partitions: "passed", row_counts: Object.fromEntries(Object.keys(result.sides.variant).map(name => [name, result.sides.variant[name].rows.length])), period_100: { baseline: total("baseline"), variant: total("variant") }, resources_21: { baseline: rows(result, "baseline", "ict_resource_rows")[20], variant: rows(result, "variant", "ict_resource_rows")[20] } }), contentType: "application/json" });
  });
}

test("AP7: eigene Sitzung, abhängiger Q-Pfad, entwertetes Ergebnis, JSON und Google-Excel", async ({ page }, info) => {
  test.setTimeout(240_000);
  const { panel } = await load(page);
  await expect(panel.getByLabel("Ersatzpfad", { exact: true })).toBeDisabled();
  await panel.getByRole("button", { name: "Als eigene Schocksitzung übernehmen", exact: true }).click();
  await panel.getByLabel("Ersatzpfad", { exact: true }).selectOption("q-dependent");
  const dependent = await calculate(page);
  assert.equal(rows(dependent, "variant", "ict_resource_rows")[20].capacity_work, "0.0000");
  await expect(panel.locator(".shock-path-proof")).toContainText("fällt mit ap7-shock aus");
  await panel.locator(".shock-path-proof").scrollIntoViewIfNeeded();
  await capture(page, info, "ap7_dependent_q_25_light_1440x900.png");
  const saved = page.waitForEvent("download");
  await panel.getByRole("button", { name: "AP7-Bündel als JSON sichern", exact: true }).click();
  const path = (await (await saved).path())!;
  assert.deepEqual(JSON.parse(await readFile(path, "utf8")), dependent.shock_bundle);
  await panel.getByLabel("Schockdauer in Stunden", { exact: true }).fill("48");
  await expect(panel.getByTestId("shock-results")).toHaveCount(0);
  await panel.getByText("Vollständiges portables Schockbündel und Ereignisfolge", { exact: true }).click();
  const invalid = structuredClone(dependent.shock_bundle);
  invalid.events[0].start_hour = "96";
  await panel.getByLabel("AP7-Quellenbündel JSON", { exact: true }).fill(JSON.stringify(invalid));
  await panel.getByRole("button", { name: "AP7-JSON übernehmen und prüfen", exact: true }).click();
  await expect(panel.getByRole("alert")).toBeVisible();
  await expect(panel.getByTestId("shock-results")).toHaveCount(0);
  await page.reload();
  await panel.getByLabel("AP7-Sitzung aus JSON laden", { exact: true }).setInputFiles(path);
  await expect(panel.getByTestId("shock-original")).toContainText("Eigene bearbeitbare Sitzung");
  assert.equal((await calculate(page)).content_digest, dependent.content_digest);
  await load(page, "google_motor_entry"); await calculate(page);
  await panel.getByLabel("Erklär-VU", { exact: true }).selectOption("1000000");
  const exported = page.waitForEvent("download");
  const reply = page.waitForResponse(r => r.url().endsWith("/api/market/export.xlsx"));
  await panel.getByRole("button", { name: "Erklär-VU in Excel sichern", exact: true }).click();
  assert.equal((await reply).status(), 200); expect((await exported).suggestedFilename()).toContain("VU1000000");
  const help = await page.context().newPage();
  await help.goto("/api/seminar/handbook/market_ap7.html");
  await expect(help.getByRole("heading", { level: 1 })).toContainText("Schockfälle");
  await expect(help.locator("body")).toContainText("US-IAM");
  const images = await help.locator("img").evaluateAll(items => items.map(item => item.getAttribute("src")!));
  assert.equal(images.length, 8);
  for (const image of images) {
    const reply = await help.request.get(`/api/seminar/handbook/${image}`);
    assert.equal(reply.status(), 200);
    assert.ok(reply.headers()["content-type"].startsWith("image/png"));
    assert.ok((await reply.body()).length > 1000);
  }
  await help.close();
});

for (const viewport of [{ width: 1440, height: 900 }, { width: 1024, height: 768 }, { width: 390, height: 844 }]) for (const theme of ["light", "dark"] as const) {
  test(`AP7 ${viewport.width}×${viewport.height} ${theme}: ICT-Erklärung, Kontrast, Tastatur`, async ({ page }, info) => {
    test.setTimeout(120_000);
    await page.setViewportSize(viewport);
    await page.addInitScript(value => localStorage.setItem("ims.theme", value), theme);
    const { panel } = await load(page); await calculate(page);
    await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
    await panel.getByLabel("Rollenfokus", { exact: true }).selectOption("cio");
    await expect(panel.locator(".shock-focus")).toBeFocused();
    await panel.getByLabel("Erklärseite", { exact: true }).focus(); await page.keyboard.press("Tab");
    expect(await page.evaluate(() => document.activeElement?.tagName)).not.toBe("BODY");
    const report = await new AxeBuilder({ page }).include('[data-testid="market-shock-workbench"]').withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze();
    assert.deepEqual(report.violations, []);
    const ratios = report.passes.filter(v => v.id === "color-contrast").flatMap(v => v.nodes.flatMap(n => n.any.map(c => (c.data as { contrastRatio?: number } | null)?.contrastRatio).filter((r): r is number => typeof r === "number")));
    expect(ratios.length).toBeGreaterThan(0); expect(Math.min(...ratios)).toBeGreaterThanOrEqual(4.5);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true);
    await panel.getByTestId("shock-dependencies").scrollIntoViewIfNeeded();
    await capture(page, info, `ap7_ict_${theme}_${viewport.width}x${viewport.height}.png`);
    await info.attach("AP7 Kontrast", { body: JSON.stringify({ viewport, theme, minimumContrast: Math.min(...ratios), checkedTextNodes: ratios.length }), contentType: "application/json" });
  });
}
