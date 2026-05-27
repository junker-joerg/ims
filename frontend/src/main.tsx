import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  Archive,
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

type CapabilityState = {
  enabled: boolean;
  boundary?: string;
  reason: string;
};

const statusItems: StatusItem[] = [
  { label: "Backend", value: "bereit", tone: "ready" },
  { label: "Fachlogik", value: "abgegrenzt", tone: "quiet" },
  { label: "Persistenz", value: "vorbereitet", tone: "quiet" }
];

const validationRows = [
  ["Simulationskern", "560 Tests", "gruen"],
  ["Legacy-Fenster", "portierte Pfade", "abgedeckt"],
  ["Historische Vollgleichheit", "nicht behauptet", "offen"]
];

function App() {
  const [scenarios, setScenarios] = useState<ScenarioMetadata[]>([]);
  const [runs, setRuns] = useState<RunMetadata[]>([]);
  const [capabilities, setCapabilities] = useState<MetadataCapabilities | null>(null);
  const [metadataState, setMetadataState] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    let active = true;

    async function loadMetadata() {
      try {
        const [scenarioResponse, runResponse, capabilityResponse] = await Promise.all([
          fetch("/api/scenarios"),
          fetch("/api/runs"),
          fetch("/api/metadata/capabilities")
        ]);
        if (!scenarioResponse.ok || !runResponse.ok || !capabilityResponse.ok) {
          throw new Error("metadata request failed");
        }
        const [scenarioPayload, runPayload, capabilityPayload] = await Promise.all([
          scenarioResponse.json() as Promise<MetadataResponse<ScenarioMetadata>>,
          runResponse.json() as Promise<MetadataResponse<RunMetadata>>,
          capabilityResponse.json() as Promise<MetadataCapabilities>
        ]);
        if (active) {
          setScenarios(scenarioPayload.items);
          setRuns(runPayload.items);
          setCapabilities(capabilityPayload);
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

  const primaryScenario = scenarios[0];
  const primaryRun = runs[0];
  const writeLabel = capabilities?.writes.scenario_metadata.enabled ? "aktiv" : "gesperrt";

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
                <div className="metadata-row" key={scenario.id}>
                  <span>{scenario.display_name}</span>
                  <strong>{scenario.status}</strong>
                </div>
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
            <div className="metadata-list compact" aria-label="Run-Metadaten">
              {runs.map((run) => (
                <div className="metadata-row" key={run.id}>
                  <span>{run.period_window}</span>
                  <strong>{run.status}</strong>
                </div>
              ))}
            </div>
          </article>
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
