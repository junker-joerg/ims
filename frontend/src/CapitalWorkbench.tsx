import { useEffect, useRef, useState } from "react";
import { Calculator, CircleAlert, Download, ShieldCheck } from "lucide-react";
import type { CheckedFourSector } from "./fourSectorSources";

type Issue = { path: string; code: string; message: string };
type Report = { valid: boolean; content_digest: string | null; issues: Issue[] };
type ModelBalance = Report & {
  source_content_digest: string;
  insurer_id: number;
  scenario_id: string;
  variant_id: string;
  checkpoint: { model_period: number; reference_date: string };
  sector_rows: { sector_id: string; model_own_funds_proxy: string }[];
};
type RiskAggregation = Report & {
  source_model_balance_content_digest: string;
  component_rows: { risk_kind: string; model_loss_amount: string }[];
  totals: { gross_model_stress_loss: string; model_buffer_applied: string; net_model_stress_loss: string };
};
type CapitalReadiness = Report & {
  source_model_balance_content_digest: string;
  source_risk_aggregation_content_digest: string;
  insurer_id: number;
  scenario_id: string;
  variant_id: string;
  checkpoint: { model_period: number; reference_date: string };
  management_evaluation: {
    model_own_funds_proxy: string;
    net_model_stress_loss: string;
    remaining_model_equity_proxy: string;
    loss_limit_met: boolean;
    equity_floor_met: boolean;
    both_limits_met: boolean;
  };
  regulatory_metrics: Record<string, string | null>;
  readiness_rows: { requirement_code: string; status: string; message: string }[];
  compliance_decision_enabled: boolean;
};
type Contract = {
  input_schema_version: string;
  source_input_schema_version: string;
  scope_contract_schema_version?: string;
  calculation_endpoint: string;
  xlsx_endpoint?: string;
  writes_enabled: boolean;
  runner_enabled: boolean;
};
type Contracts = { model: Contract; shock: Contract; module: Contract; aggregation: Contract; readiness: Contract };
type Adjustment = { asset_delta: string; liability_delta: string };
type ExposureDraft = { amount: string; rate: string };
type CapitalResult = { input: object; balance: ModelBalance; aggregation: RiskAggregation; readiness: CapitalReadiness };

const SECTORS = [
  { id: "motor", label: "Kfz" },
  { id: "property_liability", label: "Sach-Haftpflicht" },
  { id: "life", label: "Leben" },
  { id: "health", label: "Kranken" }
] as const;
const EXPOSURES = [
  { id: "motor_assets", label: "Kfz-Anlagen", sector: "motor", side: "assets", kind: "asset_market_value" },
  { id: "motor_claims", label: "Kfz-Schadenpflicht", sector: "motor", side: "liabilities", kind: "non_life_claim_obligation" },
  { id: "property_claims", label: "Sach-Haftpflicht", sector: "property_liability", side: "liabilities", kind: "non_life_claim_obligation" },
  { id: "life_liability", label: "Lebensverpflichtung", sector: "life", side: "liabilities", kind: "life_obligation" },
  { id: "health_benefit", label: "Krankenleistung", sector: "health", side: "liabilities", kind: "health_benefit_obligation" },
  { id: "health_assets", label: "Kranken-Gegenpartei", sector: "health", side: "assets", kind: "counterparty_model_loss" }
] as const;
const RISKS = [
  { id: "asset_market_value", label: "Marktwert Aktiva" },
  { id: "non_life_claim_obligation", label: "Schadenverpflichtung" },
  { id: "life_obligation", label: "Lebensverpflichtung" },
  { id: "health_benefit_obligation", label: "Krankenleistung" },
  { id: "counterparty_model_loss", label: "Gegenpartei" },
  { id: "operational_model_loss", label: "Betriebsereignis" }
] as const;
const REGULATORY_KEYS = ["eligible_own_funds", "scr", "mcr", "scr_coverage_ratio", "mcr_coverage_ratio"];

function today(): string {
  const date = new Date();
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function initialAdjustments(): Adjustment[] {
  return SECTORS.map(() => ({ asset_delta: "0", liability_delta: "0" }));
}

function initialExposures(): ExposureDraft[] {
  return EXPOSURES.map(() => ({ amount: "0", rate: "0" }));
}

function initialFactors(): Record<string, string> {
  return Object.fromEntries(RISKS.map(({ id }) => [id, "1"]));
}

function decimal(value: string): string {
  return value.replace(",", ".");
}

function display(value: string): string {
  return value.replace(".", ",");
}

async function checkedPost<T extends Report>(endpoint: string, input: object): Promise<T> {
  const response = await fetch(endpoint, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(input)
  });
  const report = await response.json() as T;
  if (!response.ok || !report.valid || !report.content_digest) {
    const issue = report.issues?.[0];
    throw new Error(issue ? `${issue.message} (${issue.path})` : "Kapital-Modellrechnung nicht verfügbar.");
  }
  if (response.headers.get("etag") !== `"${report.content_digest}"`) {
    throw new Error("Der Ergebnisnachweis stimmt nicht mit der Serverantwort überein.");
  }
  return report;
}

function saveBlob(name: string, contents: Blob): void {
  const url = URL.createObjectURL(contents);
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  document.body.append(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 0);
}

export default function CapitalWorkbench({ source }: { source: CheckedFourSector | null }) {
  const [contracts, setContracts] = useState<Contracts | null>(null);
  const [contractError, setContractError] = useState<string | null>(null);
  const [period, setPeriod] = useState(1);
  const [referenceDate, setReferenceDate] = useState(today);
  const [note, setNote] = useState("Deklarierte Annahme fuer Managementseminar");
  const [adjustments, setAdjustments] = useState(initialAdjustments);
  const [exposures, setExposures] = useState(initialExposures);
  const [factors, setFactors] = useState(initialFactors);
  const [operationalLoss, setOperationalLoss] = useState("0");
  const [bufferCapacity, setBufferCapacity] = useState("0");
  const [bufferApplied, setBufferApplied] = useState("0");
  const [maxLoss, setMaxLoss] = useState("0");
  const [minEquity, setMinEquity] = useState("0");
  const [confirmed, setConfirmed] = useState(false);
  const [result, setResult] = useState<CapitalResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<"calculate" | "xlsx" | null>(null);
  const revision = useRef(0);

  useEffect(() => {
    let active = true;
    const endpoints = ["solvency-model-balance", "solvency-scenario-shocks", "solvency-risk-modules",
      "solvency-risk-aggregation", "solvency-capital-readiness"];
    Promise.all(endpoints.map(async (name) => {
      const response = await fetch(`/api/accounting/${name}-contract`);
      if (!response.ok) throw new Error("Kapitalverträge nicht erreichbar");
      return response.json() as Promise<Contract>;
    })).then(([model, shock, module, aggregation, readiness]) => {
      if (!active) return;
      const ordered = [model, shock, module, aggregation, readiness];
      if (ordered.some((item) => item.writes_enabled !== false || item.runner_enabled !== false) ||
          shock.source_input_schema_version !== model.input_schema_version ||
          module.source_input_schema_version !== shock.input_schema_version ||
          aggregation.source_input_schema_version !== module.input_schema_version ||
          readiness.source_input_schema_version !== aggregation.input_schema_version ||
          !readiness.xlsx_endpoint) {
        throw new Error("Kapitalverträge passen nicht zusammen oder erlauben unerwartete Aktionen.");
      }
      setContracts({ model, shock, module, aggregation, readiness });
    }).catch((cause) => {
      if (active) setContractError(cause instanceof Error ? cause.message : "Kapitaldienst nicht erreichbar");
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    revision.current += 1;
    setResult(null);
    setBusy(null);
    setError(null);
    setConfirmed(false);
    setPeriod(1);
    setAdjustments(initialAdjustments());
    setExposures(initialExposures());
    setFactors(initialFactors());
    setOperationalLoss("0");
    setBufferCapacity("0");
    setBufferApplied("0");
    setMaxLoss("0");
    setMinEquity("0");
  }, [source]);

  function invalidate(): void {
    revision.current += 1;
    setResult(null);
    setError(null);
    setBusy(null);
    setConfirmed(false);
  }

  function setAdjustment(index: number, field: keyof Adjustment, value: string): void {
    setAdjustments((current) => current.map((row, position) => position === index
      ? { ...row, [field]: decimal(value) } : row));
    invalidate();
  }

  function setExposure(index: number, field: keyof ExposureDraft, value: string): void {
    setExposures((current) => current.map((row, position) => position === index
      ? { ...row, [field]: decimal(value) } : row));
    invalidate();
  }

  function requestInputs(current: CheckedFourSector, versions: Contracts) {
    const balanceInput = {
      schema_version: versions.model.input_schema_version,
      scope_contract_schema_version: versions.model.scope_contract_schema_version,
      model_only_confirmed: true,
      four_sector_input: current.input,
      checkpoint: { model_period: period, reference_date: referenceDate, date_linkage: "scenario_declared" },
      adjustments: SECTORS.map(({ id }, index) => ({
        sector_id: id, ...adjustments[index], assumption_id: `workshop_${id}`, assumption_note: note
      }))
    };
    const shockInput = {
      schema_version: versions.shock.input_schema_version,
      solvency_model_balance_input: balanceInput,
      exposures: EXPOSURES.map(({ id, sector, side }, index) => ({
        exposure_id: id, sector_id: sector, balance_side: side, base_amount: exposures[index].amount,
        source_kind: "scenario_declared_non_overlapping_subposition"
      })),
      shocks: []
    };
    const moduleInput = {
      schema_version: versions.module.input_schema_version,
      solvency_scenario_shocks_input: shockInput,
      module_parameters: EXPOSURES.slice(0, 5).map(({ id, kind }, index) => ({
        module_id: id, module_kind: kind, exposure_id: id, stress_rate: exposures[index].rate,
        parameter_source_kind: "scenario_declared_not_regulatory", assumption_note: note
      }))
    };
    const aggregationInput = {
      schema_version: versions.aggregation.input_schema_version,
      solvency_risk_modules_input: moduleInput,
      counterparty_cases: [{ case_id: "cp_health", exposure_id: "health_assets",
        loss_rate: exposures[5].rate, source_kind: "scenario_declared_not_regulatory", assumption_note: note }],
      operational_events: [{ event_id: "workshop_operation", loss_amount: operationalLoss,
        source_kind: "scenario_declared_not_regulatory", assumption_note: note }],
      aggregation_assumptions: { source_kind: "scenario_declared_not_regulatory",
        assumption_note: note, factor_loadings: factors },
      loss_absorption: { buffer_id: "workshop_buffer", capacity_amount: bufferCapacity,
        applied_amount: bufferApplied, source_kind: "scenario_declared_independent_model_buffer",
        assumption_note: note }
    };
    return { balanceInput, aggregationInput, readinessInput: {
      schema_version: versions.readiness.input_schema_version,
      solvency_risk_aggregation_input: aggregationInput,
      management_limits: { source_kind: "management_workshop_declared_not_regulatory",
        assumption_note: note, max_net_model_stress_loss: maxLoss,
        min_remaining_model_equity_proxy: minEquity }
    } };
  }

  async function calculate(): Promise<void> {
    if (!source || !contracts || !confirmed || busy) return;
    const currentRevision = revision.current;
    const input = requestInputs(source, contracts);
    setBusy("calculate");
    setError(null);
    setResult(null);
    try {
      const balance = await checkedPost<ModelBalance>(contracts.model.calculation_endpoint, input.balanceInput);
      if (currentRevision !== revision.current) return;
      if (balance.source_content_digest !== source.evidenceDigest || balance.insurer_id !== source.insurerId ||
          balance.scenario_id !== source.scenarioId || balance.variant_id !== source.variantId ||
          balance.checkpoint.model_period !== period) {
        throw new Error("Die Modellbilanz gehört nicht zur geprüften Vier-Sparten-Quelle.");
      }
      const aggregation = await checkedPost<RiskAggregation>(contracts.aggregation.calculation_endpoint, input.aggregationInput);
      if (currentRevision !== revision.current) return;
      if (aggregation.source_model_balance_content_digest !== balance.content_digest) {
        throw new Error("Die Stressrechnung gehört nicht zur Modellbilanz.");
      }
      const readiness = await checkedPost<CapitalReadiness>(contracts.readiness.calculation_endpoint, input.readinessInput);
      if (currentRevision !== revision.current) return;
      if (readiness.source_model_balance_content_digest !== balance.content_digest ||
          readiness.source_risk_aggregation_content_digest !== aggregation.content_digest ||
          readiness.insurer_id !== source.insurerId || readiness.scenario_id !== source.scenarioId ||
          readiness.variant_id !== source.variantId || readiness.checkpoint.model_period !== period ||
          readiness.compliance_decision_enabled !== false ||
          readiness.regulatory_metrics.status !== "blocked_missing_regulatory_basis" ||
          REGULATORY_KEYS.some((key) => readiness.regulatory_metrics[key] !== null)) {
        throw new Error("Die Kapitalantwort verletzt die Quellen- oder Regulatorik-Sperre.");
      }
      setResult({ input: input.readinessInput, balance, aggregation, readiness });
    } catch (cause) {
      if (currentRevision === revision.current) {
        setError(cause instanceof Error ? cause.message : "Kapitaldienst nicht erreichbar");
      }
    } finally {
      if (currentRevision === revision.current) setBusy(null);
    }
  }

  function downloadJson(): void {
    if (!result || !source) return;
    const content = { schema_version: "ims.solvency-capital-workbench-export.v1",
      four_sector_content_digest: source.evidenceDigest,
      input: result.input, model_balance: result.balance,
      risk_aggregation: result.aggregation, capital_readiness: result.readiness };
    saveBlob(`ims-kapital-modell-vu-${source.insurerId}-p-${period}.json`,
      new Blob([JSON.stringify(content, null, 2)], { type: "application/json" }));
  }

  async function downloadXlsx(): Promise<void> {
    if (!result || !contracts?.readiness.xlsx_endpoint || busy) return;
    const currentRevision = revision.current;
    setBusy("xlsx");
    setError(null);
    try {
      const response = await fetch(contracts.readiness.xlsx_endpoint, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(result.input)
      });
      if (currentRevision !== revision.current) return;
      if (!response.ok || response.headers.get("etag") !== `"${result.readiness.content_digest}"`) {
        throw new Error("Der XLSX-Nachweis stimmt nicht mit dem angezeigten Ergebnis überein.");
      }
      const contents = await response.blob();
      if (currentRevision !== revision.current) return;
      saveBlob(`ims-kapital-modell-vu-${result.readiness.insurer_id}-p-${period}.xlsx`, contents);
    } catch (cause) {
      if (currentRevision === revision.current) {
        setError(cause instanceof Error ? cause.message : "XLSX-Export nicht erreichbar");
      }
    } finally {
      if (currentRevision === revision.current) setBusy(null);
    }
  }

  const management = result?.readiness.management_evaluation;
  const totals = result?.aggregation.totals;

  return <section className="panel capital-workbench" id="capital" data-testid="capital-workbench">
    <div className="capital-heading">
      <div className="panel-heading"><ShieldCheck size={20} aria-hidden="true" /><h2>Kapitalwirkung im Modell</h2></div>
      <span>Managementseminar · keine Aufsichtsmeldung</span>
    </div>
    {!source && <p className="capital-gate" role="status"><CircleAlert size={17} aria-hidden="true" />
      Zuerst die Vier-Sparten-Gesamtbilanz prüfen.</p>}
    {contractError && <p className="capital-error" role="alert">{contractError}</p>}
    {source && <>
      <div className="capital-source"><strong>Bilanzquelle</strong>
        <span>VU {source.insurerId} · {source.scenarioId} · {source.variantId === "baseline" ? "Baseline" : "Variante"} · {source.periodCount} Perioden</span>
        <code title={source.evidenceDigest}>{source.evidenceDigest.slice(0, 12)}</code></div>
      <div className="capital-fields capital-context">
        <label>Modellperiode<select value={period} onChange={(event) => { setPeriod(Number(event.target.value)); invalidate(); }}>
          {Array.from({ length: source.periodCount }, (_, index) => <option value={index + 1} key={index}>{index + 1}</option>)}
        </select></label>
        <label>Szenario-Referenztag<input type="date" value={referenceDate} onChange={(event) => { setReferenceDate(event.target.value); invalidate(); }} /></label>
        <label>Annahmenotiz<input type="text" maxLength={160} value={note} onChange={(event) => { setNote(event.target.value); invalidate(); }} /></label>
      </div>

      <div className="capital-group">
        <h3>Modellbewertung je Sparte</h3>
        <div className="capital-table-wrap capital-adjustments"><table><thead><tr><th scope="col">Sparte</th><th scope="col">Aktiva-Änderung</th>
          <th scope="col">Verpflichtungs-Änderung</th></tr></thead><tbody>
          {SECTORS.map(({ id, label }, index) => <tr key={id}><th scope="row">{label}</th>
            <td><input aria-label={`${label} Aktiva-Änderung`} inputMode="decimal" value={adjustments[index].asset_delta}
              onChange={(event) => setAdjustment(index, "asset_delta", event.target.value)} /></td>
            <td><input aria-label={`${label} Verpflichtungs-Änderung`} inputMode="decimal" value={adjustments[index].liability_delta}
              onChange={(event) => setAdjustment(index, "liability_delta", event.target.value)} /></td></tr>)}
        </tbody></table></div>
      </div>

      <div className="capital-group">
        <h3>Teilpositionen und Stresssätze</h3>
        <div className="capital-table-wrap capital-exposures"><table><thead><tr><th scope="col">Position</th><th scope="col">Betrag</th>
          <th scope="col">Stresssatz 0–1</th></tr></thead><tbody>
          {EXPOSURES.map(({ id, label }, index) => <tr key={id}><th scope="row">{label}</th>
            <td><input aria-label={`${label} Teilbetrag`} inputMode="decimal" value={exposures[index].amount}
              onChange={(event) => setExposure(index, "amount", event.target.value)} /></td>
            <td><input aria-label={`${label} Stresssatz`} inputMode="decimal" value={exposures[index].rate}
              onChange={(event) => setExposure(index, "rate", event.target.value)} /></td></tr>)}
        </tbody></table></div>
      </div>

      <div className="capital-group">
        <h3>Aggregation und Workshop-Grenzen</h3>
        <div className="capital-fields">
          <label>Betriebsverlust<input inputMode="decimal" value={operationalLoss} onChange={(event) => { setOperationalLoss(decimal(event.target.value)); invalidate(); }} /></label>
          <label>Modellpuffer-Kapazität<input inputMode="decimal" value={bufferCapacity} onChange={(event) => { setBufferCapacity(decimal(event.target.value)); invalidate(); }} /></label>
          <label>Angerechneter Puffer<input inputMode="decimal" value={bufferApplied} onChange={(event) => { setBufferApplied(decimal(event.target.value)); invalidate(); }} /></label>
          <label>Maximaler Nettoverlust<input inputMode="decimal" value={maxLoss} onChange={(event) => { setMaxLoss(decimal(event.target.value)); invalidate(); }} /></label>
          <label>Minimaler Restproxy<input inputMode="decimal" value={minEquity} onChange={(event) => { setMinEquity(decimal(event.target.value)); invalidate(); }} /></label>
        </div>
        <details className="capital-factors"><summary>Faktorladungen für die Szenarioaggregation · {
          Object.values(factors).every((value) => value === "1") ? "alle 1" : "individuell"
        }</summary>
          <div className="capital-fields">{RISKS.map(({ id, label }) => <label key={id}>{label}
            <input inputMode="decimal" value={factors[id]} onChange={(event) => {
              setFactors((current) => ({ ...current, [id]: decimal(event.target.value) })); invalidate();
            }} /></label>)}</div></details>
      </div>

      <div className="capital-actions">
        <label className="capital-confirm"><input type="checkbox" checked={confirmed} disabled={!contracts || Boolean(busy)}
          onChange={(event) => { setConfirmed(event.target.checked); if (!event.target.checked) invalidate(); }} />
          <span>Diese Werte sind ausdrücklich deklarierte Modellannahmen, keine regulatorischen Parameter.</span></label>
        <button className="primary-action" type="button" disabled={!contracts || !confirmed || Boolean(busy)} onClick={calculate}>
          <Calculator size={17} aria-hidden="true" />{busy === "calculate" ? "Berechnet…" : "Kapitalwirkung berechnen"}</button>
      </div>
      {error && <p className="capital-error" role="alert">{error}</p>}

      {result && management && totals && <div className="capital-results" data-testid="capital-results">
        <div className="capital-results-head"><h3>Modellwirkung · Periode {period}</h3>
          <span title={result.readiness.content_digest ?? ""}>Nachweis {result.readiness.content_digest?.slice(0, 12)}</span></div>
        <div className="capital-summary" aria-label="Kapital-Modellwerte">
          <div><span>Eigenmittel-Proxy</span><strong>{display(management.model_own_funds_proxy)}</strong></div>
          <div><span>Brutto-Stress</span><strong>{display(totals.gross_model_stress_loss)}</strong></div>
          <div><span>Modellpuffer</span><strong>{display(totals.model_buffer_applied)}</strong></div>
          <div><span>Netto-Stress</span><strong>{display(management.net_model_stress_loss)}</strong></div>
          <div><span>Restproxy</span><strong>{display(management.remaining_model_equity_proxy)}</strong></div>
        </div>
        <p className="capital-unit">Alle Beträge in Modellwährung, nicht in EUR. Der Stress ist keine Bilanzbuchung.</p>
        <div className="capital-result-grid">
          <div><h4>Stresskomponenten</h4>
            <div className="capital-breakdown">{result.aggregation.component_rows.map((row) => <div key={row.risk_kind}>
              <span>{RISKS.find((item) => item.id === row.risk_kind)?.label ?? row.risk_kind}</span>
              <strong>{display(row.model_loss_amount)}</strong></div>)}</div></div>
          <div><h4>Managementgrenzen</h4>
            <div className="capital-breakdown">
              <div><span>Nettoverlust innerhalb Grenze</span><strong>{management.loss_limit_met ? "Ja" : "Nein"}</strong></div>
              <div><span>Restproxy oberhalb Grenze</span><strong>{management.equity_floor_met ? "Ja" : "Nein"}</strong></div>
              <div><span>Beide Workshop-Grenzen</span><strong>{management.both_limits_met ? "Ja" : "Nein"}</strong></div>
            </div></div>
        </div>
        <div className="capital-regulatory" data-testid="capital-regulatory">
          <h4>Regulatorische Kennzahlen · gesperrt</h4>
          <div className="capital-breakdown">{[
            ["Anrechenbare Eigenmittel", "eligible_own_funds"], ["SCR", "scr"], ["MCR", "mcr"],
            ["SCR-Bedeckungsquote", "scr_coverage_ratio"], ["MCR-Bedeckungsquote", "mcr_coverage_ratio"]
          ].map(([label, key]) => <div key={key}><span>{label}</span><strong>nicht berechnet</strong></div>)}</div>
          <details><summary>Fehlende Voraussetzungen ({result.readiness.readiness_rows.length})</summary>
            <ul>{result.readiness.readiness_rows.map((row) => <li key={row.requirement_code}>{row.message}</li>)}</ul>
          </details>
        </div>
        <div className="capital-downloads">
          <button type="button" onClick={downloadJson} disabled={Boolean(busy)}><Download size={17} aria-hidden="true" /> JSON</button>
          <button type="button" onClick={downloadXlsx} disabled={Boolean(busy)}><Download size={17} aria-hidden="true" /> XLSX</button>
        </div>
      </div>}
    </>}
  </section>;
}
