import { test, expect } from "@playwright/test";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { resolve } from "node:path";
import { mkdir } from "node:fs/promises";

const run = promisify(execFile);
for (const script of ["health_workbench_pr169d.mjs", "four_sector_balance_pr170a.mjs", "solvency_capital_pr178.mjs"]) {
  test(`Vorhandener Modellnachweis: ${script}`, async ({ baseURL }, testInfo) => {
    test.setTimeout(150_000);
    await mkdir(testInfo.outputDir, { recursive: true });
    const result = await run(process.execPath, [resolve("../tests/browser", script)], {
      cwd: resolve(".."), timeout: 140_000,
      env: { ...process.env, IMS_BASE_URL: baseURL!, IMS_SCREENSHOT_DIR: testInfo.outputDir },
    });
    expect(result.stdout).toContain("browser smoke passed");
    await testInfo.attach("Modellnachweis", { body: result.stdout, contentType: "text/plain" });
  });
}
