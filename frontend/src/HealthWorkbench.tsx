import { useEffect, useState } from "react";
import { Activity, Calculator, Download, RefreshCw, Save } from "lucide-react";
import {
  buildHealthInput, defaultHealthDraft, HEALTH_HORIZONS,
  type HealthDraft, type HealthSide
} from "./healthScenario";

type Issue = { path: string; code: string; message: string };
type Row = { period: number } & Record<string, string | number>;
type Report = {
  valid: boolean; insurer_id: number; scenario_id: string; variant_id: HealthSide;
  calculated_period_count: number; rows: Row[]; issues: Issue[];
};
type Preview = { valid: boolean; input_digest: string; result_digest: string; report: Report };
type Stored = {
  result_id: string; input_digest: string; result_digest: string; stored_at: string;
  report: Report; stored_result_verified: boolean;
};
type History = {
  result_id: string; insurer_id: number; scenario_id: string; variant_id: HealthSide;
  period_count: number; stored_at: string; result_digest: string;
};
type Metric = { key: string; label: string };

const BASE = "/api/accounting/health-period-chain";
const METRICS: Metric[] = [
  { key: "closing_active_policies", label: "Aktive Verträge" },
  { key: "premiums_collected", label: "Beiträge" },
  { key: "benefits_incurred", label: "Leistungsanfall" },
  { key: "benefits_paid", label: "Auszahlungen" },
  { key: "closing_cash", label: "Kasse" },
  { key: "closing_benefit_liability", label: "Offene Leistungen" },
  { key: "closing_equity", label: "Eigenkapital" },
  { key: "period_profit", label: "Periodenergebnis" }
];
const BASE_AMOUNTS: { key: keyof HealthDraft; label: string }[] = [
  { key: "premiumPerPolicy", label: "Beitrag je aktivem Vertrag" },
  { key: "benefitPerPolicy", label: "Leistungsanfall je Vertrag" },
  { key: "benefitsPaid", label: "Auszahlung je Periode" },
  { key: "investmentResult", label: "Anlageergebnis je Periode" },
  { key: "operatingExpensePaid", label: "Betriebsaufwand je Periode" },
  { key: "capitalContribution", label: "Kapitalzufuhr je Periode" },
  { key: "capitalDistribution", label: "Kapitalausschüttung je Periode" }
];
const VARIANT_AMOUNTS: { key: keyof HealthDraft; label: string }[] = [
  { key: "variantPremiumPerPolicy", label: "Beitrag je aktivem Vertrag" },
  { key: "variantBenefitPerPolicy", label: "Leistungsanfall je Vertrag" },
  { key: "variantBenefitsPaid", label: "Auszahlung je Periode" }
];

function valueText(value: string | number | undefined): string {
  return value === undefined ? "–" : String(value).replace(".", ",");
}

function issueText(issue: Issue): string {
  const match = issue.path.match(/periods\[(\d+)\]/);
  return `${match ? `Periode ${Number(match[1]) + 1}` : "Eingabe"}: ${issue.message}`;
}

function apiError(response: Response, body: { code?: string }): string {
  if (response.status === 422) return "Bitte die Eingaben und die Bilanzgrenzen prüfen.";
  if (response.status === 503) return "Die Ergebnisablage ist in dieser Installation nicht eingerichtet.";
  if (response.status === 504) return "Die Berechnung hat das Zeitbudget überschritten.";
  if (response.status === 429) return "Eine Krankenrechnung läuft bereits. Bitte kurz warten.";
  if (response.status === 409 || response.status === 428) return "Der geprüfte Ergebnisstand passt nicht mehr. Bitte erneut laden.";
  return body.code ? `Anfrage nicht möglich: ${body.code}` : "Der Krankendienst ist nicht erreichbar.";
}

function linePath(rows: Row[], key: string, minimum: number, maximum: number): string {
  const span = maximum - minimum || 1;
  return rows.map((row, index) => {
    const x = 30 + index * (740 / Math.max(1, rows.length - 1));
    const y = 160 - ((Number(row[key]) - minimum) / span) * 124;
    return `${index ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`;
  }).join(" ");
}

export default function HealthWorkbench() {
  const [draft, setDraft] = useState<HealthDraft>(defaultHealthDraft);
  const [previews, setPreviews] = useState<Record<HealthSide, Preview | null>>({ baseline: null, variant: null });
  const [keys, setKeys] = useState<Record<HealthSide, string>>({ baseline: crypto.randomUUID(), variant: crypto.randomUUID() });
  const [selectedSide, setSelectedSide] = useState<HealthSide>("variant");
  const [metric, setMetric] = useState("closing_equity");
  const [view, setView] = useState<"compare" | "stored">("compare");
  const [busy, setBusy] = useState<"preview" | "store" | "download" | "history" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [confirmed, setConfirmed] = useState(false);
  const [stored, setStored] = useState<Stored | null>(null);
  const [history, setHistory] = useState<History[]>([]);
  const [historyReady, setHistoryReady] = useState(false);
  const [storageError, setStorageError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    fetch(`${BASE}/results`).then(async (response) => {
      if (!response.ok) throw new Error(apiError(response, await response.json()));
      return response.json() as Promise<{ results: History[] }>;
    }).then((payload) => {
      if (active) { setHistory(payload.results); setHistoryReady(true); setStorageError(null); }
    }).catch((cause) => {
      if (active) setStorageError(cause instanceof Error ? cause.message : "Verlauf nicht erreichbar.");
    });
    return () => { active = false; };
  }, []);

  function edit<K extends keyof HealthDraft>(key: K, value: HealthDraft[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
    setPreviews({ baseline: null, variant: null });
    setKeys({ baseline: crypto.randomUUID(), variant: crypto.randomUUID() });
    setStored(null);
    setView("compare");
    setConfirmed(false);
    setIssues([]);
    setError(null);
  }

  function horizon(value: number) {
    setDraft((current) => ({ ...current, periodCount: value }));
    setPreviews({ baseline: null, variant: null });
    setKeys({ baseline: crypto.randomUUID(), variant: crypto.randomUUID() });
    setStored(null);
    setView("compare");
    setConfirmed(false);
    setIssues([]);
    setError(null);
  }

  async function calculate() {
    if (busy) return;
    if (!Number.isInteger(draft.variantStartPeriod) || draft.variantStartPeriod < 1 || draft.variantStartPeriod > 100) {
      setError("Der Variantenbeginn muss zwischen Periode 1 und 100 liegen.");
      setPreviews({ baseline: null, variant: null });
      return;
    }
    setBusy("preview");
    setError(null);
    setIssues([]);
    setPreviews({ baseline: null, variant: null });
    setView("compare");
    try {
      const next: Record<HealthSide, Preview | null> = { baseline: null, variant: null };
      for (const side of ["baseline", "variant"] as HealthSide[]) {
        const response = await fetch(`${BASE}/preview`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify(buildHealthInput(draft, side))
        });
        const payload = await response.json() as Preview & Report & { code?: string };
        if (!response.ok || !payload.valid) {
          setIssues(payload.issues ?? []);
          setError(`${side === "baseline" ? "Baseline" : "Variante"}: ${apiError(response, payload)}`);
          return;
        }
        next[side] = payload;
      }
      setPreviews(next);
    } catch {
      setError("Der Krankendienst ist nicht erreichbar.");
    } finally {
      setBusy(null);
    }
  }

  async function refreshHistory() {
    setBusy("history");
    try {
      const response = await fetch(`${BASE}/results`);
      if (!response.ok) throw new Error(apiError(response, await response.json()));
      const payload = await response.json() as { results: History[] };
      setHistory(payload.results);
      setHistoryReady(true);
      setStorageError(null);
    } catch (cause) {
      setHistoryReady(false);
      setConfirmed(false);
      setStorageError(cause instanceof Error ? cause.message : "Verlauf nicht erreichbar.");
    } finally {
      setBusy(null);
    }
  }

  async function store() {
    const preview = previews[selectedSide];
    if (!preview || !confirmed || !historyReady || busy || view !== "compare") return;
    setBusy("store");
    setError(null);
    try {
      const response = await fetch(`${BASE}/start`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          schema_version: "ims.health-result-start.v1",
          health_chain_input: buildHealthInput(draft, selectedSide),
          expected_input_digest: preview.input_digest,
          expected_result_digest: preview.result_digest,
          idempotency_key: keys[selectedSide],
          explicit_storage_release: true
        })
      });
      const payload = await response.json() as Stored & { code?: string };
      if (!response.ok) throw new Error(apiError(response, payload));
      if (payload.input_digest !== preview.input_digest || payload.result_digest !== preview.result_digest || !payload.stored_result_verified) {
        throw new Error("Gespeichertes Ergebnis stimmt nicht mit der Vorschau überein.");
      }
      setStored(payload);
      setView("stored");
      setConfirmed(false);
      try {
        const latest = await fetch(`${BASE}/results`);
        if (!latest.ok) throw new Error(apiError(latest, await latest.json()));
        setHistory((await latest.json() as { results: History[] }).results);
        setHistoryReady(true);
        setStorageError(null);
      } catch {
        setHistoryReady(false);
        setStorageError("Der Fall ist gespeichert, aber der Verlauf konnte nicht neu geladen werden.");
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Speichern nicht möglich.");
    } finally {
      setBusy(null);
    }
  }

  async function selectHistory(resultId: string) {
    if (busy) return;
    setBusy("history");
    setError(null);
    setStored(null);
    setView("compare");
    try {
      const response = await fetch(`${BASE}/result/${encodeURIComponent(resultId)}`);
      const payload = await response.json() as Stored & { code?: string };
      if (!response.ok) throw new Error(apiError(response, payload));
      if (!payload.stored_result_verified) throw new Error("Gespeichertes Ergebnis nicht verifiziert.");
      setStored(payload);
      setView("stored");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Gespeichertes Ergebnis nicht erreichbar.");
    } finally {
      setBusy(null);
    }
  }

  async function download(format: "csv" | "json" | "xlsx") {
    if (!stored || busy) return;
    setBusy("download");
    setError(null);
    try {
      const etag = `"${stored.result_digest}"`;
      const response = await fetch(`${BASE}/result/${encodeURIComponent(stored.result_id)}.${format}`, {
        headers: { "If-Match": etag }
      });
      if (!response.ok) throw new Error(apiError(response, await response.json()));
      if (response.headers.get("etag") !== etag) throw new Error("Der Download gehört nicht zum ausgewählten Ergebnis.");
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = `ims-kranken-${stored.result_id}.${format}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Download nicht möglich.");
    } finally {
      setBusy(null);
    }
  }

  const comparisonReady = previews.baseline !== null && previews.variant !== null;
  const baselineRows = view === "compare" ? previews.baseline?.report.rows ?? [] : [];
  const variantRows = view === "compare" ? previews.variant?.report.rows ?? [] : stored?.report.rows ?? [];
  const values = [...baselineRows, ...variantRows].map((row) => Number(row[metric]));
  const minimum = values.length ? Math.min(0, ...values) : 0;
  const maximum = values.length ? Math.max(1, ...values) : 1;
  const showResults = view === "stored" ? stored !== null : comparisonReady;
  const shownCount = view === "stored" ? stored?.report.calculated_period_count : draft.periodCount;

  return (
    <section className="panel health-workbench" id="health" data-testid="health-workbench">
      <div className="health-heading">
        <div className="panel-heading"><Activity size={20} aria-hidden="true" /><h2>Kranken im Seminar</h2></div>
        <span>IMS 2.x · explizite Modellannahmen · keine historische Krankenreferenz</span>
      </div>

      <div className="health-top-controls">
        <label><span>Versicherer</span><input type="number" min="1" max="25" value={draft.insurerId} disabled={busy !== null}
          onChange={(event) => edit("insurerId", Number(event.target.value))} /></label>
        <label><span>Szenario</span><input type="text" maxLength={40} value={draft.scenarioId} disabled={busy !== null}
          onChange={(event) => edit("scenarioId", event.target.value)} /></label>
        <label><span>Perioden</span><select value={draft.periodCount} disabled={busy !== null}
          onChange={(event) => horizon(Number(event.target.value))}>
          {HEALTH_HORIZONS.map((count) => <option key={count} value={count}>{count}</option>)}
        </select></label>
      </div>

      <div className="health-opening">
        <h3>Anfangsbestand</h3>
        <div className="health-fields">
          <label><span>Aktive Verträge</span><input type="number" min="0" max="1000000000" value={draft.openingActivePolicies}
            disabled={busy !== null} onChange={(event) => edit("openingActivePolicies", Number(event.target.value))} /></label>
          {([[
            "openingCash", "Kasse"
          ], ["openingLiability", "Offene Leistungen"], ["openingEquity", "Eigenkapital"]] as const).map(([key, label]) =>
            <label key={key}><span>{label}</span><input type="text" inputMode="decimal" value={draft[key]} disabled={busy !== null}
              onChange={(event) => edit(key, event.target.value)} /></label>)}
        </div>
      </div>

      <div className="health-editor-layout">
        <section className="health-editor-block" aria-label="Baseline-Annahmen">
          <h3>Baseline</h3>
          <div className="health-fields">
            <label><span>Neugeschäft je Periode</span><input type="number" min="0" max="1000000000" value={draft.newBusinessPerPeriod}
              disabled={busy !== null} onChange={(event) => edit("newBusinessPerPeriod", Number(event.target.value))} /></label>
            <label><span>Abgang je Periode</span><input type="number" min="0" max="1000000000" value={draft.exitsPerPeriod}
              disabled={busy !== null} onChange={(event) => edit("exitsPerPeriod", Number(event.target.value))} /></label>
            {BASE_AMOUNTS.map(({ key, label }) => <label key={key}><span>{label}</span>
              <input type="text" inputMode="decimal" value={String(draft[key])} disabled={busy !== null}
                onChange={(event) => edit(key, event.target.value)} /></label>)}
          </div>
        </section>
        <section className="health-editor-block" aria-label="Varianten-Annahmen">
          <h3>Variante</h3>
          <div className="health-fields">
            <label><span>Änderung ab Periode</span><input type="number" min="1" max="100"
              value={draft.variantStartPeriod} disabled={busy !== null}
              onChange={(event) => edit("variantStartPeriod", Number(event.target.value))} /></label>
            {VARIANT_AMOUNTS.map(({ key, label }) => <label key={key}><span>{label}</span>
              <input type="text" inputMode="decimal" value={String(draft[key])} disabled={busy !== null}
                onChange={(event) => edit(key, event.target.value)} /></label>)}
          </div>
          <p>{draft.variantStartPeriod > draft.periodCount
            ? "Die Änderung liegt hinter dem gewählten Horizont; beide Fälle bleiben bis dahin gleich."
            : "Bestand, Zu- und Abgänge, Anlage, Aufwand und Kapital bleiben wie in der Baseline."}</p>
        </section>
      </div>

      <div className="health-actions">
        <button className="primary-action" type="button" onClick={calculate} disabled={busy !== null}>
          <Calculator size={17} aria-hidden="true" />{busy === "preview" ? "Berechnung läuft…" : "Beide Fälle berechnen"}
        </button>
        <span>{comparisonReady ? `${draft.periodCount} Perioden geprüft` : "Vorschau offen"}</span>
      </div>
      {error && <p className="health-error" role="alert">{error}</p>}
      {issues.length > 0 && <div className="health-issues" role="alert">{issues.slice(0, 6).map((issue, index) =>
        <p key={`${issue.code}-${index}`}>{issueText(issue)}</p>)}</div>}

      {showResults && <div className="health-results" data-testid="health-results">
        <div className="health-results-head">
          <div><h3>{view === "stored" ? "Gespeichertes Ergebnis" : "Wirkung über die Zeit"}</h3>
            <span>{shownCount} Perioden · {view === "stored" ? stored?.report.scenario_id : draft.scenarioId}</span></div>
          <div className="health-results-controls">
            {stored && comparisonReady && <div className="health-view-tabs" role="group" aria-label="Ergebnisansicht">
              <button type="button" className={view === "compare" ? "active" : ""} aria-pressed={view === "compare"}
                onClick={() => setView("compare")}>Vergleich</button>
              <button type="button" className={view === "stored" ? "active" : ""} aria-pressed={view === "stored"}
                onClick={() => setView("stored")}>Gespeichert</button>
            </div>}
            <label><span>Kennzahl</span><select value={metric} onChange={(event) => setMetric(event.target.value)}>
              {METRICS.map((item) => <option key={item.key} value={item.key}>{item.label}</option>)}
            </select></label>
          </div>
        </div>
        <div className="health-chart" role="img" aria-label={`${METRICS.find((item) => item.key === metric)?.label}: ${view === "stored" ? "gespeicherte Zeitreihe" : "Baseline und Variante"}; exakte Werte in der Tabelle`}>
          <div className="health-chart-range">Wertebereich {valueText(minimum)} bis {valueText(maximum)}</div>
          <svg viewBox="0 0 800 180" preserveAspectRatio="none" aria-hidden="true">
            <line x1="30" y1="160" x2="770" y2="160" className="health-axis" />
            {baselineRows.length > 0 && <path d={linePath(baselineRows, metric, minimum, maximum)} className="health-line-baseline" />}
            {variantRows.length > 0 && <path d={linePath(variantRows, metric, minimum, maximum)} className="health-line-variant" />}
            {baselineRows.length === 1 && <circle cx="30" cy={160 - ((Number(baselineRows[0][metric]) - minimum) / (maximum - minimum || 1)) * 124}
              r="6" className="health-point-baseline" />}
            {variantRows.length === 1 && <circle cx="30" cy={160 - ((Number(variantRows[0][metric]) - minimum) / (maximum - minimum || 1)) * 124}
              r="3" className="health-point-variant" />}
          </svg>
          <div className="health-chart-periods"><span>Periode 1</span><span>Periode {shownCount}</span></div>
          <div className="health-chart-legend">
            {view === "compare" && <span><i className="health-legend-baseline" />Baseline</span>}
            <span><i className="health-legend-variant" />{view === "compare" ? "Variante" : stored?.report.variant_id === "baseline" ? "Baseline" : "Variante"}</span>
          </div>
        </div>
        <div className="health-table-wrap" role="region" aria-label="Kranken-Zeitreihe" tabIndex={0}>
          <table className="health-table"><thead><tr><th scope="col">Periode</th>
            {view === "compare" && <th scope="col">Baseline</th>}
            <th scope="col">{view === "compare" ? "Variante" : "Gespeichert"}</th></tr></thead>
            <tbody>{variantRows.map((row, index) => <tr key={row.period}><th scope="row">{row.period}</th>
              {view === "compare" && <td>{valueText(baselineRows[index]?.[metric])}</td>}
              <td>{valueText(row[metric])}</td></tr>)}</tbody>
          </table>
        </div>
        <p className="health-model-note">IMS-2.x-Modellrechnung aus expliziten Seminarannahmen. Keine historische Vollgleichheit oder gesetzliche Krankenbilanz.</p>
      </div>}

      <div className="health-storage">
        <h3>Ergebnis sichern</h3>
        <div className="health-storage-controls">
          <div className="health-side-tabs" role="group" aria-label="Fall speichern">
            {(["baseline", "variant"] as HealthSide[]).map((side) => <button type="button" key={side}
              aria-pressed={selectedSide === side} className={selectedSide === side ? "active" : ""}
              disabled={busy !== null} onClick={() => { setSelectedSide(side); setConfirmed(false); }}>
              {side === "baseline" ? "Baseline" : "Variante"}</button>)}
          </div>
          <label className="health-check"><input type="checkbox" checked={confirmed}
            disabled={!previews[selectedSide] || !historyReady || busy !== null || view !== "compare"}
            onChange={(event) => setConfirmed(event.target.checked)} />
            <span>{selectedSide === "baseline" ? "Baseline" : "Variante"} ausdrücklich speichern</span></label>
          <button className="secondary-action" type="button" onClick={store}
            disabled={!previews[selectedSide] || !historyReady || !confirmed || busy !== null || view !== "compare"}>
            <Save size={17} aria-hidden="true" />{busy === "store" ? "Speichert…" : "Geprüften Fall speichern"}
          </button>
        </div>
        {storageError && <p className="health-storage-error" role="status">{storageError}</p>}
        {stored && <div className="health-stored">
          <span>Gespeichert · VU {stored.report.insurer_id} · {stored.report.variant_id === "baseline" ? "Baseline" : "Variante"} · {stored.report.calculated_period_count} Perioden</span>
          <div className="health-downloads">
            {(["csv", "json", "xlsx"] as const).map((format) => <button className="secondary-action" key={format}
              type="button" onClick={() => download(format)} disabled={busy !== null}>
              <Download size={16} aria-hidden="true" />{format === "xlsx" ? "Excel" : format.toUpperCase()}</button>)}
          </div>
        </div>}
      </div>

      <div className="health-history">
        <div className="health-history-head"><h3>Gespeicherte Krankenfälle</h3>
          <button className="secondary-action" type="button" title="Verlauf aktualisieren" aria-label="Verlauf aktualisieren"
            onClick={refreshHistory} disabled={busy !== null}><RefreshCw size={16} aria-hidden="true" /></button>
        </div>
        {!historyReady ? <p>Kein Verlauf verfügbar</p> : history.length === 0 ? <p>Noch keine gespeicherten Fälle</p> :
          <div className="health-history-list">{history.slice(0, 10).map((item) =>
            <button type="button" key={item.result_id} disabled={busy !== null}
              aria-pressed={stored?.result_id === item.result_id && view === "stored"}
              onClick={() => selectHistory(item.result_id)}>
              <strong>VU {item.insurer_id} · {item.scenario_id} · {item.variant_id === "baseline" ? "Baseline" : "Variante"}</strong>
              <span>{item.period_count} Perioden · {new Date(item.stored_at).toLocaleString("de-DE")}</span>
            </button>)}</div>}
      </div>
    </section>
  );
}
