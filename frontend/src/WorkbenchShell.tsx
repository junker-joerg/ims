import { Fragment, createContext, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { Activity, ArrowRight, BarChart3, FileText, HelpCircle, Home, Moon, Play, Sun } from "lucide-react";
import ReleaseBadge from "./ReleaseBadge";
import ManagementOverview from "./ManagementOverview";
import ExperimentLanding from "./ExperimentLanding";
import { ManagementSessionProvider, RoleOrientation, RolePicker, useManagementSession } from "./ManagementSession";

type AreaName = "overview" | "scenario" | "simulation" | "results" | "help";
type ModelName = "balance" | "life" | "health" | "four-sector-balance" | "management" | "seminar" | "market" | "capital" | "ict" | "hundred" | "strategies" | "execution";
type Route = { area: AreaName; model: ModelName };
const areas = [
  { id: "overview", label: "Übersicht", icon: Home },
  { id: "scenario", label: "Fallablage", icon: FileText },
  { id: "simulation", label: "Modellwerkzeuge", icon: Play },
  { id: "results", label: "Ergebnisse", icon: Activity },
  { id: "help", label: "Hilfe", icon: HelpCircle },
] as const;
const models: { id: ModelName; label: string }[] = [
  { id: "balance", label: "Kfz / Sach" }, { id: "life", label: "Leben" },
  { id: "health", label: "Kranken" }, { id: "four-sector-balance", label: "Gesamtbilanz" },
  { id: "capital", label: "Kapitalwirkung" }, { id: "strategies", label: "Strategien" },
  { id: "ict", label: "ICT-Wirkung" },
  { id: "hundred", label: "100-Perioden-Lauf" },
  { id: "management", label: "100er-Gesamtbilanz" },
  { id: "seminar", label: "Managementseminar" },
  { id: "market", label: "Markt und Strategien" },
  { id: "execution", label: "Ausführung" },
];
const RouteContext = createContext<Route>({ area: "overview", model: "balance" });

function readRoute(previousModel: ModelName = "balance"): Route {
  const hash = window.location.hash.slice(1);
  if (models.some((model) => model.id === hash)) return { area: "simulation", model: hash as ModelName };
  if (hash === "scenarios" || hash === "runs" || hash === "scenario") return { area: "scenario", model: previousModel };
  if (hash === "validation" || hash === "help") return { area: "help", model: previousModel };
  if (hash === "simulation") return { area: "simulation", model: previousModel === "market" ? "balance" : previousModel };
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
  const financial = model !== "strategies" && model !== "execution" && model !== "hundred";
  const visible = (route.area === "simulation" && route.model === model) || (financial && route.area === "results" && route.model === model);
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
  return <ManagementSessionProvider><WorkbenchLayout>{children}</WorkbenchLayout></ManagementSessionProvider>;
}

function WorkbenchLayout({ children }: { children: ReactNode }) {
  const { role } = useManagementSession();
  const previousRole = useRef(role), roleGuidance = useRef<HTMLDetailsElement>(null);
  const [route, setRoute] = useState<Route>(() => readRoute());
  const [theme, setTheme] = useState(initialTheme);
  const marketActive = route.area === "simulation" && route.model === "market";
  const areaTitle = marketActive ? "Markt und Strategien" : areas.find(area => area.id === route.area)?.label;
  const title = useRef<HTMLHeadingElement>(null);
  const previousRoute = useRef(route);
  useEffect(()=>{if(role!==previousRole.current&&roleGuidance.current)roleGuidance.current.open=true;previousRole.current=role;},[role]);
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
    document.title = `${areaTitle} · IMS Workbench`;
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
        <div className="brand"><div className="brand-mark">IMS<span className="brand-dot"/></div><div><strong>Managementlabor</strong><span>STRATEGIE. MARKT. WIRKUNG.</span></div></div>
        <div className="sidebar-navigation">
          <nav className="area-navigation" aria-label="Hauptnavigation">{areas.map(({ id, label, icon: Icon }) =>
            <Fragment key={id}>
            <a href={`#${id}`} className={route.area === id && !marketActive ? "active" : ""} aria-current={route.area === id && !marketActive ? "page" : undefined}>
              <Icon size={20} aria-hidden="true" /><span>{label}</span>
            </a>
            {id === "overview" && <a href="#market" className={marketActive ? "active" : ""} aria-current={marketActive ? "page" : undefined}>
              <BarChart3 size={20} aria-hidden="true" /><span>Markt und Strategien</span>
            </a>}
            </Fragment>)}</nav>
          <div className="sidebar-lab"><span className="lab-dot"/> LOKALES SIMULATIONSLABOR</div><p className="sidebar-note">Strategien entscheiden.<br/>Umwelt verändern.<br/>Wirkung verstehen.</p>
          <ReleaseBadge />
        </div>
      </aside>
      <main className="content" id="workbench-content">
        <header className="topbar"><div><p className="eyebrow">IMS · Versicherungsmodelle</p>
          <h1 ref={title} tabIndex={-1}>{areaTitle}</h1></div>
          <div className="topbar-actions"><RolePicker /><button className="theme-toggle secondary-action" type="button" aria-label="Dunkelmodus" aria-pressed={theme === "dark"}
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
            {theme === "dark" ? <Sun size={18} aria-hidden="true" /> : <Moon size={18} aria-hidden="true" />}<span>{theme === "dark" ? "Hell" : "Dunkel"}</span>
          </button></div></header><details className="role-guidance" ref={roleGuidance}><summary>Hinweise für meine Rolle</summary><RoleOrientation /></details>
        <Area name="overview"><ExperimentLanding /><div className="section-kicker"><span>EINZEL-VU / MANAGEMENTSEMINAR</span><h2>Vorhandene Entscheidungsfälle</h2><p>Drei erklärte Demos mit einer bilanzierten VU. Die gemeinsame Marktsimulation öffnen Sie oben.</p></div><ManagementOverview /></Area>
        <Area name="simulation">{!marketActive && <><p className="area-intro">Aktueller Modellfall: <strong>{models.find(model => model.id === route.model)?.label}</strong>. Wechseln Sie zu einem anderen Modellfall oder öffnen Sie weitere Werkzeuge.</p>
          <nav className="model-navigation" aria-label="Modellfälle">{models.filter(model => ["balance", "life", "health", "seminar"].includes(model.id)).map(({ id, label }) =>
            <a key={id} href={`#${id}`} className={route.model === id ? "active" : ""} aria-current={route.model === id ? "page" : undefined}>{label}</a>)}</nav>
          <details className="model-tools"><summary>Weitere Modellwerkzeuge</summary><div className="model-tool-groups">
            {[{ title: "Bilanzen und Kapital", ids: ["four-sector-balance", "capital", "management"] },
              { title: "Prozesse und längere Läufe", ids: ["ict", "hundred"] },
              { title: "Expertenwerkzeuge", ids: ["strategies", "execution"] }].map(group => <section key={group.title}><h2>{group.title}</h2>
                {models.filter(model => group.ids.includes(model.id)).map(model => <a key={model.id} href={`#${model.id}`} aria-current={route.model === model.id ? "page" : undefined}>{model.label}</a>)}
              </section>)}
          </div></details></>}
          {(route.model === "strategies" || route.model === "execution") && <p className="expert-notice">Expertenwerkzeuge: Die dort angezeigten Ausführungssperren und ausdrücklichen Freigaben gelten weiterhin.</p>}
        </Area>
        <Area name="scenario"><p className="area-intro">Hier verwalten Sie lokale Metadaten. Eine Änderung startet keine Simulation; Rechenannahmen bearbeiten Sie im jeweiligen Modellfall.</p></Area>
        <Area name="results"><p className="area-intro">Ergebnisbereich des zuletzt geöffneten Modellfalls: <strong>{models.find(model=>model.id===route.model)?.label}</strong>. Ein Wechsel des Modells erfolgt im jeweiligen Arbeitsbereich.</p>
          <section className="panel results-empty"><h2>Noch keine Berechnung in dieser Sitzung</h2><p>Öffnen Sie einen Modellfall und berechnen Sie ihn. Bereits gespeicherte Lebens- und Krankenfälle finden Sie im Verlauf unten.</p>
            <a className="secondary-action" href="#balance">Zur Simulation <ArrowRight size={18} aria-hidden="true" /></a></section></Area>
        <Area name="help"><section className="panel help-guide"><h2>So arbeiten Sie mit der Workbench</h2>
          <ol><li><a href="#balance">Modellfall wählen</a> und Annahmen für Baseline und Variante eingeben.</li>
            <li>Berechnen, Unterschiede in Tabelle und Diagramm prüfen. Ungültige Eingaben lassen sich im selben Formular korrigieren.</li>
            <li><a href="#results">Ergebnisse</a> exportieren. Speichern erfolgt erst nach ausdrücklicher Freigabe; geänderte Eingaben entwerten abhängige Nachweise.</li></ol>
          <p>Alle Berechnungen und Daten bleiben lokal. Hell-/Dunkelmodus ist oben umschaltbar. Tabulator bewegt den Fokus; breite Tabellen sind innerhalb ihrer Fläche scrollbar.</p>
          <p><a href="/api/seminar/handbook/management_ap4.html" target="_blank" rel="noreferrer">Einsteigeranleitung AP4 mit 15-Minuten-Übung</a>: Demofall direkt von der Übersicht laden, Kennzahlen vergleichen und eine Buchung erklären. Die Übungszeit ist ein Ziel; ihre tatsächliche Dauer wird bei der Benutzerabnahme erfasst.</p>
          <p><a href="#market">Markt und Strategien</a>: Markt verstehen, Schocks bearbeiten und Quellen prüfen. <a href="/api/seminar/handbook/market_ap8.html" target="_blank" rel="noreferrer">Anleitung zu den sechs Marktansichten</a>. <a href="/api/seminar/handbook/market_ap5.html" target="_blank" rel="noreferrer">Handfälle und Marktgrundlagen</a>.</p>
          <dl className="beginner-glossary"><div><dt>VU</dt><dd>Anbieter / Versicherungsunternehmen; im Seminar wird eine VU bilanziert.</dd></div><div><dt>VN</dt><dd>Kunden / Versicherungsnehmer; benannte Gruppen tragen Expositionsgewichte.</dd></div><div><dt>BAV</dt><dd>Historischer Markt- und Koordinationskontext; keine heutige Aufsichtsberechnung.</dd></div><div><dt>Verhaltensregel</dt><dd>Ausgeführte Strategieregel mit Parametern und Zeitfenster.</dd></div><div><dt>Periode</dt><dd>Modellperiode; ihre zeitliche Einheit gehört zum jeweiligen Vertrag.</dd></div></dl>
          <p><a href="#seminar">Managementseminar öffnen</a>: moderne Strategiekopplung, benannte Gruppen, 100er-Bilanz und portable Fallbündel. Die <a href="/api/seminar/handbook/seminar_ap3.html" target="_blank" rel="noreferrer">aktuelle Seminaranleitung</a> mit Arbeitsblatt und realen Ergebnissen ist auch offline verfügbar.</p>
          <p>Die Seminar- und Bilanzmodelle sind keine gesetzliche Bilanz und kein regulatorischer SCR-/MCR-Nachweis. Die moderne Kopplung ist ausdrücklich erklärt; historische Spartenidentität und vollständiger Versicherungsmarkt bleiben offen.</p>
        </section></Area>
        {children}
        <footer className="workbench-footer">IMS 2.x · Lokale Workbench · Annahmen, Herkunft und Freigaben bestimmen die Aussagekraft.</footer>
      </main>
    </div>
  </RouteContext.Provider>;
}
