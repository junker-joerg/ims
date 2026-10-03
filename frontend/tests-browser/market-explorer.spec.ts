import assert from "node:assert/strict";
import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { amountUnits, amountText } from "../src/seminarPresentation";
import { divided, families, position, raw } from "../src/marketExplorerPresentation";

type Row = Record<string, any>;
function rows(result: any, side: string, name: string): Row[] {
  const table = result.sides[side][name];
  return table.rows.map((values: any[],i:number)=>Object.fromEntries(table.columns.map((key:string,j:number)=>[key,values[j]]).filter(([key]:[string,any])=>!table.missing?.[String(i)]?.includes(key))));
}
async function observePost(page:Page,path:string){
  let accept!:(value:any)=>void, reject!:(failure:unknown)=>void;
  const reply=new Promise<any>((res,rej)=>{accept=res;reject=rej;});
  // Bounded transport retry only for ECONNRESET (idle HTTP keep-alive race).
  // HTTP/model errors are never retried or replaced with fixtures.
  await page.route(`**/api/market/${path}`,async route=>{try{const response=await route.fetch({timeout:360_000,maxRetries:2});assert.equal(response.status(),200);const result=await response.json();await route.fulfill({response});accept({result,etag:response.headers().etag});}catch(error){reject(error);await route.abort();}},{times:1});
  return {reply};
}
async function load(page:Page,caseId="us_hyperscaler_outage",n=25){
  await page.goto("/#market");const panel=page.getByTestId("market-explorer-workbench");
  await panel.getByLabel("Analysefall",{exact:true}).selectOption(caseId);await panel.getByLabel("Analyseperioden",{exact:true}).selectOption(String(n));
  const {reply}=await observePost(page,caseId==="bafin"?"reference-case":caseId==="switch"||caseId==="market"?"workshop-case":"shock-case");
  await panel.getByRole("button",{name:"Analysevorlage laden",exact:true}).click();const {result}=await reply;
  await expect(panel.getByTestId("explorer-source")).toContainText("Schreibfreie Vorlage");
  return {panel,source:result.shock_bundle||result.source_bundle||result.source_input};
}
async function calculate(page:Page){const {reply}=await observePost(page,"explore");await page.getByTestId("market-explorer-workbench").getByRole("button",{name:"Marktansichten frisch berechnen",exact:true}).click();const {result,etag}=await reply;assert.equal(etag,`"${result.content_digest}"`);await expect(page.getByTestId("explorer-results")).toBeVisible({timeout:60_000});return result;}
async function capture(page:Page,info:any,name:string,section?:string){const directory=process.env.IMS_AP8_CAPTURE==="1"?resolve("../docs/handbook/images"):info.outputDir;await mkdir(directory,{recursive:true});const path=resolve(directory,name);if(section)await page.getByTestId(section).screenshot({path});else await page.screenshot({path});}
const digests:Record<string,string>={us_hyperscaler_outage:"7ee786bf1266f74c4e95aaca4f01bd50e60c1a9c708cea6169d1be32b8b10c66",google_motor_entry:"8d5e165ab934891c5abedf1d10dce231d06e0bcbc5b69844b98dc7514611225f",life_demand_shock:"b5e4dcc1f876e5f76ec6ebf6abdef705eec1a975a1d750a36205dbfb191ae96a",dora_2_workshop:"f2a21bdc95f946eb77b479f489dd81b7ec0308ccbde9fabe8e1f48fc2c3c2a38"};

test("AP8 unabhängige Gewichte, HHI, Rundung, Rang und Nullnenner",()=>{
  const source=[{insurer_id:1,family_id:"F",opening_assets:"90",period_profit:"9",premium_income:"90"},{insurer_id:2,family_id:"F",opening_assets:"10",period_profit:"3",premium_income:"10"}];
  const f=families(source)[0],p=position(source);assert.equal(f.mean,120000n);assert.equal(f.minimum,100000n);assert.equal(f.maximum,300000n);assert.equal(p.hhi,82000000n);assert.deepEqual(p.entries.map(e=>e.share),[900000n,100000n]);
  assert.equal(divided(1n,2n),0n);assert.equal(divided(3n,2n),2n);assert.equal(divided(-3n,2n),-2n);
  assert.equal(position([{insurer_id:1,premium_income:"0"}]).hhi,null);assert.equal(position([{insurer_id:1,premium_income:"-1"},{insurer_id:2,premium_income:"2"}]).hhi,null);
  assert.deepEqual(position([{insurer_id:1,premium_income:"10"},{insurer_id:2,premium_income:"10"}]).entries.map(e=>e.rank),[1,1]);
});

for(const caseId of Object.keys(digests)){
  test(`AP8 ${caseId}: echter 100er-Lauf, sechs Ansichten, unverändertes AP7 und 25er-Prefix`,async({page},info)=>{
    test.setTimeout(480_000);const errors:string[]=[];page.on("pageerror",e=>errors.push(e.message));
    const {panel,source}=await load(page,caseId,100);const began=Date.now();const result=await calculate(page);
    assert.equal(result.model_result_digest,digests[caseId]);assert.equal(result.period_count,100);assert.equal(result.reference.german_direct_selection_verified,false);
    assert.ok(Buffer.byteLength(JSON.stringify(result))<=40*1024*1024);
    for(const side of ["baseline","variant"]){
      const vu=rows(result,side,"financial_rows"),market=rows(result,side,"market_rows");
      for(const row of vu){const money=(key:string)=>amountUnits(row[key]);assert.equal(money("period_profit"),money("premium_income")+money("investment_income")-money("insurance_expense")-money("operating_expense"));assert.equal(money("closing_equity"),money("opening_equity")+money("period_profit")+money("capital_contribution")-money("capital_distribution"));}
      for(const m of market){const selected=vu.filter(r=>r.period===m.period&&(m.sector_id==="total"||r.sector_id===m.sector_id));assert.equal(selected.reduce((sum,r)=>sum+amountUnits(r.premium_income),0n),amountUnits(m.premium_income));assert.equal(position(selected).hhi,m.hhi===null?null:amountUnits(m.hhi));}
      const switches=rows(result,side,"switch_rows");assert.ok(switches.every(r=>r.period>1&&r.previous_insurer_id!==r.insurer_id));
      assert.deepEqual(switches,rows(result,side,"customer_rows").filter(r=>r.period>1&&r.previous_insurer_id!==r.insurer_id));
      for(const f of rows(result,side,"family_rows")){const actual=vu.filter(r=>r.period===f.period&&r.family_id===f.family_id&&(f.sector_id==="total"||r.sector_id===f.sector_id));assert.deepEqual(f.member_ids,[...new Set(actual.map(r=>r.insurer_id))].sort((a,b)=>a-b));const derived=families(actual)[0];assert.equal(derived.mean,f.weighted_profit_percent===null?null:amountUnits(f.weighted_profit_percent));}
    }
    for(const [id,label] of [["market","1 Verlauf"],["shares","2 Position"],["families","3 Familien"],["flows","4 Wechsel"],["timeline","5 Zeitlinie"],["provider","6 ICT / Prozesse"]]){await panel.getByRole("tab",{name:label,exact:true}).click();await expect(panel.getByTestId(`explorer-${id}`)).toBeVisible();assert.equal(await panel.locator(".explorer-card:visible").count(),1);}await panel.getByRole("tab",{name:"1 Verlauf",exact:true}).click();
    const vu=rows(result,"variant","financial_rows").filter(r=>r.period===21),total=vu.reduce((sum,r)=>sum+amountUnits(r.premium_income),0n);
    await expect(panel.getByTestId("explorer-denominator")).toHaveAttribute("data-value",raw(total));
    await expect(panel.getByTestId("explorer-model-digest")).toHaveText(result.model_result_digest);
    const focus=source.model_input.insurers[0].insurer_id;
    const focusPremium=vu.filter(r=>r.insurer_id===focus).reduce((sum,r)=>sum+amountUnits(r.premium_income),0n);
    await expect(panel.locator('[data-kind="Fokus"]')).toHaveAttribute("data-premium",raw(focusPremium));
    await expect(panel.locator('[data-kind="Rivalen"]')).toHaveAttribute("data-premium",raw(total-focusPremium));
    let fresh=0;page.on("request",r=>{if(r.url().endsWith("/api/market/explore"))fresh++;});
    const family=vu.find(r=>r.insurer_id===focus).family_id;await panel.getByLabel("Vergleichsgruppe",{exact:true}).selectOption(`family:${family}`);
    await expect(panel.getByTestId("explorer-denominator")).toHaveAttribute("data-value",raw(total));
    const familyPremium=vu.filter(r=>r.family_id===family).reduce((sum,r)=>sum+amountUnits(r.premium_income),0n);
    await expect(panel.getByTestId("explorer-selected-premium")).toHaveAttribute("data-value",raw(familyPremium));
    await panel.getByRole("tab",{name:"3 Familien",exact:true}).click();await expect(panel.getByTestId("explorer-composition")).toBeVisible();
    await panel.getByLabel("Erklärrolle",{exact:true}).selectOption("cio");await expect(panel.getByTestId("explorer-provider")).toBeFocused();
    await panel.getByLabel("Vergleichsgruppe",{exact:true}).selectOption("market");
    await panel.getByRole("button",{name:"Konkrete Buchungsdetails öffnen",exact:true}).click();
    const terms=await panel.getByTestId("explorer-book").locator("tr[data-term]").evaluateAll(nodes=>nodes.map(n=>({key:n.getAttribute("data-term"),value:n.getAttribute("data-value")!})));
    assert.equal(terms.slice(0,-1).reduce((sum,r)=>sum+amountUnits(r.value),0n),amountUnits(terms.at(-1)!.value));
    const coreFor=(s:string,k:string)=>rows(result,s,"financial_rows").filter(r=>r.period===21&&r.insurer_id===focus).reduce((sum,r)=>sum+amountUnits(r[k]),0n);
    assert.equal(amountUnits(terms.at(-1)!.value),coreFor("variant","closing_equity")-coreFor("baseline","closing_equity"));
    assert.equal(fresh,0);
    if(caseId==="us_hyperscaler_outage"){
      const b=rows(result,"baseline","resource_rows")[20],v=rows(result,"variant","resource_rows")[20];assert.equal(b.capacity_work,"0.0000");assert.equal(v.capacity_work,"96.0000");
      await panel.getByRole("button",{name:/q-dependent.*Q mit gemeinsamem US-IAM/}).click();await expect(panel.getByTestId("explorer-path-proof")).toContainText("us-iam");
      for(const [id,label] of [["market","1 Verlauf"],["shares","2 Position"],["families","3 Familien"],["flows","4 Wechsel"],["timeline","5 Zeitlinie"],["provider","6 ICT / Prozesse"]]){await panel.getByRole("tab",{name:label,exact:true}).click();await capture(page,info,`ap8_view_${id}.png`,`explorer-${id}`);}
    }
    if(caseId==="google_motor_entry") {await panel.getByLabel("Analyseperiode",{exact:true}).selectOption("20");await expect(panel.getByTestId("explorer-shares")).toContainText("41 registriert · 40 aktiv");await panel.getByLabel("Analyseperiode",{exact:true}).selectOption("21");await expect(panel.getByTestId("explorer-shares")).toContainText("41 registriert · 41 aktiv");}
    // Independent shorter actual run must be exactly the same prefix for every table.
    const reply=await page.request.post("/api/market/shock-case",{data:{case_id:caseId,period_count:25}});const shorterSource=(await reply.json()).shock_bundle;
    const shortReply=await page.request.post("/api/market/explore",{data:shorterSource,timeout:180_000});assert.equal(shortReply.status(),200);const shorter=await shortReply.json();
    for(const s of ["baseline","variant"])for(const name of Object.keys(result.sides[s])){if(name==="terminal_process_rows")continue;const prefix=rows(result,s,name).filter(r=>(r.period??r.completed_period??r.issue_period??1000)<=25);assert.deepEqual(rows(shorter,s,name),prefix);}
    assert.deepEqual(errors,[]);
    await info.attach("AP8 frischer Lauf",{body:JSON.stringify({caseId,periods:100,elapsedSeconds:(Date.now()-began)/1000,wireBytes:Buffer.byteLength(JSON.stringify(result)),modelDigest:result.model_result_digest,viewDigest:result.content_digest}),contentType:"application/json"});
  });
}

test("AP8 Handfall: wirksamer Wechsel, lokale Filter und frischer JSON/Einzel-VU-Excel-Export",async({page})=>{
  test.setTimeout(180_000);const {panel,source}=await load(page,"switch",10);const result=await calculate(page);
  await panel.getByLabel("Analyseperiode",{exact:true}).selectOption("6");await panel.getByLabel("Analysesparte",{exact:true}).selectOption("motor");await panel.getByLabel("Fokus-VU",{exact:true}).selectOption("2");
  await panel.getByRole("tab",{name:"4 Wechsel",exact:true}).click();await expect(panel.getByTestId("explorer-flows")).toContainText("Kfz · 10,0000");await expect(panel.getByTestId("explorer-denominator")).toHaveAttribute("data-value","20.0000");
  await panel.getByLabel("Analyseperiode",{exact:true}).selectOption("1");await expect(panel.getByTestId("explorer-flows")).toContainText("kein wirksamer Eigentümerwechsel");await panel.getByRole("tab",{name:"2 Position",exact:true}).click();await expect(panel.getByTestId("explorer-shares").getByRole("group",{name:"Gebuchte Modellbeitragsanteile · ausgewählte VUs",exact:true})).toContainText("Nicht definiert");
  await panel.getByRole("tab",{name:"3 Familien",exact:true}).click();await panel.getByLabel("Analysesparte",{exact:true}).selectOption("health");await expect(panel.getByTestId("explorer-families")).toContainText("Keine auswertbaren Mitglieder");await panel.getByLabel("Analysesparte",{exact:true}).selectOption("motor");
  await panel.getByLabel("Analyseperiode",{exact:true}).selectOption("6");
  const portablePromise=page.waitForEvent("download");await panel.getByRole("button",{name:"Analysequelle frisch als JSON exportieren",exact:true}).click();const portable=await portablePromise;const imported=JSON.parse(await readFile((await portable.path())!,"utf8"));assert.deepEqual(imported,source);
  const excelPromise=page.waitForEvent("download");await panel.getByRole("button",{name:"Fokus-VU frisch als Excel exportieren",exact:true}).click();const excel=await excelPromise;assert.ok((await readFile((await excel.path())!)).length>5000);assert.ok(excel.suggestedFilename().includes("VU2"));
  const apiExcel=await page.request.post("/api/market/export.xlsx",{data:{source_input:source,insurer_id:2},headers:{"If-Match":`"${result.model_result_digest}"`}});assert.equal(apiExcel.status(),200);assert.equal(apiExcel.headers().etag,`"${result.model_result_digest}"`);
  await panel.getByText("Eigene Analysequelle importieren",{exact:true}).click();await panel.getByLabel("Eigene Analysequelle importieren",{exact:true}).setInputFiles({name:"same.json",mimeType:"application/json",buffer:Buffer.from(JSON.stringify(imported))});await expect(panel.getByTestId("explorer-results")).toHaveCount(0);const reloaded=await calculate(page);assert.equal(reloaded.content_digest,result.content_digest);
  const uninsuredSource=structuredClone(source);
  for(const s of ["baseline","variant"])uninsuredSource.measures[s]=[1,2].map(aid=>({measure_id:`KapNull_${aid}`,insurer_id:aid,sector_id:"motor",decision_period:6,lead_periods:0,duration:5,cost:"0",overrides:{capacity:"0"}}));
  await panel.getByLabel("Eigene Analysequelle importieren",{exact:true}).setInputFiles({name:"uninsured.json",mimeType:"application/json",buffer:Buffer.from(JSON.stringify(uninsuredSource))});const uninsured=await calculate(page);
  await panel.getByLabel("Analyseperiode",{exact:true}).selectOption("6");const switchRow=rows(uninsured,"variant","switch_rows").find(r=>r.period===6)!;
  assert.equal(switchRow.insurer_id,null);assert.equal(switchRow.uninsured_loss,"40.0000");assert.equal(rows(uninsured,"variant","financial_rows").filter(r=>r.period===6).reduce((sum,r)=>sum+amountUnits(r.insurance_expense),0n),0n);
  await panel.getByRole("tab",{name:"4 Wechsel",exact:true}).click();await panel.getByTestId("explorer-flows").getByText("Alle wirksamen Wechsel · keine gemischte Mengensumme",{exact:false}).click();
  await expect(panel.getByTestId("explorer-vu-risk")).toHaveAttribute("data-value","0.0000");await expect(panel.getByTestId("explorer-uninsured-risk")).toHaveAttribute("data-value","40.0000");
  await panel.getByLabel("Eigene Analysequelle importieren",{exact:true}).setInputFiles({name:"invalid.json",mimeType:"application/json",buffer:Buffer.from("{}")} );await panel.getByRole("button",{name:"Marktansichten frisch berechnen",exact:true}).click();await expect(panel.getByRole("alert")).toBeVisible();await expect(panel.getByTestId("explorer-results")).toHaveCount(0);
});

test("AP8 BaFin-Referenz und offline Anleitung im echten Backend",async({page})=>{
  test.setTimeout(150_000);const {panel}=await load(page,"bafin",10);const result=await calculate(page);assert.equal(result.actors.length,40);assert.equal(result.clock,null);await expect(panel.getByTestId("explorer-provider")).toContainText("keinen ICT-/Prozesskanal");await expect(panel.getByTestId("explorer-reference")).toContainText("nicht belegt");await expect(panel.getByTestId("explorer-reference")).toContainText(String(result.reference.rest.selected_unmodeled_million_eur).replace(".",","));
  const help=await page.context().newPage();await help.goto("/api/seminar/handbook/market_ap8.html");await expect(help.getByRole("heading",{level:1})).toContainText("Sechs verknüpfte Marktansichten");await expect(help.locator("body")).toContainText("keine isolierte Kausalzuordnung");
  const images=await help.locator("img").evaluateAll(nodes=>nodes.map(n=>n.getAttribute("src")!));assert.equal(images.length,13);assert.ok(images.includes("images/ap8_start_light_1440x900.png"));for(const image of images){const reply=await help.request.get(`/api/seminar/handbook/${image}`);assert.equal(reply.status(),200);assert.ok((await reply.body()).length>1000);}await help.close();
});

for(const viewport of [{width:1440,height:900},{width:1024,height:768},{width:390,height:844}])for(const theme of ["light","dark"] as const){
  test(`AP8 ${viewport.width}x${viewport.height} ${theme}: sechs Ansichten, ICT, Tastatur und Kontrast`,async({page},info)=>{
    test.setTimeout(180_000);await page.setViewportSize(viewport);await page.addInitScript(value=>localStorage.setItem("ims.theme",value),theme);
    const {panel}=await load(page);await calculate(page);await expect(page.locator("html")).toHaveAttribute("data-theme",theme);
    await panel.getByLabel("Erklärrolle",{exact:true}).selectOption("cio");await expect(panel.getByTestId("explorer-provider")).toBeFocused();
    await panel.getByRole("button",{name:/q-dependent.*Q mit gemeinsamem US-IAM/}).focus();await page.keyboard.press("Enter");await expect(panel.getByTestId("explorer-path-proof")).toContainText("us-iam");
    const chart=panel.getByRole("slider",{name:"Ausgewählter Schlussrückstand · Anzahl Vorgänge: Periode wählen mit Pfeiltasten"});await chart.focus();await page.keyboard.press("ArrowRight");await expect(panel.getByLabel("Analyseperiode",{exact:true})).toHaveValue("22");await page.keyboard.press("ArrowLeft");
    const report=await new AxeBuilder({page}).include('[data-testid="market-explorer-workbench"]').withTags(["wcag2a","wcag2aa","wcag21aa"]).analyze();assert.deepEqual(report.violations,[]);
    const contrasts=report.passes.filter(v=>v.id==="color-contrast").flatMap(v=>v.nodes.flatMap(n=>n.any.map(c=>(c.data as {contrastRatio?:number}|null)?.contrastRatio).filter((r):r is number=>typeof r==="number")));assert.ok(contrasts.length>0);assert.ok(Math.min(...contrasts)>=4.5);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
    await panel.getByTestId("explorer-provider").evaluate(node=>node.scrollIntoView({block:"start"}));await capture(page,info,`ap8_ict_${theme}_${viewport.width}x${viewport.height}.png`);
    await info.attach("AP8 Kontrast",{body:JSON.stringify({viewport,theme,minimumContrast:Math.min(...contrasts),checkedTextNodes:contrasts.length}),contentType:"application/json"});
  });
}
