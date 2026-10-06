import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFile } from "node:fs/promises";

for (const viewport of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
  for (const theme of ["light", "dark"]) {
    test(`Geführter 100er ${viewport.width} ${theme}: frische Kette, Prefix, Lauf, ZIP`, async ({ page }, info) => {
      const serverErrors: string[] = [];
      page.on("response", response => { if (response.status() >= 500 && response.url().includes("/api/")) serverErrors.push(`${response.status()} ${response.url()}`); });
      await page.setViewportSize(viewport);
      await page.addInitScript(value => localStorage.setItem("ims.theme", value), theme);
      await page.goto("/#hundred");
      const wizard = page.getByTestId("guided-chain-workbench");
      await wizard.getByLabel("100er Seed", { exact: true }).fill(String(viewport.width + (theme === "dark" ? 1 : 0)));
      await wizard.getByLabel("100er Laufindex", { exact: true }).fill("0");
      await wizard.getByRole("button", { name: "100 vollständige Kontexte erzeugen", exact: true }).click();
      await wizard.getByRole("button", { name: "Alle Periodenkontexte prüfen", exact: true }).click();
      await expect(wizard.getByTestId("guided-chain-checked")).toBeVisible();
      const store = wizard.getByRole("button", { name: "Geprüftes Bündel atomar speichern", exact: true });
      await expect(store).toBeDisabled();
      await wizard.getByRole("checkbox", { name: "Die geprüften Kandidaten und Ketten unveränderlich lokal speichern.", exact: true }).check();
      const saved = page.waitForResponse(response => response.url().endsWith("/api/strategies/guided-period-chain/store") && response.request().method() === "POST");
      await store.click();
      const stored = await (await saved).json();
      await expect(wizard.getByTestId("guided-chain-stored")).toBeVisible();
      await wizard.getByRole("checkbox", { name: "Referenzläufe 1–2 und 1–5 ausführen und ihre unveränderlichen Ergebnisse speichern; vorhandene Nachweise erneut prüfen.", exact: true }).check();
      await wizard.getByRole("button", { name: "Referenzläufe kontrolliert vorbereiten", exact: true }).click();
      await expect(wizard.getByTestId("guided-prefix-ready")).toBeVisible();
      const runner = page.getByRole("region", { name: "Kontrollierter 100-Perioden-Lauf", exact: true });
      await runner.getByTestId("hundred-chain-select").selectOption(stored.chains.find((chain: { period_count: number }) => chain.period_count === 100).chain_id);
      await runner.getByTestId("hundred-prefix-select").selectOption(stored.chains.find((chain: { period_count: number }) => chain.period_count === 5).chain_id);
      const button = runner.getByTestId("hundred-run-start");
      await expect(button).toBeDisabled();
      await runner.getByTestId("hundred-run-confirm").check();
      await expect(button).toBeEnabled();
      await button.click();
      await expect(runner.getByTestId("hundred-result")).toBeVisible();
      await expect(runner.locator(".hundred-table tbody tr")).toHaveCount(100);
      const downloaded = page.waitForEvent("download");
      await runner.getByTestId("hundred-download").click();
      const download = await downloaded;
      expect(download.suggestedFilename()).toBe("ims-100-perioden.zip");
      expect((await readFile((await download.path())!)).subarray(0, 2).toString()).toBe("PK");
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
      expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
      await page.screenshot({ path: info.outputPath(`guided-${viewport.width}-${theme}.png`) });
      await runner.getByTestId("hundred-result").screenshot({ path: info.outputPath(`guided-result-${viewport.width}-${theme}.png`) });
      await page.getByRole("link", { name: "Übersicht", exact: true }).click();
      await page.getByRole("link", { name: "Modellwerkzeuge", exact: true }).click();
      await expect(runner.getByTestId("hundred-result")).toBeVisible();
      await wizard.getByText("Expertenmodus: alle Periodenkontexte, Schocks und Zuweisungen", { exact: true }).click();
      await wizard.getByLabel("100er Quellenvertrag", { exact: true }).fill("{");
      await expect(wizard.getByTestId("guided-chain-stored")).toHaveCount(0);
      await wizard.getByRole("button", { name: "Alle Periodenkontexte prüfen", exact: true }).click();
      await expect(wizard.getByRole("alert")).toBeVisible();
      await expect(wizard.getByTestId("guided-chain-checked")).toHaveCount(0);
      expect(serverErrors).toEqual([]);
    });
  }
}
