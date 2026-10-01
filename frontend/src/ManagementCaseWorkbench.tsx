import { useRef, useState } from "react";
import type { CheckedFourSector } from "./fourSectorSources";

type Side = "baseline" | "variant";
type Row = { period: number; opening_assets: string; opening_liabilities: string; opening_equity: string; period_profit: string; closing_assets: string; closing_liabilities: string; closing_equity: string };
type FourInput = { insurer_id: number; scenario_id: string; variant_id: Side; sectors: Record<string, unknown> };
type Source = { sides: Record<Side, { four_sector_input: FourInput; source_contract: { economic_assumption: string } }> };
type Result = { valid: boolean; content_digest: string; period_count: number; insurer_id: number; scenario_id: string; sides: Record<Side, { content_digest: string; sectors: { sector_id: string; rows: Row[] }[]; total_rows: Row[] }> };
const BASE = "/api/management-case";
const sectors = { motor: "Kfz", property_liability: "Sach-Haftpflicht", life: "Leben", health: "Kranken", total: "Gesamt" };
const shown = (value: string) => value.replace(".", ",");

async function post(path: string, value: unknown) {
  const response = await fetch(BASE + path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(value) });
  const body = await response.json();
  if (!response.ok || !body.valid) throw new Error(body.issues?.[0] ? `${body.issues[0].message} (${body.issues[0].path})` : "Gemeinsame Rechnung nicht verfügbar.");
  if (body.content_digest && response.headers.get("etag") !== `"${body.content_digest}"`) throw new Error("Antwortnachweis stimmt nicht überein.");
  return body;
}

export default function ManagementCaseWorkbench({ onReady }: { onReady: (source: CheckedFourSector | null) => void }) {
  const [caseId, setCaseId] = useState("inflation"), [horizon, setHorizon] = useState(100), [insurer, setInsurer] = useState(1);
  const [source, setSource] = useState<Source | null>(null), [expert, setExpert] = useState("");
  const [dirty, setDirty] = useState(false), [confirmed, setConfirmed] = useState(false);
  const [result, setResult] = useState<Result | null>(null), [period, setPeriod] = useState(6), [side, setSide] = useState<Side>("variant");
  const [busy, setBusy] = useState(false), [error, setError] = useState<string | null>(null);
  const revision = useRef(0);
  function invalidate() { revision.current++; setResult(null); setConfirmed(false); setError(null); onReady(null); }
  async function act(work: (version: number) => Promise<void>) {
    const version = revision.current; setBusy(true); setError(null);
    try { await work(version); }
    catch (failure) { if (revision.current === version) setError(failure instanceof Error ? failure.message : "Gemeinsame Rechnung fehlgeschlagen."); }
    finally { if (revision.current === version) setBusy(false); }
  }
  function publish(nextResult: Result, nextSource: Source, nextSide: Side) {
    onReady({ input: nextSource.sides[nextSide].four_sector_input, evidenceDigest: nextResult.sides[nextSide].content_digest,
      insurerId: nextResult.insurer_id, scenarioId: nextResult.scenario_id, variantId: nextSide, periodCount: nextResult.period_count });
  }
  async function load() {
    invalidate();
    await act(async version => {
      const body = await post("/workshop-case", { case_id: caseId, period_count: horizon, insurer_id: insurer });
      if (revision.current === version) { setSource(body.source_input); setExpert(JSON.stringify(body.source_input, null, 2)); setDirty(false); }
    });
  }
  async function declare() {
    if (!confirmed) return;
    await act(async version => {
      const body = await post("/declare-sources", { source_input: JSON.parse(expert), explicit_common_source_declaration: true });
      if (revision.current === version) { setSource(body.source_input); setExpert(JSON.stringify(body.source_input, null, 2)); setDirty(false); setConfirmed(false); }
    });
  }
  async function calculate() {
    if (!source || !confirmed || dirty) return;
    await act(async version => {
      const body = await post("/calculate", source);
      if (revision.current === version) { setResult(body); setPeriod(Math.min(6, body.period_count)); setConfirmed(false); publish(body, source, side); }
    });
  }
  async function download(extension: string) {
    if (!source || !result) return;
    await act(async version => {
      const response = await fetch(`${BASE}/export.${extension}`, { method: "POST", headers: { "Content-Type": "application/json", "If-Match": `"${result.content_digest}"` }, body: JSON.stringify(source) });
      if (!response.ok || response.headers.get("etag") !== `"${result.content_digest}"`) throw new Error("Export benötigt denselben unveränderten Nachweis.");
      const data = await response.blob(); if (revision.current !== version) return;
      const url = URL.createObjectURL(data), link = document.createElement("a");
      link.href = url; link.download = `IMS-Management-${result.content_digest.slice(0, 12)}.${extension}`; link.click();
      setTimeout(() => URL.revokeObjectURL(url), 0);
    });
  }
  return <section className="panel ict-workbench management-case" data-testid="management-case-workbench" aria-label="Gemeinsamer Vier-Sparten-Fall">
    <div className="management-heading"><h2>Vier Sparten über 100 Perioden vergleichen</h2><p>Die bestehenden Teilmodelle werden für beide Seiten neu berechnet. Gemeinsame Modellwährung und ausdrücklich erklärte Quellen; keine still gleichgesetzten historischen Sparten oder VN-Populationen.</p></div>
    {error && <p role="alert" className="management-error ict-error">{error}</p>}
    <div className="management-inputs"><div className="ict-fields"><label>Fall<select aria-label="Managementfall" disabled={busy} value={caseId} onChange={e => { invalidate(); setSource(null); setCaseId(e.target.value); }}><option value="inflation">Deklarierte Schaden- und Leistungskosten</option><option value="price">Deklarierte Prämienvariante</option><option value="capital">Deklarierter Anlageertrag</option></select></label>
      <label>Perioden<select aria-label="Managementperioden" disabled={busy} value={horizon} onChange={e => { invalidate(); setSource(null); setHorizon(Number(e.target.value)); }}>{[2, 5, 10, 25, 50, 100].map(value => <option key={value}>{value}</option>)}</select></label>
      <label>VU-ID<input aria-label="Management VU-ID" type="number" min="1" max="25" disabled={busy} value={insurer} onChange={e => { invalidate(); setSource(null); setInsurer(Number(e.target.value)); }} /></label></div>
      <button type="button" disabled={busy} onClick={load}>Gemeinsame Quellen erzeugen</button>
      {source && <><p>{source.sides.baseline.source_contract.economic_assumption}</p><p>Die Vorlagen ändern deklarierte Eingaben ab Periode 6. Sie führen noch keine PR154-Katalogstrategie aus. Die Nichtleben-/Leben-Quellen besitzen keine gemeinsame technische Szenario-ID; der Quellenvertrag bindet ihren genauen Inhalt ausdrücklich über Digests.</p>
        <details><summary>Expertenmodus: vier Sparten und gemeinsame Quellen</summary><label>Management Quellenvertrag<textarea aria-label="Management Quellenvertrag" rows={12} disabled={busy} value={expert} onChange={e => { invalidate(); setExpert(e.target.value); setDirty(true); }} /></label></details>
        <label><input type="checkbox" disabled={busy} checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />Die wirtschaftliche Zusammengehörigkeit dieser Quellen und Varianten ist ausdrücklich erklärt.</label>
        {dirty && <><p role="status">Geänderte Quellen benötigen neue Inhaltsbindungen. Ihre VU-/Szenario-IDs werden dabei geprüft und bleiben erhalten.</p><button type="button" disabled={busy || !confirmed} onClick={declare}>Geänderte Quellen prüfen und neu binden</button></>}
        <button type="button" className="primary-action" disabled={busy || dirty || !confirmed} onClick={calculate}>Vier Sparten gemeinsam berechnen</button>
      </>}
    </div>
    {busy && <p role="status">Vier-Sparten-Quellen und Ergebnisse werden geprüft …</p>}
    {result && <div className="management-results" data-testid="management-case-results"><h3>Gemeinsame Modellbilanz · {result.period_count} Perioden · VU {result.insurer_id}</h3><p>Fall {result.scenario_id} · Nachweis <code>{result.content_digest}</code></p>
      <div className="ict-fields"><label>Ergebnisperiode<select aria-label="Management Ergebnisperiode" value={period} disabled={busy} onChange={e => setPeriod(Number(e.target.value))}>{Array.from({ length: result.period_count }, (_, i) => <option key={i + 1}>{i + 1}</option>)}</select></label>
        <label>Quelle für Kapitalwirkung<select aria-label="Management Kapitalquelle" value={side} disabled={busy} onChange={e => { const selected = e.target.value as Side; setSide(selected); if (source) publish(result, source, selected); }}><option value="baseline">Baseline</option><option value="variant">Variante</option></select></label></div>
      <div className="table-scroll" role="region" aria-label="Management Modellbilanz" tabIndex={0}><table><thead><tr><th>Seite</th><th>Sparte</th><th>Aktiva</th><th>Passiva</th><th>Eigenkapital</th><th>Ergebnis</th></tr></thead><tbody>{(["baseline", "variant"] as const).flatMap(current => [...result.sides[current].sectors, { sector_id: "total", rows: result.sides[current].total_rows }].map(sector => { const row = sector.rows[period - 1]; return <tr key={`${current}-${sector.sector_id}`}><td>{current === "baseline" ? "Baseline" : "Variante"}</td><td>{sectors[sector.sector_id as keyof typeof sectors]}</td><td>{shown(row.closing_assets)}</td><td>{shown(row.closing_liabilities)}</td><td>{shown(row.closing_equity)}</td><td>{shown(row.period_profit)}</td></tr>; }))}</tbody></table></div>
      <div className="ict-downloads"><button type="button" disabled={busy} onClick={() => download("json")}>Management JSON</button><button type="button" disabled={busy} onClick={() => download("csv")}>Management CSV</button><button type="button" disabled={busy} onClick={() => download("xlsx")}>Management Excel</button><a href="#capital">Kapitalwirkung dieser geprüften Quelle</a></div>
      <p>Alle Formate enthalten denselben Digest. Die Gesamtbilanz ist die abgestimmte Summe der vier neu berechneten Teilmodelle. SCR, MCR, regulatorische Bedeckung und eine endogene All-Sparten-Marktreaktion bleiben offen.</p>
    </div>}
  </section>;
}
