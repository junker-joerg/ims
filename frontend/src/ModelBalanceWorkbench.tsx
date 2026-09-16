import { useEffect, useState } from "react";
import { Calculator, Download, Landmark, Plus, Trash2 } from "lucide-react";

type SectorId = "motor" | "property_liability";
type ViewId = SectorId | "total";
type OpeningKey = "opening_cash" | "opening_claim_liability" | "opening_equity";
type FlowKey =
  | "premium_income" | "investment_income" | "claims_incurred" | "claims_paid"
  | "operating_expense" | "capital_contribution" | "capital_distribution";
type Opening = Record<OpeningKey, string>;
type Flow = { period: number } & Record<FlowKey, string>;
type SectorDraft = { opening: Opening; periods: Flow[] };
type Contract = {
  input_schema_version: string;
  sector_input_schema_version: string;
  model_balance_contract_schema_version: string;
  sector_taxonomy_schema_version: string;
  calculation_endpoint: string;
  xlsx_endpoint: string;
};
type Issue = { path: string; code: string; message: string };
type BalanceRow = { period: number } & Record<string, string | number>;
type Result = {
  valid: boolean;
  insurer_id: number;
  period_count: number;
  content_digest: string;
  total_rows: BalanceRow[];
  sectors: { sector_id: SectorId; rows: BalanceRow[] }[];
  issues: Issue[];
};

const SECTORS: { id: SectorId; label: string }[] = [
  { id: "motor", label: "Kfz" },
  { id: "property_liability", label: "Sach-Haftpflicht" }
];
const OPENING_FIELDS: { key: OpeningKey; label: string }[] = [
  { key: "opening_cash", label: "Cash" },
  { key: "opening_claim_liability", label: "Schadenverbindlichkeit" },
  { key: "opening_equity", label: "Eigenkapital" }
];
const FLOW_FIELDS: { key: FlowKey; label: string; short: string }[] = [
  { key: "premium_income", label: "Prämieneinnahme", short: "Prämien" },
  { key: "investment_income", label: "Zinsertrag", short: "Zins" },
  { key: "claims_incurred", label: "Angefallene Schäden", short: "Schäden" },
  { key: "claims_paid", label: "Bezahlte Schäden", short: "Bezahlt" },
  { key: "operating_expense", label: "Laufender Aufwand", short: "Aufwand" },
  { key: "capital_contribution", label: "Kapitalzuführung", short: "Zuführung" },
  { key: "capital_distribution", label: "Kapitalausschüttung", short: "Ausschüttung" }
];
const RESULT_COLUMNS = [
  ["premium_income", "Prämien"], ["claims_incurred", "Schäden"],
  ["claims_paid", "Bezahlt"], ["period_profit", "Ergebnis"],
  ["closing_cash", "Cash"], ["closing_claim_liability", "Schuld"],
  ["closing_equity", "Eigenkapital"]
] as const;

function flow(period: number, values: Partial<Record<FlowKey, string>> = {}): Flow {
  return {
    period,
    premium_income: values.premium_income ?? "0",
    investment_income: values.investment_income ?? "0",
    claims_incurred: values.claims_incurred ?? "0",
    claims_paid: values.claims_paid ?? "0",
    operating_expense: values.operating_expense ?? "0",
    capital_contribution: values.capital_contribution ?? "0",
    capital_distribution: values.capital_distribution ?? "0"
  };
}

function initialDrafts(): Record<SectorId, SectorDraft> {
  return {
    motor: {
      opening: { opening_cash: "100", opening_claim_liability: "30", opening_equity: "70" },
      periods: [
        flow(1, { premium_income: "20", investment_income: "2", claims_incurred: "8",
          claims_paid: "5", operating_expense: "3", capital_contribution: "4", capital_distribution: "1" }),
        flow(2, { premium_income: "12", investment_income: "-1", claims_incurred: "6",
          claims_paid: "10", operating_expense: "2" })
      ]
    },
    property_liability: {
      opening: { opening_cash: "50", opening_claim_liability: "10", opening_equity: "40" },
      periods: [
        flow(1, { premium_income: "10", investment_income: "1", claims_incurred: "3",
          claims_paid: "2", operating_expense: "2" }),
        flow(2, { premium_income: "8", claims_incurred: "4", claims_paid: "3", operating_expense: "1" })
      ]
    }
  };
}

function requestBody(contract: Contract, insurerId: number, drafts: Record<SectorId, SectorDraft>) {
  return {
    schema_version: contract.input_schema_version,
    insurer_id: insurerId,
    sectors: SECTORS.map(({ id }) => ({
      schema_version: contract.sector_input_schema_version,
      model_balance_contract_schema_version: contract.model_balance_contract_schema_version,
      sector_taxonomy_schema_version: contract.sector_taxonomy_schema_version,
      source_kind: "explicit_scenario",
      historical_mapping_status: "unresolved",
      insurer_id: insurerId,
      sector_id: id,
      opening: drafts[id].opening,
      periods: drafts[id].periods
    }))
  };
}

function issueLocation(issue: Issue): string {
  const sectorIndex = issue.path.match(/sectors\[(\d+)\]/)?.[1];
  const periodIndex = issue.path.match(/periods\[(\d+)\]/)?.[1];
  const field = issue.path.split(".").at(-1) ?? "";
  const label = [...OPENING_FIELDS, ...FLOW_FIELDS].find((item) => item.key === field)?.label;
  return [
    sectorIndex === undefined ? "Gesamt" : SECTORS[Number(sectorIndex)]?.label ?? "Sparte",
    periodIndex === undefined ? null : `Periode ${Number(periodIndex) + 1}`,
    label ?? null
  ].filter(Boolean).join(" · ");
}

function displayAmount(value: string | number): string {
  return String(value).replace(".", ",");
}

export default function ModelBalanceWorkbench() {
  const [contract, setContract] = useState<Contract | null>(null);
  const [contractError, setContractError] = useState<string | null>(null);
  const [insurerId, setInsurerId] = useState(1);
  const [drafts, setDrafts] = useState<Record<SectorId, SectorDraft>>(initialDrafts);
  const [activeSector, setActiveSector] = useState<SectorId>("motor");
  const [view, setView] = useState<ViewId>("total");
  const [result, setResult] = useState<Result | null>(null);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [actionError, setActionError] = useState<string | null>(null);
  const [busy, setBusy] = useState<"calculate" | "download" | null>(null);
  const [edited, setEdited] = useState(false);

  useEffect(() => {
    let active = true;
    fetch("/api/accounting/insurer-balance-contract")
      .then(async (response) => {
        if (!response.ok) throw new Error("Bilanzvertrag nicht erreichbar");
        return response.json() as Promise<Contract>;
      })
      .then((payload) => { if (active) setContract(payload); })
      .catch(() => { if (active) setContractError("Bilanzdienst nicht erreichbar"); });
    return () => { active = false; };
  }, []);

  function invalidate() {
    setEdited(true);
    setResult(null);
    setIssues([]);
    setActionError(null);
  }

  function setOpening(key: OpeningKey, value: string) {
    setDrafts((current) => ({
      ...current,
      [activeSector]: {
        ...current[activeSector],
        opening: { ...current[activeSector].opening, [key]: value }
      }
    }));
    invalidate();
  }

  function setPeriodValue(index: number, key: FlowKey, value: string) {
    setDrafts((current) => ({
      ...current,
      [activeSector]: {
        ...current[activeSector],
        periods: current[activeSector].periods.map((item, position) => (
          position === index ? { ...item, [key]: value } : item
        ))
      }
    }));
    invalidate();
  }

  function addPeriod() {
    if (drafts.motor.periods.length >= 100) return;
    setDrafts((current) => {
      const next = { ...current };
      for (const { id } of SECTORS) {
        const previous = current[id].periods.at(-1)!;
        next[id] = { ...current[id], periods: [...current[id].periods, flow(previous.period + 1)] };
      }
      return next;
    });
    invalidate();
  }

  function removePeriod() {
    if (drafts.motor.periods.length <= 1) return;
    setDrafts((current) => ({
      motor: { ...current.motor, periods: current.motor.periods.slice(0, -1) },
      property_liability: { ...current.property_liability, periods: current.property_liability.periods.slice(0, -1) }
    }));
    invalidate();
  }

  async function calculate() {
    if (!contract || busy) return;
    setBusy("calculate");
    setResult(null);
    setIssues([]);
    setActionError(null);
    try {
      const response = await fetch(contract.calculation_endpoint, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody(contract, insurerId, drafts))
      });
      const payload = await response.json() as Result;
      if (!response.ok || !payload.valid || !payload.content_digest) {
        setIssues(payload.issues ?? []);
        if (!payload.issues?.length) setActionError("Bilanz konnte nicht berechnet werden");
        return;
      }
      if (response.headers.get("etag") !== `"${payload.content_digest}"`) {
        throw new Error("Ergebnisnachweis stimmt nicht überein");
      }
      setResult(payload);
      setView("total");
    } catch (error) {
      setActionError(error instanceof Error ? error.message : "Bilanzdienst nicht erreichbar");
    } finally {
      setBusy(null);
    }
  }

  async function download() {
    if (!contract || !result || busy) return;
    setBusy("download");
    setActionError(null);
    try {
      const response = await fetch(contract.xlsx_endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", "If-Match": `"${result.content_digest}"` },
        body: JSON.stringify(requestBody(contract, insurerId, drafts))
      });
      if (!response.ok) throw new Error("XLSX-Download konnte nicht erstellt werden");
      if (response.headers.get("etag") !== `"${result.content_digest}"` ||
          !response.headers.get("content-type")?.includes("spreadsheetml.sheet")) {
        throw new Error("Download stimmt nicht mit der angezeigten Bilanz überein");
      }
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = `ims-modellbilanz-vu-${insurerId}.xlsx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (error) {
      setActionError(error instanceof Error ? error.message : "XLSX-Download nicht erreichbar");
    } finally {
      setBusy(null);
    }
  }

  const selectedRows = result ? (
    view === "total" ? result.total_rows : result.sectors.find((item) => item.sector_id === view)?.rows ?? []
  ) : [];
  const last = selectedRows.at(-1);
  const periodCount = drafts.motor.periods.length;

  return (
    <section className="panel balance-panel" id="balance" data-testid="model-balance-workbench">
      <div className="balance-heading">
        <div className="panel-heading"><Landmark size={20} aria-hidden="true" /><h2>Versicherer-Modellbilanz</h2></div>
        <div className="balance-provenance" aria-label="Herkunft"><span>Quelle: {edited ? "eigene Szenariowerte" : "Beispielwerte"}</span><span>Historische Zuordnung: offen</span></div>
      </div>

      <div className="balance-controls">
        <label className="balance-insurer"><span>Versicherer-ID</span><input type="number" min="1" max="25" value={insurerId} disabled={busy !== null}
          onChange={(event) => { setInsurerId(Number(event.target.value)); invalidate(); }} /></label>
        <div className="balance-period-actions" aria-label="Periodenanzahl">
          <span>{periodCount} {periodCount === 1 ? "Periode" : "Perioden"}</span>
          <button className="secondary-action" type="button" onClick={removePeriod} disabled={periodCount <= 1 || busy !== null} title="Letzte Periode entfernen" aria-label="Letzte Periode entfernen"><Trash2 size={16} aria-hidden="true" /></button>
          <button className="secondary-action" type="button" onClick={addPeriod} disabled={periodCount >= 100 || busy !== null} title="Periode ergänzen" aria-label="Periode ergänzen"><Plus size={16} aria-hidden="true" /></button>
        </div>
        <div className="balance-sector-tabs" role="group" aria-label="Sparte bearbeiten">
          {SECTORS.map((sector) => <button key={sector.id} type="button" className={activeSector === sector.id ? "active" : ""}
            onClick={() => setActiveSector(sector.id)} aria-pressed={activeSector === sector.id}>{sector.label}</button>)}
        </div>
      </div>

      <div className="balance-opening" aria-label={`Anfangsbestände ${SECTORS.find((item) => item.id === activeSector)?.label}`}>
        {OPENING_FIELDS.map(({ key, label }) => <label key={key}><span>{label} Anfang</span><input type="text" inputMode="decimal"
          value={drafts[activeSector].opening[key]} onChange={(event) => setOpening(key, event.target.value)} disabled={busy !== null} /></label>)}
      </div>

      <div className="balance-period-editor" role="region" aria-label={`Periodenwerte ${SECTORS.find((item) => item.id === activeSector)?.label}`} tabIndex={0}>
        <div className="balance-period-head"><span>Per.</span>{FLOW_FIELDS.map((field) => <span key={field.key} title={field.label}>{field.short}</span>)}</div>
        {drafts[activeSector].periods.map((period, index) => <div className="balance-period-row" key={period.period}>
          <strong>{period.period}</strong>
          {FLOW_FIELDS.map(({ key, label }) => <label key={key}><span>{label}</span><input type="text" inputMode="decimal"
            aria-label={`${label}, ${SECTORS.find((item) => item.id === activeSector)?.label}, Periode ${period.period}`}
            value={period[key]} onChange={(event) => setPeriodValue(index, key, event.target.value)} disabled={busy !== null} /></label>)}
        </div>)}
      </div>

      <div className="balance-actions">
        <button className="primary-action" type="button" onClick={calculate} disabled={!contract || busy !== null}>
          <Calculator size={17} aria-hidden="true" />{busy === "calculate" ? "Berechnet..." : "Bilanz berechnen"}
        </button>
        <button className="secondary-action" type="button" onClick={download} disabled={!result || busy !== null}>
          <Download size={17} aria-hidden="true" />XLSX
        </button>
      </div>
      {contractError && <p className="balance-error" role="alert">{contractError}</p>}
      {actionError && <p className="balance-error" role="alert">{actionError}</p>}
      {issues.length > 0 && <div className="balance-issues" role="alert">{issues.slice(0, 8).map((issue, index) =>
        <div key={`${issue.path}-${index}`}><strong>{issueLocation(issue)}</strong><span>{issue.message}</span></div>)}</div>}

      {result && <div className="balance-results" data-testid="model-balance-results">
        <div className="balance-result-head">
          <div className="balance-view-tabs" role="group" aria-label="Bilanzansicht">
            {([{ id: "total", label: "Gesamt" }, ...SECTORS] as { id: ViewId; label: string }[]).map((item) =>
              <button key={item.id} type="button" className={view === item.id ? "active" : ""}
                aria-pressed={view === item.id} onClick={() => setView(item.id)}>{item.label}</button>)}
          </div>
          <span>VU {result.insurer_id} · {result.period_count} {result.period_count === 1 ? "Periode" : "Perioden"}</span>
        </div>
        {last && <div className="balance-summary" aria-label="Schlussbilanz">
          {([
            ["Cash", last.closing_cash], ["Offene Schäden", last.closing_claim_liability],
            ["Eigenkapital", last.closing_equity], ["Periodenergebnis", last.period_profit]
          ] as [string, string | number][]).map(([label, value]) =>
            <div key={label}><span>{label}</span><strong>{displayAmount(value)}</strong></div>)}
        </div>}
        <div className="balance-table-wrap" role="region" aria-label="Bilanz-Zeitreihe" tabIndex={0}>
          <table className="balance-table"><thead><tr><th>Per.</th>{RESULT_COLUMNS.map(([key, label]) => <th key={key}>{label}</th>)}</tr></thead>
            <tbody>{selectedRows.map((row) => <tr key={row.period}><th scope="row">{row.period}</th>
              {RESULT_COLUMNS.map(([key]) => <td key={key}>{displayAmount(row[key])}</td>)}</tr>)}</tbody>
          </table>
        </div>
      </div>}
    </section>
  );
}
