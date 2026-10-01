import { useRef, useState } from "react";
import type { CheckedFourSector } from "./fourSectorSources";
import type { SeminarCapitalDefaults } from "./CapitalWorkbench";

type Assignment = { actor_type: string; target_id: string; sector_id: string; strategy_id: string; period_from: number; period_through: number; parameters: Record<string, string | number> };
type Input = { period_count: number; case_id: string; policyholder_groups: { group_id: string; sector_id: string; exposure: string; initial_insurer_id: number }[]; strategies: Record<"baseline" | "variant", Assignment[]> };
type Row = { period: number; closing_assets: string; closing_liabilities: string; closing_equity: string; period_profit: string };
type Trace = { period: number; sector_id: string; quoted_price?: string; covered_exposure?: string; premium_income?: string; advertising_expense?: string; group_decisions?: { group_id: string; chosen_insurer_id: number | null; booked_premium: string }[]; generated_period_source?: Record<string, string | number> };
type Result = { valid: boolean; content_digest: string; insurer_id: number; scenario_id: string; period_count: number; generated_sources: Record<"baseline" | "variant", CheckedFourSector["input"]>; sides: Record<"baseline" | "variant", { content_digest: string; total_rows: Row[]; sectors: { sector_id: string; rows: Row[] }[] }>; decision_traces: Record<"baseline" | "variant", Trace[]> };
export type SeminarCompanions = { ict: unknown; guided: unknown };
const BASE = "/api/seminar";
const sectors: Record<string, string> = { motor: "Kfz", property_liability: "Sach-Haftpflicht", life: "Leben", health: "Kranken", total: "Gesamt" };
const rules: Record<string, string> = { "vu.vrvu01": "Preis und Werbung · Zufall I", "vn.vrvn06": "VN-Auswahl · Beste Information", "life.opening_assets_rate": "Lebens-Anlagesatz", "health.opening_policy_price": "Kranken-Beitrag", "health.declared_new_business": "Kranken-Neugeschäft", "health.declared_exits": "Kranken-Abgänge" };
const parameters: Record<string, string> = { premium_factor: "Preisfaktor", advertising_factor: "Werbefaktor", premium_factor_shock: "Preisfaktor bei Änderungsschock", advertising_factor_shock: "Werbefaktor bei Änderungsschock", insurance_threshold: "Versicherungsschwelle", insurance_threshold_shock: "Schwelle bei Änderungsschock", rate_per_period: "Anlagesatz je Periode", amount_per_opening_policy: "Beitrag je Anfangspolice", count: "Anzahl je Periode" };
const key = (item: Assignment) => `${item.target_id}|${item.sector_id}|${item.strategy_id}`;
const shown = (value: string | number) => String(value).replace(".", ",");

async function post(path: string, value: unknown) {
  const response = await fetch(BASE + path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(value) });
  const body = await response.json();
  if (!response.ok || !body.valid) throw new Error(body.issues?.[0] ? `${body.issues[0].message} (${body.issues[0].path})` : "Seminarprüfung fehlgeschlagen.");
  if (body.content_digest && response.headers.get("etag") !== `"${body.content_digest}"`) throw new Error("Inhaltsnachweis der Antwort stimmt nicht.");
  return body;
}

export default function SeminarWorkbench({ onReady, onSources }: { onReady: (source: CheckedFourSector | null, capital: SeminarCapitalDefaults | null) => void; onSources: (sources: SeminarCompanions) => void }) {
  const [caseId, setCaseId] = useState("price"), [horizon, setHorizon] = useState(100), [title, setTitle] = useState("");
  const [input, setInput] = useState<Input | null>(null), [companions, setCompanions] = useState<SeminarCompanions | null>(null);
  const [capitalAssumptions, setCapitalAssumptions] = useState<SeminarCapitalDefaults | null>(null);
  const [expert, setExpert] = useState(""), [expertDirty, setExpertDirty] = useState(false), [confirmed, setConfirmed] = useState(false);
  const [result, setResult] = useState<Result | null>(null), [period, setPeriod] = useState(6), [side, setSide] = useState<"baseline" | "variant">("variant");
  const [target, setTarget] = useState(""), [start, setStart] = useState(6), [end, setEnd] = useState(100), [edits, setEdits] = useState<Record<string, string | number>>({}), [pending, setPending] = useState(false);
  const [demo, setDemo] = useState(false), [busy, setBusy] = useState(false), [error, setError] = useState<string | null>(null), [bundleDigest, setBundleDigest] = useState<string | null>(null);
  const revision = useRef(0);
  function invalidate() { revision.current++; setResult(null); setConfirmed(false); setError(null); setBundleDigest(null); onReady(null, null); }
  function changed(source: Input) { invalidate(); setInput(source); setExpert(JSON.stringify(source, null, 2)); setExpertDirty(false); }
  function choose(source: Input, id: string) {
    setTarget(id); const item = source.strategies.variant.find(a => key(a) === id && a.period_from <= 6 && a.period_through >= Math.min(6, source.period_count)) || source.strategies.baseline.find(a => key(a) === id);
    setEdits({ ...item?.parameters }); setStart(6); setEnd(source.period_count); setPending(false);
  }
  async function act(work: (version: number) => Promise<void>) {
    const version = revision.current; setBusy(true); setError(null);
    try { await work(version); }
    catch (failure) { if (version === revision.current) setError(failure instanceof Error ? failure.message : "Seminaraktion fehlgeschlagen."); }
    finally { if (version === revision.current) setBusy(false); }
  }
  function publish(next: Result, selected: "baseline" | "variant", capital = capitalAssumptions) {
    onReady({ input: next.generated_sources[selected], evidenceDigest: next.sides[selected].content_digest, insurerId: next.insurer_id, scenarioId: next.scenario_id, variantId: selected, periodCount: next.period_count }, capital ? { ...capital, source_content_digest: next.sides[selected].content_digest } : null);
  }
  async function load() {
    invalidate();
    await act(async version => {
      const body = await post("/workshop-case", { case_id: caseId, period_count: horizon });
      if (version === revision.current) { setInput(body.source_input); setExpert(JSON.stringify(body.source_input, null, 2)); setExpertDirty(false); setCompanions(body.companion_sources); setCapitalAssumptions(body.capital_assumptions); setTitle(body.title); setDemo(false); choose(body.source_input, key(body.source_input.strategies.baseline[0])); }
    });
  }
  function applyAssignment() {
    if (!input) return;
    const template = input.strategies.baseline.find(item => key(item) === target);
    if (!template) return;
    const next = structuredClone(input), kept: Assignment[] = [];
    for (const item of next.strategies.variant) {
      if (key(item) !== target || item.period_through < start || item.period_from > end) kept.push(item);
      else { if (item.period_from < start) kept.push({ ...item, period_through: start - 1 }); if (item.period_through > end) kept.push({ ...item, period_from: end + 1 }); }
    }
    kept.push({ ...template, period_from: start, period_through: end, parameters: edits });
    next.strategies.variant = kept; changed(next); setPending(false);
  }
  async function calculate() {
    if (!confirmed || pending || !input) return;
    await act(async version => {
      const source = expertDirty ? JSON.parse(expert) : input;
      const body = await post("/calculate", source);
      if (version === revision.current) { setInput(source); setExpert(JSON.stringify(source, null, 2)); setExpertDirty(false); setResult(body); setPeriod(Math.min(6, body.period_count)); setConfirmed(false); choose(source, source.strategies.baseline.length ? key(source.strategies.baseline[0]) : ""); publish(body, side); }
    });
  }
  async function download(extension: string) {
    if (!input || !result) return;
    await act(async version => {
      const bundle = extension === "bundle";
      const response = await fetch(BASE + (bundle ? "/bundle.json" : `/export.${extension}`), { method: "POST", headers: { "Content-Type": "application/json", "If-Match": `"${result.content_digest}"` }, body: JSON.stringify(bundle ? { title, sources: { modern: input, ...companions } } : input) });
      if (!response.ok || (!bundle && response.headers.get("etag") !== `"${result.content_digest}"`)) throw new Error("Export benötigt dieselben vollständig geprüften Quellen.");
      const blob = await response.blob(); if (version !== revision.current) return;
      const digest = response.headers.get("etag")?.replaceAll('"', "");
      if (!digest) throw new Error("Export ohne Inhaltsnachweis.");
      const url = URL.createObjectURL(blob), link = document.createElement("a"); link.href = url; link.download = `IMS-${bundle ? "Seminar" : "Strategie"}-${digest.slice(0, 12)}.${bundle ? "json" : extension}`; link.click(); setTimeout(() => URL.revokeObjectURL(url), 0);
    });
  }
  async function importBundle(read: () => Promise<unknown>) {
    invalidate();
    await act(async version => {
      const imported = await post("/import-bundle", await read());
      if (version !== revision.current) return;
      const source = imported.bundle.sources.modern, next = imported.results.modern;
      setCaseId(source.case_id); setHorizon(source.period_count);
      setInput(source); setExpert(JSON.stringify(source, null, 2)); setExpertDirty(false); setTitle(imported.bundle.title); setCompanions({ ict: imported.bundle.sources.ict, guided: imported.bundle.sources.guided });
      setCapitalAssumptions(imported.bundle.capital_assumptions); setResult(next); setPeriod(Math.min(6, next.period_count)); setDemo(true); setBundleDigest(imported.content_digest); choose(source, source.strategies.baseline.length ? key(source.strategies.baseline[0]) : ""); publish(next, side, imported.bundle.capital_assumptions);
    });
  }
  return <section className="panel ict-workbench seminar-workbench" data-testid="seminar-workbench" aria-label="Modernes Managementseminar">
    <h2>Strategie, VN-Auswahl und Bilanz im Seminar verfolgen</h2><p>Eine ausdrücklich moderne Kopplung mit benannten Gruppen: Preis je gedeckter Exposition × Menge ergibt gebuchte Prämie. Schäden und Leistungen sind deklarierte Eingaben. Die Bilanz zeigt eine VU; konkurrierende Angebote werden für die VN-Auswahl berücksichtigt.</p>
    {error && <p role="alert" className="ict-error">{error}</p>}
    <div className="ict-fields"><label>Seminarfall<select aria-label="Seminarfall" disabled={busy || demo} value={caseId} onChange={e => { invalidate(); setInput(null); setCaseId(e.target.value); }}><option value="price">Preis und Anbieterwechsel</option><option value="inflation">Kosten und Beitragsreaktion</option><option value="capital">Lebens-Anlageentscheidung</option>{!["price", "inflation", "capital"].includes(caseId) && <option value={caseId}>Importierter Fall: {caseId}</option>}</select></label><label>Perioden<select aria-label="Seminarperioden" disabled={busy || demo} value={horizon} onChange={e => { invalidate(); setInput(null); setHorizon(Number(e.target.value)); }}>{[2, 5, 10, 25, 50, 100].map(n => <option key={n}>{n}</option>)}</select></label></div>
    <div className="ict-downloads"><button type="button" disabled={busy || demo || !["price", "inflation", "capital"].includes(caseId)} onClick={load}>Seminarfall laden</button><button type="button" disabled={busy || !["price", "inflation", "capital"].includes(caseId)} onClick={() => importBundle(async () => { const response = await fetch(`${BASE}/bundles/${caseId}.json`); if (!response.ok) throw new Error("Kuratierter Seminarfall nicht verfügbar."); return response.json(); })}>Kuratierte Demo öffnen</button>{["price", "inflation", "capital"].includes(caseId) && <a href={`${BASE}/bundles/${caseId}.json`} download>Kuratierter Musterfall</a>}</div>
    <label>Portables Seminarbündel importieren<input aria-label="Portables Seminarbündel importieren" type="file" accept=".json,application/json" disabled={busy} onChange={e => { const file = e.target.files?.[0]; if (file) void importBundle(async () => { if (file.size > 16 * 1024 * 1024) throw new Error("Seminarbündel überschreitet 16 MiB."); return JSON.parse(await file.text()); }); e.target.value = ""; }} /></label>
    {input && <div className="management-inputs"><h3>{title}</h3>
      {demo && <p role="status">Demomodus: Alle Quellen wurden frisch geprüft und gerechnet. Änderungen und Speicherung sind gesperrt. Bündelnachweis <code>{bundleDigest}</code></p>}
      {demo && <button type="button" disabled={busy} onClick={() => { setDemo(false); setConfirmed(false); }}>Als bearbeitbare Sitzung übernehmen</button>}
      <details><summary>Benannte VN-Gruppen und Anfangsverträge</summary><p>Jede Exposition ist ein ausdrücklich erklärtes Workshopgewicht. Beide Varianten teilen dieselben Gruppen und denselben Anfang.</p><div className="ict-fields">{input.policyholder_groups.map(group => <label key={group.group_id}>{group.group_id} · {sectors[group.sector_id]} · Anfang VU {group.initial_insurer_id}<input aria-label={`Exposition ${group.group_id}`} value={group.exposure} disabled={busy || demo || expertDirty} onChange={e => { const next = structuredClone(input); next.policyholder_groups.find(g => g.group_id === group.group_id)!.exposure = e.target.value.replace(",", "."); changed(next); }} /></label>)}</div></details>
      <fieldset disabled={busy || demo || expertDirty || input.period_count < 6}><legend>Strategie für die Variante ab Periode 6</legend><label>Gruppe und Strategiekanal<select aria-label="Gruppe und Strategiekanal" value={target} onChange={e => choose(input, e.target.value)}>{input.strategies.baseline.map(item => <option key={key(item)} value={key(item)}>{item.target_id} · {sectors[item.sector_id]} · {rules[item.strategy_id]}</option>)}</select></label>
        <div className="ict-fields"><label>Beginn einschließlich<input aria-label="Strategiebeginn" type="number" min="6" max={input.period_count} value={start} onChange={e => { invalidate(); setStart(Number(e.target.value)); setPending(true); }} /></label><label>Ende einschließlich<input aria-label="Strategieende" type="number" min={start} max={input.period_count} value={end} onChange={e => { invalidate(); setEnd(Number(e.target.value)); setPending(true); }} /></label>
          {Object.entries(edits).map(([field, value]) => <label key={field}>{parameters[field]}<input aria-label={`Strategie ${parameters[field]}`} value={value} onChange={e => { invalidate(); setEdits({ ...edits, [field]: field === "count" ? Number(e.target.value) : e.target.value.replace(",", ".") }); setPending(true); }} /></label>)}</div>
        <button type="button" disabled={!pending || start < 6 || start > end || end > input.period_count} onClick={applyAssignment}>Zuordnung für Variante übernehmen</button>
      </fieldset>
      <details><summary>Expertenmodus: vollständige Gruppen, Ziehungen und Quellen</summary><label>Moderne Seminarquellen<textarea aria-label="Moderne Seminarquellen" rows={12} value={expert} disabled={busy || demo} onChange={e => { invalidate(); setExpert(e.target.value); setExpertDirty(true); setPending(false); }} /></label></details>
      {!demo && <><label><input type="checkbox" checked={confirmed} disabled={busy} onChange={e => setConfirmed(e.target.checked)} />Die modernen Einheiten, Gruppen und exogenen Annahmen dieses Falls sind erklärt.</label><button type="button" className="primary-action" disabled={busy || pending || !confirmed} onClick={calculate}>Moderne Kopplung berechnen</button></>}
      {companions && <div className="ict-downloads"><button type="button" disabled={busy || demo} onClick={() => onSources(companions)}>ICT- und 100er-Quellen bereitstellen</button><a href="#ict">Zur ICT-Wirkung</a><a href="#hundred">Zum kontrollierten 100er-Lauf</a></div>}
    </div>}
    {busy && <p role="status">Seminarquellen werden vollständig geprüft und gerechnet …</p>}
    {result && <div className="management-results" data-testid="seminar-results"><h3>Nachgewiesene moderne Wirkung · {result.period_count} Perioden</h3><p>Nachweis <code>{result.content_digest}</code></p>
      <div className="ict-fields"><label>Seminar-Ergebnisperiode<select aria-label="Seminar-Ergebnisperiode" value={period} disabled={busy} onChange={e => setPeriod(Number(e.target.value))}>{Array.from({ length: result.period_count }, (_, i) => <option key={i + 1}>{i + 1}</option>)}</select></label><label>Quelle für Kapitalwirkung<select aria-label="Seminar Kapitalquelle" value={side} disabled={busy} onChange={e => { const selected = e.target.value as "baseline" | "variant"; setSide(selected); publish(result, selected); }}><option value="baseline">Baseline</option><option value="variant">Variante</option></select></label></div>
      <div className="table-scroll" role="region" aria-label="Seminar Modellbilanz" tabIndex={0}><table><thead><tr><th>Seite</th><th>Sparte</th><th>Aktiva</th><th>Passiva</th><th>Eigenkapital</th><th>Ergebnis</th></tr></thead><tbody>{(["baseline", "variant"] as const).flatMap(current => [...result.sides[current].sectors, { sector_id: "total", rows: result.sides[current].total_rows }].map(sector => { const row = sector.rows[period - 1]; return <tr key={`${current}-${sector.sector_id}`}><td>{current === "baseline" ? "Baseline" : "Variante"}</td><td>{sectors[sector.sector_id]}</td><td>{shown(row.closing_assets)}</td><td>{shown(row.closing_liabilities)}</td><td>{shown(row.closing_equity)}</td><td>{shown(row.period_profit)}</td></tr>; }))}</tbody></table></div>
      <h4>Entscheidung → Menge/Fluss → Bilanz · {side === "baseline" ? "Baseline" : "Variante"}</h4>
      {result.decision_traces[side].filter(item => item.period === period).map(trace => <div key={trace.sector_id} className="seminar-trace"><h5>{sectors[trace.sector_id]}</h5>{trace.quoted_price ? <><p>Preis {shown(trace.quoted_price)} × gedeckte Exposition {shown(trace.covered_exposure!)} = gebuchte Prämie {shown(trace.premium_income!)}. Werbeaufwand {shown(trace.advertising_expense!)}.</p><p>{trace.group_decisions?.map(group => `${group.group_id}: ${group.chosen_insurer_id === null ? "unversichert" : `VU ${group.chosen_insurer_id}`} · gebucht ${shown(group.booked_premium)}`).join("; ")}</p></> : <p>{Object.entries(trace.generated_period_source || {}).map(([field, amount]) => `${({ rate_per_period: "Anlagesatz", investment_result: "Anlageertrag", opening_backing_assets: "Anfangsaktiva", amount_per_opening_policy: "Beitrag je Anfangspolice", opening_policies: "Anfangspolicen", premium_income: "Beitragseinnahmen", new_business: "Neugeschäft", exits: "Abgänge", benefits_paid_exogenous: "Exogene Leistungszahlung" } as Record<string, string>)[field] || field}: ${shown(amount)}`).join(" · ")}</p>}</div>)}
      <div className="ict-downloads">{[["JSON", "json"], ["CSV", "csv"], ["Excel", "xlsx"]].map(([label, extension]) => <button key={extension} type="button" disabled={busy} onClick={() => download(extension)}>Strategie {label}</button>)}<button type="button" disabled={busy || !companions} onClick={() => download("bundle")}>Portables Seminarbündel</button><a href="#capital">Kapitalwirkung des Seminarfalls</a></div>
      <p>Nur die erklärten Kanäle sind gekoppelt. Der historische 100er und die ICT-Wirkung sind gesonderte Quellenpfade. Lebens-VN-Verhalten, endogene Schäden/Todesfälle, spartenübergreifende Finanzierung und regulatorische SCR/MCR-/Bedeckungsquoten bleiben offen.</p>
    </div>}
  </section>;
}
