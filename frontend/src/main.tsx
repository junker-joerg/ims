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
  name: string;
  scope: string;
  state: string;
  source: string;
  notes: string;
};

type RunMetadata = {
  id: string;
  label: string;
  scenario_id: string;
  state: string;
  period_window: string;
  validation_scope: string;
};

const statusItems: StatusItem[] = [
  { label: "Backend", value: "bereit", tone: "ready" },
  { label: "Fachlogik", value: "abgegrenzt", tone: "quiet" },
  { label: "Persistenz", value: "geplant", tone: "warn" }
];

const validationRows = [
  ["Simulationskern", "548 Tests", "gruen"],
  ["Legacy-Fenster", "portierte Pfade", "abgedeckt"],
  ["Historische Vollgleichheit", "nicht behauptet", "offen"]
];

function App() {
  const [scenarios, setScenarios] = useState<ScenarioMetadata[]>([]);
  const [runs, setRuns] = useState<RunMetadata[]>([]);
  const [metadataState, setMetadataState] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    let active = true;

    async function loadMetadata() {
      try {
        const [scenarioResponse, runResponse] = await Promise.all([
          fetch("/api/scenarios"),
          fetch("/api/runs")
        ]);
        if (!scenarioResponse.ok || !runResponse.ok) {
          throw new Error("metadata request failed");
        }
        const [scenarioPayload, runPayload] = await Promise.all([
          scenarioResponse.json() as Promise<ScenarioMetadata[]>,
          runResponse.json() as Promise<RunMetadata[]>
        ]);
        if (active) {
          setScenarios(scenarioPayload);
          setRuns(runPayload);
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
                <strong>{primaryScenario?.scope ?? "wird geladen"}</strong>
              </div>
              <div>
                <span>Steuerung</span>
                <strong>{metadataState === "error" ? "API nicht erreichbar" : "noch nicht aktiv"}</strong>
              </div>
            </div>
            <p className="muted">
              {primaryScenario?.notes ??
                "Diese Ansicht bereitet Bedienflaechen fuer lokale Szenario- und Run-Metadaten vor."}
              {" "}Der Simulationskern bleibt in diesem Schritt unveraendert.
            </p>
            <div className="metadata-list" aria-label="Szenario-Metadaten">
              {scenarios.map((scenario) => (
                <div className="metadata-row" key={scenario.id}>
                  <span>{scenario.name}</span>
                  <strong>{scenario.state}</strong>
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
                ? `${primaryRun.label}: ${primaryRun.validation_scope}.`
                : "Run- und Szenario-Metadaten werden spaeter lokal persistiert."}
            </p>
            <div className="metadata-list compact" aria-label="Run-Metadaten">
              {runs.map((run) => (
                <div className="metadata-row" key={run.id}>
                  <span>{run.period_window}</span>
                  <strong>{run.state}</strong>
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
