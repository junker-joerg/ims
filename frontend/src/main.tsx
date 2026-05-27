import React from "react";
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

const statusItems: StatusItem[] = [
  { label: "Backend", value: "bereit", tone: "ready" },
  { label: "Fachlogik", value: "abgegrenzt", tone: "quiet" },
  { label: "Persistenz", value: "geplant", tone: "warn" }
];

const validationRows = [
  ["Simulationskern", "540 Tests", "gruen"],
  ["Legacy-Fenster", "portierte Pfade", "abgedeckt"],
  ["Historische Vollgleichheit", "nicht behauptet", "offen"]
];

function App() {
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
                <strong>Agrsich / VN / VU</strong>
              </div>
              <div>
                <span>Steuerung</span>
                <strong>noch nicht aktiv</strong>
              </div>
            </div>
            <p className="muted">
              Diese Ansicht bereitet Bedienflaechen fuer lokale Szenario- und Run-Metadaten vor.
              Der Simulationskern bleibt in diesem Schritt unveraendert.
            </p>
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
            <p className="muted">Run- und Szenario-Metadaten werden spaeter lokal persistiert.</p>
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
