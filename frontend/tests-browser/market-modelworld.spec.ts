import {test,expect} from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

for (const theme of ["light","dark"]) for(const viewport of [{width:1440,height:900},{width:1024,height:768},{width:390,height:844}]) test(`AP8 Modellwelt und Portfolio verbinden dieselbe Quelle · ${theme} · ${viewport.width}`,async({page})=>{
  await page.setViewportSize(viewport);
  await page.addInitScript(theme=>localStorage.setItem("ims.theme",theme),theme);
  await page.goto("/#market");const panel=page.getByTestId("market-explorer-workbench");
  await panel.getByLabel("Analysefall",{exact:true}).selectOption("switch");
  await panel.getByLabel("Analyseperioden",{exact:true}).selectOption("10");
  await panel.getByRole("button",{name:"Analysevorlage laden",exact:true}).click();
  await expect(panel.getByTestId("explorer-source")).toBeVisible();
  await panel.getByRole("button",{name:"Modellwelt",exact:true}).click();
  const world=panel.getByTestId("model-world");await expect(world).toContainText("2 Anbieter");
  await expect(world).toContainText("Rechnung noch offen");
  await world.getByRole("button",{name:"Modellebene ICT & Geschäftsvorgänge",exact:true}).focus();await page.keyboard.press("Enter");
  await expect(world.getByRole("complementary")).toContainText("verschieben keine Schadenzahlungen");
  expect((await new AxeBuilder({page}).analyze()).violations).toEqual([]);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(viewport.width);
  await panel.getByRole("button",{name:"Unternehmen",exact:true}).click();const portfolio=panel.getByTestId("company-portfolio");
  await expect(portfolio).toContainText("Noch nicht gerechnet");
  await portfolio.getByLabel("VU 2 für Anzeigevergleich",{exact:true}).check();
  const second=portfolio.locator("tbody tr").nth(1).getByRole("button");await second.click();
  await portfolio.getByRole("button",{name:"Strategie bearbeiten",exact:true}).click();
  await expect(panel.getByLabel("Vorstands-VU",{exact:true})).toHaveValue("2");
  const response=page.waitForResponse(r=>r.url().endsWith("/api/market/explore"));
  await panel.getByRole("button",{name:"Marktansichten frisch berechnen",exact:true}).click();const result=await (await response).json();
  await expect(panel.getByTestId("explorer-results")).toBeVisible();await expect(panel.getByLabel("Fokus-VU",{exact:true})).toHaveValue("2");
  const digest=result.model_result_digest;let calls=0;page.on("request",r=>{if(r.url().endsWith("/api/market/explore"))calls++;});
  await panel.getByRole("button",{name:"Unternehmen",exact:true}).click();await expect(portfolio).not.toContainText("Noch nicht gerechnet");
  await expect(portfolio.getByLabel("VU 2 für Anzeigevergleich")).toBeChecked();
  await portfolio.getByLabel("Unternehmen suchen",{exact:true}).fill("no such company");await expect(portfolio).toContainText("Kein Unternehmen passt");
  await portfolio.getByLabel("Unternehmen suchen",{exact:true}).fill("");
  expect((await new AxeBuilder({page}).analyze()).violations).toEqual([]);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(viewport.width);
  await panel.getByRole("button",{name:"Laufansicht",exact:true}).click();const replay=panel.getByTestId("run-replay");
  await expect(replay).toContainText("Vollständiger Lauf bereits gerechnet");await replay.getByRole("button",{name:"Anzeige auf P1",exact:true}).click();
  await replay.getByRole("button",{name:"Eine Periode weiter",exact:true}).click();await expect(replay).toContainText("Anzeige P2 von 10");
  await replay.getByRole("button",{name:"Anzeige abspielen",exact:true}).click();await expect(replay).toContainText("Anzeige P3 von 10");
  await replay.getByRole("button",{name:"Anzeige pausieren",exact:true}).click();const p=await replay.getByRole("slider").last().inputValue();
  await page.waitForTimeout(1300);await expect(replay.getByRole("slider").last()).toHaveValue(p);
  expect((await new AxeBuilder({page}).analyze()).violations).toEqual([]);
  await panel.getByRole("button",{name:"04 Wirkung verstehen",exact:true}).click();await expect(panel.getByTestId("explorer-model-digest")).toHaveText(digest);expect(calls).toBe(0);
});

test("AP8 Offline-Rechenkern: drei lesbare SVGs und Eingabeinventar",async({request})=>{
  for(const name of ["rechenkern","eingabeinventar"]){const r=await request.get(`/api/seminar/handbook/${name}.html`);expect(r.status()).toBe(200);expect(await r.text()).toContain("Modellwährung");}
  for(const name of ["architecture","period","deviations"]){const r=await request.get(`/api/seminar/handbook/images/ap8_core_${name}.svg`);expect(r.status()).toBe(200);expect(r.headers()["content-type"]).toContain("image/svg+xml");expect(await r.text()).toContain("<svg");}
});

test("AP8 BaFin-Portfolio: Seiten und Suche verändern die geladene Quelle nicht",async({page})=>{
  await page.goto("/#market");const panel=page.getByTestId("market-explorer-workbench");
  await panel.getByLabel("Analysefall",{exact:true}).selectOption("bafin");
  await panel.getByLabel("Analyseperioden",{exact:true}).selectOption("10");
  await panel.getByRole("button",{name:"Analysevorlage laden",exact:true}).click();await expect(panel.getByTestId("explorer-source")).toBeVisible();
  await panel.getByRole("button",{name:"Unternehmen",exact:true}).click();const portfolio=panel.getByTestId("company-portfolio");
  await expect(portfolio.locator("tbody tr")).toHaveCount(8);await expect(portfolio).toContainText("Seite 1 von 5");
  await portfolio.getByLabel("VU 2012 für Anzeigevergleich").check();
  await portfolio.getByRole("button",{name:"Weiter",exact:true}).click();await expect(portfolio).toContainText("Seite 2 von 5");
  await portfolio.getByLabel("Unternehmen suchen",{exact:true}).fill("Allianz");await expect(portfolio.locator("tbody tr")).toHaveCount(1);
  await expect(portfolio).toContainText("Seite 1 von 1");await expect(portfolio.getByLabel("VU 2012 für Anzeigevergleich")).toBeChecked();
  await portfolio.getByRole("button",{name:"Strategie bearbeiten",exact:true}).click();
  await expect(panel.getByLabel("Vorstands-VU",{exact:true})).toHaveValue("2012");
  await expect(panel.getByLabel("Vorstand: Angebotspreis · Modellwährung",{exact:true})).toBeDisabled();
  await expect(panel.getByTestId("explorer-source")).toHaveText("Schreibfreie Vorlage geladen");
});
