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

type MetadataSourceStatus = {
  schema_version: string;
  storage_kind: "memory" | "sqlite";
  configured: boolean;
  path?: string;
  writes_enabled: boolean;
  execution_enabled: boolean;
};

type CapabilityState = {
  enabled: boolean;
  boundary?: string;
  reason: string;
};

type DetailState = "idle" | "loading" | "ready" | "error";

const statusItems: StatusItem[] = [
  { label: "Backend", value: "bereit", tone: "ready" },
  { label: "Fachlogik", value: "abgegrenzt", tone: "quiet" },
  { label: "Persistenz", value: "vorbereitet", tone: "quiet" }
];

const validationRows = [
  ["Simulationskern", "587 Tests", "gruen"],
  ["Legacy-Fenster", "portierte Pfade", "abgedeckt"],
  ["Historische Vollgleichheit", "nicht behauptet", "offen"]
];

const importShapeRows = [
  ["schema_version", "ims.workbench.metadata.v1"],
  ["scenarios", "Szenario-Metadaten"],
  ["runs", "Run-Metadaten"]
];

function App() {
  const [scenarios, setScenarios] = useState<ScenarioMetadata[]>([]);
  const [runs, setRuns] = useState<RunMetadata[]>([]);
  const [capabilities, setCapabilities] = useState<MetadataCapabilities | null>(null);
  const [metadataSource, setMetadataSource] = useState<MetadataSourceStatus | null>(null);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [scenarioDetail, setScenarioDetail] = useState<ScenarioMetadata | null>(null);
  const [runDetail, setRunDetail] = useState<RunMetadata | null>(null);
  const [detailState, setDetailState] = useState<DetailState>("idle");
  const [detailError, setDetailError] = useState<string | null>(null);
  const [metadataState, setMetadataState] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    let active = true;

    async function loadMetadata() {
      try {
        const [scenarioResponse, runResponse, capabilityResponse, sourceResponse] = await Promise.all([
          fetch("/api/scenarios"),
          fetch("/api/runs"),
          fetch("/api/metadata/capabilities"),
          fetch("/api/metadata/source")
        ]);
        if (!scenarioResponse.ok || !runResponse.ok || !capabilityResponse.ok || !sourceResponse.ok) {
          throw new Error("metadata request failed");
        }
        const [scenarioPayload, runPayload, capabilityPayload, sourcePayload] = await Promise.all([
          scenarioResponse.json() as Promise<MetadataResponse<ScenarioMetadata>>,
          runResponse.json() as Promise<MetadataResponse<RunMetadata>>,
          capabilityResponse.json() as Promise<MetadataCapabilities>,
          sourceResponse.json() as Promise<MetadataSourceStatus>
        ]);
        if (active) {
          setScenarios(scenarioPayload.items);
          setRuns(runPayload.items);
          setCapabilities(capabilityPayload);
          setMetadataSource(sourcePayload);
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
  const storageLabel = metadataSource?.storage_kind === "sqlite" ? "SQLite-Datei" : "Memory";
  const storagePath = metadataSource?.path ?? "nicht konfiguriert";
  const detailStatusLabel = detailState === "error" ? "nicht gefunden" : detailState === "loading" ? "laedt" : "lesend";

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
                  onClick={() => setSelectedRunId(run.id)}
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
                <li><code>execution_enabled</code> bleibt <code>false</code></li>
                <li>Browser schreibt keine Metadaten</li>
              </ul>
            </article>
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
