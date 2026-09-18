import { useEffect, useState } from "react";
import { Calculator, Download, HeartPulse, RefreshCw, Save } from "lucide-react";
import type { CheckedSides } from "./fourSectorSources";

type Side = "baseline" | "variant";
type Issue = { path: string; code: string; message: string };
type Flow = {
  policy_id: string;
  renewal_premiums_collected: string;
  renewal_liability_allocation: string;
  death_benefit_if_death: string;
  maturity_benefit_if_due: string;
};
type NewBusiness = {
  cohort_id: string;
  new_business_premiums_collected: string;
  new_business_liability_allocation: string;
  policies: { policy_id: string; new_business_premiums_collected: string; new_business_liability_allocation: string }[];
};
type LifePeriod = {
  period: number;
  policy_flows: Flow[];
  new_business: NewBusiness[];
  operating_expense_paid: string;
  capital_contribution: string;
  capital_distribution: string;
};
type LifeInput = {
  insurer_id: number;
  opening: {
    opening_active_policies: number;
    opening_backing_assets: string;
    opening_guarantee_liability: string;
    opening_equity: string;
    policies: { policy_id: string; guarantee_liability: string; guaranteed_rate_per_period: string; remaining_periods: number }[];
  };
  assumptions: {
    insurer_id: number;
    investment: { mode: string; periods: { period: number; investment_result: string }[] };
    mortality: { periods: { period: number; death_policy_ids: string[] }[] };
  };
  periods: LifePeriod[];
};
type Case = { id: string; name: string; focus: string; baseline: LifeInput; variant: LifeInput };
type Presets = { schema_version: string; cases: Case[] };
type Row = { period: number } & Record<string, string | number | object[]>;
type Source = { period: number; investment_result: string; death_policy_ids: string[]; investment_mode: string; mortality_mode: string };
type Report = { valid: boolean; insurer_id: number; calculated_period_count: number; rows: Row[]; resolved_sources: Source[]; issues: Issue[] };
type Preview = { valid: boolean; input_digest: string; result_digest: string; report: Report };
type Stored = { result_id: string; result_digest: string; stored_at: string; report: Report; life_chain_input: LifeInput };
type History = { result_id: string; insurer_id: number; period_count: number; stored_at: string; result_digest: string };
type Metric = { key: string; label: string };

const BASE = "/api/accounting/life-period-chain";
const METRICS: Metric[] = [
  { key: "closing_active_policies", label: "Aktive Policen" },
  { key: "premiums_collected", label: "Prämien" },
  { key: "death_benefits_paid", label: "Todesfallleistungen" },
  { key: "maturity_benefits_paid", label: "Ablaufleistungen" },
  { key: "closing_backing_assets", label: "Deckungsaktiva" },
  { key: "closing_guarantee_liability", label: "Garantieverpflichtung" },
  { key: "closing_equity", label: "Eigenkapital" },
  { key: "period_profit", label: "Periodenergebnis" }
];
const FLOW_FIELDS: { key: keyof Omit<Flow, "policy_id">; label: string }[] = [
  { key: "renewal_premiums_collected", label: "Folgebeitrag" },
  { key: "renewal_liability_allocation", label: "Garantiezuführung" },
  { key: "death_benefit_if_death", label: "Leistung bei Tod" },
  { key: "maturity_benefit_if_due", label: "Leistung bei Ablauf" }
];
const PERIOD_FIELDS: { key: "operating_expense_paid" | "capital_contribution" | "capital_distribution"; label: string }[] = [
  { key: "operating_expense_paid", label: "Betriebsaufwand" },
  { key: "capital_contribution", label: "Kapitalzufuhr" },
  { key: "capital_distribution", label: "Kapitalausschüttung" }
];

function copy<T>(value: T): T { return structuredClone(value); }
function freshKey(): string { return crypto.randomUUID(); }
function amount(value: string | number | object[] | undefined): string {
  return value === undefined ? "–" : String(value).replace(".", ",");
}
function issueText(issue: Issue): string {
  const period = issue.path.match(/periods\[(\d+)\]/)?.[1];
  return `${period === undefined ? "Eingabe" : `Periode ${Number(period) + 1}`}: ${issue.message}`;
}
function apiError(response: Response, body: { code?: string }): string {
  if (response.status === 422) return "Bitte die markierten Eingaben prüfen.";
  if (response.status === 503) return "Die Ergebnisablage ist in dieser Installation nicht eingerichtet.";
  if (response.status === 504) return "Die Berechnung hat das Zeitbudget überschritten. Bitte einen kleineren Fall wählen.";
  if (response.status === 429) return "Eine Berechnung läuft noch. Bitte kurz warten.";
  if (response.status === 409) return "Der geprüfte Stand hat sich geändert. Bitte erneut berechnen.";
  return body.code ? `Anfrage nicht möglich: ${body.code}` : "Der Lebensdienst ist nicht erreichbar.";
}
function linePath(rows: Row[], key: string, min: number, max: number): string {
  const span = max - min || 1;
  return rows.map((row, index) => {
    const x = 34 + index * (720 / Math.max(1, rows.length - 1));
    const y = 164 - ((Number(row[key]) - min) / span) * 126;
    return `${index === 0 ? "M" : "L"}${x.toFixed(1)} ${y.toFixed(1)}`;
  }).join(" ");
}

export default function LifeWorkbench({ onReady }: { onReady?: (value: CheckedSides | null) => void }) {
  const [presets, setPresets] = useState<Presets | null>(null);
  const [selectedCase, setSelectedCase] = useState("death");
  const [selectedSide, setSelectedSide] = useState<Side>("variant");
  const [drafts, setDrafts] = useState<Record<Side, LifeInput> | null>(null);
  const [previews, setPreviews] = useState<Record<Side, Preview | null>>({ baseline: null, variant: null });
  const [keys, setKeys] = useState<Record<Side, string>>({ baseline: freshKey(), variant: freshKey() });
  const [metric, setMetric] = useState(METRICS[6].key);
  const [busy, setBusy] = useState<"preview" | "store" | "download" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [confirmed, setConfirmed] = useState(false);
  const [stored, setStored] = useState<Stored | null>(null);
  const [history, setHistory] = useState<History[]>([]);
  const [historyReady, setHistoryReady] = useState(false);
  const [storageError, setStorageError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    fetch(`${BASE}/presets`).then(async (response) => {
      if (!response.ok) throw new Error("Seminarfälle nicht erreichbar");
      return response.json() as Promise<Presets>;
    }).then((payload) => {
      if (!active) return;
      setPresets(payload);
      const first = payload.cases[0];
      setSelectedCase(first.id);
      setDrafts({ baseline: copy(first.baseline), variant: copy(first.variant) });
    }).catch((cause) => { if (active) setError(cause instanceof Error ? cause.message : "Seminarfälle nicht erreichbar"); });
    fetch(`${BASE}/results`).then(async (response) => {
      if (!response.ok) throw new Error(response.status === 503
        ? "Die Ergebnisablage ist nicht eingerichtet." : "Der Verlauf ist derzeit nicht erreichbar.");
      return response.json() as Promise<{ results: History[] }>;
    }).then((payload) => { if (active) { setHistory(payload.results); setHistoryReady(true); setStorageError(null); } })
      .catch((cause) => { if (active) setStorageError(cause instanceof Error ? cause.message : "Der Verlauf ist derzeit nicht erreichbar."); });
    return () => { active = false; };
  }, []);

  function chooseCase(id: string) {
    const next = presets?.cases.find((item) => item.id === id);
    if (!next) return;
    onReady?.(null);
    setSelectedCase(id);
    setDrafts({ baseline: copy(next.baseline), variant: copy(next.variant) });
    setPreviews({ baseline: null, variant: null });
    setKeys({ baseline: freshKey(), variant: freshKey() });
    setStored(null);
    setConfirmed(false);
    setIssues([]);
    setError(null);
  }

  function edit(side: Side, change: (draft: LifeInput) => void) {
    if (!drafts) return;
    onReady?.(null);
    const next = copy(drafts[side]);
    change(next);
    setDrafts({ ...drafts, [side]: next });
    setPreviews((current) => ({ ...current, [side]: null }));
    setKeys((current) => ({ ...current, [side]: freshKey() }));
    setStored(null);
    setConfirmed(false);
    setIssues([]);
    setError(null);
  }

  function insurer(value: number) {
    if (!drafts) return;
    onReady?.(null);
    const next = copy(drafts);
    for (const side of ["baseline", "variant"] as Side[]) {
      next[side].insurer_id = value;
      next[side].assumptions.insurer_id = value;
    }
    setDrafts(next);
    setPreviews({ baseline: null, variant: null });
    setKeys({ baseline: freshKey(), variant: freshKey() });
    setStored(null);
    setConfirmed(false);
    setIssues([]);
    setError(null);
  }

  function death(side: Side, checked: boolean) {
    const template = presets?.cases.find((item) => item.id === "death")?.baseline.periods[1].policy_flows.find((flow) => flow.policy_id === "A2");
    edit(side, (draft) => {
      draft.assumptions.mortality.periods[0].death_policy_ids = checked ? ["A2"] : [];
      draft.periods[1].policy_flows = draft.periods[1].policy_flows.filter((flow) => flow.policy_id !== "A2");
      if (!checked && template) draft.periods[1].policy_flows.push(copy(template));
    });
  }

  function newBusiness(side: Side, checked: boolean) {
    const template = presets?.cases.find((item) => item.id === "new_business")?.variant;
    edit(side, (draft) => {
      draft.periods[0].new_business = checked && template ? copy(template.periods[0].new_business) : [];
      draft.periods[1].policy_flows = draft.periods[1].policy_flows.filter((flow) => flow.policy_id !== "C1");
      if (checked && template) {
        const flow = template.periods[1].policy_flows.find((item) => item.policy_id === "C1");
        if (flow) draft.periods[1].policy_flows.push(copy(flow));
      }
    });
  }

  async function calculate() {
    if (!drafts || busy) return;
    onReady?.(null);
    setBusy("preview");
    setError(null);
    setIssues([]);
    setPreviews({ baseline: null, variant: null });
    try {
      const next: Record<Side, Preview | null> = { baseline: null, variant: null };
      for (const side of ["baseline", "variant"] as Side[]) {
        const response = await fetch(`${BASE}/preview`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify(drafts[side])
        });
        const payload = await response.json() as Preview & Report & { code?: string };
        if (!response.ok || !payload.valid) {
          setIssues(payload.issues ?? []);
          setError(`${side === "baseline" ? "Baseline" : "Variante"}: ${apiError(response, payload)}`);
          setPreviews(next);
          return;
        }
        next[side] = payload;
      }
      setPreviews(next);
      onReady?.({
        baseline: {
          input: copy(drafts.baseline), insurerId: drafts.baseline.insurer_id,
          periodCount: drafts.baseline.periods.length, evidenceDigest: next.baseline!.result_digest
        },
        variant: {
          input: copy(drafts.variant), insurerId: drafts.variant.insurer_id,
          periodCount: drafts.variant.periods.length, evidenceDigest: next.variant!.result_digest
        }
      });
    } catch {
      setError("Der Lebensdienst ist nicht erreichbar.");
    } finally {
      setBusy(null);
    }
  }

  async function refreshHistory() {
    try {
      const response = await fetch(`${BASE}/results`);
      if (!response.ok) throw new Error(response.status === 503
        ? "Die Ergebnisablage ist nicht eingerichtet." : "Der Verlauf ist derzeit nicht erreichbar.");
      const payload = await response.json() as { results: History[] };
      setHistory(payload.results);
      setHistoryReady(true);
      setStorageError(null);
    } catch (cause) {
      setHistoryReady(false);
      setConfirmed(false);
      setStorageError(cause instanceof Error ? cause.message : "Der Verlauf ist derzeit nicht erreichbar.");
    }
  }

  async function store() {
    const preview = previews[selectedSide];
    if (!drafts || !preview || !confirmed || busy) return;
    setBusy("store");
    setError(null);
    try {
      const response = await fetch(`${BASE}/start`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          schema_version: "ims.life-result-start.v1",
          life_chain_input: drafts[selectedSide],
          expected_input_digest: preview.input_digest,
          expected_result_digest: preview.result_digest,
          idempotency_key: keys[selectedSide],
          explicit_storage_release: true
        })
      });
      const payload = await response.json() as Stored & { code?: string };
      if (!response.ok) throw new Error(apiError(response, payload));
      if (payload.result_digest !== preview.result_digest) throw new Error("Gespeichertes Ergebnis stimmt nicht mit der Vorschau überein.");
      setStored(payload);
      setConfirmed(false);
      await refreshHistory();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Speichern nicht möglich");
    } finally {
      setBusy(null);
    }
  }

  async function selectHistory(resultId: string) {
    setError(null);
    try {
      const response = await fetch(`${BASE}/result/${encodeURIComponent(resultId)}`);
      const payload = await response.json() as Stored & { code?: string };
      if (!response.ok) throw new Error(apiError(response, payload));
      setStored(payload);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Gespeichertes Ergebnis nicht erreichbar");
    }
  }

  async function download() {
    if (!stored || busy) return;
    setBusy("download");
    setError(null);
    try {
      const response = await fetch(`${BASE}/result/${encodeURIComponent(stored.result_id)}.xlsx`, {
        headers: { "If-Match": `"${stored.result_digest}"` }
      });
      if (!response.ok || response.headers.get("etag") !== `"${stored.result_digest}"`) {
        const body = response.ok ? {} : await response.json() as { code?: string };
        throw new Error(apiError(response, body));
      }
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = `ims-leben-${stored.result_id}.xlsx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Excel-Download nicht möglich");
    } finally {
      setBusy(null);
    }
  }

  const current = drafts?.[selectedSide];
  const caseInfo = presets?.cases.find((item) => item.id === selectedCase);
  const baselineRows = previews.baseline?.report.rows ?? [];
  const variantRows = previews.variant?.report.rows ?? [];
  const points = [...baselineRows, ...variantRows].map((row) => Number(row[metric]));
  const minimum = points.length ? Math.min(0, ...points) : 0;
  const maximum = points.length ? Math.max(1, ...points) : 1;
  const selectedPreview = previews[selectedSide];

  return (
    <section className="panel life-workbench" id="life" data-testid="life-workbench">
      <div className="life-heading">
        <div className="panel-heading"><HeartPulse size={20} aria-hidden="true" /><h2>Leben im Seminar</h2></div>
        <span>IMS 2.x · Modellfall · keine historische Lebensreferenz</span>
      </div>

      <div className="life-top-controls">
        <label><span>Seminarfall</span><select value={selectedCase} disabled={!presets || busy !== null} onChange={(event) => chooseCase(event.target.value)}>
          {presets?.cases.map((item) => <option key={item.id} value={item.id}>{item.id === "new_business" ? "Neugeschäft" : item.name}</option>)}
        </select></label>
        <label><span>Versicherer</span><input type="number" min="1" max="25" value={drafts?.baseline.insurer_id ?? 1}
          disabled={!drafts || busy !== null} onChange={(event) => insurer(Number(event.target.value))} /></label>
        <div className="life-case-focus"><strong>{caseInfo?.id === "new_business" ? "Neugeschäft" : caseInfo?.name ?? "Leben"}</strong><span>{caseInfo?.focus ?? ""}</span></div>
      </div>

      <div className="life-side-tabs" role="group" aria-label="Fall bearbeiten">
        {(["baseline", "variant"] as Side[]).map((side) => <button key={side} type="button"
          aria-pressed={selectedSide === side} className={selectedSide === side ? "active" : ""}
          onClick={() => { setSelectedSide(side); setIssues([]); setError(null); }}>
          {side === "baseline" ? "Baseline" : "Variante"}
          {previews[side] && <span className="life-ready-mark">✓</span>}
        </button>)}
      </div>

      {current && <>
        <div className="life-opening" aria-label="Ausgangsbestand">
          <div><span>Policen Anfang</span><strong>{current.opening.opening_active_policies}</strong></div>
          <div><span>Deckungsaktiva</span><strong>{amount(current.opening.opening_backing_assets)}</strong></div>
          <div><span>Garantieverpflichtung</span><strong>{amount(current.opening.opening_guarantee_liability)}</strong></div>
          <div><span>Eigenkapital</span><strong>{amount(current.opening.opening_equity)}</strong></div>
        </div>

        <div className="life-editor-layout">
          <section className="life-editor-block" aria-label="Ereignisse und Neugeschäft">
            <h3>Bestand und Ereignisse</h3>
            <div className="life-policy-list">
              {current.opening.policies.map((policy) => <div key={policy.policy_id}>
                <strong>{policy.policy_id}</strong><span>{policy.remaining_periods} Perioden</span>
                <span>Garantie {amount(policy.guarantee_liability)}</span><span>Zins {amount(policy.guaranteed_rate_per_period)}</span>
              </div>)}
            </div>
            <label className="life-check"><input type="checkbox" checked={current.assumptions.mortality.periods[0].death_policy_ids.includes("A2")}
              disabled={busy !== null} onChange={(event) => death(selectedSide, event.target.checked)} />
              <span>Todesfall A2 in Periode 1</span></label>
            <label className="life-check"><input type="checkbox" checked={current.periods[0].new_business.length > 0}
              disabled={busy !== null} onChange={(event) => newBusiness(selectedSide, event.target.checked)} />
              <span>Neuer Vertrag C1 ab Periode 1</span></label>
            {current.periods[0].new_business.map((bundle) => <div className="life-new-fields" key={bundle.cohort_id}>
              {([
                ["new_business_premiums_collected", "Beitrag C1"],
                ["new_business_liability_allocation", "Garantiezuführung C1"]
              ] as const).map(([key, label]) => <label key={key}><span>{label}</span><input type="text" inputMode="decimal"
                value={bundle[key]} disabled={busy !== null}
                onChange={(event) => edit(selectedSide, (draft) => {
                  draft.periods[0].new_business[0][key] = event.target.value;
                  draft.periods[0].new_business[0].policies[0][key] = event.target.value;
                })} /></label>)}
            </div>)}
          </section>

          <section className="life-editor-block" aria-label="Periodische Annahmen">
            <h3>Perioden und Kapital</h3>
            {current.periods.map((period, index) => <div className="life-period-edit" key={period.period}>
              <h4>Periode {period.period}</h4>
              <div className="life-fields">
                <label><span>Anlageergebnis</span><input type="text" inputMode="decimal"
                  value={current.assumptions.investment.periods[index].investment_result} disabled={busy !== null}
                  onChange={(event) => edit(selectedSide, (draft) => { draft.assumptions.investment.periods[index].investment_result = event.target.value; })} /></label>
                {PERIOD_FIELDS.map(({ key, label }) => <label key={key}><span>{label}</span><input type="text" inputMode="decimal"
                  value={period[key]} disabled={busy !== null}
                  onChange={(event) => edit(selectedSide, (draft) => { draft.periods[index][key] = event.target.value; })} /></label>)}
              </div>
              <details className="life-policy-flows"><summary>Policenflüsse</summary>
                {period.policy_flows.map((flow) => <div className="life-flow-row" key={flow.policy_id}>
                  <strong>{flow.policy_id}</strong><div className="life-fields">
                    {FLOW_FIELDS.map(({ key, label }) => <label key={key}><span>{label}</span><input type="text" inputMode="decimal"
                      value={flow[key]} disabled={busy !== null}
                      onChange={(event) => edit(selectedSide, (draft) => {
                        const target = draft.periods[index].policy_flows.find((item) => item.policy_id === flow.policy_id);
                        if (target) target[key] = event.target.value;
                      })} /></label>)}
                  </div></div>)}
              </details>
            </div>)}
          </section>
        </div>
      </>}

      <div className="life-actions">
        <button className="primary-action" type="button" onClick={calculate} disabled={!drafts || busy !== null}>
          <Calculator size={17} aria-hidden="true" />{busy === "preview" ? "Berechnung läuft…" : "Beide Fälle berechnen"}
        </button>
        <span>{previews.baseline && previews.variant ? "Beide Fälle geprüft" : "Vorschau offen"}</span>
      </div>
      {error && <p className="life-error" role="alert">{error}</p>}
      {issues.length > 0 && <div className="life-issues" role="alert">{issues.slice(0, 6).map((issue, index) =>
        <p key={`${issue.code}-${index}`}>{issueText(issue)}</p>)}</div>}

      {previews.baseline && previews.variant && <div className="life-results" data-testid="life-results">
        <div className="life-results-head"><h3>Wirkung über die Zeit</h3><label><span>Kennzahl</span><select value={metric} onChange={(event) => setMetric(event.target.value)}>
          {METRICS.map((item) => <option key={item.key} value={item.key}>{item.label}</option>)}
        </select></label></div>
        <div className="life-chart" role="img" aria-label={`${METRICS.find((item) => item.key === metric)?.label}: Baseline und Variante, genaue Werte in der Tabelle`}>
          <div className="life-chart-range">Wertebereich {amount(minimum)} bis {amount(maximum)}</div>
          <svg viewBox="0 0 790 190" preserveAspectRatio="none">
            <line x1="34" y1="164" x2="754" y2="164" className="life-axis" />
            <path d={linePath(baselineRows, metric, minimum, maximum)} className="life-line-baseline" />
            <path d={linePath(variantRows, metric, minimum, maximum)} className="life-line-variant" />
          </svg>
          <div className="life-chart-periods"><span>Periode 1</span><span>Periode 2</span></div>
          <div className="life-chart-legend"><span><i className="life-legend-baseline" />Baseline</span><span><i className="life-legend-variant" />Variante</span></div>
        </div>
        <div className="life-table-wrap" role="region" aria-label="Lebens-Zeitreihe" tabIndex={0}>
          <table className="life-table"><thead><tr><th>Periode</th><th>Fall</th>{METRICS.map((item) => <th key={item.key}>{item.label}</th>)}</tr></thead>
            <tbody>{(["baseline", "variant"] as Side[]).flatMap((side) => previews[side]!.report.rows.map((row) =>
              <tr key={`${side}-${row.period}`}><th scope="row">{row.period}</th><td>{side === "baseline" ? "Baseline" : "Variante"}</td>
                {METRICS.map((item) => <td key={item.key}>{amount(row[item.key])}</td>)}</tr>))}</tbody>
          </table>
        </div>
        <div className="life-source"><h3>Annahmen und Herkunft · {selectedSide === "baseline" ? "Baseline" : "Variante"}</h3>
          {selectedPreview?.report.resolved_sources.map((source) => <div key={source.period}>
            <strong>Periode {source.period}</strong><span>Anlage {amount(source.investment_result)}</span>
            <span>Todesfälle {source.death_policy_ids.length ? source.death_policy_ids.join(", ") : "keine"}</span>
            <span>Quelle: explizite Anlage- und Todesfallannahmen</span>
          </div>)}
          <p>Modellrechnung aus expliziten Seminarannahmen; keine historische Vollgleichheit oder gesetzliche Bilanz.</p>
        </div>
      </div>}

      <div className="life-storage">
        <h3>Ergebnis sichern</h3>
        <div className="life-storage-controls">
          <label className="life-check"><input type="checkbox" checked={confirmed} disabled={!selectedPreview || !historyReady || busy !== null}
            onChange={(event) => setConfirmed(event.target.checked)} /><span>{selectedSide === "baseline" ? "Baseline" : "Variante"} ausdrücklich speichern</span></label>
          <button className="secondary-action" type="button" onClick={store} disabled={!selectedPreview || !historyReady || !confirmed || busy !== null}>
            <Save size={17} aria-hidden="true" />{busy === "store" ? "Speichert…" : "Geprüften Fall speichern"}
          </button>
        </div>
        {storageError && <p className="life-storage-error" role="status">{storageError}</p>}
        {stored && <div className="life-stored"><span>Gespeichert · VU {stored.report.insurer_id} · {stored.report.calculated_period_count} Perioden</span>
          <button className="secondary-action" type="button" onClick={download} disabled={busy !== null}>
            <Download size={17} aria-hidden="true" />Excel</button></div>}
      </div>
      <div className="life-history"><div className="life-history-head"><h3>Gespeicherte Lebensfälle</h3>
        <button className="secondary-action" type="button" title="Verlauf aktualisieren" aria-label="Verlauf aktualisieren" onClick={refreshHistory}>
          <RefreshCw size={16} aria-hidden="true" /></button></div>
        {!historyReady ? <p>Kein Verlauf verfügbar</p> : history.length === 0 ? <p>Noch keine gespeicherten Fälle</p> : <div className="life-history-list">
          {history.slice(0, 8).map((item) => <button key={item.result_id} type="button" onClick={() => selectHistory(item.result_id)}>
            <strong>VU {item.insurer_id} · {item.period_count} Perioden</strong><span>{new Date(item.stored_at).toLocaleString("de-DE")}</span>
          </button>)}
        </div>}
      </div>
    </section>
  );
}
