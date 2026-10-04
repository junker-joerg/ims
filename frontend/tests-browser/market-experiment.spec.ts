import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { decodeResult } from "../src/marketExplorerPresentation";

async function open(page:Page,caseId="switch",periods="10") {
  await page.goto("/#market");const panel=page.getByTestId("market-explorer-workbench");
  await panel.getByLabel("Analysefall",{exact:true}).selectOption(caseId);
  await panel.getByLabel("Analyseperioden",{exact:true}).selectOption(periods);
  const reply=page.waitForResponse(r=>r.url().endsWith("/api/market/"+(caseId==="switch"?"workshop-case":"shock-case")));
  await panel.getByRole("button",{name:"Analysevorlage laden",exact:true}).click();await reply;
  await expect(panel.getByTestId("explorer-source")).toBeVisible();return panel;
}
async function run(page:Page) {
  const response=page.waitForResponse(r=>r.url().endsWith("/api/market/explore"));
  await page.getByRole("button",{name:"Marktansichten frisch berechnen",exact:true}).click();
  const reply=await response;expect(reply.status()).toBe(200);const body=await reply.json();
  expect(body.valid).toBe(true);expect(reply.headers().etag).toBe(`"${body.content_digest}"`);
  await expect(page.getByTestId("explorer-results")).toBeVisible();return {body:decodeResult(body),source:reply.request().postDataJSON()};
}
test("AP8 gemeinsames Experiment: endogene Parameter, VN-Verhalten, Kosten und frischer Export",async({page})=>{
  const panel=await open(page);const initial=await run(page);
  await panel.getByLabel("Erklärrolle",{exact:true}).selectOption("ceo");
  await panel.getByRole("button",{name:"02 Vorstand & Strategien",exact:true}).click();
  const price=panel.getByLabel("Vorstand: Angebotspreis · Modellwährung",{exact:true});await expect(price).toBeDisabled();
  await panel.getByRole("button",{name:"Als eigenes Experiment übernehmen"}).click();
  await expect(panel.getByTestId("explorer-results")).toHaveCount(0);
  await price.fill("1,5");await panel.getByLabel("Einmalige Maßnahmenkosten",{exact:true}).fill("3");
  await panel.getByLabel("Entscheidung · Periode",{exact:true}).fill("2");
  await panel.getByRole("button",{name:"Marktansichten frisch berechnen",exact:true}).click();
  await expect(panel.getByRole("alert")).toContainText("frühestens in P6");
  await expect(panel.getByTestId("explorer-results")).toHaveCount(0);
  await panel.getByLabel("Entscheidung · Periode",{exact:true}).fill("6");
  await panel.getByLabel("VN Versicherungsschwelle",{exact:true}).fill("0.9");
  const changed=await run(page);expect(changed.body.model_result_digest).not.toBe(initial.body.model_result_digest);
  await expect(panel.getByLabel("Erklärrolle",{exact:true})).toHaveValue("ceo");
  await expect(panel.getByTestId("explorer-shares")).toBeVisible();
  expect(changed.source.measures.variant).toContainEqual(expect.objectContaining({decision_period:6,cost:"3",overrides:{price:"1.5"}}));
  expect(changed.source.customer_groups[0].insurance_threshold).toBe("0.9");
  // Model evidence, not a snapshot of the editor: the cost is booked once at P6.
  const actor=changed.source.measures.variant.find((m:{cost:string})=>m.cost==="3").insurer_id;
  const bookings=changed.body.sides.variant.financial_rows.filter((r:{insurer_id:number;sector_id:string})=>r.insurer_id===actor&&r.sector_id==="motor");
  expect(bookings.find((r:{period:number})=>r.period===6).measure_cost).toBe("3.0000");
  expect(bookings.find((r:{period:number})=>r.period===7).measure_cost).toBe("0.0000");
  const exported=page.waitForResponse(r=>r.url().endsWith("/api/market/source.json"));
  await panel.getByRole("button",{name:"Analysequelle frisch als JSON exportieren",exact:true}).click();
  const response=await exported;expect(response.status()).toBe(200);expect(response.headers().etag).toBe(`"${changed.body.model_result_digest}"`);
  expect(response.request().postDataJSON()).toEqual(changed.source);
  await panel.getByRole("button",{name:"02 Vorstand & Strategien",exact:true}).click();await expect(price).toHaveValue("1.5");
  await panel.getByRole("button",{name:"03 Umwelt & Schocks",exact:true}).click();await expect(panel.getByText("Exogene Risikoannahmen dieses Marktes",{exact:true})).toBeVisible();
  const report=await new AxeBuilder({page}).analyze();expect(report.violations).toEqual([]);
});
test("AP8 ICT-Experiment: exogener Ausfall, endogene Ersatzentscheidung und tatsächliches Netz",async({page})=>{
  test.setTimeout(180_000);await page.addInitScript(()=>localStorage.setItem("ims.theme","dark"));
  const panel=await open(page,"us_hyperscaler_outage","25");
  await panel.getByRole("button",{name:"03 Umwelt & Schocks",exact:true}).click();
  await panel.getByRole("button",{name:"Als eigenes Experiment übernehmen"}).click();
  await panel.getByLabel("Umwelt: Dauer · Stunden",{exact:true}).fill("24");
  await expect(panel.getByLabel("Vorstand: Angebotspreis · Modellwährung")).toBeHidden();
  await panel.getByRole("button",{name:"02 Vorstand & Strategien",exact:true}).click();
  await panel.getByLabel("Konkreter Ersatzpfad",{exact:true}).selectOption("q-dependent");
  await panel.getByLabel("Experimentvergleich",{exact:true}).selectOption("no_shock_vs_shock");
  const result=await run(page);expect(result.source.events[0].duration_hours).toBe("24");
  expect(result.source.responses.variant[0].replacement_asset_id).toBe("q-dependent");
  expect(result.body.comparison_labels.baseline).toBe("Kein Schock; beschlossene Vorsorge bleibt");
  await panel.getByRole("tab",{name:"6 ICT / Prozesse",exact:true}).click();
  const graph=panel.getByRole("group",{name:"ICT-Abhängigkeitsnetz mit tatsächlichem Ausfallstatus",exact:true});
  await expect(graph).toBeVisible();expect(await graph.getByRole("button").count()).toBe(result.source.ict.assets.length);
  await graph.getByRole("button",{name:/Q mit gemeinsamem US-IAM/}).focus();await page.keyboard.press("Enter");
  await expect(panel.getByTestId("explorer-path-proof")).toContainText("us-iam");
  const report=await new AxeBuilder({page}).analyze();expect(report.violations).toEqual([]);
  await panel.getByRole("button",{name:"03 Umwelt & Schocks",exact:true}).click();
  await panel.getByLabel("Umwelt: Intensität · 0 bis 1",{exact:true}).fill("2");
  await expect(panel.getByTestId("explorer-results")).toHaveCount(0);
  const invalid=page.waitForResponse(r=>r.url().endsWith("/api/market/explore"));
  await panel.getByRole("button",{name:"Marktansichten frisch berechnen",exact:true}).click();
  expect((await invalid).status()).toBe(422);await expect(panel.getByRole("alert")).toBeVisible();
  await expect(panel.getByRole("button",{name:"Analysequelle frisch als JSON exportieren"})).toHaveCount(0);
});
