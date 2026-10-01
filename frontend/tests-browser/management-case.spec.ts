import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFile } from "node:fs/promises";

for (const viewport of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
  for (const theme of ["light", "dark"]) {
    test(`Gemeinsame Bilanz ${viewport.width} ${theme}: 100er, Quellen, Exporte, Kapital`, async ({ page }, info) => {
      const serverErrors: string[] = [];
      page.on("response", response => { if (response.status() >= 500 && response.url().includes("/api/")) serverErrors.push(`${response.status()} ${response.url()}`); });
      await page.setViewportSize(viewport);
      await page.addInitScript(value => localStorage.setItem("ims.theme", value), theme);
      await page.goto("/#management");
      const workbench = page.getByTestId("management-case-workbench");
      await workbench.getByRole("button", { name: "Gemeinsame Quellen erzeugen", exact: true }).click();
      const calculate = workbench.getByRole("button", { name: "Vier Sparten gemeinsam berechnen", exact: true });
      await expect(calculate).toBeDisabled();
      await workbench.getByRole("checkbox", { name: "Die wirtschaftliche Zusammengehörigkeit dieser Quellen und Varianten ist ausdrücklich erklärt.", exact: true }).check();
      await calculate.click();
      await expect(workbench.getByTestId("management-case-results")).toBeVisible();
      await workbench.getByLabel("Management Ergebnisperiode", { exact: true }).selectOption("100");
      await expect(workbench.getByRole("region", { name: "Management Modellbilanz" }).getByText("87500,0000", { exact: true })).toHaveCount(1);
      const digest = await workbench.getByTestId("management-case-results").locator("code").innerText();
      for (const [label, extension] of [["Management JSON", "json"], ["Management CSV", "csv"], ["Management Excel", "xlsx"]]) {
        const downloaded = page.waitForEvent("download");
        await workbench.getByRole("button", { name: label, exact: true }).click();
        const download = await downloaded;
        expect(download.suggestedFilename()).toBe(`IMS-Management-${digest.slice(0, 12)}.${extension}`);
        const bytes = await readFile((await download.path())!);
        if (extension === "json") expect(JSON.parse(bytes.toString()).content_digest).toBe(digest);
        else if (extension === "csv") expect(bytes.toString()).toContain(digest);
        else expect(bytes.subarray(0, 2).toString()).toBe("PK");
      }
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
      expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
      await page.screenshot({ path: info.outputPath(`management-${viewport.width}-${theme}.png`) });
      await page.getByRole("link", { name: "Ergebnisse", exact: true }).click();
      await expect(workbench.getByTestId("management-case-results")).toBeVisible();
      await expect(calculate).toBeHidden();
      await expect(page.locator(".results-empty")).toBeHidden();
      await page.getByRole("link", { name: "Simulation", exact: true }).click();
      await workbench.getByRole("link", { name: "Kapitalwirkung dieser geprüften Quelle", exact: true }).click();
      const capital = page.getByTestId("capital-workbench");
      await expect(capital.getByRole("button", { name: "Kapitalwirkung berechnen", exact: true })).toBeVisible();
      await capital.getByRole("combobox", { name: "Modellperiode", exact: true }).selectOption("100");
      await capital.getByRole("checkbox").check();
      await capital.getByRole("button", { name: "Kapitalwirkung berechnen", exact: true }).click();
      await expect(capital.getByTestId("capital-results")).toBeVisible();
      await expect(capital.getByTestId("capital-regulatory")).toContainText("gesperrt");
      await page.getByRole("link", { name: "100er-Gesamtbilanz", exact: true }).click();
      await workbench.getByText("Expertenmodus: vier Sparten und gemeinsame Quellen", { exact: true }).click();
      const editor = workbench.getByLabel("Management Quellenvertrag", { exact: true });
      const source = JSON.parse(await editor.inputValue());
      source.sides.variant.four_sector_input.sectors.motor.periods[0].premium_income = "250";
      await editor.fill(JSON.stringify(source));
      await expect(workbench.getByTestId("management-case-results")).toHaveCount(0);
      await page.getByRole("link", { name: "Ergebnisse", exact: true }).click();
      await expect(page.locator(".results-empty")).toBeVisible();
      await page.getByRole("link", { name: "Simulation", exact: true }).click();
      await workbench.getByRole("checkbox").check();
      const rebind = workbench.getByRole("button", { name: "Geänderte Quellen prüfen und neu binden", exact: true });
      await rebind.click();
      await expect(rebind).toHaveCount(0);
      await workbench.getByRole("checkbox").check();
      await calculate.click();
      await expect(workbench.getByTestId("management-case-results")).toBeVisible();
      await editor.fill("{");
      await workbench.getByRole("checkbox").check();
      await workbench.getByRole("button", { name: "Geänderte Quellen prüfen und neu binden", exact: true }).click();
      await expect(workbench.getByRole("alert")).toBeVisible();
      await expect(workbench.getByTestId("management-case-results")).toHaveCount(0);
      expect(serverErrors).toEqual([]);
    });
  }
}
