import { useEffect, useMemo, useState } from "react";
import {
  Activity, CheckCircle2, CircleAlert, Download, LineChart, LockKeyhole,
  Play, RefreshCw, ShieldCheck
} from "lucide-react";

type Chain = {
  chain_id: string;
  content_digest: string;
  period_count: number;
  max_periods: number;
  candidate_count: number;
  transition_count: number;
  run_index: number;
  digest_verified: boolean;
};

type Baseline = {
  chain_id: string;
  expected_content_digest: string;
  expected_result_digest: string;
  run_index: number;
};

type Actor = Record<string, number | boolean | number[]>;
type Effect = {
  period: number;
  global_period: number;
  applications: { vu_total: number; vn_total: number };
  state_after: { insurers: Actor[]; policyholders: Actor[] };
};

type ProbeResult = {
  schema_version: string;
  period_count: number;
  period_chain_identity: { chain_id: string; content_digest: string };
  period_effects: Effect[];
  transition_effects: unknown[];
  prefix_proof: {
    baseline_chain_id: string;
    baseline_result_digest: string;
    canonical_json_byte_equal: boolean;
  };
  effect_digest: string;
  runner_invocation_count: number;
  result_persisted: boolean;
  historical_full_equality_claim: boolean;
};

type Contract = {
  schema_version: string;
  request_schema_version: string;
  release_request_schema_version: string;
  effect_probe_endpoint: string;
  bundle_endpoint: string;
  period_count: number;
  bundle_if_match_supported: boolean;
  result_persisted: boolean;
};

type Run = { result: ProbeResult; request: Record<string, unknown> };
type ActorKind = "insurers" | "policyholders";
type Metric = { field: string; label: string; vector: boolean };

const METRICS: Record<ActorKind, Metric[]> = {
  insurers: [
    { field: "premiums_current", label: "Praemien", vector: false },
    { field: "advertising_current", label: "Werbung", vector: false },
    { field: "policyholders_current", label: "Versicherungsnehmer", vector: false },
    { field: "premiums_current_sector", label: "Praemien je Position", vector: true },
    { field: "reserves_current", label: "Reserven je Position", vector: true },
    { field: "claims_count_current", label: "Schaeden je Position", vector: true },
    { field: "claims_sum_current", label: "Schadensumme je Position", vector: true }
  ],
  policyholders: [
    { field: "end_wealth_current", label: "Endvermoegen", vector: false },
    { field: "paid_premium_current", label: "Bezahlte Praemie je Position", vector: true },
    { field: "claim_sum_current", label: "Schadensumme je Position", vector: true },
    { field: "end_wealth_sector_current", label: "Endvermoegen je Position", vector: true }
  ]
};

function shortId(value: string): string {
  return value.length > 20 ? `...${value.slice(-12)}` : value;
}

function message(value: unknown, fallback: string): string {
  if (value && typeof value === "object") {
    const payload = value as { message?: unknown; code?: unknown };
    if (typeof payload.message === "string") return payload.message;
    if (payload.code === "effect_digest_mismatch") {
      return "Der neue Lauf weicht vom angezeigten Ergebnis ab. Es wurde kein ZIP ausgegeben.";
    }
    if (typeof payload.code === "string") return payload.code;
  }
  return fallback;
}

function point(effect: Effect, kind: ActorKind, actorId: number, metric: Metric, sector: number): number | null {
  const idField = kind === "insurers" ? "insurer_id" : "policyholder_id";
  const actor = effect.state_after[kind].find((item) => item[idField] === actorId);
  if (!actor) return null;
  const raw = actor[metric.field];
  const value = metric.vector && Array.isArray(raw) ? raw[sector] : raw;
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function series(result: ProbeResult | null, kind: ActorKind, actorId: number,
                metric: Metric, sector: number): Array<number | null> {
  return result?.period_effects.map((effect) => point(effect, kind, actorId, metric, sector)) ?? [];
}

function Trend({ primary, comparison }: {
  primary: Array<number | null>; comparison: Array<number | null>;
}) {
  const finite = [...primary, ...comparison].filter((value): value is number => value !== null);
  if (finite.length === 0) return <div className="empty-state">Keine Werte fuer diese Auswahl.</div>;
  const low = Math.min(...finite);
  const high = Math.max(...finite);
  const span = high - low || 1;
  const path = (values: Array<number | null>) => values.map((value, index) => (
    value === null ? null : `${index === 0 || values[index - 1] === null ? "M" : "L"} ${32 + index * 7.5} ${175 - (value - low) / span * 140}`
  )).filter(Boolean).join(" ");
  return (
    <div className="hundred-chart" aria-label="Zeitreihe fuer 100 Perioden">
      <svg viewBox="0 0 800 200" role="img" aria-label="Zeitreihe; genaue Werte stehen in der Tabelle">
        <line x1="32" y1="175" x2="775" y2="175" className="hundred-chart-axis" />
        <line x1="32" y1="35" x2="32" y2="175" className="hundred-chart-axis" />
        <path d={path(primary)} className="hundred-chart-primary" />
        {comparison.length > 0 && <path d={path(comparison)} className="hundred-chart-compare" />}
      </svg>
      <div className="hundred-chart-scale"><span>1</span><span>25</span><span>50</span><span>75</span><span>100</span></div>
      <div className="hundred-chart-legend">
        <span><i className="hundred-chart-primary-key" />Ausgewaehlter Lauf</span>
        {comparison.length > 0 && <span><i className="hundred-chart-compare-key" />Vergleichslauf</span>}
        <span>Wertebereich: {low.toLocaleString("de-DE")} bis {high.toLocaleString("de-DE")}</span>
      </div>
    </div>
  );
}

export default function HundredPeriodResults() {
  const [contract, setContract] = useState<Contract | null>(null);
  const [chains, setChains] = useState<Chain[]>([]);
  const [baselines, setBaselines] = useState<Baseline[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [baselineId, setBaselineId] = useState("");
  const [detail, setDetail] = useState<Record<string, unknown> | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [revision, setRevision] = useState(0);
  const [actor, setActor] = useState("workbench-ui");
  const [reason, setReason] = useState("100-Perioden-Ergebnis ansehen");
  const [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState<"run" | "download" | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [runs, setRuns] = useState<Record<string, Run>>({});
  const [comparisonId, setComparisonId] = useState("");
  const [actorKind, setActorKind] = useState<ActorKind>("insurers");
  const [actorId, setActorId] = useState(0);
  const [metricField, setMetricField] = useState("premiums_current");
  const [sector, setSector] = useState(0);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      setLoadError(null);
      try {
        const [contractResponse, overviewResponse] = await Promise.all([
          fetch("/api/run-control/strategy-period-chain-hundred-workbench-contract"),
          fetch("/api/strategies/execution-period-chains")
        ]);
        if (!contractResponse.ok || !overviewResponse.ok) throw new Error("Ergebnisquellen nicht erreichbar");
        const nextContract = await contractResponse.json() as Contract;
        const overview = await overviewResponse.json() as {
          storage: { configured: boolean }; period_chains: Chain[]
        };
        if (!overview.storage.configured) throw new Error("Keine lokale SQLite-Ablage konfiguriert");
        const available = overview.period_chains.filter((chain) => (
          chain.period_count === 100 && chain.max_periods === 100 &&
          chain.candidate_count === 100 && chain.transition_count === 99 && chain.digest_verified
        ));
        const five = overview.period_chains.filter((chain) => chain.period_count === 5 && chain.digest_verified);
        const prefixResults = await Promise.all(five.map(async (chain) => {
          try {
            const response = await fetch(
              `/api/run-control/strategy-period-chain-five-period-effect-probe-result/${encodeURIComponent(chain.chain_id)}`
            );
            const read = await response.json() as {
              result_available: boolean; record?: { result_digest: string }
            };
            return response.ok && read.result_available && read.record ? {
              chain_id: chain.chain_id,
              expected_content_digest: chain.content_digest,
              expected_result_digest: read.record.result_digest,
              run_index: chain.run_index
            } : null;
          } catch { return null; }
        }));
        if (!active) return;
        const ready = prefixResults.filter((item): item is Baseline => item !== null);
        setContract(nextContract);
        setChains(available);
        setBaselines(ready);
        setSelectedId((current) => available.some((chain) => chain.chain_id === current)
          ? current : available[0]?.chain_id ?? "");
        setBaselineId((current) => ready.some((item) => item.chain_id === current)
          ? current : ready[0]?.chain_id ?? "");
      } catch (error) {
        if (active) setLoadError(error instanceof Error ? error.message : "Ergebnisse nicht erreichbar");
      } finally { if (active) setLoading(false); }
    }
    void load();
    return () => { active = false; };
  }, [revision]);

  useEffect(() => {
    let active = true;
    setDetail(null);
    setDetailError(null);
    setConfirmed(false);
    setActionError(null);
    if (!selectedId) return () => { active = false; };
    async function loadDetail() {
      try {
        const response = await fetch(
          `/api/strategies/execution-period-chains/${encodeURIComponent(selectedId)}`
        );
        const read = await response.json() as {
          status: string; record?: { chain_id: string; period_chain_input: Record<string, unknown> }
        };
        if (!response.ok || read.status !== "ok" || read.record?.chain_id !== selectedId) {
          throw new Error("Kettendetails nicht erreichbar oder nicht mehr passend");
        }
        if (active) setDetail(read.record.period_chain_input);
      } catch (error) {
        if (active) setDetailError(error instanceof Error ? error.message : "Kettendetails nicht erreichbar");
      }
    }
    void loadDetail();
    return () => { active = false; };
  }, [selectedId]);

  const selected = chains.find((chain) => chain.chain_id === selectedId);
  const matchingBaselines = baselines.filter((item) => item.run_index === selected?.run_index);
  const prefix = matchingBaselines.find((item) => item.chain_id === baselineId)
    ?? matchingBaselines[0];
  const current = runs[selectedId]?.result ?? null;
  const comparable = chains.filter((chain) => {
    const other = runs[chain.chain_id]?.result;
    return chain.chain_id !== selectedId && other && current &&
      other.prefix_proof.baseline_chain_id === current.prefix_proof.baseline_chain_id &&
      other.prefix_proof.baseline_result_digest === current.prefix_proof.baseline_result_digest;
  });
  const comparison = comparable.find((chain) => chain.chain_id === comparisonId);
  const compared = comparison ? runs[comparison.chain_id]?.result ?? null : null;
  const actorIdField = actorKind === "insurers" ? "insurer_id" : "policyholder_id";
  const actors = current?.period_effects.flatMap((effect) => effect.state_after[actorKind]) ?? [];
  const ids = [...new Set(actors.map((entry) => Number(entry[actorIdField]))
    .filter(Number.isFinite))].sort((a, b) => a - b);
  const chosenActorId = ids.includes(actorId) ? actorId : ids[0] ?? 0;
  const metrics = METRICS[actorKind].filter((item) => actors[0] && item.field in actors[0]);
  const metric = metrics.find((item) => item.field === metricField) ?? metrics[0];
  const positions = metric?.vector && actors[0] && Array.isArray(actors[0][metric.field])
    ? (actors[0][metric.field] as number[]).map((_, index) => index) : [];
  const chosenSector = positions.includes(sector) ? sector : positions[0] ?? 0;
  const values = useMemo(() => metric && current
    ? series(current, actorKind, chosenActorId, metric, chosenSector) : [],
    [current, actorKind, chosenActorId, metric, chosenSector]);
  const compareValues = useMemo(() => metric && compared
    ? series(compared, actorKind, chosenActorId, metric, chosenSector) : [],
    [compared, actorKind, chosenActorId, metric, chosenSector]);

  const canRun = Boolean(contract && selected && prefix && detail && actor.trim() &&
    reason.trim() && confirmed && !busy && contract.period_count === 100 &&
    contract.result_persisted === false);

  async function start() {
    if (!canRun || !contract || !selected || !prefix || !detail) return;
    const request = {
      schema_version: contract.request_schema_version,
      period_chain_input: detail,
      five_period_baseline: {
        chain_id: prefix.chain_id,
        expected_content_digest: prefix.expected_content_digest,
        expected_result_digest: prefix.expected_result_digest
      },
      release: {
        schema_version: contract.release_request_schema_version,
        chain_id: selected.chain_id,
        expected_content_digest: selected.content_digest,
        idempotency_key: `workbench-100-${crypto.randomUUID()}`,
        explicit_run_control_release: true,
        released_by: actor.trim(),
        released_at: new Date().toISOString(),
        release_reason: reason.trim()
      },
      explicit_extended_effect_probe_execution: true
    };
    setBusy("run");
    setActionError(null);
    try {
      const response = await fetch(contract.effect_probe_endpoint, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request)
      });
      const payload = await response.json() as ProbeResult | { code?: string; message?: string };
      if (!response.ok) throw new Error(message(payload, "100-Perioden-Lauf fehlgeschlagen"));
      const result = payload as ProbeResult;
      if (result.period_count !== 100 || result.period_effects.length !== 100 ||
          result.period_chain_identity.chain_id !== selected.chain_id ||
          result.period_chain_identity.content_digest !== selected.content_digest ||
          result.prefix_proof.baseline_chain_id !== prefix.chain_id ||
          result.prefix_proof.canonical_json_byte_equal !== true ||
          result.result_persisted !== false) {
        throw new Error("Ergebnis passt nicht zur freigegebenen Kette");
      }
      setRuns((previous) => ({ ...previous, [selected.chain_id]: { result, request } }));
      setConfirmed(false);
    } catch (error) {
      setActionError(error instanceof Error ? error.message : "100-Perioden-Lauf nicht erreichbar");
    } finally { setBusy(null); }
  }

  async function download() {
    const run = runs[selectedId];
    if (!run || !contract || busy || !contract.bundle_if_match_supported) return;
    setBusy("download");
    setActionError(null);
    try {
      const response = await fetch(contract.bundle_endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", "If-Match": `"${run.result.effect_digest}"` },
        body: JSON.stringify(run.request)
      });
      if (!response.ok) {
        throw new Error(message(await response.json(), "Download fehlgeschlagen"));
      }
      if (response.headers.get("etag") !== `"${run.result.effect_digest}"` ||
          !response.headers.get("content-type")?.includes("application/zip")) {
        throw new Error("Download stimmt nicht mit dem sichtbaren Ergebnis ueberein");
      }
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = "ims-100-perioden.zip";
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (error) {
      setActionError(error instanceof Error ? error.message : "Download nicht erreichbar");
    } finally { setBusy(null); }
  }

  return (
    <div className="hundred-results" data-testid="hundred-period-results">
      <div className="strategy-candidate-toolbar">
        <div><strong>100-Perioden-Ergebnisse</strong><span>Gespeicherte Ketten, fluechtige Ergebnisse</span></div>
        <button className="secondary-action" type="button" onClick={() => setRevision((value) => value + 1)}
          disabled={loading || busy !== null}><RefreshCw size={16} aria-hidden="true" />Aktualisieren</button>
      </div>
      {loadError ? <div className="empty-state" role="alert">{loadError}</div> : loading ? (
        <div className="empty-state">Gespeicherte Ketten werden geprueft.</div>
      ) : chains.length === 0 ? (
        <div className="empty-state">Keine gepruefte 100-Perioden-Kette vorhanden.</div>
      ) : (
        <>
          <div className="hundred-run-controls">
            <div className="hundred-run-fields">
              <label><span>Periodenkette</span><select value={selectedId} onChange={(event) => setSelectedId(event.target.value)}
                disabled={busy !== null} data-testid="hundred-chain-select">
                {chains.map((chain) => <option key={chain.chain_id} value={chain.chain_id}>
                  Lauf {chain.run_index} · {shortId(chain.chain_id)}
                </option>)}
              </select></label>
              <label><span>Prefixnachweis</span><select value={prefix?.chain_id ?? ""} onChange={(event) => setBaselineId(event.target.value)}
                disabled={busy !== null || matchingBaselines.length === 0} data-testid="hundred-prefix-select">
                {matchingBaselines.length === 0 && <option value="">Kein Fuenf-Perioden-Nachweis</option>}
                {matchingBaselines.map((item) => <option key={item.chain_id} value={item.chain_id}>{shortId(item.chain_id)}</option>)}
              </select></label>
              <label><span>Freigabe durch</span><input value={actor} onChange={(event) => setActor(event.target.value)}
                disabled={busy !== null} /></label>
              <label><span>Grund</span><input value={reason} onChange={(event) => setReason(event.target.value)}
                disabled={busy !== null} /></label>
            </div>
            <div className="hundred-run-actions">
              <label><input type="checkbox" checked={confirmed} onChange={(event) => setConfirmed(event.target.checked)}
                disabled={busy !== null} data-testid="hundred-run-confirm" />
                100 Perioden jetzt fluechtig ausfuehren</label>
              <button className="primary-action" type="button" disabled={!canRun} onClick={() => void start()}
                data-testid="hundred-run-start"><Play size={16} aria-hidden="true" />
                {busy === "run" ? "Lauf laeuft" : "100 Perioden starten"}</button>
            </div>
          </div>
          {detailError ? (
            <div className="hundred-status error" role="alert"><CircleAlert size={16} aria-hidden="true" />{detailError}</div>
          ) : !detail && <div className="hundred-status"><LockKeyhole size={16} aria-hidden="true" />Kettendetails werden geprueft.</div>}
          {matchingBaselines.length === 0 && <div className="hundred-status"><LockKeyhole size={16} aria-hidden="true" />Fuenf-Perioden-Nachweis fuer diesen Lauf fehlt.</div>}
          {busy === "run" && <div className="hundred-status" role="status"><Activity size={16} aria-hidden="true" />Isolierter Lauf aktiv. Das Ergebnis erscheint erst nach allen 100 Perioden.</div>}
          {actionError && <div className="hundred-status error" role="alert" data-testid="hundred-run-error"><CircleAlert size={16} aria-hidden="true" />{actionError}</div>}
          {current && metric && (
            <section className="hundred-result" data-testid="hundred-result">
              <div className="hundred-result-head">
                <div><strong><CheckCircle2 size={17} aria-hidden="true" />100 Perioden geprueft</strong>
                  <span>Prefix 1-5 bytegenau · {current.transition_effects.length} Uebergaenge · nur im Browser</span></div>
                <button type="button" className="secondary-action" onClick={() => void download()}
                  disabled={busy !== null} data-testid="hundred-download"><Download size={16} aria-hidden="true" />
                  {busy === "download" ? "Buendel wird erzeugt" : "ZIP herunterladen"}</button>
              </div>
              <div className="hundred-provenance"><ShieldCheck size={16} aria-hidden="true" />
                <span title={current.effect_digest}>Wirkungsdigest: {current.effect_digest}</span></div>
              <div className="hundred-result-filters">
                <div className="hundred-segment" role="group" aria-label="Akteursart">
                  <button type="button" className={actorKind === "insurers" ? "active" : ""}
                    aria-pressed={actorKind === "insurers"} onClick={() => { setActorKind("insurers"); setMetricField("premiums_current"); }}>
                    Versicherer</button>
                  <button type="button" className={actorKind === "policyholders" ? "active" : ""}
                    aria-pressed={actorKind === "policyholders"} onClick={() => { setActorKind("policyholders"); setMetricField("end_wealth_current"); }}>
                    Versicherungsnehmer</button>
                </div>
                <label><span>Akteur</span><select value={chosenActorId} onChange={(event) => setActorId(Number(event.target.value))}>
                  {ids.map((id) => <option key={id} value={id}>#{id}</option>)}
                </select></label>
                <label><span>Kennzahl</span><select value={metric.field} onChange={(event) => setMetricField(event.target.value)}>
                  {metrics.map((item) => <option key={item.field} value={item.field}>{item.label}</option>)}
                </select></label>
                {metric.vector && <label><span>Vektorposition</span><select value={chosenSector} onChange={(event) => setSector(Number(event.target.value))}>
                  {positions.map((index) => <option key={index} value={index}>{index}</option>)}
                </select></label>}
                <label><span>Vergleichslauf</span><select value={comparison?.chain_id ?? ""}
                  onChange={(event) => setComparisonId(event.target.value)}>
                  <option value="">Keiner</option>
                  {comparable.map((chain) => <option key={chain.chain_id} value={chain.chain_id}>
                    Lauf {chain.run_index} · {shortId(chain.chain_id)}
                  </option>)}
                </select></label>
              </div>
              <Trend primary={values} comparison={compareValues} />
              <div className="hundred-table-scroll"><table className="hundred-table">
                <thead><tr><th>Periode</th><th>Ausgewaehlter Lauf</th>{compared && <th>Vergleichslauf</th>}</tr></thead>
                <tbody>{values.map((value, index) => <tr key={index}>
                  <th scope="row">{index + 1}</th><td>{value === null ? "-" : String(value)}</td>
                  {compared && <td>{compareValues[index] === null ? "-" : String(compareValues[index])}</td>}
                </tr>)}</tbody>
              </table></div>
              <div className="hundred-status"><LineChart size={16} aria-hidden="true" />
                Zwei Laeufe sind ein Vergleich, kein Nachweis einer Ursache oder historischer Vollgleichheit.</div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
