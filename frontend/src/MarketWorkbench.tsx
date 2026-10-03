import { useRef, useState } from "react";
import { amountText, amountUnits, percentText, sectorNames, type Side } from "./seminarPresentation";
import "./MarketWorkbench.css";

type Family = { family_id: string; label: string; sector_id: string; rule: string; parameters: Record<string, string | number> };
type Assignment = { insurer_id: number; sector_id: string; family_id: string; start: number; end: number };
type Measure = { measure_id: string; insurer_id: number; sector_id: string; decision_period: number; lead_periods: number; duration: number; cost: string; overrides: Record<string, string> };
type Actor = { insurer_id: number; insurance_group_id: string; name: string; sectors: Record<string, object> };
type Source = { case_id: string; period_count: number; seed: number; insurers: Actor[]; families: Family[]; assignments: Record<Side, Assignment[]>; measures: Record<Side, Measure[]>; peer_groups: { group_id: string; label: string }[]; provenance: { description: string }; };
type ReferenceGroup = { insurer_id: number; group_id: string; name: string; rank: number; total: string; sectors: Record<string, string>; selected_weight: string; source_weight: string; unmodeled_million_eur: string; entity_rows: number[]; override_rows: number[]; };
type ReferenceView = { source_scope: { notice: string }; groups: ReferenceGroup[]; universe_total_million_eur: string; selected_total_million_eur: string; modeled_selected_million_eur: string; rest: { unselected_groups_million_eur: string; selected_unmodeled_million_eur: string }; rank_40: { name: string; total: string }; rank_41: { name: string; total: string }; model_binding?: string; };
type Bundle = { schema_version: string; title: string; source_catalog: { entities: { workbook_row: number; group_assertion: string; entity_source_name: string; source_sector: string; premium_million_eur: string; source_sheet: string; source_cell: string; source_id: string; value_status: string }[]; source_files: { id: string; url: string; sha256: string }[] }; workshop: { nonlife_mix: Record<string, string>; note: string; scale_model_currency_per_million_eur: string; model_price: string; loss_ratio: string; opening_assets_multiple: string }; overrides: { entity_row: number; premium_million_eur: string; note: string }[]; model_input: Source; };
type Row = { period: number; sector_id: string; insurer_id?: number; family_id?: string; group_id?: string; closing_assets: string; closing_liabilities: string; closing_equity: string; period_profit: string; premium_income: string; insurance_expense: string; operating_expense: string; measure_cost: string; covered_quantity: string | null; weighted_price: string | null; active_vu_count: number; rule?: string; parameters?: object; active_measures?: string[]; information_period?: number; };
type Decision = { period: number; sector_id: string; group_id: string; insurer_id: number | null; previous_insurer_id: number | null; quantity: string; premium_income: string; risk_loss: string; uninsured_loss: string; };
type Result = { valid: boolean; content_digest: string; period_count: number; source_input: Source; source_bundle?: Bundle; reference?: ReferenceView; sides: Record<Side, { market_rows: Row[]; family_rows: Row[]; peer_rows: Row[]; insurance_group_rows: Row[]; vu_rows: Row[]; customer_decisions: Decision[] }>; };
const BASE = "/api/market";
const names: Record<string, string> = { ...sectorNames, total: "Alle Sparten · Geldsummen" };
const caseNames: Record<string, string> = { bafin: "BaFin-Gruppenauswertung 2024 – Workshop", market: "Synthetischer Modellmarkt", switch: "Wechsel mit Altreserve", capacity: "Kapazität und unversicherte Nachfrage" };
const eur = (v: string) => Number(v).toLocaleString("de-DE", { minimumFractionDigits: 3, maximumFractionDigits: 4 });

async function post(path: string, source: unknown) {
  const reply = await fetch(BASE + path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(source) });
  const body = await reply.json();
  if (!reply.ok || !body.valid) throw new Error(body.issues?.[0]?.message || "Marktprüfung fehlgeschlagen.");
  if (body.content_digest && reply.headers.get("etag") !== `"${body.content_digest}"`) throw new Error("Inhaltsnachweis der Marktantwort stimmt nicht.");
  if (body.transport === "ims.market-row-table.v1") {
    for (const side of ["baseline", "variant"]) for (const name of Object.keys(body.sides[side])) {
      const table = body.sides[side][name] as { columns: string[]; rows: unknown[][]; missing?: Record<string, string[]> };
      body.sides[side][name] = table.rows.map((values, i) => Object.fromEntries(table.columns.map((key, j) => [key, values[j]]).filter(([key]) => !table.missing?.[String(i)]?.includes(key as string))));
    }
  }
  return body;
}

function Timeline({ baseline, variant }: { baseline: Row[]; variant: Row[] }) {
  const values = [...baseline, ...variant].map(r => Number(r.closing_equity));
  const min = Math.min(0, ...values), max = Math.max(0, ...values), range = max - min || 1;
  const x = (i: number) => 56 + i / Math.max(baseline.length - 1, 1) * 560;
  const y = (value: number) => 218 - (value - min) / range * 170;
  const line = (rows: Row[]) => rows.map((r, i) => `${i ? "L" : "M"}${x(i).toFixed(2)},${y(Number(r.closing_equity)).toFixed(2)}`).join(" ");
  return <><svg className="management-chart" viewBox="0 0 640 268" role="img" aria-label="Markt- oder Gruppenverlauf: Eigenkapital Baseline und Variante. Exakte Werte stehen in der Tabelle.">
    {[0, 1, 2, 3, 4].map(i => { const value = min + i / 4 * range; return <g key={i}><line x1="56" x2="616" y1={y(value)} y2={y(value)} className="chart-grid" /><text x="48" y={y(value) + 4} textAnchor="end">{Math.round(value).toLocaleString("de-DE")}</text></g>; })}
    <path d={line(baseline)} className="baseline-line" /><path d={line(variant)} className="variant-line" />
    <text x="56" y="242">1</text><text x="616" y="242" textAnchor="end">{baseline.length}</text><text x="336" y="262" textAnchor="middle">Modellperiode</text>
  </svg><div className="chart-legend"><span><i className="baseline-key" />Baseline</span><span><i className="variant-key" />Variante</span></div></>;
}

export default function MarketWorkbench() {
  const [caseId, setCaseId] = useState("bafin"), [horizon, setHorizon] = useState(100), [count, setCount] = useState(40);
  const [input, setInput] = useState<Source | null>(null), [result, setResult] = useState<Result | null>(null), [expert, setExpert] = useState("");
  const [busy, setBusy] = useState(false), [error, setError] = useState<string | null>(null), [hadResult, setHadResult] = useState(false);
  const [period, setPeriod] = useState(6), [side, setSide] = useState<Side>("variant"), [sector, setSector] = useState("total"), [filter, setFilter] = useState("market");
  const [actor, setActor] = useState(1), [family, setFamily] = useState(""), [end, setEnd] = useState(20);
  const [cost, setCost] = useState("3"), [lead, setLead] = useState(2), [duration, setDuration] = useState(3), [capacity, setCapacity] = useState("60");
  const [bundle, setBundle] = useState<Bundle | null>(null), [reference, setReference] = useState<ReferenceView | null>(null), [original, setOriginal] = useState(false);
  const [mix, setMix] = useState({ motor: "40", property_liability: "40", unmodeled: "20" });
  const [mixPending, setMixPending] = useState(false);
  const [entityRow, setEntityRow] = useState(5), [overrideAmount, setOverrideAmount] = useState(""), [overrideNote, setOverrideNote] = useState("");
  const revision = useRef(0);
  const presetCount = caseId === "bafin" ? 40 : caseId === "market" ? count : caseId === "switch" ? 2 : 3;
  function invalidate() { revision.current++; setResult(null); setError(null); }
  function changed(source: Source) { invalidate(); setInput(source); const next = bundle ? { ...bundle, model_input: source } : null; setBundle(next); setExpert(JSON.stringify(next || source, null, 2)); }
  function accept(body: { source_input: Source; source_bundle?: Bundle; reference?: ReferenceView }, readOnly = false, keepSelection = false) {
    setInput(body.source_input); setBundle(body.source_bundle || null); setReference(body.reference || null); setOriginal(readOnly);
    setExpert(JSON.stringify(body.source_bundle || body.source_input, null, 2));
    setActor(keepSelection && body.source_input.insurers.some(a => a.insurer_id === actor) ? actor : body.source_input.insurers[0].insurer_id); setFamily(keepSelection && body.source_input.families.some(f => f.family_id === family) ? family : body.source_input.families.find((f: Family) => f.sector_id === "motor")?.family_id || ""); setMixPending(false);
    if (body.source_bundle) setMix(Object.fromEntries(Object.entries(body.source_bundle.workshop.nonlife_mix).map(([s, v]) => [s, String(Number(v) * 100)])) as typeof mix);
  }
  async function act(work: (version: number) => Promise<void>) {
    const version = revision.current; setBusy(true); setError(null);
    try { await work(version); } catch (e) { if (version === revision.current) setError(e instanceof Error ? e.message : "Marktaktion fehlgeschlagen."); }
    finally { if (version === revision.current) setBusy(false); }
  }
  async function load() {
    invalidate(); setInput(null); setBundle(null); setReference(null); setOriginal(false);
    await act(async version => {
      const body = caseId === "bafin" ? await post("/reference-case", { period_count: horizon, workshop: null, overrides: null }) : await post("/workshop-case", { case_id: caseId, period_count: horizon, vu_count: presetCount });
      if (version !== revision.current) return;
      accept(body, caseId === "bafin"); setEnd(Math.min(20, horizon)); setFilter("market");
    });
  }
  async function calculate(source?: Source) {
    invalidate();
    await act(async version => {
      const body: Result = await post("/calculate", source || JSON.parse(expert));
      if (version !== revision.current) return;
      const wasOriginal = original; accept(body, wasOriginal, true); setResult(body); setHadResult(true); setPeriod(Math.min(6, body.period_count));
    });
  }
  async function rebuildReference(override: boolean) {
    if (!bundle || original) return;
    invalidate(); setReference(null);
    await act(async version => {
      const settings = structuredClone(bundle.workshop);
      settings.nonlife_mix = Object.fromEntries(Object.entries(mix).map(([s, v]) => [s, String(Number(v.replace(",", ".")) / 100)]));
      const overrides = structuredClone(bundle.overrides).filter(item => !override || item.entity_row !== entityRow);
      if (override) overrides.push({ entity_row: entityRow, premium_million_eur: overrideAmount.replace(",", "."), note: overrideNote });
      const body = await post("/reference-case", { period_count: input!.period_count, workshop: settings, overrides });
      if (version !== revision.current) return;
      accept(body); setFilter("market");
    });
  }
  function assignFamily() {
    if (!input) return;
    const next = structuredClone(input), kept: Assignment[] = [];
    for (const item of next.assignments.variant) {
      if (item.insurer_id !== actor || item.sector_id !== "motor" || item.end < 6 || item.start > end) kept.push(item);
      else { if (item.start < 6) kept.push({ ...item, end: 5 }); if (item.end > end) kept.push({ ...item, start: end + 1 }); }
    }
    kept.push({ insurer_id: actor, sector_id: "motor", family_id: family, start: 6, end }); next.assignments.variant = kept; changed(next);
  }
  function applyMeasure() {
    if (!input) return;
    const next = structuredClone(input);
    next.measures.variant = next.measures.variant.filter(m => m.insurer_id !== actor || m.sector_id !== "motor");
    next.measures.variant.push({ measure_id: `Aufnahme_${actor}`, insurer_id: actor, sector_id: "motor", decision_period: 6, lead_periods: lead, duration, cost: cost.replace(",", "."), overrides: { capacity: capacity.replace(",", ".") } });
    changed(next);
  }
  async function download(excel: boolean) {
    if (!input || !result) return;
    await act(async version => {
      const source = bundle || input;
      const response = await fetch(BASE + (excel ? "/export.xlsx" : "/source.json"), { method: "POST", headers: { "Content-Type": "application/json", "If-Match": `"${result.content_digest}"` }, body: JSON.stringify(excel ? { source_input: source, insurer_id: actor } : source) });
      if (!response.ok || response.headers.get("etag") !== `"${result.content_digest}"`) throw new Error("Export benötigt dieselben unveränderten geprüften Quellen.");
      const blob = await response.blob(); if (version !== revision.current) return;
      const url = URL.createObjectURL(blob), link = document.createElement("a"); link.href = url; link.download = `IMS-${excel ? `VU${actor}` : "Modellmarkt"}-${result.content_digest.slice(0, 12)}.${excel ? "xlsx" : "json"}`; link.click(); setTimeout(() => URL.revokeObjectURL(url), 0);
    });
  }
  function view(current: Side): Row[] {
    if (!result) return [];
    const data = result.sides[current];
    const [kind, id] = filter.split(":");
    const rows = kind === "family" ? data.family_rows.filter(r => r.family_id === id) : kind === "peer" ? data.peer_rows.filter(r => r.group_id === id) : kind === "insurance" ? data.insurance_group_rows.filter(r => r.group_id === id) : data.market_rows;
    return rows.filter(r => r.sector_id === sector);
  }
  const baseline = view("baseline"), variant = view("variant"), chosen = side === "baseline" ? baseline : variant;
  const row = chosen[period - 1], baseRow = baseline[period - 1], variantRow = variant[period - 1];
  const grand = result?.sides[side].market_rows.find(r => r.period === period && r.sector_id === "total");
  const groups = result?.sides[side].customer_decisions.filter(r => r.period === period && (sector === "total" || r.sector_id === sector)) || [];
  const families = result?.sides[side].family_rows.filter(r => r.period === period && r.sector_id === sector && r.active_vu_count > 0) || [];
  return <section className="panel ict-workbench market-workbench" data-testid="market-workbench" aria-label="Gemeinsamer Modellmarkt">
    <h2>Markt und Strategiefamilien verstehen</h2><p>Alle aktiven Modellanbieter werden gemeinsam bilanziert. Künftige Risiken folgen dem gewählten Versicherer; alte Schadenreserven bleiben beim bisherigen Träger. Die Einheiten sind Modellwährung.</p>
    <p><a href="/api/seminar/handbook/market_ap5.html" target="_blank" rel="noreferrer">Einsteigeranleitung: Markt, Gruppen und Handfälle</a></p>
    <p><a href="/api/seminar/handbook/market_ap6.html" target="_blank" rel="noreferrer">BaFin-Referenzfall: Quellen, Gewichte und Workshop-Annahmen</a></p>
    {error && <p role="alert" className="ict-error">{error}</p>}
    <div className="ict-fields"><label>Marktfall<select aria-label="Marktfall" value={caseId} disabled={busy} onChange={e => { invalidate(); setInput(null); setCaseId(e.target.value); }}>{Object.entries(caseNames).map(([id, label]) => <option key={id} value={id}>{label}</option>)}</select></label>
      <label>Marktperioden<select aria-label="Marktperioden" value={horizon} disabled={busy} onChange={e => { invalidate(); setInput(null); setHorizon(Number(e.target.value)); }}>{[2, 5, 10, 25, 50, 100].map(n => <option key={n}>{n}</option>)}</select></label>
      <label>Anzahl Modellanbieter<select aria-label="Anzahl Modellanbieter" value={presetCount} disabled={busy || caseId !== "market"} onChange={e => { invalidate(); setInput(null); setCount(Number(e.target.value)); }}>{[2, 3, 40, 41].map(n => <option key={n}>{n}</option>)}</select></label></div>
    <div className="ict-downloads"><button type="button" disabled={busy} onClick={load}>Modellmarkt laden</button><label>Marktdatei öffnen<input type="file" accept=".json,application/json" aria-label="Marktdatei öffnen" disabled={busy} onChange={e => { const file = e.target.files?.[0]; if (file) { invalidate(); setInput(null); setBundle(null); setReference(null); void act(async version => { if (file.size > 16 * 1024 * 1024) throw new Error("Marktdatei überschreitet 16 MiB."); const source = JSON.parse(await file.text()); const body: Result = await post("/calculate", source); if (version === revision.current) { accept(body); setResult(body); setHadResult(true); setFilter("market"); setPeriod(Math.min(6, body.period_count)); } }); } e.target.value = ""; }} /></label></div>
    {!result && hadResult && <p role="status">Eingaben geändert: Das bisherige Marktergebnis ist veraltet. Bitte neu berechnen.</p>}
    {input && <><p>{input.provenance.description}</p><p>{input.insurers.length} Modellanbieter · {input.period_count} Perioden. Fehlende Sparten werden nicht automatisch ergänzt.</p>
      {bundle && <div data-testid="bafin-reference"><h3>BaFin-Gruppenauswertung 2024 – Workshop</h3><p>{original ? "Schreibfreies Demooriginal. Für Änderungen als eigene Sitzung übernehmen." : "Eigene bearbeitbare Sitzung. Faktenoriginal und Workshop-Annahmen bleiben getrennt."}</p>{original && <button type="button" disabled={busy} onClick={() => { setOriginal(false); changed(structuredClone(input)); }}>Als eigene Sitzung übernehmen</button>}
        <p>Verdiente Bruttobeiträge einschließlich Ausland und übernommener Rückversicherung; redaktionelle Gruppen ohne konzerninterne Eliminierung. Kein vollständiger deutscher Direktmarkt. Kfz-/Sach-Aufteilung unbekannt; der folgende Mix ist eine Workshop-Annahme.</p>
        <fieldset disabled={busy || original}><legend>Schaden/Unfall auf Modellsparten und Rest aufteilen</legend><div className="ict-fields">{Object.entries(mix).map(([s, v]) => <label key={s}>{s === "unmodeled" ? "Nicht modellierter Rest" : names[s]} in %<input aria-label={`Workshop-Anteil ${s}`} value={v} onChange={e => { invalidate(); setReference(null); setMixPending(true); setMix({ ...mix, [s]: e.target.value }); }} /></label>)}</div><p>Zusammen 100 %. Neu abbilden erzeugt die Modellquelle einschließlich einer neuen Baseline/Variante; eigene Modelländerungen werden dabei ersetzt.</p><button type="button" onClick={() => rebuildReference(false)}>Spartenmix neu abbilden</button></fieldset>
        {mixPending && <p role="status">Spartenmix geändert: Zuerst neu abbilden, dann den neuen Modellmarkt berechnen.</p>}
        <details><summary>Quellenwerte und bearbeitete Annahmen</summary><fieldset disabled={busy || original}><legend>Beitragswert für eine Workshop-Variante überschreiben</legend><label>Quellenzeile<select aria-label="BaFin Quellenzeile" value={entityRow} onChange={e => { const id = Number(e.target.value); setEntityRow(id); setOverrideAmount(bundle.source_catalog.entities.find(r => r.workbook_row === id)!.premium_million_eur); }}>{bundle.source_catalog.entities.map(r => <option key={r.workbook_row} value={r.workbook_row}>{r.entity_source_name} · {r.group_assertion}</option>)}</select></label><div className="ict-fields"><label>Angenommener Beitrag in Mio. EUR<input aria-label="BaFin angenommener Beitrag" value={overrideAmount} onChange={e => setOverrideAmount(e.target.value)} /></label><label>Begründung der Workshop-Annahme<input aria-label="BaFin Override Begründung" value={overrideNote} onChange={e => setOverrideNote(e.target.value)} /></label></div><button type="button" onClick={() => rebuildReference(true)}>Annahme übernehmen und Auswahl neu abbilden</button></fieldset><p>Overrides ändern weder die Originalzellen noch ihren Herkunftsnachweis. Alle 145 Gruppen werden neu sortiert; stabile IDs bleiben erhalten. Gruppierungen sind redaktionell und nicht vollständig unabhängig geprüft.</p>
          <div className="table-scroll" role="region" aria-label="BaFin Einzelgesellschaften der ausgewählten VU" tabIndex={0}><table><thead><tr><th>Gesellschaft</th><th>Quellsparte</th><th>Original Mio. EUR</th><th>Quelle / Zelle</th><th>Aussage</th></tr></thead><tbody>{bundle.source_catalog.entities.filter(r => reference?.groups.find(g => g.insurer_id === actor)?.entity_rows.includes(r.workbook_row)).map(r => <tr key={r.workbook_row}><th scope="row">{r.entity_source_name}</th><td>{r.source_sector}</td><td>{eur(r.premium_million_eur)}</td><td><a href={bundle.source_catalog.source_files.find(s => s.id === r.source_id)?.url} target="_blank" rel="noreferrer">BaFin {r.source_sheet}!{r.source_cell}</a></td><td>{r.value_status === "source_exact_zero" ? "Belegter Nullwert" : "Gerundeter Quellenwert"}</td></tr>)}</tbody></table></div>
          {bundle.overrides.map(o => <p key={o.entity_row}>Workshop-Override Zeile {o.entity_row}: {eur(o.premium_million_eur)} Mio. EUR · {o.note}</p>)}</details>
        {reference && <><p data-testid="bafin-denominators">Erfasstes Quellenvolumen {eur(reference.universe_total_million_eur)} Mio. EUR · ausgewählte 40 Gruppen {eur(reference.selected_total_million_eur)} Mio. EUR. Anteil an diesen Nennern ist kein Anteil am gesamten deutschen Markt.</p><p data-testid="bafin-rest">Nicht ausgewählte Gruppen: {eur(reference.rest.unselected_groups_million_eur)} Mio. EUR. Nicht modellierte Zweige der ausgewählten Gruppen: {eur(reference.rest.selected_unmodeled_million_eur)} Mio. EUR (angenommener Mix). Diese Restkomponenten überlappen nicht.</p><p>Referenzgrenze: Rang 40 {reference.rank_40.name} {eur(reference.rank_40.total)}, Rang 41 {reference.rank_41.name} {eur(reference.rank_41.total)} Mio. EUR. Originalgrenze innerhalb der BaFin-Zuordnung geprüft; bearbeitete Auswahl und Rangreihenfolge haben keine neue unabhängige Quellenabnahme.</p>
          <details><summary>40 Gruppen, Gewichte und Modellbasis zeigen</summary><div className="table-scroll" role="region" aria-label="BaFin Gruppen und Quellengewichte" tabIndex={0}><table><thead><tr><th>Rang</th><th>Gruppe</th><th>Beiträge Mio. EUR</th><th>Anteil an 40 Gruppen</th><th>Anteil am Quellenvolumen</th><th>Angenommener Spartenrest</th></tr></thead><tbody>{reference.groups.map(g => <tr key={g.group_id}><td>{g.rank}</td><th scope="row">{g.name}{g.override_rows.length ? " · Workshop-Override" : ""}</th><td>{eur(g.total)}</td><td>{(Number(g.selected_weight) * 100).toLocaleString("de-DE", { maximumFractionDigits: 3 })} %</td><td>{(Number(g.source_weight) * 100).toLocaleString("de-DE", { maximumFractionDigits: 3 })} %</td><td>{eur(g.unmodeled_million_eur)}</td></tr>)}</tbody></table></div></details>
          {reference.model_binding === "custom_workshop_model" && <p>Eigene Modellquelle: Mengen und Bilanzen können von der aus Gewichten erzeugten Vorlage abweichen. Quellenanteile und berechnete Modellanteile sind getrennte Größen.</p>}</>}
        <p>Skalierung: {bundle.workshop.scale_model_currency_per_million_eur.replace(".", ",")} Modellwährung je Mio. EUR als anfängliches Beitragsziel. Kfz/Sach: Ziel ÷ Modellpreis {bundle.workshop.model_price} ergibt die auf vier Stellen gerundete Exposition. Leben: eine deklarierte Modellpolice je aktivierter Gruppe. Kranken: 100 deklarierte Modellpolicen je aktivierter Gruppe. Anfangsaktiva: Beitragsziel × {bundle.workshop.opening_assets_multiple}; Schadenquote: {Number(bundle.workshop.loss_ratio) * 100} %. Kapital, Schäden und Strategien sind Annahmen; Modellperioden sind keine historischen Jahre.</p></div>}
      <fieldset disabled={busy}><legend>Kfz-Variante ab Periode 6 · Einzel-VU-Auswahl jederzeit</legend><div className="ict-fields"><label>Anbieter für Variante und Einzel-VU-Excel<select aria-label="Markt Anbieter" value={actor} onChange={e => setActor(Number(e.target.value))}>{input.insurers.map(a => <option key={a.insurer_id} value={a.insurer_id}>{a.name}</option>)}</select></label>
        <label>Ausführbare Strategiefamilie<select aria-label="Markt Strategiefamilie" value={family} onChange={e => setFamily(e.target.value)}>{input.families.filter(f => f.sector_id === "motor").map(f => <option key={f.family_id} value={f.family_id}>{f.label}</option>)}</select></label>
        <label>Familienende einschließlich<input aria-label="Markt Familienende" type="number" min="6" max={input.period_count} value={end} onChange={e => setEnd(Number(e.target.value))} /></label></div>
        <button type="button" disabled={original || input.period_count < 6 || !family || end < 6 || end > input.period_count || !input.insurers.find(a => a.insurer_id === actor)?.sectors.motor} onClick={assignFamily}>Familie für Variante übernehmen</button>
        <details><summary>Aufnahme mit Kosten und Vorlauf erweitern</summary><p>Entscheidung und einmalige Kosten in Periode 6. Die höhere Aufnahme wirkt erst nach dem Vorlauf; danach gilt wieder die Grundkapazität. Ersetzt die Kfz-Aufnahmemaßnahme dieser VU in der Variante.</p><div className="ict-fields">
          <label>Maßnahmenkosten<input aria-label="Markt Maßnahmenkosten" value={cost} onChange={e => setCost(e.target.value)} /></label><label>Vorlauf in Perioden<input aria-label="Markt Vorlauf" type="number" min="0" max="100" value={lead} onChange={e => setLead(Number(e.target.value))} /></label><label>Wirkdauer<input aria-label="Markt Wirkdauer" type="number" min="1" max="100" value={duration} onChange={e => setDuration(Number(e.target.value))} /></label><label>Aufnahmekapazität<input aria-label="Markt Aufnahmekapazität" value={capacity} onChange={e => setCapacity(e.target.value)} /></label></div>
          <button type="button" disabled={original || input.period_count < 6 || !input.insurers.find(a => a.insurer_id === actor)?.sectors.motor} onClick={applyMeasure}>Aufnahmeplan für Variante übernehmen</button></details></fieldset>
      <details><summary>Quellen und vollständige Eingaben bearbeiten</summary><label>Vollständige Marktquelle<textarea aria-label="Vollständige Marktquelle" rows={12} value={expert} disabled={busy || original} onChange={e => { invalidate(); setReference(null); setExpert(e.target.value); }} /></label></details>
      <button className="primary-action" type="button" disabled={busy || mixPending} onClick={() => calculate()}>Gemeinsamen Markt berechnen</button></>}
    {busy && <p role="status">Alle Anbieter, Kunden und Bestände werden gemeinsam geprüft …</p>}
    {result && row && <div data-testid="market-results"><h3>Geprüfter Modellmarkt · {result.period_count} Perioden</h3><p>Nachweis <code>{result.content_digest}</code></p>
      <div className="ict-fields"><label>Markt Ergebnisperiode<select aria-label="Markt Ergebnisperiode" value={period} onChange={e => setPeriod(Number(e.target.value))}>{Array.from({ length: result.period_count }, (_, i) => <option key={i + 1}>{i + 1}</option>)}</select></label>
        <label>Markt Ergebnisvariante<select aria-label="Markt Ergebnisvariante" value={side} onChange={e => setSide(e.target.value as Side)}><option value="baseline">Baseline</option><option value="variant">Variante</option></select></label>
        <label>Markt Sparte<select aria-label="Markt Sparte" value={sector} onChange={e => setSector(e.target.value)}>{Object.entries(names).map(([id, label]) => <option key={id} value={id}>{label}</option>)}</select></label>
        <label>Markt Vergleichsgruppe<select aria-label="Markt Vergleichsgruppe" value={filter} onChange={e => setFilter(e.target.value)}><option value="market">Gesamter Modellmarkt</option>{input?.families.map(f => <option key={f.family_id} value={`family:${f.family_id}`}>Familie: {f.label}</option>)}{input?.peer_groups.map(g => <option key={g.group_id} value={`peer:${g.group_id}`}>Vergleich: {g.label}</option>)}{[...new Set(input?.insurers.map(a => a.insurance_group_id))].map(g => <option key={g} value={`insurance:${g}`}>Versicherungsgruppe: {input?.insurers.find(a => a.insurance_group_id === g)?.name || g}</option>)}</select></label></div>
      <p data-testid="market-grand-total">Gesamter Modellmarkt in P{period}: Eigenkapital {amountText(grand!.closing_equity)} · Aktiva {amountText(grand!.closing_assets)} · Passiva {amountText(grand!.closing_liabilities)}. Filter verändern keine Berechnung.</p>
      {filter.startsWith("peer:") && <p>Vergleichsgruppen können sich überlappen; ihre Summen werden nicht zum Markt addiert.</p>}
      <div className="market-kpis"><div><span>Eigenkapital der Auswahl</span><strong data-testid="market-equity">{amountText(row.closing_equity)}</strong></div><div><span>Periodenergebnis</span><strong>{amountText(row.period_profit)}</strong></div><div><span>Variante gegenüber Baseline</span><strong>{amountText(amountUnits(variantRow.closing_equity) - amountUnits(baseRow.closing_equity), true)}</strong><span>{percentText(variantRow.closing_equity, baseRow.closing_equity)}</span></div></div>
      <h4>Eigenkapitalverlauf der Auswahl</h4><Timeline baseline={baseline} variant={variant} />
      <details><summary>Exakte Markt-Verlaufstabelle öffnen</summary><div className="table-scroll" role="region" aria-label="Exakte Markt-Verlaufstabelle" tabIndex={0}><table><thead><tr><th>Periode</th><th>Eigenkapital Baseline</th><th>Eigenkapital Variante</th><th>Ergebnis Baseline</th><th>Ergebnis Variante</th></tr></thead><tbody>{baseline.map((r, i) => <tr key={r.period}><td>{r.period}</td><td>{amountText(r.closing_equity)}</td><td>{amountText(variant[i].closing_equity)}</td><td>{amountText(r.period_profit)}</td><td>{amountText(variant[i].period_profit)}</td></tr>)}</tbody></table></div></details>
      <h4>Strategiefamilien · disjunkte Buchungen des Modellmarkts</h4><p>Eine VU/Sparte/Periode gehört genau einer ausführbaren Familie. Diese Summen beziehen sich auf den ganzen Modellmarkt der gewählten Sparte.</p>
      <div className="market-families">{families.map(f => <div key={f.family_id}><span>{input?.families.find(x => x.family_id === f.family_id)?.label}</span><meter min="0" max={Math.max(1, ...families.map(x => Math.abs(Number(x.closing_equity))))} value={Math.abs(Number(f.closing_equity))} aria-label={`Betrag Eigenkapital ${f.family_id}`} /><strong>{amountText(f.closing_equity)}</strong><span>{f.active_vu_count} aktive VUs</span></div>)}</div>
      <div className="table-scroll" role="region" aria-label="Marktbuchung und Familien" tabIndex={0}><table><caption>{names[sector]} · {side === "baseline" ? "Baseline" : "Variante"} · P{period}</caption><thead><tr><th>Auswahl</th><th>Aktiva</th><th>Passiva</th><th>Eigenkapital</th><th>Prämie</th><th>Versicherungsaufwand</th><th>Betrieb</th><th>Gedeckte Menge</th><th>Gewichteter Preis</th></tr></thead><tbody>{[row, ...families].map((r, i) => <tr key={i}><th scope="row">{i ? input?.families.find(f => f.family_id === r.family_id)?.label : "Gefilterte Auswahl"}</th>{[r.closing_assets, r.closing_liabilities, r.closing_equity, r.premium_income, r.insurance_expense, r.operating_expense].map((v, j) => <td key={j}>{amountText(v)}</td>)}<td>{r.covered_quantity === null ? "Verschiedene Sparten-Einheiten" : amountText(r.covered_quantity)}</td><td>{r.weighted_price === null ? "Nicht definiert" : amountText(r.weighted_price)}</td></tr>)}</tbody></table></div>
      <h4>Kundenwahl und Risiko · ganzer Modellmarkt</h4><p>Die ganze Kohorte folgt einem Träger; alte Verbindlichkeiten bleiben zurück. In Kfz/Sach ist Menge Exposition, in Leben/Kranken ist sie Anfangspolicenbestand. Diese Mengen werden über Sparten nicht addiert.</p>
      <div className="table-scroll" role="region" aria-label="Kunden und Risikobuchung" tabIndex={0}><table><thead><tr><th>Kohorte</th><th>Sparte</th><th>Bisher</th><th>Aktuell</th><th>Menge</th><th>Prämie</th><th>Risiko dieser Periode</th><th>Unversicherter Schaden</th></tr></thead><tbody>{groups.map(g => <tr key={g.group_id}><th scope="row">{g.group_id}</th><td>{names[g.sector_id]}</td><td>{g.previous_insurer_id ?? "unversichert"}</td><td>{g.insurer_id ?? "unversichert"}</td><td>{amountText(g.quantity)}</td><td>{amountText(g.premium_income)}</td><td>{amountText(g.risk_loss)}</td><td>{amountText(g.uninsured_loss)}</td></tr>)}</tbody></table></div>
      <details><summary>Ausgeführte Familien, Parameter und Maßnahmen zeigen</summary>{result.sides[side].vu_rows.filter(r => r.period === period && (sector === "total" || r.sector_id === sector)).map(r => <p key={`${r.insurer_id}-${r.sector_id}`}>VU{r.insurer_id} · {names[r.sector_id]} · {input?.families.find(f => f.family_id === r.family_id)?.label} · {JSON.stringify(r.parameters)} · Maßnahmen {r.active_measures?.join(", ") || "keine"} · Kosten {amountText(r.measure_cost)} · Informationsstand P{r.information_period}</p>)}</details>
      <div className="ict-downloads"><button type="button" disabled={busy} onClick={() => download(true)}>Einzel-VU {actor} in Excel</button><button type="button" disabled={busy} onClick={() => download(false)}>Marktquelle als JSON sichern</button></div>
      <p>Nur deklarierte oder synthetische Modellwerte. Kein deutsches Top-40-Ranking, neue Lebens-Nachfrage, gekoppelter ICT-Schock, dynamische Insolvenz oder regulatorische Kapitalrechnung. Die vorhandenen AP3-Fälle bleiben separat verfügbar.</p>
    </div>}
  </section>;
}
