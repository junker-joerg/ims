import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFile } from "node:fs/promises";

for (const viewport of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
  for (const theme of ["light", "dark"]) {
    test(`Modernes Seminar ${viewport.width} ${theme}: Entscheidung, Exposition, Bilanz und Bündel`, async ({ page }, info) => {
      test.setTimeout(240_000);
      const errors: string[] = [];
      page.on("response", response => { if (response.status() >= 500 && response.url().includes("/api/")) errors.push(`${response.status()} ${response.url()}`); });
      await page.setViewportSize(viewport);
      await page.addInitScript(value => localStorage.setItem("ims.theme", value), theme);
      await page.goto("/#seminar");
      const workbench = page.getByTestId("seminar-workbench");
      await workbench.getByRole("button", { name: "Seminarfall laden", exact: true }).click();
      const calculate = workbench.getByRole("button", { name: "Moderne Kopplung berechnen", exact: true });
      await expect(calculate).toBeDisabled();
      await workbench.getByRole("checkbox", { name: "Die modernen Einheiten, Gruppen und exogenen Annahmen dieses Falls sind erklärt.", exact: true }).check();
      await calculate.click();
      await expect(workbench.getByTestId("seminar-results")).toBeVisible();
      await expect(workbench.getByText("Preis 3,6000 × gedeckte Exposition 0,0000 = gebuchte Prämie 0,0000. Werbeaufwand 2,0000.", { exact: true })).toBeVisible();
      await workbench.getByTestId("seminar-results").screenshot({ path: info.outputPath(`seminar-decision-${viewport.width}-${theme}.png`) });
      await workbench.getByLabel("Seminar-Ergebnisperiode", { exact: true }).selectOption("100");
      await expect(workbench.getByRole("region", { name: "Seminar Modellbilanz" }).getByText("87325,7633", { exact: true })).toHaveCount(1);
      const digest = await workbench.getByTestId("seminar-results").locator("code").innerText();
      const overflow = await page.evaluate(() => ({ width: innerWidth, document: document.documentElement.scrollWidth, controls: [...document.querySelectorAll("input,select,fieldset")].filter(item => item.getBoundingClientRect().right > innerWidth && item.getBoundingClientRect().width > 0).map(item => ({ label: item.getAttribute("aria-label"), width: item.getBoundingClientRect().width, right: item.getBoundingClientRect().right })) }));
      expect(overflow.document, JSON.stringify(overflow)).toBeLessThanOrEqual(overflow.width);
      expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
      await page.screenshot({ path: info.outputPath(`seminar-${viewport.width}-${theme}.png`) });
      await page.getByRole("link", { name: "Ergebnisse", exact: true }).click();
      await expect(workbench.getByTestId("seminar-results")).toBeVisible();
      await expect(calculate).toBeHidden();
      await page.getByRole("link", { name: "Modellwerkzeuge", exact: true }).click();
      if (viewport.width === 1440 && theme === "light") {
        for (const [label, extension] of [["Strategie JSON", "json"], ["Strategie CSV", "csv"], ["Strategie Excel", "xlsx"]]) {
          const downloaded = page.waitForEvent("download"); await workbench.getByRole("button", { name: label, exact: true }).click();
          const download = await downloaded; expect(download.suggestedFilename()).toBe(`IMS-Strategie-${digest.slice(0, 12)}.${extension}`);
          const content = await readFile((await download.path())!);
          if (extension === "json") expect(JSON.parse(content.toString()).content_digest).toBe(digest);
          else if (extension === "csv") expect(content.toString()).toContain(digest);
          else expect(content.subarray(0, 2).toString()).toBe("PK");
        }
        const downloaded = page.waitForEvent("download"); await workbench.getByRole("button", { name: "Portables Seminarbündel", exact: true }).click();
        const bundleFile = await (await downloaded).path();
        await workbench.getByLabel("Portables Seminarbündel importieren", { exact: true }).setInputFiles(bundleFile!);
        await expect(workbench.getByRole("status")).toContainText("Demomodus", { timeout: 30_000 });
        await expect(workbench.getByLabel("Seminarfall", { exact: true })).toBeDisabled();
        await expect(workbench.getByTestId("seminar-results").locator("code")).toHaveText(digest);
        await workbench.screenshot({ path: info.outputPath("seminar-demo-1440-light.png") });
        await workbench.getByRole("button", { name: "Als bearbeitbare Sitzung übernehmen", exact: true }).click();
        await workbench.getByRole("button", { name: "ICT- und 100er-Quellen bereitstellen", exact: true }).click();
        await workbench.getByRole("link", { name: "Kapitalwirkung des Seminarfalls", exact: true }).click();
        const capital = page.getByTestId("capital-workbench");
        await capital.getByRole("combobox", { name: "Modellperiode", exact: true }).selectOption("100");
        await capital.getByRole("checkbox").check(); await capital.getByRole("button", { name: "Kapitalwirkung berechnen", exact: true }).click();
        await expect(capital.getByTestId("capital-results")).toBeVisible();
        await expect(capital.locator(".capital-summary > div").filter({ has: page.getByText("Netto-Stress", { exact: true }) }).locator("strong")).toHaveText("150,0000");
        await expect(capital.locator(".capital-summary > div").filter({ has: page.getByText("Restproxy", { exact: true }) }).locator("strong")).toHaveText("87175,7633");
        await expect(capital.getByTestId("capital-regulatory")).toContainText("gesperrt");
        await capital.getByTestId("capital-results").screenshot({ path: info.outputPath("seminar-model-capital-1440-light.png") });
        if (!await page.getByRole("link", { name: "ICT-Wirkung", exact: true }).isVisible()) await page.getByText("Weitere Modellwerkzeuge", { exact:true }).click();
        await page.getByRole("link", { name: "ICT-Wirkung", exact: true }).click();
        const ict = page.getByTestId("ict-workbench");
        await ict.getByRole("button", { name: "Baseline und ICT-Variante berechnen", exact: true }).click();
        await expect(ict.getByTestId("ict-results")).toBeVisible();
        await page.getByRole("link", { name: "100-Perioden-Lauf", exact: true }).click();
        const wizard = page.getByTestId("guided-chain-workbench");
        await wizard.getByRole("button", { name: "Alle Periodenkontexte prüfen", exact: true }).click();
        await expect(wizard.getByTestId("guided-chain-checked")).toBeVisible();
        await wizard.getByRole("checkbox", { name: "Die geprüften Kandidaten und Ketten unveränderlich lokal speichern.", exact: true }).check();
        const saved = page.waitForResponse(response => response.url().endsWith("/api/strategies/guided-period-chain/store") && response.request().method() === "POST");
        await wizard.getByRole("button", { name: "Geprüftes Bündel atomar speichern", exact: true }).click();
        const stored = await (await saved).json();
        await wizard.getByRole("checkbox", { name: "Referenzläufe 1–2 und 1–5 ausführen und ihre unveränderlichen Ergebnisse speichern; vorhandene Nachweise erneut prüfen.", exact: true }).check();
        await wizard.getByRole("button", { name: "Referenzläufe kontrolliert vorbereiten", exact: true }).click();
        await expect(wizard.getByTestId("guided-prefix-ready")).toBeVisible();
        const runner = page.getByRole("region", { name: "Kontrollierter 100-Perioden-Lauf", exact: true });
        await runner.getByTestId("hundred-chain-select").selectOption(stored.chains.find((c: { period_count: number }) => c.period_count === 100).chain_id);
        await runner.getByTestId("hundred-prefix-select").selectOption(stored.chains.find((c: { period_count: number }) => c.period_count === 5).chain_id);
        await runner.getByTestId("hundred-run-confirm").check(); await runner.getByTestId("hundred-run-start").click();
        await expect(runner.getByTestId("hundred-result")).toBeVisible();
        const zipDownload = page.waitForEvent("download"); await runner.getByTestId("hundred-download").click();
        expect((await zipDownload).suggestedFilename()).toBe("ims-100-perioden.zip");
        await page.getByRole("link", { name: "Managementseminar", exact: true }).click();
        await workbench.getByText("Expertenmodus: vollständige Gruppen, Ziehungen und Quellen", { exact: true }).click();
        await workbench.getByLabel("Moderne Seminarquellen", { exact: true }).fill("{");
        await expect(workbench.getByTestId("seminar-results")).toHaveCount(0);
        await workbench.getByRole("checkbox").check(); await calculate.click();
        await expect(workbench.getByRole("alert")).toBeVisible();
        // A damaged import must invalidate the previously calculated result.
        await workbench.getByLabel("Portables Seminarbündel importieren", { exact: true }).setInputFiles({ name: "broken.json", mimeType: "application/json", buffer: Buffer.from('{"schema_version":"unknown"}') });
        await expect(workbench.getByRole("alert")).toContainText("Vollständige");
        await expect(workbench.getByTestId("seminar-results")).toHaveCount(0);
        for (const caseId of ["inflation", "capital"]) {
          await workbench.getByLabel("Seminarfall", { exact: true }).selectOption(caseId);
          await workbench.getByRole("button", { name: "Seminarfall laden", exact: true }).click();
          await workbench.getByRole("checkbox").check(); await calculate.click();
          await expect(workbench.getByTestId("seminar-results")).toBeVisible();
          await workbench.getByLabel("Seminar-Ergebnisperiode", { exact: true }).selectOption("100");
          await expect(workbench.getByRole("region", { name: "Seminar Modellbilanz" }).getByText(caseId === "inflation" ? "118865,7633" : "117045,6230", { exact: true })).toHaveCount(1);
          await workbench.getByTestId("seminar-results").screenshot({ path: info.outputPath(`seminar-case-${caseId}-1440-light.png`) });
          if (caseId === "capital") {
            await workbench.getByRole("link", { name: "Kapitalwirkung des Seminarfalls", exact: true }).click();
            await capital.getByRole("checkbox").check();
            await capital.getByRole("button", { name: "Kapitalwirkung berechnen", exact: true }).click();
            await expect(capital.locator(".capital-summary > div").filter({ has: page.getByText("Netto-Stress", { exact: true }) }).locator("strong")).toHaveText("550,0000");
            await expect(capital.locator(".capital-breakdown > div").filter({ has: page.getByText("Nettoverlust innerhalb Grenze", { exact: true }) }).locator("strong")).toHaveText("Nein");
            await capital.getByTestId("capital-results").screenshot({ path: info.outputPath("seminar-pressure-1440-light.png") });
            await page.getByRole("link", { name: "Managementseminar", exact: true }).click();
          }
        }
        await workbench.getByRole("button", { name: "Kuratierte Demo öffnen", exact: true }).click();
        await expect(workbench.getByRole("status")).toContainText("Demomodus", { timeout: 30_000 });
        await expect(workbench.getByLabel("Seminarfall", { exact: true })).toHaveValue("capital");
        await page.goto("/api/seminar/handbook/seminar_ap3.html");
        await expect(page.getByRole("heading", { name: "Managementseminar mit AP3", exact: true })).toBeVisible();
        for (const figure of await page.locator("img").all()) {
          await figure.scrollIntoViewIfNeeded();
          await expect(figure).toBeVisible();
          expect(await figure.evaluate(element => (element as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);
        }
        await page.screenshot({ path: info.outputPath("seminar-handbook-1440-light.png"), fullPage: true });
      } else {
        await workbench.getByLabel("Strategie Preisfaktor", { exact: true }).fill("6");
        await expect(workbench.getByTestId("seminar-results")).toHaveCount(0);
        await workbench.getByRole("button", { name: "Zuordnung für Variante übernehmen", exact: true }).click();
        await workbench.getByRole("checkbox").check(); await calculate.click();
        await expect(workbench.getByText("Preis 3,0000 × gedeckte Exposition 100,0000 = gebuchte Prämie 300,0000. Werbeaufwand 2,0000.", { exact: true })).toBeVisible();
      }
      expect(errors).toEqual([]);
    });
  }
}
