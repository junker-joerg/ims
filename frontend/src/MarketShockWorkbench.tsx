import { useEffect, useMemo, useRef, useState } from "react";
import { amountText, amountUnits, sectorNames, type Side } from "./seminarPresentation";
import "./MarketShockWorkbench.css";

type Row = Record<string, unknown>;
type Actor = { insurer_id: number; name: string; insurance_group_id: string; sectors: Record<string, unknown> };
type Event = { event_id: string; kind: string; start_hour: string; duration_hours: string; intensity: string; insurer_ids: number[]; asset_ids: string[]; channels: string[]; assumption_note: string };
type Response = { response_id: string; kind: string; decision_period: number; lead_periods: number; duration_periods: number; value: string; cost: string; cost_per_hour: string; replacement_asset_id: string };
type Bundle = { schema_version: string; case_id: string; title: string; assumption_note: string; period_hours: string; comparison: string;
  model_input: { period_count: number; seed: number; insurers: Actor[] }; reference_bundle: { source_catalog: { source_scope: { notice: string } } };
  events: Event[]; responses: Record<Side, Response[]>; life: { pool_per_period: number }; ict: { resources: { resource_id: string; owners: { insurer_id: number; sector_id: string; weight: string }[] }[] } };
type Result = { valid: boolean; content_digest: string; period_count: number; shock_bundle: Bundle; comparison_labels: Record<Side, string>; sides: Record<Side, Record<string, Row[]>> };
const cases: Record<string, { title: string; story: string }> = {
  google_motor_entry: { title: "Google kommt in die Kfz-Versicherung", story: "Ein fiktiver Anbieter 41 tritt mit erklärter Finanzierung, Preis und Reichweite ein. Wer übernimmt Prämie und Risiko?" },
  life_demand_shock: { title: "LV wird unattraktiv", story: "Weniger neue Interessenten schließen ab. Altpolicen und ihre Garantien bleiben erhalten. Hilft die erklärte Vertriebsantwort?" },
  dora_2_workshop: { title: "Regulierungsschock ICT DORA 2.0", story: "Hypothetische Umstellung: zehn Perioden weniger Kapazität und einmalige Kosten. Was erreicht rechtzeitig vorbereitete Kapazität?" },
  us_hyperscaler_outage: { title: "Alle US-Hyperscaler fallen aus", story: "Gemeinsamer 36-Stunden-Ausfall deklarierter US-Vorleistungen. Trägt der unabhängige Ersatz, während ein gemeinsamer IAM-Pfad mit ausfällt?" },
};
const num = (row: Row | undefined, key: string) => Number(row?.[key] ?? 0);
const text = (row: Row | undefined, key: string) => String(row?.[key] ?? "0");
const sum = (rows: Row[], key: string) => rows.reduce((total, row) => total + amountUnits(text(row, key)), 0n);
const per = (rows: Row[], period: number) => rows.filter(row => row.period === period);
const processNames: Record<string, string> = { underwriting: "Antrag / Vertragswechsel", claims: "Schadenverwaltung", service: "Serviceverwaltung" };

async function post(path: string, source: unknown) {
  const response = await fetch("/api/market" + path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(source) });
  const body = await response.json();
  if (!response.ok || !body.valid) throw new Error(body.issues?.[0]?.message || "Schockfall konnte nicht geprüft werden.");
  if (body.content_digest && response.headers.get("etag") !== `"${body.content_digest}"`) throw new Error("Inhaltsnachweis der Antwort stimmt nicht.");
  if (body.transport === "ims.market-row-table.v1") for (const side of ["baseline", "variant"]) for (const key of Object.keys(body.sides[side])) {
    const table = body.sides[side][key] as { columns: string[]; rows: unknown[][]; missing?: Record<string, string[]> };
    body.sides[side][key] = table.rows.map((values, i) => Object.fromEntries(table.columns.map((column, j) => [column, values[j]]).filter(([column]) => !table.missing?.[String(i)]?.includes(column as string))));
  }
  return body;
}

function Plot({ title, baseline, variant, period, event }: { title: string; baseline: number[]; variant: number[]; period: number; event: Event }) {
  const n = baseline.length, min = Math.min(0, ...baseline, ...variant), max = Math.max(1, ...baseline, ...variant), range = max - min;
  const x = (p: number) => 62 + (p - 1) / Math.max(1, n - 1) * 530;
  const y = (v: number) => 202 - (v - min) / range * 145;
  const path = (values: number[]) => values.map((v, i) => `${i ? "L" : "M"}${x(i + 1)},${y(v)}`).join(" ");
  const begin = Number(event.start_hour) / 24 + 1, finish = Math.min(n, begin + Number(event.duration_hours) / 24);
  return <figure className="shock-plot"><figcaption>{title}</figcaption><svg className="management-chart" viewBox="0 0 640 248" role="img" aria-label={`${title}. Baseline gestrichelt, Variante durchgezogen; schattiertes Ereignisfenster. Exakte Werte in der Verlaufstabelle.`}>
    {begin <= n && <rect className="shock-window" x={x(begin)} y="42" width={Math.max(5, x(finish) - x(begin))} height="164" />}
    {[0, 1, 2, 3].map(i => <g key={i}><line className="chart-grid" x1="62" x2="592" y1={y(min + range * i / 3)} y2={y(min + range * i / 3)} /><text x="54" y={y(min + range * i / 3) + 4} textAnchor="end">{(min + range * i / 3).toLocaleString("de-DE", { maximumFractionDigits: 1 })}</text></g>)}
    <path d={path(baseline)} className="baseline-line" /><path d={path(variant)} className="variant-line" /><line className="chart-cursor" x1={x(period)} x2={x(period)} y1="42" y2="206" />
    <text x="62" y="229">P1</text><text x="592" y="229" textAnchor="end">P{n}</text>
  </svg><div className="chart-legend"><span><i className="baseline-key" />Baseline</span><span><i className="variant-key" />Variante</span><span>Ereignisfenster</span></div></figure>;
}

export default function MarketShockWorkbench() {
  const [caseId, setCaseId] = useState("us_hyperscaler_outage"), [horizon, setHorizon] = useState(100);
  const [bundle, setBundle] = useState<Bundle | null>(null), [result, setResult] = useState<Result | null>(null), [original, setOriginal] = useState(true);
  const [expert, setExpert] = useState(""), [dirty, setDirty] = useState(false), [hadResult, setHadResult] = useState(false);
  const [busy, setBusy] = useState(false), [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState(21), [side, setSide] = useState<Side>("variant"), [actor, setActor] = useState(0), [role, setRole] = useState("cio");
  const revision = useRef(0), resultHeading = useRef<HTMLHeadingElement>(null);
  useEffect(() => { if (result) resultHeading.current?.focus(); }, [result]);
  function invalidate() { revision.current++; setResult(null); setError(null); }
  function accept(source: Bundle, readOnly: boolean) { setBundle(source); setExpert(JSON.stringify(source, null, 2)); setDirty(false); setOriginal(readOnly); setCaseId(source.case_id); setHorizon(source.model_input.period_count); }
  async function act(work: (version: number) => Promise<void>) {
    const version = revision.current; setBusy(true); setError(null);
    try { await work(version); } catch (failure) { if (version === revision.current) setError(failure instanceof Error ? failure.message : "Prüfung fehlgeschlagen."); }
    finally { if (version === revision.current) setBusy(false); }
  }
  async function load(id = caseId) {
    invalidate(); setBundle(null); setExpert("");
    await act(async version => { const body = await post("/shock-case", { case_id: id, period_count: horizon }); if (version === revision.current) { accept(body.shock_bundle, true); setActor(0); } });
  }
  async function calculate() {
    if (!bundle) return;
    invalidate();
    await act(async version => {
      const body = await post("/calculate", bundle) as Result;
      if (version !== revision.current) return;
      accept(body.shock_bundle, original); setResult(body); setHadResult(true); setPeriod(Math.min(21, body.period_count));
    });
  }
  function change(work: (next: Bundle) => void) {
    if (!bundle || original || busy || dirty) return;
    const next = structuredClone(bundle); work(next); invalidate(); accept(next, false);
  }
  async function importSource(source: unknown) {
    invalidate();
    await act(async version => { const body = await post("/shock-source", source); if (version === revision.current) { accept(body.shock_bundle, false); setActor(0); } });
  }
  async function readFile(file?: File) {
    if (!file) return;
    if (file.size > 16 * 1024 * 1024) { invalidate(); setError("AP7-Datei überschreitet 16 MiB."); return; }
    try { await importSource(JSON.parse(await file.text())); } catch { invalidate(); setError("Datei enthält kein lesbares AP7-JSON."); }
  }
  async function download(excel: boolean) {
    if (!bundle || !result) return;
    await act(async version => {
      const response = await fetch("/api/market" + (excel ? "/export.xlsx" : "/source.json"), { method: "POST", headers: { "Content-Type": "application/json", "If-Match": `"${result.content_digest}"` }, body: JSON.stringify(excel ? { source_input: bundle, insurer_id: actor } : bundle) });
      if (!response.ok || response.headers.get("etag") !== `"${result.content_digest}"`) throw new Error("Export benötigt denselben frisch geprüften unveränderten Fall.");
      const blob = await response.blob(); if (version !== revision.current) return;
      const url = URL.createObjectURL(blob), link = document.createElement("a"); link.href = url; link.download = `IMS-AP7-${excel ? `VU${actor}` : bundle.case_id}-${result.content_digest.slice(0, 12)}.${excel ? "xlsx" : "json"}`; link.click(); setTimeout(() => URL.revokeObjectURL(url), 0);
    });
  }
  const current = result?.sides[side], firstEvent = bundle?.events[0], response = bundle?.responses.variant[0];
  const actors = bundle?.model_input.insurers || [];
  const selectRows = (name: string) => per(current?.[name] || [], period).filter(row => !actor || row.insurer_id === actor);
  const processRows = selectRows("ict_process_rows"), costs = selectRows("cost_rows");
  const lifeRow = current?.life_demand_rows[period - 1];
  const sharedCapacity = (chosen: Side) => sum(per(result?.sides[chosen].ict_resource_rows || [], period), "capacity_work");
  const vuRows = selectRows("vu_rows");
  const market = (chosen: Side) => result!.sides[chosen].market_rows.find(row => row.period === period && row.sector_id === "total")!;
  const queues = useMemo(() => {
    const values = { baseline: Array<number>(result?.period_count || 0).fill(0), variant: Array<number>(result?.period_count || 0).fill(0) };
    if (result) for (const chosen of ["baseline", "variant"] as const) for (const row of result.sides[chosen].ict_process_rows) values[chosen][num(row, "period") - 1] += num(row, "closing_queue");
    return values;
  }, [result]);
  const actorName = (aid: unknown) => actors.find(item => item.insurer_id === aid)?.name || "Unversichert";
  const disabled = original || busy || dirty;
  return <section className="panel ict-workbench market-shock-workbench" data-testid="market-shock-workbench" aria-label="Vier Markt-Schockfälle">
    <h2>Vier Schockfälle: Markt und ICT erklären</h2><p>Vom Ereignis über Abhängigkeiten und Rückstände bis zum gültigen Vertrag und zur Buchung. Ausgangsquelle: BaFin-Gruppenauswertung 2024 einschließlich Ausland und Rückversicherung; Strategien und Provider sind Workshop-Annahmen.</p>
    <div className="ict-controls"><label>Schockfall<select aria-label="Schockfall" value={caseId} disabled={busy} onChange={event => setCaseId(event.target.value)}>{Object.entries(cases).map(([id, item]) => <option key={id} value={id}>{item.title}</option>)}</select></label><label>Schockperioden<select aria-label="Schockperioden" value={horizon} disabled={busy} onChange={event => setHorizon(Number(event.target.value))}>{[2, 5, 10, 25, 50, 100].map(n => <option key={n} value={n}>{n}</option>)}</select></label><button type="button" disabled={busy} onClick={() => load()}>Schockdemo laden</button></div>
    <p>{cases[caseId]?.story}</p>
    {error && <p role="alert" className="shock-error">{error} Eingaben, Kosten und Bilanzbestände prüfen; es wird kein Teilergebnis angezeigt.</p>}
    {busy && <p role="status" className="shock-status">Frische Prüfung läuft. Vollständige 100-Perioden-Fälle und ihre Exporte können einige Minuten benötigen.</p>}
    {bundle && firstEvent && <>
      <p className="shock-status" data-testid="shock-original">{original ? "Schreibfreies Demooriginal" : "Eigene bearbeitbare Sitzung"} · {bundle.title} · {bundle.model_input.insurers.length} registrierte Anbieter · Seed {bundle.model_input.seed} · {bundle.model_input.period_count} Perioden × 24 deklarierte Prozessstunden.</p>
      {original && <button type="button" disabled={busy} onClick={() => { setOriginal(false); }}>Als eigene Schocksitzung übernehmen</button>}
      <fieldset disabled={disabled}><legend>Ereignis und ausführbare Gegenmaßnahme</legend><div className="ict-controls">
        <label>Schockbeginn in Periode<input type="number" min="6" max="100" value={Number(firstEvent.start_hour) / 24 + 1} onChange={event => change(next => { next.events[0].start_hour = String((Number(event.target.value) - 1) * 24); if (firstEvent.kind === "entry") next.events[0].duration_hours = String(Math.max(24, (next.model_input.period_count - Number(event.target.value) + 1) * 24)); })} /></label>
        <label>Schockdauer in Stunden<input type="number" min="0.0001" max="2400" step="0.0001" value={firstEvent.duration_hours} disabled={firstEvent.kind === "entry"} onChange={event => change(next => { next.events[0].duration_hours = event.target.value; })} /></label>
        <label>{firstEvent.kind === "life_demand" ? "Rückgang der Attraktivität" : "Intensität / Kapazitätsverlust"}<input type="number" min="0" max="1" step="0.01" value={firstEvent.intensity} onChange={event => change(next => { next.events[0].intensity = event.target.value; })} disabled={firstEvent.kind === "entry"} /></label>
        <label>Vergleichsachse<select aria-label="Vergleichsachse" value={bundle.comparison} onChange={event => change(next => { next.comparison = event.target.value; })}><option value="shock_with_response">Schock ohne / mit Gegenmaßnahme</option><option value="no_shock_vs_shock">Kein Schock / Schock, gleiche beschlossene Vorsorge</option></select></label>
        {response && <><label>Entscheidungsperiode der Gegenmaßnahme<input type="number" min="6" max="100" value={response.decision_period} onChange={event => change(next => { next.responses.variant[0].decision_period = Number(event.target.value); })} /></label><label>Vorlauf in Perioden<input type="number" min="0" max="100" value={response.lead_periods} onChange={event => change(next => { next.responses.variant[0].lead_periods = Number(event.target.value); })} /></label><label>Einmalige Vorsorgekosten<input type="number" min="0" step="0.0001" value={response.cost} onChange={event => change(next => { next.responses.variant[0].cost = event.target.value; })} /></label>
          {response.kind === "fallback" ? <label>Ersatzpfad<select aria-label="Ersatzpfad" value={response.replacement_asset_id} onChange={event => change(next => { next.responses.variant[0].replacement_asset_id = event.target.value; })}><option value="q-independent">Q mit unabhängigen Vorleistungen</option><option value="q-dependent">Q mit gemeinsamem US-IAM</option></select></label> : <label>{response.kind === "price" ? "Antwortpreis" : response.kind === "life_attractiveness" ? "Attraktivität mit Vertriebsantwort" : "Kapazitätsfaktor der Gegenmaßnahme"}<input type="number" min="0" step="0.01" value={response.value} onChange={event => change(next => { next.responses.variant[0].value = event.target.value; })} /></label>}</>}
      </div></fieldset>
      <p>{firstEvent.kind === "regulatory" ? "DORA 2.0 ist ein hypothetischer Seminarname. Kosten und Kapazität sind Annahmen, keine behauptete neue Vorschrift." : "Anbieter, Produkte und Providerprofile sind explizite Modellannahmen."} Der Horizont-Rückstand ist sichtbar; eine Verzögerung ist kein automatisch endgültiger Verlust.</p>
      <details><summary>Vollständiges portables Schockbündel und Ereignisfolge</summary><p>{bundle.events.length} Ereignis(se); Beginn, Dauer, Intensität, Akteure und Wirkungskanäle bleiben im Bündel. Ergänzungen in der eigenen Sitzung prüfen.</p><label>AP7-Quellenbündel JSON<textarea rows={9} value={expert} disabled={original || busy} onChange={event => { invalidate(); setExpert(event.target.value); setDirty(true); }} /></label><button type="button" disabled={original || busy || !dirty} onClick={() => { try { importSource(JSON.parse(expert)); } catch { setError("JSON ist nicht lesbar."); } }}>AP7-JSON übernehmen und prüfen</button></details>
      <button type="button" className="primary-action" disabled={busy || dirty} onClick={calculate}>Schockfall frisch berechnen</button>
      {hadResult && !result && <p role="status">Geänderte Eingaben entwerten den vorherigen Ergebnisnachweis. Neu berechnen.</p>}
    </>}
    <label>AP7-Sitzung aus JSON laden<input type="file" accept="application/json,.json" disabled={busy} onChange={event => readFile(event.target.files?.[0])} /></label>
    {result && bundle && firstEvent && current && <div data-testid="shock-results">
      <h3 ref={resultHeading} tabIndex={-1}>Was wirkt in Periode {period}?</h3><p className="shock-comparison">Baseline: {result.comparison_labels.baseline}. Variante: {result.comparison_labels.variant}.</p>
      <div className="ict-controls"><label>Erklärperiode<input type="range" min="1" max={result.period_count} value={period} onChange={event => setPeriod(Number(event.target.value))} /></label><span>P{period} · Stunden {(period - 1) * 24} bis {period * 24}</span><label>Erklärseite<select aria-label="Erklärseite" value={side} onChange={event => setSide(event.target.value as Side)}><option value="baseline">Baseline</option><option value="variant">Variante</option></select></label><label>Erklär-VU<select aria-label="Erklär-VU" value={actor} onChange={event => setActor(Number(event.target.value))}><option value="0">Ganzer Modellmarkt</option>{actors.map(item => <option key={item.insurer_id} value={item.insurer_id}>{item.name}</option>)}</select></label><label>Rollenfokus<select aria-label="Rollenfokus" value={role} onChange={event => setRole(event.target.value)}><option value="ceo">CEO · Ergebnis und Kosten</option><option value="cio">CIO · Provider und Ersatzpfad</option><option value="coo">COO · Kapazität und Aufholung</option><option value="cso">CSO Vertrieb · Anträge und Verträge</option></select></label></div>
      <div className="shock-jumps">{[20, 21, 22, 31, 40, 100].filter(p => p <= result.period_count).map(p => <button type="button" key={p} aria-pressed={period === p} onClick={() => setPeriod(p)}>P{p}{p === 20 ? " · vorher" : p === 21 ? " · Schock" : p === 22 ? " · Vertragsfolge" : p === 31 ? " · Umstellung vorbei" : p === 40 ? " · Aufholung" : " · Horizont"}</button>)}</div>
      {Number(firstEvent.start_hour) >= result.period_count * 24 && <p>Der Schock liegt hinter diesem kurzen Prüfhorizont. Für die ganze Geschichte 100 Perioden laden.</p>}
      <p className="shock-impact" data-testid="shock-impact">P{period}: gemeinsames Arbeitsbudget Baseline <strong>{amountText(sharedCapacity("baseline"))}</strong>, Variante <strong>{amountText(sharedCapacity("variant"))}</strong> Einheiten. Rückstand: <strong>{queues.baseline[period - 1]}</strong> / <strong>{queues.variant[period - 1]}</strong> Vorgänge. Erst die bearbeitete Arbeit kann einen Vertrag in P{period + 1} auslösen.</p>
      <div className="shock-plots"><Plot title="Wartende Vorgänge · ganzer Modellmarkt" baseline={queues.baseline} variant={queues.variant} period={period} event={firstEvent} /><Plot title="Neu ausgegebene Lebenspolicen · ganzer Modellmarkt" baseline={result.sides.baseline.life_demand_rows.map(row => num(row, "issued"))} variant={result.sides.variant.life_demand_rows.map(row => num(row, "issued"))} period={period} event={firstEvent} /></div>
      <details><summary>Exakte Prozess- und Vertragsverlaufstabelle</summary><div className="table-scroll" tabIndex={0} role="region" aria-label="Schockverlauf"><table><thead><tr><th>Periode</th><th>Rückstand Baseline</th><th>Rückstand Variante</th><th>Neue Policen Baseline</th><th>Neue Policen Variante</th></tr></thead><tbody>{result.sides.baseline.life_demand_rows.map((row, i) => <tr key={i}><td>{i + 1}</td><td>{queues.baseline[i]}</td><td>{queues.variant[i]}</td><td>{num(row, "issued")}</td><td>{num(result.sides.variant.life_demand_rows[i], "issued")}</td></tr>)}</tbody></table></div></details>
      <article className="shock-step"><h4>1 · Ereignis und Zeit</h4>{per(current.ict_event_rows, period).map(event => <p key={text(event, "event_id")}>{text(event, "event_id")} · {text(event, "overlap_hours")} wirksame Stunden in P{period} · Intensität {text(event, "intensity")} · {text(event, "assumption_note")}</p>)}{!per(current.ict_event_rows, period).length && <p>In dieser Vergleichsseite/Periode ist kein Ereignisfenster aktiv. Frühere Rückstände können weiterwirken.</p>}<p>Ein in P{period} bearbeiteter Antrag oder Wechsel wird ab P{period + 1} wirksam. Vorher bleiben bestehender Versicherungsschutz, Prämie und Risiko beim alten Haus.</p></article>
      <article className={`shock-step ${role === "cio" ? "shock-focus" : ""}`}><h4>2 · Abhängigkeiten und konkreter Ersatzpfad</h4><p>Ausfälle wirken über die vollständige Vorleistungskette. Ein EU-Standort allein beweist keine Unabhängigkeit. Alle dargestellten Verbindungen sind deklarierte Workshop-Annahmen.</p><div className="shock-dependency-grid" data-testid="shock-dependencies">{per(current.ict_dependency_rows, period).map(asset => <div key={text(asset, "asset_id")} className={num(asset, "lost_equivalent_hours") > 0 ? "shock-node failed" : "shock-node"}><strong>{text(asset, "label")}</strong><span>{text(asset, "control")} kontrolliert · {num(asset, "lost_equivalent_hours") > 0 ? "Beeinträchtigt" : "Im deklarierten Fenster verfügbar"}</span><span>{text(asset, "lost_equivalent_hours")} äquivalent verlorene Stunden</span><small>Vorleistungen: {(asset.depends_on as string[]).join(", ") || "keine deklariert"}. Ursache: {(asset.causing_event_ids as string[]).join(", ") || "kein Ereignis"}.</small></div>)}</div>
        {per(current.ict_resource_rows, period).map(resource => <div key={text(resource, "resource_id")} className="shock-path-proof"><strong>{text(resource, "resource_id")}: wirksames gemeinsames Budget {text(resource, "capacity_work")} Arbeitseinheiten</strong>{(resource.capacity_segments as Row[]).map((segment, i) => <p key={i}>Stunden {text(segment, "from_hour")}–{text(segment, "through_hour")}: {text(segment, "capacity_per_hour")} Einheiten/h. Aktiv: {(segment.active_response_ids as string[]).join(", ") || "keine Gegenmaßnahme"}.{(segment.replacements as Row[]).map((replacement, j) => <span key={j}> Geprüfte Vorleistungen des Ersatzes: {(replacement.path as string[]).join(", ")}: wirksamer Faktor {text(replacement, "effective_factor")}; {replacement.unknown_control ? "Kontrolle unbekannt, Unabhängigkeit nicht bestätigt" : (replacement.causes as string[]).length ? `fällt mit ${(replacement.causes as string[]).join(", ")} aus` : "deklarierte Vorleistungen verfügbar"}.</span>)}</p>)}</div>)}
      </article>
      <article className={`shock-step ${role === "coo" ? "shock-focus" : ""}`}><h4>3 · Prozesse: Bearbeitung, Rückstand, Aufholung</h4><p data-testid="shock-queue-equation">{processRows.reduce((n, row) => n + num(row, "opening_queue"), 0)} Anfang + {processRows.reduce((n, row) => n + num(row, "arrivals"), 0)} neue Vorgänge = {processRows.reduce((n, row) => n + num(row, "completed"), 0)} bearbeitet + {processRows.reduce((n, row) => n + num(row, "closing_queue"), 0)} wartend. Alle Prozesse teilen das Ressourcenbudget.</p><div className="table-scroll" tabIndex={0} role="region" aria-label="Prozesse und Warteschlangen"><table><thead><tr><th>Modell-VU</th><th>Sparte / Prozess</th><th>Anfang</th><th>Neu</th><th>Bearbeitet</th><th>Wartend</th></tr></thead><tbody>{processRows.filter(row => num(row, "opening_queue") + num(row, "arrivals") + num(row, "closing_queue") > 0).map(row => <tr key={text(row, "service_id")}><td>{actorName(row.insurer_id)}</td><td>{sectorNames[text(row, "sector_id")]} · {processNames[text(row, "kind")]}</td>{["opening_queue", "arrivals", "completed", "closing_queue"].map(key => <td key={key}>{text(row, key)}</td>)}</tr>)}</tbody></table></div><p>Schaden-/Serviceverwaltung bucht deklarierte Verwaltungsarbeit. Versicherungs-Schadenzahlungen, Tod und Ablauf werden dadurch nicht verschoben.</p></article>
      <article className={`shock-step ${role === "cso" ? "shock-focus" : ""}`}><h4>4 · Was wird ein gültiger Vertrag?</h4><p data-testid="shock-life-flow">Ganzer Lebens-Modellmarkt: Pool {text(lifeRow, "pool")}, Attraktivität {text(lifeRow, "attractiveness")}, {text(lifeRow, "willing")} kaufwillig, {text(lifeRow, "applications_created")} Anträge, {text(lifeRow, "issued")} jetzt ausgegebene Policen; {text(lifeRow, "waiting_applications")} warten und {text(lifeRow, "processed_pending_next_period")} sind für P{period + 1} bearbeitet. Wartende neue Anträge sind unversichert und buchen keine Prämie/Forderung. Altgarantien bleiben erhalten.</p>
        <div className="table-scroll" tabIndex={0} role="region" aria-label="Wirksame Vertragswechsel"><table><thead><tr><th>Kohorte</th><th>Bisher</th><th>Gültiger Träger</th><th>Prämie</th><th>Risiko</th></tr></thead><tbody>{per(current.customer_decisions, period).filter(row => !actor || row.insurer_id === actor || row.previous_insurer_id === actor).map(row => <tr key={text(row, "group_id")}><td>{text(row, "group_id")}</td><td>{actorName(row.previous_insurer_id)}</td><td>{actorName(row.insurer_id)}</td><td>{amountText(text(row, "premium_income"))}</td><td>{amountText(text(row, "risk_loss"))}</td></tr>)}</tbody></table></div>
      </article>
      <article className={`shock-step ${role === "ceo" ? "shock-focus" : ""}`}><h4>5 · Buchung genau einmal und Ergebnis</h4><div className="market-kpis"><div><span>Markt-Eigenkapital · {side}</span><strong>{amountText(text(market(side), "closing_equity"))}</strong><span>A {amountText(text(market(side), "closing_assets"))} = L {amountText(text(market(side), "closing_liabilities"))} + E</span></div><div><span>Variante gegenüber Baseline · Markt</span><strong data-testid="shock-equity-difference">{amountText(amountUnits(text(market("variant"), "closing_equity")) - amountUnits(text(market("baseline"), "closing_equity")), true)}</strong></div><div><span>Prozess-/Maßnahmenaufwand · VU-Auswahl</span><strong>{amountText(sum(costs, "amount"))}</strong><span>Davon Maßnahme {amountText(sum(costs.filter(row => row.kind === "measure"), "amount"))}</span></div></div>
        <p>Prämie und Garantie entstehen erst aus einem gültigen Vertrag. Der Markt bucht den Versicherungsfluss und die nachgewiesenen Kosten einmal; es gibt keinen zusätzlichen ICT-Margenabzug. Eigenkapital umfasst auch Bestand, Anlageergebnis und Finanzierung. Die Differenz ist ein Vergleich beider Läufe, keine pauschale exakte Ursachenzerlegung.</p>
        <div className="table-scroll" tabIndex={0} role="region" aria-label="Einmalige Kostenbuchungen"><table><thead><tr><th>Kosten-ID</th><th>VU / Sparte</th><th>Gewicht</th><th>Einmaliger Anteil</th><th>Erklärung</th></tr></thead><tbody>{costs.map(row => <tr key={`${row.cost_id}-${row.insurer_id}-${row.sector_id}`}><td>{text(row, "cost_id")}</td><td>{actorName(row.insurer_id)} · {sectorNames[text(row, "sector_id")]}</td><td>{text(row, "weight")}</td><td>{amountText(text(row, "amount"))}</td><td>{text(row, "explanation")}</td></tr>)}</tbody></table></div>
        <details><summary>VU-/Spartenbilanz und erklärte Kostenverteilung</summary><p>Der Demostandard ordnet gemeinsame Verwaltungsarbeit der nach Anfangsaktiva tragenden Modellsparte zu. Ressourcenanteile sind erklärte, gerundete Gewichte nach dieser Anfangsbasis; sie bleiben im Bündel sichtbar und bearbeitbar. Jede Zahlung belastet nur ihre ausgewiesene VU/Sparte.</p><div className="table-scroll" tabIndex={0} role="region" aria-label="Bilanz der VU-Auswahl"><table><thead><tr><th>VU / Sparte</th><th>Aktiv</th><th>A</th><th>L</th><th>E</th><th>Prämie</th><th>Kapitalzuführung</th></tr></thead><tbody>{vuRows.map(row => <tr key={`${row.insurer_id}-${row.sector_id}`}><td>{actorName(row.insurer_id)} · {sectorNames[text(row, "sector_id")]}</td><td>{row.active_in_period ? "ja" : "vor Eintritt"}</td>{["closing_assets", "closing_liabilities", "closing_equity", "premium_income", "capital_contribution"].map(key => <td key={key}>{amountText(text(row, key))}</td>)}</tr>)}</tbody></table></div></details>
      </article>
      <details><summary>Am Horizont noch wartend oder erst für die nächste Periode bearbeitet</summary><p>Aktueller Horizont P{result.period_count}: {current.terminal_process_rows.length} Vorgänge verbleiben. Das ist kein automatisch endgültiger Verlust; ein bearbeiteter letzter Antrag wird erst in P{result.period_count + 1} gültig.</p></details>
      <div className="ict-downloads"><button type="button" disabled={busy || !actor} onClick={() => download(true)}>Erklär-VU in Excel sichern</button><button type="button" disabled={busy} onClick={() => download(false)}>AP7-Bündel als JSON sichern</button></div><p>Einzel-VU für Excel auswählen. Quellen, Seed, Ereignisse, Gegenmaßnahmen und Kopplungsparameter gehören zum geprüften Bündel.</p>
      <p>Keine verifizierte reale Providerbelegung, deutsche Direktmarkt-Rangliste oder regulatorische Kapitalrechnung. <a href="/api/seminar/handbook/market_ap7.html" target="_blank" rel="noreferrer">Offline-Anleitung zu den vier Schockfällen</a></p>
    </div>}
  </section>;
}
