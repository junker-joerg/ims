import { useEffect, useRef, useState } from "react";

type Event = { event_id: string; kind: string; target_id: string; start_hour: string; duration_hours: string; capacity_loss_fraction: string; rework_fraction: string; assumption_note: string };
type Strategy = { strategy_id: string; kind: string; asset_id: string; start_hour: string; through_hour: string; effectiveness: string; cost_per_hour: string; assumption_note: string };
type Service = { service_id: string; insurer_id: number; process: string; asset_ids: string[]; demand_per_hour: string; capacity_per_hour: string; unit_margin: string; backlog_cost_per_unit_period: string; rework_cost_per_unit: string; opening_backlog: string; assumption_note: string };
type Input = { scenario_id: string; variant_id: string; period_count: number; period_hours: string; assumption_note: string; providers: { provider_id: string }[]; assets: { asset_id: string }[]; services: Service[]; events: Event[]; strategies: Strategy[] };
type Balance = { period: number; insurer_id: number; period_profit: string; operational_impact: string; strategy_cost: string; closing_assets: string; closing_liabilities: string; model_own_funds_proxy: string; loss_limit_met: boolean; equity_floor_met: boolean };
type Flow = { period: number; service_id: string; insurer_id: number; process: string; arrivals: string; processed_original: string; processed_rework: string; closing_backlog: string; operational_impact: string };
type Result = { valid: boolean; content_digest: string; input_digest: string; period_count: number; baseline: { balance_rows: Balance[]; service_rows: Flow[] }; variant: { balance_rows: Balance[]; service_rows: Flow[] }; timeline: { event_id: string; kind: string; asset_id: string; start_hour: string; effective_end_hour: string; affected_insurer_ids: number[] }[]; provider_concentration: { provider_id: string; insurer_ids: number[] }[]; issues: { message: string; path: string }[] };
const processes: Record<string, string> = { sales: "Vertrieb", underwriting: "Underwriting", claims: "Schaden", service: "Service" };
const kinds: Record<string, string> = { outage: "Asset-Vollausfall", capacity_loss: "Teilkapazität", data_integrity: "Datenintegrität / Nacharbeit", provider_outage: "Anbieterausfall" };
const measures: Record<string, string> = { prevention: "Prävention", restart: "Wiederanlauf", fallback: "Fallback" };
const fields = [
  ["demand_per_hour", "Nachfrage / Stunde"], ["capacity_per_hour", "Kapazität / Stunde"],
  ["unit_margin", "Marge je Originalvorgang"], ["backlog_cost_per_unit_period", "Kosten je Rückstand / Periode"],
  ["rework_cost_per_unit", "Kosten je erzeugter Nacharbeit"], ["opening_backlog", "Anfangsrückstand"],
] as const;
function number(value: string): string { return value.replace(",", "."); }
function shown(value: string): string { return value.replace(".", ","); }

export default function IctWorkbench({ seminarSource }: { seminarSource?: unknown }) {
  const [input, setInput] = useState<Input | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const [expert, setExpert] = useState("");
  const [expertDirty, setExpertDirty] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [period, setPeriod] = useState(1);
  const revision = useRef(0);
  const resultHeading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    const controller = new AbortController();
    const version = revision.current;
    fetch("/api/ict/workshop-case", { signal: controller.signal }).then(async (response) => {
      if (!response.ok) throw new Error("ICT-Workshopfall ist nicht erreichbar.");
      const doc = await response.json() as Input;
      if (version !== revision.current) return;
      setInput(doc); setExpert(JSON.stringify(doc, null, 2));
    }).catch((failure) => { if (!controller.signal.aborted) setError(failure.message); });
    return () => controller.abort();
  }, []);
  function change(doc: Input) {
    revision.current++; setInput(doc); setExpert(JSON.stringify(doc, null, 2)); setExpertDirty(false); setResult(null); setError(null); setBusy(false);
  }
  useEffect(() => {
    if (seminarSource) change(seminarSource as Input);
  }, [seminarSource]);
  function eventChange(patch: Partial<Event>) {
    if (input) change({ ...input, events: [{ ...input.events[0], ...patch }, ...input.events.slice(1)] });
  }
  function kindChange(kind: string) {
    if (!input) return;
    eventChange({ kind, target_id: kind === "provider_outage" ? input.providers[0].provider_id : input.assets[0].asset_id,
      capacity_loss_fraction: kind === "data_integrity" ? "0" : kind === "capacity_loss" ? "0.5" : "1",
      rework_fraction: kind === "data_integrity" ? "0.5" : "0" });
  }
  function measureChange(kind: string) {
    if (!input) return;
    change({ ...input, strategies: kind ? [{ strategy_id: "declared-measure", kind,
      asset_id: input.assets[0].asset_id, start_hour: input.events[0]?.start_hour || "0",
      through_hour: String(Number(input.events[0]?.start_hour || 0) + Number(input.events[0]?.duration_hours || 24)),
      effectiveness: "0.5", cost_per_hour: "0.25", assumption_note: "Ausdrücklich ausgewählte unkalibrierte Workshop-Gegenmaßnahme." }] : [] });
  }
  async function post(endpoint: string, doc: unknown) {
    const response = await fetch(endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(doc) });
    const body = await response.json();
    if (!response.ok || !body.valid) {
      const issue = body.issues?.[0];
      throw new Error(issue ? `${issue.message} (${issue.path})` : "ICT-Rechnung ist nicht verfügbar.");
    }
    return { response, body };
  }
  async function calculate() {
    if (!input || busy || expertDirty) return;
    const version = revision.current;
    setBusy(true); setError(null); setResult(null);
    try {
      const { response, body } = await post("/api/ict/calculate", input);
      if (response.headers.get("etag") !== `"${body.content_digest}"`) throw new Error("ICT-Ergebnisnachweis stimmt nicht mit der Antwort überein.");
      if (revision.current === version) {
        setResult(body); setPeriod(Math.min(50, body.period_count));
        window.setTimeout(() => resultHeading.current?.focus({ preventScroll: true }), 0);
      }
    } catch (failure) { if (revision.current === version) setError(failure instanceof Error ? failure.message : "ICT-Rechnung fehlgeschlagen."); }
    finally { if (revision.current === version) setBusy(false); }
  }
  async function applyExpert() {
    const version = revision.current;
    setError(null); setBusy(true);
    try {
      const doc = JSON.parse(expert);
      await post("/api/ict/validate", doc);
      if (version === revision.current) change(doc);
    } catch (failure) { if (revision.current === version) setError(failure instanceof Error ? failure.message : "Experteneingabe ist ungültig."); }
    finally { if (revision.current === version) setBusy(false); }
  }
  async function download(extension: string) {
    if (!input || !result) return;
    const version = revision.current;
    try {
      const response = await fetch(`/api/ict/export.${extension}`, { method: "POST", headers: { "Content-Type": "application/json", "If-Match": `"${result.content_digest}"` }, body: JSON.stringify(input) });
      if (!response.ok || response.headers.get("etag") !== `"${result.content_digest}"`) throw new Error("Dossierexport benötigt denselben unveränderten Ergebnisnachweis.");
      const data = await response.blob();
      if (version !== revision.current) return;
      const url = URL.createObjectURL(data); const link = document.createElement("a");
      link.href = url; link.download = `IMS-ICT-${result.content_digest.slice(0, 12)}.${extension}`; link.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 0);
    } catch (failure) { if (version === revision.current) setError(failure instanceof Error ? failure.message : "Export fehlgeschlagen."); }
  }
  const event = input?.events[0], strategy = input?.strategies[0];
  return <section className="panel ict-workbench" data-testid="ict-workbench" aria-label="ICT-Wirkungskette">
    <div className="section-heading"><div><p className="eyebrow">ICT / DORA · Workshopmodell</p><h2>Vom Ausfall zur operativen Wirkung</h2></div></div>
    <p>Vergleichen Sie deklarierte Prozesskapazität, Rückstand und Wiederanlauf bis zum Modell-Ergebnis und Eigenmittel-Proxy. Unabhängige Vorgänge und Modellwährung; keine historische Marktreaktion, regulatorische Kapitalrechnung oder DORA-Konformitätsprüfung.</p>
    {error && <p role="alert" className="ict-error">{error}</p>}
    {!input && !error && <p role="status">Workshopfall wird geladen …</p>}
    {input && <div className="ict-inputs">
      <div className="ict-fields">
        <label>Perioden<input aria-label="ICT Perioden" type="number" min="1" max="100" value={input.period_count} onChange={e => change({ ...input, period_count: Number(e.target.value) })} /></label>
        <label>Stunden je Periode<input aria-label="Stunden je ICT-Periode" value={input.period_hours} onChange={e => change({ ...input, period_hours: number(e.target.value) })} /></label>
      </div>
      <p>Die Zeitskala ist ausdrücklich deklariert: ein Tag hat 24 Stunden; die historische IMS-Periode legt ihre Länge nicht fest. Alle folgenden Beispielwerte sind sichtbar und änderbar.</p>
      {event && <fieldset><legend>Ereignis</legend><div className="ict-fields">
        <label>Ereignistyp<select aria-label="ICT Ereignistyp" value={event.kind} onChange={e => kindChange(e.target.value)}>{Object.entries(kinds).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>
        <label>Ziel<select aria-label="ICT Ereignisziel" value={event.target_id} onChange={e => eventChange({ target_id: e.target.value })}>{(event.kind === "provider_outage" ? input.providers.map(p => p.provider_id) : input.assets.map(a => a.asset_id)).map(key => <option key={key}>{key}</option>)}</select></label>
        {([ ["start_hour", "Beginn in Stunden ab 0"], ["duration_hours", "Dauer in Stunden"], ["capacity_loss_fraction", "Kapazitätsverlust (0–1)"], ["rework_fraction", "Nacharbeitsanteil (0–1)"] ] as const).map(([key, label]) => <label key={key}>{label}<input aria-label={label} value={event[key]} onChange={e => eventChange({ [key]: number(e.target.value) })} /></label>)}
      </div></fieldset>}
      <fieldset><legend>Gegenmaßnahme</legend><div className="ict-fields">
        <label>Maßnahme<select aria-label="ICT Gegenmaßnahme" value={strategy?.kind || ""} onChange={e => measureChange(e.target.value)}><option value="">Keine</option>{Object.entries(measures).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>
        {strategy && <><label>Asset<select aria-label="Maßnahmen-Asset" value={strategy.asset_id} onChange={e => change({ ...input, strategies: [{ ...strategy, asset_id: e.target.value }, ...input.strategies.slice(1)] })}>{input.assets.map(a => <option key={a.asset_id}>{a.asset_id}</option>)}</select></label>
          {([ ["start_hour", "Maßnahmenbeginn in Stunden"], ["through_hour", "Maßnahmenende in Stunden"], ["effectiveness", "Wirksamkeit (0–1)"], ["cost_per_hour", "Kosten je Stunde"] ] as const).map(([key, label]) => <label key={key}>{label}<input aria-label={label} value={strategy[key]} onChange={e => change({ ...input, strategies: [{ ...strategy, [key]: number(e.target.value) }, ...input.strategies.slice(1)] })} /></label>)}</>}
      </div></fieldset>
      <details><summary>Prozessannahmen und Herkunft bearbeiten</summary><p>{input.assumption_note}</p>
        {input.services.map((service, index) => <fieldset key={service.service_id}><legend>VU {service.insurer_id} · {processes[service.process]} · {service.service_id}</legend><p>ICT-Assets: {service.asset_ids.join(", ")} · {service.assumption_note}</p><div className="ict-fields">{fields.map(([key, label]) => <label key={key}>{label}<input aria-label={`${service.service_id} ${label}`} value={service[key]} onChange={e => change({ ...input, services: input.services.map((s, n) => n === index ? { ...s, [key]: number(e.target.value) } : s) })} /></label>)}</div></fieldset>)}
      </details>
      <details><summary>Expertenmodus: vollständiger Quellenvertrag</summary><p>Ändern Sie Services, Anbieter, gerichtete Abhängigkeiten, Bilanzannahmen oder mehrere Ereignisse. Eine Übernahme erfolgt erst nach atomarer Prüfung.</p><label>ICT Quellenvertrag<textarea aria-label="ICT Quellenvertrag" rows={12} value={expert} onChange={e => { revision.current++; setExpert(e.target.value); setExpertDirty(true); setResult(null); setBusy(false); }} /></label><button type="button" disabled={busy} onClick={applyExpert}>Experteneingabe prüfen und übernehmen</button>{expertDirty && <p role="status">Expertenentwurf noch nicht übernommen. Prüfen Sie ihn vor der Berechnung.</p>}</details>
      <button type="button" className="primary-action" disabled={busy || expertDirty} onClick={calculate}>{busy ? "ICT wird geprüft …" : "Baseline und ICT-Variante berechnen"}</button>
    </div>}
    {result && <div className="ict-results" data-testid="ict-results"><h3 ref={resultHeading} tabIndex={-1}>Geprüfte ICT-Wirkung · {result.period_count} Perioden</h3>
      <label>Ergebnisperiode<select aria-label="ICT Ergebnisperiode" value={period} onChange={e => setPeriod(Number(e.target.value))}>{Array.from({ length: result.period_count }, (_, i) => <option key={i + 1}>{i + 1}</option>)}</select></label>
      <p>Nachweis: <code>{result.content_digest}</code>. Eine Änderung der Eingaben entwertet dieses Ergebnis und die Exporte.</p>
      <div className="table-scroll" role="region" aria-label="ICT Modellbilanz" tabIndex={0}><table><thead><tr><th>Fall</th><th>VU</th><th>Ergebnis</th><th>ICT-Wirkung</th><th>Maßnahmenkosten</th><th>Modell-Eigenmittel</th><th>Workshop-Grenzen</th></tr></thead><tbody>{(["baseline", "variant"] as const).flatMap(side => result[side].balance_rows.filter(row => row.period === period).map(row => <tr key={`${side}-${row.insurer_id}`}><td>{side === "baseline" ? "Baseline" : "Variante"}</td><td>{row.insurer_id}</td><td>{shown(row.period_profit)}</td><td>{shown(row.operational_impact)}</td><td>{shown(row.strategy_cost)}</td><td>{shown(row.model_own_funds_proxy)}</td><td>{row.loss_limit_met && row.equity_floor_met ? "Eingehalten" : "Verletzt"}</td></tr>))}</tbody></table></div>
      <p>Vorübergehend ausgefallene Originalvorgänge können mit freier Kapazität aufgeholt werden. Die Margenwirkung kann dann negativ werden; deklarierte Halte-, Nacharbeits- und Maßnahmenkosten bleiben bestehen. Rückstand ist hier keine automatisch erzeugte Schadenverpflichtung.</p>
      <div className="table-scroll" role="region" aria-label="ICT Prozesswirkung" tabIndex={0}><table><thead><tr><th>VU / Prozess</th><th>Nachfrage</th><th>Originale erledigt</th><th>Nacharbeit erledigt</th><th>Rückstand</th><th>Ergebniswirkung</th></tr></thead><tbody>{result.variant.service_rows.filter(row => row.period === period).map(row => <tr key={row.service_id}><td>VU {row.insurer_id} · {processes[row.process]}</td><td>{shown(row.arrivals)}</td><td>{shown(row.processed_original)}</td><td>{shown(row.processed_rework)}</td><td>{shown(row.closing_backlog)}</td><td>{shown(row.operational_impact)}</td></tr>)}</tbody></table></div>
      <h4>Zeitlinie und gemeinsame Anbieter</h4><ul>{result.timeline.map((row, i) => <li key={i}>{row.event_id} · {kinds[row.kind]} · {row.asset_id}: Stunde {row.start_hour} bis {row.effective_end_hour}; betroffen: VU {row.affected_insurer_ids.join(", ")}</li>)}</ul><ul>{result.provider_concentration.map(row => <li key={row.provider_id}>{row.provider_id}: VU {row.insurer_ids.join(", ") || "keine aktive Servicezuordnung"}</li>)}</ul>
      <div className="ict-downloads"><button type="button" onClick={() => download("json")}>Dossier JSON</button><button type="button" onClick={() => download("csv")}>Bilanz CSV</button><button type="button" onClick={() => download("xlsx")}>Dossier Excel</button></div>
      <p>Das Dossier enthält deklarierte Quellen und Annahmen, Prozess- und Bilanzreihen, Zeitlinie, Konzentration und denselben Digest. SCR, MCR und regulatorische Quoten bleiben gesperrt.</p>
    </div>}
  </section>;
}
