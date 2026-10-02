import { createContext, useCallback, useContext, useState, type Dispatch, type ReactNode, type SetStateAction } from "react";
import type { SeminarInput, SeminarResult } from "./seminarPresentation";

export type Role = "ceo" | "cio" | "coo" | "cso_sales";
export const rolePaths: Record<Role, { label: string; question: string; explanation: string; links: { label: string; hash: string }[] }> = {
  ceo: { label: "CEO", question: "Welche Entscheidung verändert Ergebnis und Eigenkapital?", explanation: "Vergleichen Sie dieselbe VU und ihre vier Sparten. Der vollständige Modellmarkt folgt in den nächsten Paketen.", links: [{ label: "Bilanz vergleichen", hash: "overview" }, { label: "Kapitalwirkung prüfen", hash: "capital" }] },
  cio: { label: "CIO", question: "Welche technische Abhängigkeit gefährdet das Geschäft?", explanation: "ICT/DORA hat einen eigenen Workshoppfad mit Ausfall und Wiederanlauf. Seine Betriebsverluste sind nicht in die Seminarbilanz eingebucht.", links: [{ label: "DORA / ICT verstehen", hash: "ict" }, { label: "Seminarquellen prüfen", hash: "seminar" }] },
  coo: { label: "COO", question: "Wie entstehen Rückstand, Nacharbeit und Wiederanlauf?", explanation: "Prüfen Sie den getrennten ICT-Prozessfall. In der Seminarbilanz sind Schäden und Leistungen erklärte Eingaben; sie folgen keinem Kundenwechsel.", links: [{ label: "Prozesse und Rückstand", hash: "ict" }, { label: "Buchung nachvollziehen", hash: "seminar" }] },
  cso_sales: { label: "CSO Vertrieb", question: "Warum wählen Kunden ein anderes Angebot?", explanation: "Verfolgen Sie benannte Kundengruppen vom Preisangebot bis zur gedeckten Menge und gebuchten Prämie.", links: [{ label: "Preis und Kundenwahl", hash: "overview" }, { label: "Strategie bearbeiten", hash: "seminar" }] },
};
export type Snapshot = { input: SeminarInput | null; result: SeminarResult | null; title: string; demo: boolean; busy: boolean; error: string | null; hadResult: boolean };
const initial: Snapshot = { input: null, result: null, title: "", demo: false, busy: false, error: null, hadResult: false };
type Session = {
  role: Role; setRole: Dispatch<SetStateAction<Role>>;
  snapshot: Snapshot; setSnapshot: Dispatch<SetStateAction<Snapshot>>;
  demoRequest: { caseId: string; serial: number } | null; requestDemo: (caseId: string) => void;
};
const Context = createContext<Session | null>(null);
export function ManagementSessionProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<Role>("ceo"), [snapshot, setSnapshot] = useState(initial);
  const [demoRequest, setDemoRequest] = useState<Session["demoRequest"]>(null);
  const requestDemo = useCallback((caseId: string) => setDemoRequest(previous => ({ caseId, serial: (previous?.serial ?? 0) + 1 })), []);
  return <Context.Provider value={{ role, setRole, snapshot, setSnapshot, demoRequest, requestDemo }}>{children}</Context.Provider>;
}
export function useManagementSession() {
  const value = useContext(Context);
  if (!value) throw new Error("Managementsicht benötigt die bestehende Workbench-Sitzung.");
  return value;
}
export function RolePicker() {
  const { role, setRole } = useManagementSession();
  return <label className="role-picker">Meine Rolle<select aria-label="Meine Rolle" value={role} onChange={event => setRole(event.target.value as Role)}>{Object.entries(rolePaths).map(([id, path]) => <option key={id} value={id}>{path.label}</option>)}</select></label>;
}
export function RoleOrientation() {
  const { role } = useManagementSession(), path = rolePaths[role];
  return <section className="role-orientation" aria-label={`Orientierung für ${path.label}`}><div><strong>{path.label}: {path.question}</strong><p>{path.explanation}</p></div><nav aria-label="Aufgaben meiner Rolle">{path.links.map(link => <a className="secondary-action" key={link.label} href={`#${link.hash}`}>{link.label}</a>)}</nav></section>;
}
