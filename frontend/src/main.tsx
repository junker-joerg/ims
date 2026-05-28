import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  Archive,
  Braces,
  CheckCircle2,
  CircleDot,
  Database,
  FileText,
  GitBranch,
  Play,
  Search,
  ServerCog,
  ShieldCheck
} from "lucide-react";
import "./styles.css";

type StatusItem = {
  label: string;
  value: string;
  tone: "ready" | "quiet" | "warn";
};

type ScenarioMetadata = {
  id: string;
  display_name: string;
  status: string;
  domain_scope: string;
  source: MetadataSource;
  validation: ValidationSummary;
  updated_at: string;
  notes: string;
};

type RunMetadata = {
  id: string;
  display_name: string;
  scenario_id: string;
  status: string;
  source: MetadataSource;
  validation: ValidationSummary;
  period_window: string;
  execution_enabled: boolean;
  updated_at: string;
};

type MetadataSource = {
  kind: string;
  label: string;
  path?: string | null;
};

type ValidationSummary = {
  status: string;
  scope: string;
  claim: string;
};

type MetadataResponse<T> = {
  schema_version: string;
  generated_at: string;
  items: T[];
};

type MetadataCapabilities = {
  writes: {
    scenario_metadata: CapabilityState;
    run_metadata: CapabilityState;
  };
  simulation_execution: CapabilityState;
};

type HealthStatus = {
  status: string;
  service: string;
  version: string;
  frontend_available: boolean;
};

type VersionInfo = {
  name: string;
  version: string;
  api: string;
};

type MetadataSourceStatus = {
  schema_version: string;
  storage_kind: "memory" | "sqlite";
  configured: boolean;
  injected: boolean;
  path?: string;
  writes_enabled: boolean;
  execution_enabled: boolean;
};

type MetadataConsistency = {
  schema_version: string;
  generated_at: string;
  status: "ok" | "warning";
  scenario_count: number;
  run_count: number;
  runs_with_known_scenario: number;
  runs_with_missing_scenario: string[];
  runs_with_execution_enabled: string[];
  writes_enabled: boolean;
  simulation_enabled: boolean;
  issue_count: number;
};

type CapabilityState = {
  enabled: boolean;
  boundary?: string;
  reason: string;
};

type DetailState = "idle" | "loading" | "ready" | "error";

type ScenarioFilters = {
  query: string;
  status: string;
  source: string;
  scope: string;
};

type RunFilters = {
  query: string;
  status: string;
  scenario: string;
  source: string;
};

const statusItems: StatusItem[] = [
  { label: "Backend", value: "bereit", tone: "ready" },
  { label: "Fachlogik", value: "abgegrenzt", tone: "quiet" },
  { label: "Persistenz", value: "vorbereitet", tone: "quiet" }
];

const validationRows = [
  ["Simulationskern", "652 Tests", "gruen"],
  ["Legacy-Fenster", "portierte Pfade", "abgedeckt"],
  ["Historische Vollgleichheit", "nicht behauptet", "offen"]
];

const importShapeRows = [
  ["schema_version", "ims.workbench.metadata.v1"],
  ["scenarios", "Szenario-Metadaten"],
  ["runs", "Run-Metadaten"]
];

const ALL_SCENARIO_FILTERS = "alle";
const ALL_RUN_FILTERS = "alle";

export function filterScenarios(scenarios: ScenarioMetadata[], filters: ScenarioFilters): ScenarioMetadata[] {
  const query = filters.query.trim().toLocaleLowerCase();
  return scenarios.filter((scenario) => {
    const matchesQuery =
      !query ||
      scenario.display_name.toLocaleLowerCase().includes(query) ||
      scenario.id.toLocaleLowerCase().includes(query);
    const matchesStatus = filters.status === ALL_SCENARIO_FILTERS || scenario.status === filters.status;
    const matchesSource = filters.source === ALL_SCENARIO_FILTERS || scenario.source.label === filters.source;
    const matchesScope = filters.scope === ALL_SCENARIO_FILTERS || scenario.domain_scope === filters.scope;
    return matchesQuery && matchesStatus && matchesSource && matchesScope;
  });
}

export function filterRuns(runs: RunMetadata[], filters: RunFilters): RunMetadata[] {
  const query = filters.query.trim().toLocaleLowerCase();
  return runs.filter((run) => {
    const matchesQuery =
      !query ||
      run.display_name.toLocaleLowerCase().includes(query) ||
      run.id.toLocaleLowerCase().includes(query);
    const matchesStatus = filters.status === ALL_RUN_FILTERS || run.status === filters.status;
    const matchesScenario = filters.scenario === ALL_RUN_FILTERS || run.scenario_id === filters.scenario;
    const matchesSource = filters.source === ALL_RUN_FILTERS || run.source.label === filters.source;
    return matchesQuery && matchesStatus && matchesScenario && matchesSource;
  });
}

function uniqueSorted(values: string[]): string[] {
  return Array.from(new Set(values)).sort((left, right) => left.localeCompare(right));
}

function App() {
  const [scenarios, setScenarios] = useState<ScenarioMetadata[]>([]);
  const [runs, setRuns] = useState<RunMetadata[]>([]);
  const [capabilities, setCapabilities] = useState<MetadataCapabilities | null>(null);
  const [metadataSource, setMetadataSource] = useState<MetadataSourceStatus | null>(null);
  const [metadataConsistency, setMetadataConsistency] = useState<MetadataConsistency | null>(null);
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [versionInfo, setVersionInfo] = useState<VersionInfo | null>(null);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [scenarioDetail, setScenarioDetail] = useState<ScenarioMetadata | null>(null);
  const [runDetail, setRunDetail] = useState<RunMetadata | null>(null);
  const [detailState, setDetailState] = useState<DetailState>("idle");
  const [detailError, setDetailError] = useState<string | null>(null);
  const [metadataState, setMetadataState] = useState<"loading" | "ready" | "error">("loading");
  const [scenarioQuery, setScenarioQuery] = useState("");
  const [scenarioStatusFilter, setScenarioStatusFilter] = useState(ALL_SCENARIO_FILTERS);
  const [scenarioSourceFilter, setScenarioSourceFilter] = useState(ALL_SCENARIO_FILTERS);
  const [scenarioScopeFilter, setScenarioScopeFilter] = useState(ALL_SCENARIO_FILTERS);
  const [runQuery, setRunQuery] = useState("");
  const [runStatusFilter, setRunStatusFilter] = useState(ALL_RUN_FILTERS);
  const [runScenarioFilter, setRunScenarioFilter] = useState(ALL_RUN_FILTERS);
  const [runSourceFilter, setRunSourceFilter] = useState(ALL_RUN_FILTERS);

  useEffect(() => {
    let active = true;

    async function loadMetadata() {
      try {
        const [
          scenarioResponse,
          runResponse,
          capabilityResponse,
          sourceResponse,
          consistencyResponse,
          healthResponse,
          versionResponse
        ] = await Promise.all([
          fetch("/api/scenarios"),
          fetch("/api/runs"),
          fetch("/api/metadata/capabilities"),
          fetch("/api/metadata/source"),
          fetch("/api/metadata/consistency"),
          fetch("/api/health"),
          fetch("/api/version")
        ]);
        if (
          !scenarioResponse.ok ||
          !runResponse.ok ||
          !capabilityResponse.ok ||
          !sourceResponse.ok ||
          !consistencyResponse.ok ||
          !healthResponse.ok ||
          !versionResponse.ok
        ) {
          throw new Error("metadata request failed");
        }
        const [
          scenarioPayload,
          runPayload,
          capabilityPayload,
          sourcePayload,
          consistencyPayload,
          healthPayload,
          versionPayload
        ] = await Promise.all([
          scenarioResponse.json() as Promise<MetadataResponse<ScenarioMetadata>>,
          runResponse.json() as Promise<MetadataResponse<RunMetadata>>,
          capabilityResponse.json() as Promise<MetadataCapabilities>,
          sourceResponse.json() as Promise<MetadataSourceStatus>,
          consistencyResponse.json() as Promise<MetadataConsistency>,
          healthResponse.json() as Promise<HealthStatus>,
          versionResponse.json() as Promise<VersionInfo>
        ]);
        if (active) {
          setScenarios(scenarioPayload.items);
          setRuns(runPayload.items);
          setCapabilities(capabilityPayload);
          setMetadataSource(sourcePayload);
          setMetadataConsistency(consistencyPayload);
          setHealthStatus(healthPayload);
          setVersionInfo(versionPayload);
          setSelectedScenarioId((current) => current ?? scenarioPayload.items[0]?.id ?? null);
          setSelectedRunId((current) => current ?? runPayload.items[0]?.id ?? null);
          setMetadataState("ready");
        }
      } catch {
        if (active) {
          setMetadataState("error");
        }
      }
    }

    loadMetadata();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function loadDetails() {
      if (!selectedScenarioId || !selectedRunId) {
        return;
      }
      setDetailState("loading");
      setDetailError(null);
      try {
        const [scenarioResponse, runResponse] = await Promise.all([
          fetch(`/api/scenarios/${encodeURIComponent(selectedScenarioId)}`),
          fetch(`/api/runs/${encodeURIComponent(selectedRunId)}`)
        ]);
        if (scenarioResponse.status === 404 || runResponse.status === 404) {
          throw new Error("Metadaten nicht gefunden");
        }
        if (!scenarioResponse.ok || !runResponse.ok) {
          throw new Error("Detaildaten nicht erreichbar");
        }
        const [scenarioPayload, runPayload] = await Promise.all([
          scenarioResponse.json() as Promise<ScenarioMetadata>,
          runResponse.json() as Promise<RunMetadata>
        ]);
        if (active) {
          setScenarioDetail(scenarioPayload);
          setRunDetail(runPayload);
          setDetailState("ready");
        }
      } catch (error) {
        if (active) {
          setScenarioDetail(null);
          setRunDetail(null);
          setDetailError(error instanceof Error ? error.message : "Detaildaten nicht erreichbar");
          setDetailState("error");
        }
      }
    }

    loadDetails();
    return () => {
      active = false;
    };
  }, [selectedScenarioId, selectedRunId]);

  const primaryScenario = scenarios[0];
  const primaryRun = runs[0];
  const writeLabel = capabilities?.writes.scenario_metadata.enabled ? "aktiv" : "gesperrt";
  const executionLabel = capabilities?.simulation_execution.enabled ? "aktiv" : "gesperrt";
  const storageLabel = metadataSource?.storage_kind === "sqlite" ? "SQLite-Datei" : "Memory";
  const storagePath = metadataSource?.path ?? "nicht konfiguriert";
  const detailStatusLabel = detailState === "error" ? "nicht gefunden" : detailState === "loading" ? "laedt" : "lesend";
  const scenarioNameById = new Map(scenarios.map((scenario) => [scenario.id, scenario.display_name]));
  const scenarioStatusOptions = uniqueSorted(scenarios.map((scenario) => scenario.status));
  const scenarioSourceOptions = uniqueSorted(scenarios.map((scenario) => scenario.source.label));
  const scenarioScopeOptions = uniqueSorted(scenarios.map((scenario) => scenario.domain_scope));
  const runStatusOptions = uniqueSorted(runs.map((run) => run.status));
  const runScenarioOptions = uniqueSorted(runs.map((run) => run.scenario_id));
  const runSourceOptions = uniqueSorted(runs.map((run) => run.source.label));
  const filteredScenarios = filterScenarios(scenarios, {
    query: scenarioQuery,
    status: scenarioStatusFilter,
    source: scenarioSourceFilter,
    scope: scenarioScopeFilter
  });
  const filteredRuns = filterRuns(runs, {
    query: runQuery,
    status: runStatusFilter,
    scenario: runScenarioFilter,
    source: runSourceFilter
  });
  const selectedScenario =
    scenarioDetail?.id === selectedScenarioId
      ? scenarioDetail
      : scenarios.find((scenario) => scenario.id === selectedScenarioId) ?? null;
  const selectedRun =
    runDetail?.id === selectedRunId
      ? runDetail
      : runs.find((run) => run.id === selectedRunId) ?? null;
  const selectedScenarioHidden =
    selectedScenarioId !== null && !filteredScenarios.some((scenario) => scenario.id === selectedScenarioId);
  const selectedRunHidden = selectedRunId !== null && !filteredRuns.some((run) => run.id === selectedRunId);
  const filterNotice = selectedScenarioHidden || selectedRunHidden
    ? "Auswahl durch Filter aktuell nicht in den Listen sichtbar"
    : "Auswahl in den Listen sichtbar";
  const selectionRows = [
    ["Szenario", selectedScenario?.display_name ?? "wird geladen"],
    ["Run", selectedRun?.display_name ?? "wird geladen"],
    ["Periodenfenster", selectedRun?.period_window ?? "-"],
    ["Metadatenquelle", storageLabel],
    ["Schreibpfade", capabilities?.writes.scenario_metadata.enabled || capabilities?.writes.run_metadata.enabled ? "aktiv" : "gesperrt"],
    ["Ausfuehrung", capabilities?.simulation_execution.enabled || selectedRun?.execution_enabled ? "aktiv" : "gesperrt"],
    ["Filterzustand", filterNotice]
  ];
  const selectRun = (run: RunMetadata) => {
    setSelectedRunId(run.id);
    setSelectedScenarioId(run.scenario_id);
  };
  const missingScenarioLabel = metadataConsistency?.runs_with_missing_scenario.length
    ? metadataConsistency.runs_with_missing_scenario.join(", ")
    : "keine";
  const executionEnabledLabel = metadataConsistency?.runs_with_execution_enabled.length
    ? metadataConsistency.runs_with_execution_enabled.join(", ")
    : "keine";
  const consistencyRows = [
    ["Szenarien", String(metadataConsistency?.scenario_count ?? scenarios.length)],
    ["Runs", String(metadataConsistency?.run_count ?? runs.length)],
    ["Run-Bezuege", `${metadataConsistency?.runs_with_known_scenario ?? 0} bekannt`],
    ["Fehlende Bezuege", missingScenarioLabel],
    ["Aktive Ausfuehrung", executionEnabledLabel],
    ["Schreibpfade", metadataConsistency?.writes_enabled ? "aktiv" : "gesperrt"],
    ["Simulation", metadataConsistency?.simulation_enabled ? "aktiv" : "gesperrt"],
    ["Status", metadataConsistency?.status === "warning" ? "Warnung" : "ok"]
  ];
  const diagnosisRows = [
    ["Backend", healthStatus?.status === "ok" ? "bereit" : metadataState === "error" ? "nicht erreichbar" : "laedt"],
    ["Version", versionInfo ? `${versionInfo.name} ${versionInfo.version}` : "laedt"],
    ["Frontend", healthStatus?.frontend_available ? "gebaut" : "nicht gebaut"],
    ["Metadatenquelle", storageLabel],
    ["Schreibpfade", capabilities?.writes.scenario_metadata.enabled || capabilities?.writes.run_metadata.enabled ? "aktiv" : "gesperrt"],
    ["Simulation", capabilities?.simulation_execution.enabled ? "aktiv" : "gesperrt"],
    ["Import", "lokal per CLI"]
  ];

  return (
    <main className="shell">
      <aside className="sidebar" aria-label="Workbench Navigation">
        <div className="brand">
          <div className="brand-mark">IMS</div>
          <div>
            <strong>Workbench</strong>
            <span>lokale Vorschau</span>
          </div>
        </div>
        <nav>
          <a className="active" href="#overview">
            <Activity size={18} aria-hidden="true" /> Dashboard
          </a>
          <a href="#scenarios">
            <FileText size={18} aria-hidden="true" /> Szenarien
          </a>
          <a href="#validation">
            <ShieldCheck size={18} aria-hidden="true" /> Validierung
          </a>
          <a href="#runs">
            <Archive size={18} aria-hidden="true" /> Runs
          </a>
        </nav>
      </aside>

      <section className="content" id="overview">
        <header className="topbar">
          <div>
            <p className="eyebrow">IMS Modernisierung</p>
            <h1>Lokale Simulations-Workbench</h1>
          </div>
          <button className="primary-action" type="button">
            <Play size={18} aria-hidden="true" />
            Neuer Lauf
          </button>
        </header>

        <section className="status-grid" aria-label="Systemstatus">
          {statusItems.map((item) => (
            <article className="status-card" key={item.label}>
              <span className={`status-dot ${item.tone}`} />
              <p>{item.label}</p>
              <strong>{item.value}</strong>
            </article>
          ))}
        </section>

        <section className="work-grid">
          <article className="panel scenario-panel" id="scenarios">
            <div className="panel-heading">
              <FileText size={20} aria-hidden="true" />
              <h2>Szenario-Arbeitsstand</h2>
            </div>
            <div className="scenario-strip">
              <div>
                <span>Referenzfenster</span>
                <strong>{primaryScenario?.domain_scope ?? "wird geladen"}</strong>
              </div>
              <div>
                <span>Schreiben</span>
                <strong>{metadataState === "error" ? "API nicht erreichbar" : writeLabel}</strong>
              </div>
            </div>
            <p className="muted">
              {primaryScenario?.validation.claim ??
                "Diese Ansicht bereitet Bedienflaechen fuer lokale Szenario- und Run-Metadaten vor."}
              {" "}Der Simulationskern bleibt in diesem Schritt unveraendert.
            </p>
            <div className="metadata-list" aria-label="Szenario-Metadaten">
              {scenarios.map((scenario) => (
                <button
                  className={`metadata-row selectable ${scenario.id === selectedScenarioId ? "selected" : ""}`}
                  key={scenario.id}
                  type="button"
                  onClick={() => setSelectedScenarioId(scenario.id)}
                >
                  <span>{scenario.display_name}</span>
                  <strong>{scenario.status}</strong>
                </button>
              ))}
            </div>
          </article>

          <article className="panel" id="runs">
            <div className="panel-heading">
              <Database size={20} aria-hidden="true" />
              <h2>Lokale Ablage</h2>
            </div>
            <div className="meter">
              <span style={{ width: "18%" }} />
            </div>
            <p className="metric">SQLite-Vorbereitung</p>
            <p className="muted">
              {primaryRun
                ? `${primaryRun.display_name}: ${primaryRun.validation.scope}. Schreibpfade bleiben kontrolliert gesperrt.`
                : "Run- und Szenario-Metadaten werden spaeter lokal persistiert."}
            </p>
            <div className="source-status" aria-label="Metadatenquelle">
              <div>
                <span>Ablage</span>
                <strong>{metadataState === "error" ? "nicht erreichbar" : storageLabel}</strong>
              </div>
              <div>
                <span>Pfad</span>
                <strong>{storagePath}</strong>
              </div>
              <div>
                <span>Schreiben</span>
                <strong>{metadataSource?.writes_enabled ? "aktiv" : "gesperrt"}</strong>
              </div>
            </div>
            <div className="metadata-list compact" aria-label="Run-Metadaten">
              {runs.map((run) => (
                <button
                  className={`metadata-row selectable ${run.id === selectedRunId ? "selected" : ""}`}
                  key={run.id}
                  type="button"
                  onClick={() => selectRun(run)}
                >
                  <span>{run.period_window}</span>
                  <strong>{run.status}</strong>
                </button>
              ))}
            </div>
          </article>
        </section>

        <section className="panel detail-panel" aria-label="Metadaten-Details">
          <div className="panel-heading">
            <FileText size={20} aria-hidden="true" />
            <h2>Metadaten-Detail</h2>
          </div>
          <div className="detail-status">
            <span>Quelle</span>
            <strong>{detailStatusLabel}</strong>
          </div>
          {detailState === "error" ? (
            <p className="muted">{detailError}</p>
          ) : (
            <div className="detail-grid">
              <article>
                <span>Szenario</span>
                <strong>{scenarioDetail?.display_name ?? "wird geladen"}</strong>
                <dl>
                  <div>
                    <dt>ID</dt>
                    <dd>{scenarioDetail?.id ?? "-"}</dd>
                  </div>
                  <div>
                    <dt>Umfang</dt>
                    <dd>{scenarioDetail?.domain_scope ?? "-"}</dd>
                  </div>
                  <div>
                    <dt>Validierung</dt>
                    <dd>{scenarioDetail?.validation.scope ?? "-"}</dd>
                  </div>
                </dl>
              </article>
              <article>
                <span>Run</span>
                <strong>{runDetail?.display_name ?? "wird geladen"}</strong>
                <dl>
                  <div>
                    <dt>ID</dt>
                    <dd>{runDetail?.id ?? "-"}</dd>
                  </div>
                  <div>
                    <dt>Fenster</dt>
                    <dd>{runDetail?.period_window ?? "-"}</dd>
                  </div>
                  <div>
                    <dt>Ausfuehrung</dt>
                    <dd>{runDetail?.execution_enabled ? "aktiv" : "gesperrt"}</dd>
                  </div>
                </dl>
              </article>
            </div>
          )}
        </section>

        <section className="panel selection-summary-panel" aria-label="Auswahlzusammenfassung">
          <div className="panel-heading">
            <CircleDot size={20} aria-hidden="true" />
            <h2>Auswahlzusammenfassung</h2>
          </div>
          <div className="selection-summary-grid">
            {selectionRows.map(([label, value]) => (
              <div className="selection-summary-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="panel scenario-overview-panel" aria-label="Szenario-Uebersicht">
          <div className="panel-heading">
            <FileText size={20} aria-hidden="true" />
            <h2>Szenario-Uebersicht</h2>
          </div>
          <div className="scenario-filterbar" aria-label="Szenariofilter">
            <label className="scenario-search">
              <Search size={17} aria-hidden="true" />
              <span>Suche</span>
              <input
                aria-label="Szenariosuche"
                onChange={(event) => setScenarioQuery(event.target.value)}
                placeholder="Name oder ID"
                type="search"
                value={scenarioQuery}
              />
            </label>
            <label>
              <span>Status</span>
              <select
                aria-label="Szenario-Statusfilter"
                onChange={(event) => setScenarioStatusFilter(event.target.value)}
                value={scenarioStatusFilter}
              >
                <option value={ALL_SCENARIO_FILTERS}>alle</option>
                {scenarioStatusOptions.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Quelle</span>
              <select
                aria-label="Szenario-Quellenfilter"
                onChange={(event) => setScenarioSourceFilter(event.target.value)}
                value={scenarioSourceFilter}
              >
                <option value={ALL_SCENARIO_FILTERS}>alle</option>
                {scenarioSourceOptions.map((source) => (
                  <option key={source} value={source}>
                    {source}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Umfang</span>
              <select
                aria-label="Szenario-Scopefilter"
                onChange={(event) => setScenarioScopeFilter(event.target.value)}
                value={scenarioScopeFilter}
              >
                <option value={ALL_SCENARIO_FILTERS}>alle</option>
                {scenarioScopeOptions.map((scope) => (
                  <option key={scope} value={scope}>
                    {scope}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <p className="scenario-filter-count">
            {filteredScenarios.length} von {scenarios.length} Szenarien sichtbar
          </p>
          <div className="scenario-overview-table">
            <div className="scenario-overview-head" aria-hidden="true">
              <span>Szenario</span>
              <span>Umfang</span>
              <span>Quelle</span>
              <span>Validierung</span>
              <span>Aktualisiert</span>
              <span>Ausfuehrung</span>
            </div>
            {filteredScenarios.map((scenario) => (
              <button
                className={`scenario-overview-row ${scenario.id === selectedScenarioId ? "selected" : ""}`}
                key={scenario.id}
                type="button"
                onClick={() => setSelectedScenarioId(scenario.id)}
              >
                <span>
                  <strong>{scenario.display_name}</strong>
                  <small>{scenario.status}</small>
                </span>
                <span>{scenario.domain_scope}</span>
                <span>{scenario.source.label}</span>
                <span>{scenario.validation.scope}</span>
                <span>{scenario.updated_at}</span>
                <span>{executionLabel}</span>
              </button>
            ))}
          </div>
          {filteredScenarios.length === 0 ? (
            <div className="empty-state">Keine Szenarien fuer diesen Filter.</div>
          ) : null}
        </section>

        <section className="panel run-overview-panel" aria-label="Run-Uebersicht">
          <div className="panel-heading">
            <Archive size={20} aria-hidden="true" />
            <h2>Run-Uebersicht</h2>
          </div>
          <div className="run-filterbar" aria-label="Runfilter">
            <label className="run-search">
              <Search size={17} aria-hidden="true" />
              <span>Suche</span>
              <input
                aria-label="Runsuche"
                onChange={(event) => setRunQuery(event.target.value)}
                placeholder="Name oder ID"
                type="search"
                value={runQuery}
              />
            </label>
            <label>
              <span>Status</span>
              <select
                aria-label="Run-Statusfilter"
                onChange={(event) => setRunStatusFilter(event.target.value)}
                value={runStatusFilter}
              >
                <option value={ALL_RUN_FILTERS}>alle</option>
                {runStatusOptions.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Szenario</span>
              <select
                aria-label="Run-Szenariofilter"
                onChange={(event) => setRunScenarioFilter(event.target.value)}
                value={runScenarioFilter}
              >
                <option value={ALL_RUN_FILTERS}>alle</option>
                {runScenarioOptions.map((scenarioId) => (
                  <option key={scenarioId} value={scenarioId}>
                    {scenarioNameById.get(scenarioId) ?? scenarioId}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>Quelle</span>
              <select
                aria-label="Run-Quellenfilter"
                onChange={(event) => setRunSourceFilter(event.target.value)}
                value={runSourceFilter}
              >
                <option value={ALL_RUN_FILTERS}>alle</option>
                {runSourceOptions.map((source) => (
                  <option key={source} value={source}>
                    {source}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <p className="run-filter-count">
            {filteredRuns.length} von {runs.length} Runs sichtbar
          </p>
          <div className="run-overview-table">
            <div className="run-overview-head" aria-hidden="true">
              <span>Run</span>
              <span>Szenario</span>
              <span>Fenster</span>
              <span>Quelle</span>
              <span>Ausfuehrung</span>
            </div>
            {filteredRuns.map((run) => (
              <button
                className={`run-overview-row ${run.id === selectedRunId ? "selected" : ""}`}
                key={run.id}
                type="button"
                onClick={() => selectRun(run)}
              >
                <span>
                  <strong>{run.display_name}</strong>
                  <small>{run.status}</small>
                </span>
                <span>{scenarioNameById.get(run.scenario_id) ?? run.scenario_id}</span>
                <span>{run.period_window}</span>
                <span>{run.source.label}</span>
                <span>{run.execution_enabled ? "aktiv" : "gesperrt"}</span>
              </button>
            ))}
          </div>
          {filteredRuns.length === 0 ? (
            <div className="empty-state">Keine Runs fuer diesen Filter.</div>
          ) : null}
        </section>

        <section className="panel import-panel" aria-label="Importvorschau">
          <div className="panel-heading">
            <Braces size={20} aria-hidden="true" />
            <h2>Importvorschau</h2>
          </div>
          <div className="import-grid">
            <article>
              <span>JSON-Struktur</span>
              <div className="shape-list">
                {importShapeRows.map(([field, meaning]) => (
                  <div className="shape-row" key={field}>
                    <code>{field}</code>
                    <strong>{meaning}</strong>
                  </div>
                ))}
              </div>
            </article>
            <article>
              <span>Grenzen</span>
              <ul className="boundary-list">
                <li>Import aktuell nur ueber Python-Adapter</li>
                <li>Preview lokal per CLI ohne Schreiben</li>
                <li>Snapshot lokal per CLI ohne Browser-Export</li>
                <li>Export lokal per CLI nur mit explizitem Zielpfad</li>
                <li>Roundtrip lokal per CLI ohne Schreiben</li>
                <li>Dry-Run lokal per CLI ohne Import</li>
                <li>Importbericht lokal per CLI nach explizitem Schreiben</li>
                <li>Startdiagnose lokal per CLI ohne Serverstart</li>
                <li>Startplan lokal per CLI nur beschreibend</li>
                <li>Readiness lokal per CLI ohne Serverstart</li>
                <li>v1-Readiness als lokaler Abschluss-Smoke</li>
                <li>CLI-Uebersicht lokal per CLI ohne Seiteneffekte</li>
                <li>Schreibvertrag lokal per CLI nur beschreibend</li>
                <li>Schreibvertragspruefung lokal per CLI ohne Import</li>
                <li>Run-Control-Vertrag lokal per CLI ohne Ausfuehrung</li>
                <li>Run-Control-Preflight lokal per CLI ohne Ausfuehrung</li>
                <li><code>execution_enabled</code> bleibt <code>false</code></li>
                <li>Browser schreibt keine Metadaten</li>
              </ul>
            </article>
          </div>
        </section>

        <section className="panel diagnosis-panel" aria-label="Betriebsdiagnose">
          <div className="panel-heading">
            <ServerCog size={20} aria-hidden="true" />
            <h2>Betriebsdiagnose</h2>
          </div>
          <div className="diagnosis-grid">
            {diagnosisRows.map(([label, value]) => (
              <div className="diagnosis-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="panel consistency-panel" aria-label="Metadaten-Konsistenz">
          <div className="panel-heading">
            <ShieldCheck size={20} aria-hidden="true" />
            <h2>Metadaten-Konsistenz</h2>
          </div>
          <div className="consistency-summary">
            <span className={`status-dot ${metadataConsistency?.status === "warning" ? "warn" : "ready"}`} />
            <strong>{metadataConsistency?.issue_count ?? 0} offene Hinweise</strong>
          </div>
          <div className="consistency-grid">
            {consistencyRows.map(([label, value]) => (
              <div className="consistency-row" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="panel validation-panel" id="validation">
          <div className="panel-heading">
            <GitBranch size={20} aria-hidden="true" />
            <h2>Validierungsstatus</h2>
          </div>
          <div className="validation-table">
            {validationRows.map(([area, scope, state]) => (
              <div className="validation-row" key={area}>
                <span>{area}</span>
                <span>{scope}</span>
                <strong>
                  {state === "gruen" ? (
                    <CheckCircle2 size={17} aria-hidden="true" />
                  ) : (
                    <CircleDot size={17} aria-hidden="true" />
                  )}
                  {state}
                </strong>
              </div>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
