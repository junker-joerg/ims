import { useEffect, useRef, useState } from "react";
import { Calculator, CheckCircle2, CircleAlert, Landmark } from "lucide-react";
import type { CheckedFourSector, CheckedNonLife, CheckedSectorInput, CheckedSides, ScenarioSide } from "./fourSectorSources";

type SectorId = "motor" | "property_liability" | "life" | "health";
type ViewId = SectorId | "total";
type Issue = { path: string; code: string; message: string };
type BalanceRow = {
  period: number;
  opening_assets: string;
  opening_liabilities: string;
  opening_equity: string;
  period_profit: string;
  capital_contribution: string;
  capital_distribution: string;
  closing_assets: string;
  closing_liabilities: string;
  closing_equity: string;
};
type Result = {
  valid: boolean;
  insurer_id: number;
  scenario_id: string;
  variant_id: ScenarioSide;
  period_count: number;
  input_digest: string | null;
  content_digest: string | null;
  sectors: { sector_id: SectorId; rows: BalanceRow[] }[];
  total_rows: BalanceRow[];
  issues: Issue[];
};
type Contract = {
  input_schema_version: string;
  calculation_endpoint: string;
  supported_horizons: number[];
};
type Props = {
  nonLife: CheckedNonLife | null;
  life: CheckedSides | null;
  health: CheckedSides | null;
  onReady?: (value: CheckedFourSector | null) => void;
};

const SECTORS: { id: SectorId; label: string; anchor: string }[] = [
  { id: "motor", label: "Kfz", anchor: "balance" },
  { id: "property_liability", label: "Sach-Haftpflicht", anchor: "balance" },
  { id: "life", label: "Leben", anchor: "life" },
  { id: "health", label: "Kranken", anchor: "health" }
];
const COLUMNS: { key: keyof BalanceRow; label: string }[] = [
  { key: "opening_assets", label: "Vermögen Anfang" },
  { key: "closing_assets", label: "Vermögen Schluss" },
  { key: "closing_liabilities", label: "Verpflichtungen" },
  { key: "closing_equity", label: "Eigenkapital" },
  { key: "period_profit", label: "Ergebnis" },
  { key: "capital_contribution", label: "Kapitalzufuhr" },
  { key: "capital_distribution", label: "Ausschüttung" }
];

function amount(value: string): string {
  return value.replace(".", ",");
}

function sourceIssue(issue: Issue): string {
  const sector = SECTORS.find((item) => issue.path.startsWith(`$.sectors.${item.id}`));
  const period = issue.path.match(/(?:rows|periods)\[(\d+)\]/)?.[1];
  return `${sector?.label ?? "Gesamt"}${period === undefined ? "" : ` · Periode ${Number(period) + 1}`}: ${issue.message}`;
}

export default function FourSectorBalanceWorkbench({ nonLife, life, health, onReady }: Props) {
  const [contract, setContract] = useState<Contract | null>(null);
  const [contractError, setContractError] = useState<string | null>(null);
  const [side, setSide] = useState<ScenarioSide>("baseline");
  const [confirmed, setConfirmed] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const [view, setView] = useState<ViewId>("total");
  const [issues, setIssues] = useState<Issue[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const revision = useRef(0);

  useEffect(() => {
    let active = true;
    fetch("/api/accounting/four-sector-balance-contract")
      .then(async (response) => {
        if (!response.ok) throw new Error("Vertrag nicht erreichbar");
        return response.json() as Promise<Contract>;
      })
      .then((payload) => { if (active) setContract(payload); })
      .catch(() => { if (active) setContractError("Vier-Sparten-Dienst nicht erreichbar"); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    revision.current += 1;
    onReady?.(null);
    setResult(null);
    setIssues([]);
    setError(null);
    setConfirmed(false);
  }, [nonLife, life, health, side]);

  const selected: Record<SectorId, CheckedSectorInput | undefined> = {
    motor: nonLife?.motor,
    property_liability: nonLife?.property_liability,
    life: life?.[side],
    health: health?.[side]
  };
  const available = Object.values(selected).filter((item): item is CheckedSectorInput => item !== undefined);
  const missing = SECTORS.filter(({ id }) => !selected[id]);
  const insurerIds = new Set(available.map((item) => item.insurerId));
  const horizons = new Set(available.map((item) => item.periodCount));
  const matched = missing.length === 0 && insurerIds.size === 1 && horizons.size === 1;
  const periodCount = selected.health?.periodCount;
  const supported = periodCount !== undefined && contract?.supported_horizons.includes(periodCount);
  const ready = Boolean(matched && supported && selected.health?.variantId === side && selected.health?.scenarioId);
  const blockers: string[] = [];
  if (missing.length) blockers.push(`Noch nicht geprüft: ${missing.map((item) => item.label).join(", ")}.`);
  if (insurerIds.size > 1) blockers.push("Die Teilrechnungen haben verschiedene Versicherer-IDs.");
  if (horizons.size > 1) blockers.push("Die Teilrechnungen haben verschiedene Periodenzahlen.");
  if (matched && !supported && contract) blockers.push("Dieser gemeinsame Horizont ist nicht freigegeben.");

  async function calculate() {
    if (!contract || !ready || !confirmed || busy) return;
    const currentRevision = revision.current;
    setBusy(true);
    onReady?.(null);
    setResult(null);
    setIssues([]);
    setError(null);
    try {
      const payload = {
        schema_version: contract.input_schema_version,
        insurer_id: selected.motor!.insurerId,
        scenario_id: selected.health!.scenarioId,
        variant_id: side,
        sectors: {
          motor: selected.motor!.input,
          property_liability: selected.property_liability!.input,
          life: selected.life!.input,
          health: selected.health!.input
        }
      };
      const response = await fetch(contract.calculation_endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const report = await response.json() as Result;
      if (currentRevision !== revision.current) return;
      if (!response.ok || !report.valid || !report.content_digest) {
        setIssues(report.issues ?? []);
        if (!report.issues?.length) setError("Die Gesamtbilanz konnte nicht berechnet werden.");
        return;
      }
      if (response.headers.get("etag") !== `"${report.content_digest}"`) {
        throw new Error("Der Ergebnisnachweis stimmt nicht mit der Bilanz überein.");
      }
      if (report.insurer_id !== selected.motor!.insurerId ||
          report.scenario_id !== selected.health!.scenarioId ||
          report.variant_id !== side || report.period_count !== periodCount ||
          report.sectors.length !== SECTORS.length ||
          report.sectors.some((sector, index) => sector.sector_id !== SECTORS[index].id)) {
        throw new Error("Die Antwort gehört nicht zu den ausgewählten Sparten und Perioden.");
      }
      setResult(report);
      onReady?.({
        input: payload, evidenceDigest: report.content_digest,
        insurerId: report.insurer_id, scenarioId: report.scenario_id,
        variantId: report.variant_id, periodCount: report.period_count
      });
      setView("total");
    } catch (cause) {
      if (currentRevision === revision.current) {
        setError(cause instanceof Error ? cause.message : "Vier-Sparten-Dienst nicht erreichbar");
      }
    } finally {
      setBusy(false);
    }
  }

  const rows = result ? (view === "total"
    ? result.total_rows
    : result.sectors.find((sector) => sector.sector_id === view)?.rows ?? []) : [];
  const last = rows.at(-1);

  return (
    <section className="panel four-sector-workbench" id="four-sector-balance" data-testid="four-sector-workbench">
      <div className="four-sector-heading">
        <div className="panel-heading"><Landmark size={20} aria-hidden="true" /><h2>Vier-Sparten-Gesamtbilanz</h2></div>
        <span>IMS 2.x · einfache Modellbilanz</span>
      </div>

      <div className="four-sector-mode" role="group" aria-label="Szenariovariante">
        {(["baseline", "variant"] as ScenarioSide[]).map((item) => <button key={item} type="button"
          className={side === item ? "active" : ""} aria-pressed={side === item}
          onClick={() => {
            revision.current += 1;
            onReady?.(null);
            setResult(null);
            setConfirmed(false);
            setIssues([]);
            setError(null);
            setSide(item);
          }}>{item === "baseline" ? "Baseline" : "Variante"}</button>)}
      </div>

      <div className="four-sector-sources" aria-label="Geprüfte Spartenquellen">
        {SECTORS.map(({ id, label, anchor }) => {
          const source = selected[id];
          return <div className="four-sector-source" key={id}>
            {source ? <CheckCircle2 size={17} aria-hidden="true" className="four-sector-ready-icon" />
              : <CircleAlert size={17} aria-hidden="true" className="four-sector-open-icon" />}
            <strong>{label}</strong>
            <span>{source ? `VU ${source.insurerId} · ${source.periodCount} Perioden geprüft` : "Vorschau offen"}</span>
            <a href={`#${anchor}`}>{source ? "Prüfung ansehen" : "Zur Eingabe"}</a>
          </div>;
        })}
      </div>

      {blockers.length > 0 && <div className="four-sector-blockers" role="status">
        {blockers.map((message) => <p key={message}>{message}</p>)}
      </div>}
      {contractError && <p className="four-sector-error" role="alert">{contractError}</p>}
      <div className="four-sector-actions">
        <label className="four-sector-confirm"><input type="checkbox" checked={confirmed} disabled={!ready || busy}
          onChange={(event) => {
            setConfirmed(event.target.checked);
            if (!event.target.checked) {
              onReady?.(null);
              setResult(null);
            }
          }} />
          <span>Die vier Eingaben gehören fachlich zu {selected.health?.scenarioId ?? "diesem Szenario"}</span></label>
        <button className="primary-action" type="button" onClick={calculate}
          disabled={!contract || !ready || !confirmed || busy}>
          <Calculator size={17} aria-hidden="true" />{busy ? "Berechnet…" : "Gesamtbilanz berechnen"}
        </button>
      </div>
      {error && <p className="four-sector-error" role="alert">{error}</p>}
      {issues.length > 0 && <div className="four-sector-issues" role="alert">
        {issues.slice(0, 8).map((issue, index) => <p key={`${issue.path}-${index}`}>{sourceIssue(issue)}</p>)}
      </div>}

      {result && <div className="four-sector-results" data-testid="four-sector-results">
        <div className="four-sector-results-head">
          <div><h3>Bilanz je Versicherer</h3>
            <span>VU {result.insurer_id} · {result.scenario_id} · {result.variant_id === "baseline" ? "Baseline" : "Variante"} · {result.period_count} Perioden</span></div>
          <span className="four-sector-digest" title={result.content_digest ?? ""}>Nachweis {result.content_digest?.slice(0, 12)}</span>
        </div>
        <div className="four-sector-views" role="group" aria-label="Bilanzebene">
          {([{ id: "total", label: "Gesamt" }, ...SECTORS] as { id: ViewId; label: string }[]).map((item) =>
            <button key={item.id} type="button" className={view === item.id ? "active" : ""}
              aria-pressed={view === item.id} onClick={() => setView(item.id)}>{item.label}</button>)}
        </div>
        {last && <div className="four-sector-summary" aria-label="Schlussbilanz">
          <div><span>Vermögen</span><strong>{amount(last.closing_assets)}</strong></div>
          <div><span>Verpflichtungen</span><strong>{amount(last.closing_liabilities)}</strong></div>
          <div><span>Eigenkapital</span><strong>{amount(last.closing_equity)}</strong></div>
          <div><span>Periodenergebnis</span><strong>{amount(last.period_profit)}</strong></div>
        </div>}
        <div className="four-sector-table-wrap" role="region" aria-label="Vier-Sparten-Bilanz-Zeitreihe" tabIndex={0}>
          <table><thead><tr><th scope="col">Per.</th>{COLUMNS.map(({ key, label }) =>
            <th scope="col" key={key}>{label}</th>)}</tr></thead>
            <tbody>{rows.map((row) => <tr key={row.period}><th scope="row">{row.period}</th>
              {COLUMNS.map(({ key }) => <td key={key}>{amount(String(row[key]))}</td>)}</tr>)}</tbody>
          </table>
        </div>
        <p className="four-sector-provenance">Vermögen = Verpflichtungen + Eigenkapital. Dieselben Schaden-Eingaben gelten für beide Varianten; alle vier Sparten wurden serverseitig neu berechnet. Keine gesetzliche Bilanz oder historische Vollgleichheit.</p>
      </div>}
    </section>
  );
}
