import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFile } from "node:fs/promises";

for (const viewport of [{ width: 1440, height: 900 }, { width: 1024, height: 768 }, { width: 390, height: 844 }]) {
  for (const theme of ["light", "dark"]) {
    test(`ICT ${viewport.width} ${theme}: 100 Perioden, Fehler, Zustand, Dossier`, async ({ page }, info) => {
      await page.setViewportSize(viewport);
      await page.addInitScript(value => localStorage.setItem("ims.theme", value), theme);
      await page.goto("/#ict");
      const workbench = page.getByTestId("ict-workbench");
      const calculate = workbench.getByRole("button", { name: "Baseline und ICT-Variante berechnen" });
      await expect(calculate).toBeVisible();
      await workbench.getByLabel("Stunden je ICT-Periode", { exact: true }).fill("0");
      await calculate.click();
      await expect(workbench.getByRole("alert")).toContainText("Bereich");
      await expect(workbench.getByTestId("ict-results")).toHaveCount(0);
      await workbench.getByLabel("Stunden je ICT-Periode", { exact: true }).fill("24");
      await calculate.click();
      await expect(workbench.getByTestId("ict-results")).toBeVisible();
      await workbench.getByLabel("ICT Ergebnisperiode", { exact: true }).selectOption("100");
      await expect(workbench.getByRole("region", { name: "ICT Modellbilanz" }).getByText("16769,6000", { exact: true })).toHaveCount(2);
      const digest = await workbench.locator(".ict-results code").innerText();
      for (const [label, extension] of [["Dossier JSON", "json"], ["Bilanz CSV", "csv"], ["Dossier Excel", "xlsx"]]) {
        const downloaded = page.waitForEvent("download");
        await workbench.getByRole("button", { name: label, exact: true }).click();
        const download = await downloaded;
        expect(download.suggestedFilename()).toBe(`IMS-ICT-${digest.slice(0, 12)}.${extension}`);
        const bytes = await readFile((await download.path())!);
        if (extension === "json") {
          const result = JSON.parse(bytes.toString("utf-8"));
          expect(result.content_digest).toBe(digest);
          expect(result.variant.balance_rows.at(-1).model_own_funds_proxy).toBe("16769.6000");
          expect(result.regulatory_metrics.scr).toBeNull();
        } else if (extension === "csv") {
          expect(bytes.toString("utf-8")).toContain(digest);
          expect(bytes.toString("utf-8")).toContain("16769.6000");
        } else expect(bytes.subarray(0, 2).toString()).toBe("PK");
      }
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
      expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
      await page.screenshot({ path: info.outputPath(`ict-${viewport.width}-${theme}.png`) });
      await page.getByRole("link", { name: "Übersicht", exact: true }).click();
      await page.getByRole("link", { name: "Simulation", exact: true }).click();
      await expect(workbench.getByTestId("ict-results")).toBeVisible();
      await workbench.getByLabel("ICT Gegenmaßnahme", { exact: true }).selectOption("fallback");
      await expect(workbench.getByTestId("ict-results")).toHaveCount(0);
      await calculate.click();
      await expect(workbench.getByTestId("ict-results")).toBeVisible();
      await workbench.getByText("Expertenmodus: vollständiger Quellenvertrag", { exact: true }).click();
      const editor = workbench.getByLabel("ICT Quellenvertrag", { exact: true });
      await editor.fill("{");
      await expect(calculate).toBeDisabled();
      await expect(workbench.getByTestId("ict-results")).toHaveCount(0);
      await workbench.getByRole("button", { name: "Experteneingabe prüfen und übernehmen" }).click();
      await expect(workbench.getByRole("alert")).toBeVisible();
      await expect(calculate).toBeDisabled();
    });
  }
}
