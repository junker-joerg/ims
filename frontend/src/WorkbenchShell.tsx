import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { Activity, ArrowRight, FileText, HelpCircle, Home, Moon, Play, Sun } from "lucide-react";

type AreaName = "overview" | "scenario" | "simulation" | "results" | "help";
type ModelName = "balance" | "life" | "health" | "four-sector-balance" | "capital" | "strategies" | "execution";
type Route = { area: AreaName; model: ModelName };
const areas = [
  { id: "overview", label: "Übersicht", icon: Home },
  { id: "scenario", label: "Szenario", icon: FileText },
  { id: "simulation", label: "Simulation", icon: Play },
  { id: "results", label: "Ergebnisse", icon: Activity },
  { id: "help", label: "Hilfe", icon: HelpCircle },
] as const;
const models: { id: ModelName; label: string }[] = [
  { id: "balance", label: "Kfz / Sach" }, { id: "life", label: "Leben" },
  { id: "health", label: "Kranken" }, { id: "four-sector-balance", label: "Gesamtbilanz" },
  { id: "capital", label: "Kapitalwirkung" }, { id: "strategies", label: "Strategien" },
  { id: "execution", label: "Ausführung" },
];
const RouteContext = createContext<Route>({ area: "overview", model: "balance" });

function readRoute(previousModel: ModelName = "balance"): Route {
  const hash = window.location.hash.slice(1);
  if (models.some((model) => model.id === hash)) return { area: "simulation", model: hash as ModelName };
  if (hash === "scenarios" || hash === "runs" || hash === "scenario") return { area: "scenario", model: previousModel };
  if (hash === "validation" || hash === "help") return { area: "help", model: previousModel };
  if (hash === "simulation") return { area: "simulation", model: previousModel };
  if (hash === "results") return { area: "results", model: previousModel };
  return { area: "overview", model: previousModel };
}

export function Area({ name, children }: { name: AreaName; children: ReactNode }) {
  const route = useContext(RouteContext);
  return <div className="workbench-area" hidden={route.area !== name}>{children}</div>;
}

// Keep the same model instance mounted across navigation: inputs, evidence and
// explicit confirmations must retain their existing invalidation semantics.
export function ModelWorkspace({ model, children }: { model: ModelName; children: ReactNode }) {
  const route = useContext(RouteContext);
  const financial = model !== "strategies" && model !== "execution";
  const visible = (route.area === "simulation" && route.model === model) || (financial && route.area === "results");
  return <div className="model-workspace" data-model={model} hidden={!visible}>{children}</div>;
}

export function Disclosure({ title, children }: { title: string; children: ReactNode }) {
  return <details className="workbench-disclosure"><summary>{title}</summary><div>{children}</div></details>;
}

function initialTheme(): "light" | "dark" {
  try {
    const saved = localStorage.getItem("ims.theme");
    if (saved === "light" || saved === "dark") return saved;
  } catch { /* Storage restrictions must not prevent using the local application. */ }
  return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export default function WorkbenchShell({ children }: { children: ReactNode }) {
  const [route, setRoute] = useState<Route>(() => readRoute());
  const [theme, setTheme] = useState(initialTheme);
  const title = useRef<HTMLHeadingElement>(null);
  const previousRoute = useRef(route);
  useEffect(() => {
    const navigate = () => setRoute((previous) => readRoute(previous.model));
    window.addEventListener("hashchange", navigate);
    return () => window.removeEventListener("hashchange", navigate);
  }, []);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem("ims.theme", theme); } catch { /* Optional preference storage. */ }
  }, [theme]);
  useEffect(() => {
    document.title = `${areas.find((area) => area.id === route.area)?.label} · IMS Workbench`;
    if (previousRoute.current !== route) {
      title.current?.focus({ preventScroll: true });
      window.scrollTo({ top: 0 });
      previousRoute.current = route;
    }
    // Preserve the old direct link to the now collapsed validation details.
    if (window.location.hash === "#validation") {
      const target = document.getElementById("validation");
      const details = target?.closest("details");
      if (details) details.open = true;
      target?.scrollIntoView({ block: "start" });
    }
  }, [route]);
  return <RouteContext.Provider value={route}>
    <a className="skip-link" href="#workbench-content" onClick={(event) => {
      event.preventDefault(); title.current?.focus();
    }}>Zum Inhalt</a>
    <div className="shell" data-view={route.area}>
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">IMS</div><div><strong>Workbench</strong><span>Lokal auf Ihrem Rechner</span></div></div>
        <nav className="area-navigation" aria-label="Hauptnavigation">{areas.map(({ id, label, icon: Icon }) =>
          <a key={id} href={`#${id}`} className={route.area === id ? "active" : ""} aria-current={route.area === id ? "page" : undefined}>
            <Icon size={20} aria-hidden="true" /><span>{label}</span>
          </a>)}</nav>
        <p className="sidebar-note">Modellannahmen und Nachweise bleiben an jedem Ergebnis sichtbar.</p>
      </aside>
      <main className="content" id="workbench-content">
        <header className="topbar"><div><p className="eyebrow">IMS · Versicherungsmodelle</p>
          <h1 ref={title} tabIndex={-1}>{areas.find((area) => area.id === route.area)?.label}</h1></div>
          <button className="theme-toggle secondary-action" type="button" aria-label="Dunkelmodus" aria-pressed={theme === "dark"}
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
            {theme === "dark" ? <Sun size={18} aria-hidden="true" /> : <Moon size={18} aria-hidden="true" />}<span>{theme === "dark" ? "Hell" : "Dunkel"}</span>
          </button></header>
        <Area name="overview"><section className="welcome-panel">
          <p className="eyebrow">Vom Fall zur Entscheidung</p><h2>Versicherungsmodelle verstehen.<br />Wirkungen nachvollziehen.</h2>
          <p>Vergleichen Sie Annahmen, berechnen Sie vorhandene Modellfälle und prüfen Sie die Ergebnisse mit ihren Herkunftsnachweisen.</p>
          <a className="primary-action" href="#balance">Modellfall öffnen <ArrowRight size={18} aria-hidden="true" /></a>
        </section><div className="start-grid">
          <a href="#scenario"><FileText size={22} aria-hidden="true" /><strong>Szenario vorbereiten</strong><span>Lokale Szenario- und Laufmetadaten bearbeiten.</span></a>
          <a href="#results"><Activity size={22} aria-hidden="true" /><strong>Ergebnisse ansehen</strong><span>Berechnete und gespeicherte Fälle prüfen und exportieren.</span></a>
          <a href="#help"><HelpCircle size={22} aria-hidden="true" /><strong>Orientierung finden</strong><span>Bedienung, Freigaben und Modellgrenzen verstehen.</span></a>
        </div></Area>
        <Area name="simulation"><p className="area-intro">Wählen Sie einen vorhandenen Modellfall. Für Gesamtbilanz und Kapitalwirkung werden zuvor geprüfte Spartenquellen benötigt.</p>
          <nav className="model-navigation" aria-label="Modellfälle">{models.map(({ id, label }) =>
            <a key={id} href={`#${id}`} className={route.model === id ? "active" : ""} aria-current={route.model === id ? "page" : undefined}>{label}</a>)}</nav>
          {(route.model === "strategies" || route.model === "execution") && <p className="expert-notice">Expertenwerkzeuge: Die dort angezeigten Ausführungssperren und ausdrücklichen Freigaben gelten weiterhin.</p>}
        </Area>
        <Area name="scenario"><p className="area-intro">Hier verwalten Sie lokale Metadaten. Eine Änderung startet keine Simulation; Rechenannahmen bearbeiten Sie im jeweiligen Modellfall.</p></Area>
        <Area name="results"><p className="area-intro">Ergebnisse der aktuellen Sitzung und lokale Fallverläufe. Exporte enthalten weiterhin ihre fachlichen Grenzen und Nachweise.</p>
          <section className="panel results-empty"><h2>Noch keine Berechnung in dieser Sitzung</h2><p>Öffnen Sie einen Modellfall und berechnen Sie ihn. Bereits gespeicherte Lebens- und Krankenfälle finden Sie im Verlauf unten.</p>
            <a className="secondary-action" href="#balance">Zur Simulation <ArrowRight size={18} aria-hidden="true" /></a></section></Area>
        <Area name="help"><section className="panel help-guide"><h2>So arbeiten Sie mit der Workbench</h2>
          <ol><li><a href="#balance">Modellfall wählen</a> und Annahmen für Baseline und Variante eingeben.</li>
            <li>Berechnen, Unterschiede in Tabelle und Diagramm prüfen. Ungültige Eingaben lassen sich im selben Formular korrigieren.</li>
            <li><a href="#results">Ergebnisse</a> exportieren. Speichern erfolgt erst nach ausdrücklicher Freigabe; geänderte Eingaben entwerten abhängige Nachweise.</li></ol>
          <p>Alle Berechnungen und Daten bleiben lokal. Hell-/Dunkelmodus ist oben umschaltbar. Tabulator bewegt den Fokus; breite Tabellen sind innerhalb ihrer Fläche scrollbar.</p>
          <p>Die vorhandenen Seminar- und Bilanzmodelle sind keine gesetzliche Bilanz und kein regulatorischer SCR-/MCR-Nachweis. Der geführte Ablauf für das 100-Perioden-Managementlabor ist Gegenstand von AP3.</p>
        </section></Area>
        {children}
        <footer className="workbench-footer">IMS 2.x · Lokale Workbench · Annahmen, Herkunft und Freigaben bestimmen die Aussagekraft.</footer>
      </main>
    </div>
  </RouteContext.Provider>;
}
