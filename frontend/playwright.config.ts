import { defineConfig } from "@playwright/test";
import { join, resolve } from "node:path";
import { tmpdir } from "node:os";

const root = resolve("..");
const python = join(root, ".venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
const baseURL = process.env.IMS_BASE_URL || "http://127.0.0.1:48192/";
export default defineConfig({
  testDir: "./tests-browser",
  outputDir: "../.tmp-pr-ap2/browser-results",
  timeout: 90_000,
  expect: { timeout: 15_000 },
  workers: 1,
  retries: 0,
  reporter: [["list"], ["json", { outputFile: "../.tmp-pr-ap2/browser-report.json" }]],
  use: { baseURL, viewport: { width: 1440, height: 900 }, trace: "retain-on-failure", screenshot: "only-on-failure", acceptDownloads: true },
  webServer: process.env.IMS_BASE_URL ? undefined : {
    command: `"${python}" -m ims.desktop.launcher --headless --no-browser --port 48192 --data-dir "${join(tmpdir(), `ims-ap2-browser-${process.pid}`)}"`,
    cwd: root, url: baseURL + "api/health", reuseExistingServer: false, timeout: 60_000,
  },
});
