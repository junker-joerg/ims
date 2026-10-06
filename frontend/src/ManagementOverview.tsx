import { useEffect, useRef, useState } from "react";
import { ArrowRight, CalendarDays, CheckCircle2, Database, FolderOpen, TrendingUp } from "lucide-react";
import { useManagementSession } from "./ManagementSession";
import { amountText, amountUnits, cumulativeFlows, percentText, sectorNames, type SeminarResult, type Side } from "./seminarPresentation";
import SeminarExplanation from "./SeminarExplanation";
import "./ManagementOverview.css";

const demos = [
  { id: "price", title: "Preis und Anbieterwechsel", description: "Ein höherer Preis kann Kunden zum konkurrierenden Angebot führen. Verfolgen Sie Menge, Prämie und Werbung." },
  { id: "inflation", title: "Kosten und Beitragsreaktion", description: "Vergleichen Sie erklärte höhere Schaden-/Leistungskosten mit einer begrenzten Beitragsreaktion." },
  { id: "capital", title: "Lebens-Anlageentscheidung", description: "Ein Anlagesatz wirkt auf die Anfangsaktiva und über die Fortschreibung auf spätere Perioden." },
];
function Timeline({ result, period }: { result: SeminarResult; period: number }) {
  const baseline = result.sides.baseline.total_rows, variant = result.sides.variant.total_rows;
  const values = [...baseline, ...variant].map(row => Number(row.closing_equity));
  const minimum = Math.min(0, ...values), maximum = Math.max(0, ...values), range = maximum - minimum || 1;
  const x = (index: number) => 56 + index / Math.max(result.period_count - 1, 1) * 560;
  const y = (value: number) => 218 - (value - minimum) / range * 170;
  const line = (side: Side) => result.sides[side].total_rows.map((row, index) => `${index ? "L" : "M"}${x(index).toFixed(2)},${y(Number(row.closing_equity)).toFixed(2)}`).join(" ");
  return <><svg className="management-chart" viewBox="0 0 640 268" role="img" aria-label={`Eigenkapitalverlauf Baseline und Variante über ${result.period_count} Modellperioden. Ausgewählt P${period}. Exakte Werte stehen in der Datentabelle.`}>
    {[0, 1, 2, 3, 4].map(tick => { const value = minimum + tick / 4 * range; return <g key={tick}><line x1="56" x2="616" y1={y(value)} y2={y(value)} className="chart-grid" /><text x="48" y={y(value) + 4} textAnchor="end">{Math.round(value).toLocaleString("de-DE")}</text></g>; })}
    <path d={line("baseline")} className="baseline-line" /><path d={line("variant")} className="variant-line" />
    <line x1={x(period - 1)} x2={x(period - 1)} y1="44" y2="222" className="chart-cursor" />
    <text x="56" y="242">1</text><text x="616" y="242" textAnchor="end">{result.period_count}</text><text x="336" y="262" textAnchor="middle">Modellperiode</text>
  </svg><div className="chart-legend"><span><i className="baseline-key" />Baseline</span><span><i className="variant-key" />Variante</span></div>
  <details><summary>Exakte Verlaufstabelle öffnen</summary><div className="table-scroll" role="region" aria-label="Eigenkapitalverlauf als Tabelle" tabIndex={0}><table><caption>Eine VU · Schluss-Eigenkapital und Periodenergebnis in Modellwährung</caption><thead><tr><th>Periode</th><th>Eigenkapital Baseline</th><th>Eigenkapital Variante</th><th>Ergebnis Baseline</th><th>Ergebnis Variante</th></tr></thead><tbody>{baseline.map((row, index) => <tr key={row.period}><td>{row.period}</td><td>{amountText(row.closing_equity)}</td><td>{amountText(variant[index].closing_equity)}</td><td>{amountText(row.period_profit)}</td><td>{amountText(variant[index].period_profit)}</td></tr>)}</tbody></table></div></details></>;
}

export default function ManagementOverview() {
  const { snapshot, requestDemo } = useManagementSession(), { input, result, title, demo, busy, error, hadResult } = snapshot;
  const [side, setSide] = useState<Side>("variant"), [period, setPeriod] = useState(100), [sector, setSector] = useState("motor");
  const chooser = useRef<HTMLDetailsElement>(null);
  useEffect(() => {
    if (result) { setPeriod(result.period_count); setSector(input?.case_id === "capital" ? "life" : input?.case_id === "inflation" ? "health" : "motor"); }
  }, [result, input?.case_id]);
  const selectedPeriod = result ? Math.min(period, result.period_count) : period;
  const row = result?.sides[side].total_rows[selectedPeriod - 1], base = result?.sides.baseline.total_rows[selectedPeriod - 1], variant = result?.sides.variant.total_rows[selectedPeriod - 1];
  const ready = !!result && !busy && !error;
  const status = error ? "Prüfung fehlgeschlagen" : busy ? "Quellen werden geprüft und gerechnet …" : result ? "Lauf abgeschlossen" : hadResult ? "Ergebnis veraltet – neu berechnen" : input ? "Eingaben geladen – noch kein Lauf" : "Noch kein Szenario geöffnet";
  function openChooser() { if (chooser.current) { chooser.current.open = true; chooser.current.querySelector<HTMLButtonElement>("button")?.focus(); chooser.current.scrollIntoView({ block: "start" }); } }
  function explain() { const heading = document.getElementById("explain-heading"); heading?.focus(); heading?.scrollIntoView({ block: "start" }); }
  return <div className="management-overview" data-testid="management-overview">
    <div className="management-intro"><div><p className="eyebrow">IMS · Managementlabor</p><h2>Entscheidungen verstehen.</h2><p>Szenarien vergleichen. Wirkungen nachvollziehen.</p></div><button className="primary-action" type="button" onClick={openChooser} disabled={busy}><FolderOpen size={20} aria-hidden="true" />Szenario öffnen</button></div>
    <details className="panel demo-chooser" ref={chooser} open={!result}>
      <summary>Drei vorhandene Demofälle – ohne Expertenformular beginnen</summary><p>Die vollständigen AP3-Fälle werden offline frisch geprüft und gerechnet. Sie öffnen eine schreibfreie Demo. Eigene Änderungen sind anschließend im Managementseminar möglich.</p>
      <div className="demo-grid">{demos.map(item => <article key={item.id}><h3>{item.title}</h3><p>{item.description}</p><button type="button" className="secondary-action" disabled={busy} onClick={() => requestDemo(item.id)} aria-label={`Demo öffnen: ${item.title}`}>Demo öffnen <ArrowRight size={18} aria-hidden="true" /></button></article>)}</div>
    </details>
    <section className="panel management-case"><div><h2>{input && title ? title : "Seminarfall einer VU"}</h2><p>Seminarfall einer VU{result ? ` · VU ${result.insurer_id}` : ""} · vier Modellsparten · erklärte Modellwährung</p></div><p className={`management-status${error ? " failed" : ""}`} role="status" data-testid="management-run-status">{ready && <CheckCircle2 size={18} aria-hidden="true" />}{status}</p></section>
    {error && <p role="alert" className="ict-error">{error} Öffnen Sie den Demofall erneut oder korrigieren Sie die Eingaben im <a href="#seminar">Managementseminar</a>.</p>}
    {!ready && <section className="panel management-empty"><h2>{hadResult ? "Der frühere Ergebnisstand gilt nicht mehr." : "In drei Schritten zum ersten Vergleich"}</h2><ol><li>Unter Szenario öffnen einen vorhandenen Demofall wählen.</li><li>Baseline und Variante vergleichen, dann eine Modellperiode auswählen.</li><li>Warum verändert sich der Wert? öffnen und die Buchung bis zur Bilanz verfolgen.</li></ol><p>{hadResult ? "Nach neuen Eingaben bleiben Kennzahlen und Diagramme ausgeblendet, bis die vollständigen Quellen erneut geprüft und gerechnet sind." : "Es werden erst nach einem erfolgreichen Lauf Kennzahlen und Diagramme gezeigt."}</p><a className="secondary-action" href="/api/seminar/handbook/management_ap4.html" target="_blank" rel="noreferrer">Einsteigeranleitung und 15-Minuten-Übung</a></section>}
    {ready && row && base && variant && result && input && <div data-testid="management-checked-results">
      <div className="management-controls"><div className="comparison-toggle" role="group" aria-label="Vergleichsseite">{(["baseline", "variant"] as const).map(value => <button type="button" key={value} aria-pressed={side === value} onClick={() => setSide(value)}>{value === "baseline" ? "Baseline" : "Variante"}</button>)}</div><label>Kennzahlen und Erklärweg für Modellperiode<select aria-label="Übersichtsperiode" value={selectedPeriod} onChange={event => setPeriod(Number(event.target.value))}>{Array.from({ length: result.period_count }, (_, index) => <option key={index + 1}>{index + 1}</option>)}</select></label><span>{demo ? "Geprüfte Demo · schreibfrei" : "Geprüfte Sitzung"}</span></div>
      <div className="management-kpis">
        <article className="panel kpi"><Database aria-hidden="true" /><h3>Periodenergebnis · P{selectedPeriod}</h3><strong data-testid="kpi-profit">{amountText(row.period_profit)}</strong><p>Modellwährung · {side === "baseline" ? "Baseline" : "Variante"}</p><details><summary>Was bedeutet das?</summary><p>Ergebnis dieser einen Periode; kein Eigenkapitalbestand und keine Summe aller Prämien. Variante minus Baseline in P{selectedPeriod}: {amountText(amountUnits(variant.period_profit) - amountUnits(base.period_profit), true)}.</p><button type="button" onClick={explain}>Warum verändert sich das Ergebnis?</button></details></article>
        <article className="panel kpi"><TrendingUp aria-hidden="true" /><h3>Schluss-Eigenkapital · P{selectedPeriod}</h3><strong data-testid="kpi-equity">{amountText(row.closing_equity)}</strong><p data-testid="kpi-equity-percent">Variante gegenüber Baseline: {percentText(variant.closing_equity, base.closing_equity)}</p><details><summary>Was bedeutet das?</summary><p>Aktiva abzüglich Passiva am Periodenende. Absolute Differenz Variante minus Baseline: {amountText(amountUnits(variant.closing_equity) - amountUnits(base.closing_equity), true)}. Prozentwert: Differenz geteilt durch den Betrag des Baseline-Eigenkapitals × 100; bei Baseline 0 nicht definiert. Es ist keine regulatorische Kapitalquote.</p><button type="button" onClick={explain}>Warum verändert sich das Eigenkapital?</button></details></article>
        <article className="panel kpi"><CalendarDays aria-hidden="true" /><h3>Abgeschlossene Modellperioden</h3><strong data-testid="kpi-periods">{result.period_count}</strong><p>Aus dem vollständig geprüften Lauf</p><details><summary>Was bedeutet das?</summary><p>Der Lauf endet bei P{result.period_count}. Die ausgewählte Periode ist P{selectedPeriod}. Eine Modellperiode ist nicht automatisch ein Kalendertag oder ein Versicherungsjahr.</p></details></article>
      </div>
      <div className="management-charts"><section className="panel"><h2>Eigenkapitalverlauf</h2><p>Baseline und Variante · Schlussbestände einer VU · Modellwährung</p><Timeline result={result} period={selectedPeriod} /></section><section className="panel"><h2>Vier Sparten · P{selectedPeriod}</h2><p>Schluss-Eigenkapital im selben Modellfall. Breite zeigt den Betrag; das Vorzeichen steht am Wert.</p><div className="sector-comparison">{result.sides[side].sectors.map(item => {
        const current = item.rows[selectedPeriod - 1], reference = result.sides.baseline.sectors.find(candidate => candidate.sector_id === item.sector_id)!.rows[selectedPeriod - 1];
        const maximum = Math.max(1, ...result.sides[side].sectors.map(candidate => Math.abs(Number(candidate.rows[selectedPeriod - 1].closing_equity))));
        return <button type="button" className="sector-entry" key={item.sector_id} onClick={() => { setSector(item.sector_id); explain(); }} aria-label={`${sectorNames[item.sector_id]} erklären`}><span>{sectorNames[item.sector_id]}</span><strong data-testid={`sector-equity-${item.sector_id}`}>{amountText(current.closing_equity)}</strong><span className="sector-bar" aria-hidden="true"><i style={{ width: `${Math.abs(Number(current.closing_equity)) / maximum * 100}%` }} /></span><small>Gegenüber Baseline: {amountText(amountUnits(current.closing_equity) - amountUnits(reference.closing_equity), true)}</small></button>;
      })}</div><p>Ein Klick erklärt die Buchung dieser Sparte. Dies ist keine Markt- oder Strategiefamiliensumme.</p></section></div>
      <section className="panel cumulative-flows"><h2>Kumulierte gezeigte Flüsse · P1–P{selectedPeriod}</h2><p>Diese Einnahmen und Ausgaben werden aus den gebuchten Entscheidungstraces addiert. Sie bilden gemeinsam noch kein Ergebnis: weitere Kosten, Schäden und Kapitalflüsse stehen in der vollständigen Bilanz.</p><dl>{Object.entries(cumulativeFlows(result.decision_traces[side], selectedPeriod)).map(([name, value]) => <div key={name}><dt>{({ premium: "Prämien / Beiträge", advertising: "Werbeaufwand", investment: "Lebens-Anlageertrag" } as Record<string, string>)[name]}</dt><dd data-testid={`cumulative-${name}`}>{amountText(value)}</dd></div>)}</dl></section>
      <SeminarExplanation input={input} result={result} side={side} period={selectedPeriod} sector={sector} setSector={setSector} />
      <section className="panel management-next"><div><h2>Nächster Schritt</h2><p>Eine Buchung erklären oder im Managementseminar eine eigene Variante übernehmen und neu berechnen.</p></div><a href="#seminar" className="primary-action">Managementseminar öffnen <ArrowRight size={18} aria-hidden="true" /></a></section>
      <details className="panel"><summary>Ergebnisnachweis und weitere Grenzen</summary><p>Gemeinsamer Ergebnisnachweis <code>{result.content_digest}</code>. Baseline <code>{result.sides.baseline.content_digest}</code>, Variante <code>{result.sides.variant.content_digest}</code>. Exporte der Einzel-VU im <a href="#seminar">Managementseminar</a> verwenden dieselben geprüften Quellen.</p><p>Die vorbereiteten Fälle sind unkalibrierte Workshop-Annahmen. Preisangebote anderer VUs werden für die Kundenwahl berücksichtigt, ihre Bilanzen bleiben außerhalb dieser Ansicht. ICT und historischer 100er-Lauf bleiben getrennte Quellenpfade. Die vier Markt-Schockfälle und der BaFin-Referenzmarkt sind unter „Markt und Strategien“ erreichbar. Der deutsche Direktmarkt bleibt unbelegt.</p></details>
    </div>}
  </div>;
}
