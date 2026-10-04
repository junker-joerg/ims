import { useState } from "react";
import { Building2, Users, Zap, ShieldCheck, Clock3, ArrowRight } from "lucide-react";
import { sectorNames, type Side } from "./seminarPresentation";
import { type Row } from "./marketExplorerPresentation";

const object = (value: unknown): Row => value && typeof value === "object" && !Array.isArray(value) ? value as Row : {};
const rows = (value: unknown): Row[] => Array.isArray(value) ? value.filter(v => v && typeof v === "object") as Row[] : [];
export function experimentModel(source: unknown): Row {
  const root = object(source);
  return root.schema_version === "ims.modern-market.v1" ? root : object(root.model_input);
}
export function experimentSummary(source: unknown) {
  const root = object(source), model = experimentModel(source);
  return { actors: rows(model.insurers), families: rows(model.families), customers: rows(model.customer_groups), events: rows(root.events), periodCount:Number(model.period_count || 0), shock: root.schema_version === "ims.market-shock-bundle.v1", reference: root.schema_version === "ims.bafin-reference-bundle.v1" };
}
const parameterLabels: Record<string, string> = {
  price: "Angebotspreis · Modellwährung", advertising: "Werbung · Modellwährung",
  premium_factor: "Prämienfaktor", advertising_factor: "Werbefaktor",
  rate_per_period: "Anlagesatz je Periode · Anteil", price_per_policy: "Beitrag je Police",
  new_business: "Neugeschäft · Policen", exits: "Abgänge · Policen", capacity: "Aufnahmekapazität",
};
const eventNames: Record<string,string> = { provider_outage:"Provider-Ausfall", entry:"Markteintritt", life_demand:"Lebens-Nachfrage", regulatory:"Hypothetische Regulierung" };
const responseNames: Record<string,string> = { price:"Preisreaktion", life_attractiveness:"Vertriebsreaktion", fallback:"Ersatzpfad", migration:"ICT-Umstellung", capacity:"Kapazitätsreaktion" };

export default function MarketExperimentEditor({ source, original, busy, mode, onOwn, onChange }: {
  source: unknown; original: boolean; busy: boolean; mode: "board" | "environment";
  onOwn: () => void; onChange: (source: unknown) => void;
}) {
  const summary = experimentSummary(source), root = object(source), model = experimentModel(source);
  const [actorId, setActorId] = useState(0), [sector, setSector] = useState("motor"), [cohortId, setCohortId] = useState("");
  const actor = summary.actors.find(a => a.insurer_id === actorId) || summary.actors[0];
  const sectors = Object.keys(object(actor?.sectors)), selectedSector = sectors.includes(sector) ? sector : sectors[0];
  const assignments = rows(object(model.assignments).variant).filter(a => a.insurer_id === actor?.insurer_id && a.sector_id === selectedSector);
  const family = summary.families.find(f => f.family_id === assignments.find(a => Number(a.start) <= 6 && Number(a.end) >= 6)?.family_id) || summary.families.find(f => f.family_id === assignments[0]?.family_id);
  const ownId = `Board_${actor?.insurer_id}_${selectedSector}`;
  const measures = rows(object(model.measures).variant);
  const own = measures.find(m => m.measure_id === ownId);
  const cohort = summary.customers.find(c => c.group_id === cohortId) || summary.customers[0];
  const periodCount = Number(model.period_count || 0);
  // The immutable BaFin reference is bound to its catalogue mapping. AP7 has a
  // separate derived model_input; only that and plain AP5 inputs are editable.
  const reference = !!root.source_catalog && !summary.shock;
  const disabled = busy || original || reference;
  function mutate(update: (root: Row, model: Row) => void) {
    if (disabled) return;
    const next = structuredClone(source), nextRoot = object(next);
    update(nextRoot, experimentModel(next)); onChange(next);
  }
  function boardParameter(key: string, value: string) {
    mutate((_root, nextModel) => {
      const nextMeasures = rows(object(nextModel.measures).variant);
      let target = nextMeasures.find(m => m.measure_id === ownId) || nextMeasures.find(m => m.insurer_id === actor?.insurer_id && m.sector_id === selectedSector && key in object(m.overrides));
      if (!target) {
        target = { measure_id:ownId, insurer_id:actor?.insurer_id, sector_id:selectedSector, decision_period:6, lead_periods:0, duration:Math.max(1,periodCount-5), cost:"0", overrides:{} };
        nextMeasures.push(target); object(nextModel.measures).variant = nextMeasures;
      }
      object(target.overrides)[key] = typeof object(family?.parameters)[key] === "number" ? Number(value.replace(",",".")) : value.replace(",",".");
    });
  }
  if (!actor) return <div className="experiment-empty"><Building2 size={32} aria-hidden="true"/><h3>Zuerst einen Markt öffnen</h3><p>Strategien und Umwelt beziehen sich auf denselben geladenen Markt.</p></div>;
  return <div className={`experiment-editor ${mode}`}>
    <div className="editor-heading"><div><span className={`domain-tag ${mode}`} >{mode === "board" ? "ENDOGEN · ENTSCHEIDUNGEN" : "EXOGEN · MARKTUMWELT"}</span><h3>{mode === "board" ? "Strategien bestimmen den Kurs." : "Die Umwelt setzt den Markt unter Druck."}</h3><p>{mode === "board" ? "Der Vorstand setzt Parameter und Gegenmaßnahmen. Anbieter- und Nachfrageregeln führen sie im Markt aus." : "Eintritt, Dauer und Intensität sind äußere Annahmen. Sie werden über die erklärten Modellkanäle wirksam."}</p></div>{mode === "board" ? <Building2 size={40} aria-hidden="true"/> : <Zap size={40} aria-hidden="true"/>}</div>
    <div className="editor-ownership" role="status">{reference ? <p>Dieser BaFin-Referenzfall bleibt an seine Quellenabbildung gebunden. Workshop-Mapping im Bereich „Quellen und Handfälle“ bearbeiten; für Vorstands- und Umweltvarianten einen der vier abgeleiteten Schockfälle wählen.</p> : original ? <><p>Geladene Vorlage. Für Änderungen übernehmen Sie dieselbe Quelle als eigenes Experiment.</p><button className="primary-action" disabled={busy} onClick={onOwn}>Als eigenes Experiment übernehmen <ArrowRight size={17} aria-hidden="true"/></button></> : <p><ShieldCheck size={18} aria-hidden="true"/> Eigenes Experiment · jede Änderung erfordert eine frische Rechnung.</p>}</div>
    {mode === "board" ? <>
      <section className="decision-card"><div className="card-heading"><Building2 size={22} aria-hidden="true"/><div><h4>Anbieterstrategie</h4><p>Variante · ab P6 oder dem vorhandenen Maßnahmenfenster</p></div></div>
        <div className="editor-fields"><label>Vorstands-VU<select aria-label="Vorstands-VU" value={String(actor.insurer_id)} onChange={e => setActorId(Number(e.target.value))}>{summary.actors.map(a => <option key={String(a.insurer_id)} value={String(a.insurer_id)}>{String(a.name)}</option>)}</select></label><label>Vorstands-Sparte<select aria-label="Vorstands-Sparte" value={selectedSector} onChange={e=>setSector(e.target.value)}>{sectors.map(s=><option key={s} value={s}>{sectorNames[s] || s}</option>)}</select></label></div>
        <p className="rule-caption">Regelkern <code>{String(family?.rule || "Keine Familie")}</code> · {String(family?.label || "")}<br/>P1–P5 bleiben der gemeinsame Vergleichsanfang. Änderungen erzeugen eine ausführbare Maßnahme; Kosten und Vorlauf bleiben explizit.</p>
        <fieldset disabled={disabled || periodCount < 6}><legend>Vom Vorstand gesetzte Parameter</legend><div className="editor-fields">{Object.entries(object(family?.parameters)).map(([key,value])=>{
          const measure = own || measures.find(m=>m.insurer_id===actor.insurer_id && m.sector_id===selectedSector && key in object(m.overrides));
          return <label key={key}>{parameterLabels[key] || key}<input aria-label={`Vorstand: ${parameterLabels[key] || key}`} inputMode="decimal" value={String(object(measure?.overrides)[key] ?? value)} onChange={e=>boardParameter(key,e.target.value)}/></label>;
        })}</div></fieldset>
        {own && <fieldset disabled={disabled}><legend>Entscheidung und Buchung dieser Maßnahme</legend><div className="editor-fields">{[["decision_period","Entscheidung · Periode"],["lead_periods","Vorlauf · Perioden"],["duration","Wirksamkeit · Perioden"],["cost","Einmalige Maßnahmenkosten"]].map(([key,label])=><label key={key}>{label}<input inputMode="decimal" value={String(own[key])} onChange={e=>mutate((_r,m)=>{const target=rows(object(m.measures).variant).find(v=>v.measure_id===ownId)!;target[key]=key==="cost"?e.target.value.replace(",","."):Number(e.target.value);})}/></label>)}</div></fieldset>}
      </section>
      {summary.shock && <section className="decision-card"><div className="card-heading"><ShieldCheck size={22} aria-hidden="true"/><div><h4>Gegenmaßnahmen des Vorstands</h4><p>Bestehende, ausführbare Antworten im gewählten Fall</p></div></div><fieldset disabled={disabled}><legend>Vergleichsachse</legend><label>Experimentvergleich<select aria-label="Experimentvergleich" value={String(root.comparison)} onChange={e=>mutate(r=>{r.comparison=e.target.value;})}><option value="shock_with_response">Gleicher Schock · ohne / mit Gegenmaßnahme</option><option value="no_shock_vs_shock">Gleiche Entscheidungen · ohne / mit Schock</option></select></label></fieldset>
      <p>{root.comparison==="no_shock_vs_shock" ? "Beide Seiten führen die Vorstandsentscheidungen der Variante aus. Die Basis erhält kein äußeres Ereignis." : "Beide Seiten erhalten dieselben äußeren Ereignisse. Die Maßnahmen werden für Basis und Variante getrennt ausgeführt."}</p>
      {(["baseline","variant"] as Side[]).map(side=><div key={side} className="response-side"><h5>{side==="baseline"?"Basis":"Variante"}{root.comparison==="no_shock_vs_shock"&&side==="baseline"?" · bei dieser Achse aus Variante übernommen":""}</h5>{rows(object(root.responses)[side]).length===0 && <p>Keine Gegenmaßnahme deklariert.</p>}{rows(object(root.responses)[side]).map((response,i)=><fieldset key={String(response.response_id)} disabled={disabled || (side==="baseline"&&root.comparison==="no_shock_vs_shock")}><legend>{responseNames[String(response.kind)] || String(response.kind)} · {String(response.response_id)}</legend><div className="editor-fields">{[["decision_period","Antwortentscheidung · P"],["lead_periods","Antwortvorlauf · Perioden"],["duration_periods","Antwortdauer · Perioden"],["value",response.kind==="price"?"Neues Angebot · Modellwährung":response.kind==="life_attractiveness"?"Zusätzliche Attraktivität · Anteil":"Kapazitätsfaktor"],["cost","Antwortkosten · einmalig"],["cost_per_hour","Antwortkosten · je Stunde"]].filter(([key])=>key!=="value"||response.kind!=="fallback").map(([key,label])=><label key={key}>{label}<input aria-label={`${side} ${response.response_id}: ${label}`} inputMode="decimal" value={String(response[key])} onChange={e=>mutate(r=>{rows(object(r.responses)[side])[i][key]=key.includes("period")?Number(e.target.value):e.target.value.replace(",",".");})}/></label>)}{String(response.replacement_asset_id || "") && <label>Konkreter Ersatzpfad<select aria-label="Konkreter Ersatzpfad" value={String(response.replacement_asset_id)} onChange={e=>mutate(r=>{rows(object(r.responses)[side])[i].replacement_asset_id=e.target.value;})}>{rows(object(root.ict).assets).map(a=><option key={String(a.asset_id)} value={String(a.asset_id)}>{String(a.label)}</option>)}</select></label>}</div><p>{String(response.assumption_note)}</p></fieldset>)}</div>)}
      </section>}
      {cohort && <section className="decision-card demand"><div className="card-heading"><Users size={22} aria-hidden="true"/><div><h4>Strategien auf der Nachfrageseite</h4><p>VN-Verhalten · Kunden entscheiden anhand erreichbarer Angebote.</p></div></div><label>Nachfragegruppe<select aria-label="Nachfragegruppe" value={String(cohort.group_id)} onChange={e=>setCohortId(e.target.value)}>{summary.customers.map(c=><option key={String(c.group_id)} value={String(c.group_id)}>{String(c.group_id)} · {sectorNames[String(c.sector_id)]}</option>)}</select></label><fieldset disabled={disabled}><legend>Gemeinsames Nachfrageverhalten beider Seiten</legend><label>Versicherungsschwelle · 0 bis 1<input aria-label="VN Versicherungsschwelle" inputMode="decimal" value={String(cohort.insurance_threshold)} onChange={e=>mutate((_r,m)=>{rows(m.customer_groups).find(c=>c.group_id===cohort.group_id)!.insurance_threshold=e.target.value.replace(",",".");})}/></label></fieldset><p>Der vorhandene VN-Kern vergleicht die Angebote aktiver Anbieter. Im ICT-Fall wird ein Antrag erst nach tatsächlicher Bearbeitung zum wirksamen Vertrag. Der Versicherervorstand steuert die Kundenregel nicht im laufenden Markt.</p></section>}
    </> : <>
      {summary.events.map((event,i)=><section className="decision-card environment" key={String(event.event_id)}><div className="card-heading"><Zap size={22} aria-hidden="true"/><div><h4>{eventNames[String(event.kind)] || String(event.kind)}</h4><p>{String(event.event_id)} · {Array.isArray(event.channels)?event.channels.join(" / "):""}</p></div></div><fieldset disabled={disabled}><legend>Äußeres Ereignis</legend><div className="editor-fields">{[["start_hour","Eintritt · Prozessstunde"],["duration_hours","Dauer · Stunden"],["intensity","Intensität · 0 bis 1"],["cost","Ereigniskosten · Modellwährung"]].map(([key,label])=><label key={key}>{label}<input aria-label={`Umwelt: ${label}`} inputMode="decimal" value={String(event[key])} onChange={e=>mutate(r=>{rows(r.events)[i][key]=e.target.value.replace(",",".");})}/></label>)}</div></fieldset><p className="time-equation"><Clock3 size={18} aria-hidden="true"/> 24 Prozessstunden = 1 Modellperiode · Eintritt bei Stunde {String(event.start_hour)} → P{Math.floor(Number(event.start_hour)/24)+1}</p><p>{String(event.assumption_note)}</p><div className="event-channel"><strong>Wirkungskanal</strong><span>Äußeres Ereignis</span><ArrowRight size={16} aria-hidden="true"/><span>{String(event.kind)==="entry"?"Erreichbare Angebote":String(event.kind)==="life_demand"?"Lebens-Neugeschäftspool":"Abhängigkeiten / Ressourcen"}</span><ArrowRight size={16} aria-hidden="true"/><span>Vorgang → Vertrag → Buchung</span></div></section>)}
      {!summary.events.length && <section className="decision-card"><h4>Exogene Risikoannahmen dieses Marktes</h4><p>Dieser Fall enthält keinen AP7-Ereigniskanal. Der Markt führt den deklarierten Schadenindikator und die Risikozeilen aus. Für Provider-, Eintritts-, Lebens-Nachfrage- oder Regulierungsschocks wählen Sie einen der vier Schockfälle.</p><p>Schadenindikator P1: {String(Array.isArray(model.damage_indicators)?model.damage_indicators[0]:"nicht deklariert")}</p></section>}
      <aside className="model-boundary"><h4>Was dieser Fall erklärt</h4><p>Schocks und länger anhaltende Entwicklungen wirken nur über die deklarierten Kanäle. Lebens-Nachfrage betrifft das Neugeschäft; Altgarantien bleiben erhalten. „DORA 2.0“ ist ein hypothetischer Workshop-Fall. Claims/Service wirken auf administrative Arbeit und Kosten. Zahlungen und Solvenz werden daraus nicht neu abgeleitet.</p></aside>
    </>}
  </div>;
}
