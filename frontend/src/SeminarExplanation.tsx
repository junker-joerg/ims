import { amountText, amountUnits, parameterNames, profitReconciliation, ruleNames, sectorNames, type SeminarInput, type SeminarResult, type Side } from "./seminarPresentation";

const shown = (value: string | number) => String(value).replace(".", ",");
export default function SeminarExplanation({ input, result, side, period, sector, setSector }: {
  input: SeminarInput; result: SeminarResult; side: Side; period: number; sector: string; setSector: (value: string) => void;
}) {
  const trace = result.decision_traces[side].find(item => item.period === period && item.sector_id === sector);
  if (!trace) return <p>Für diese Periode ist keine Entscheidungskette vorhanden.</p>;
  const assignments = input.strategies[side].filter(item => item.sector_id === sector && item.period_from <= period && item.period_through >= period);
  const balance = trace.model_balance, comparison = profitReconciliation(result, period);
  const next = result.sides[side].sectors.find(item => item.sector_id === sector)?.rows[period];
  return <section className="panel explanation-panel" aria-labelledby="explain-heading" data-testid="decision-explanation">
    <p className="eyebrow">Eingabe → Regel → Entscheidung → Buchung</p>
    <h2 id="explain-heading" tabIndex={-1}>Warum verändert sich der Wert?</h2>
    <label>Sparte erklären<select aria-label="Sparte erklären" value={sector} onChange={event => setSector(event.target.value)}>{result.sides[side].sectors.map(item => <option key={item.sector_id} value={item.sector_id}>{sectorNames[item.sector_id]}</option>)}</select></label>
    <p>{side === "baseline" ? "Baseline" : "Variante"} · Modellperiode {period} · bilanzierte VU {result.insurer_id} · Modellwährung</p>
    <ol className="causal-chain">
      <li><h3>Welche Eingabe gilt jetzt?</h3>
        {assignments.map((item, index) => <p key={index}><strong>{item.target_id}</strong> · {ruleNames[item.strategy_id] ?? item.strategy_id} · P{item.period_from}–P{item.period_through}: {Object.entries(item.parameters).map(([name, value]) => `${parameterNames[name] ?? name} ${shown(value)}`).join("; ")}</p>)}
        {assignments.length === 0 && <p>Es gilt der erklärte Anfangs-/Quellenplan dieser Sparte.</p>}
        {trace.draws && <p>Vorgegebene Ziehungen: {trace.draws.map(shown).join("; ")}. Diese kontrollierten Werte sind keine zufällig neu erzeugte Stichprobe.</p>}
      </li>
      <li><h3>Welche Regel wurde ausgeführt?</h3>
        {trace.quoted_price !== undefined ? <><p>{ruleNames[trace.strategy_id ?? ""] ?? trace.strategy_id}. {period === 1 ? "Periode 1 behält die deklarierten Anfangsangebote." : "Der vorhandene VU-Regelkern liefert das Preis-/Werbeziel aus den gültigen Parametern und Ziehungen."}</p><p>Ausgegebenes Preisziel: {amountText(trace.quoted_price)} je gedeckter Exposition. Preisziel und gesamte Prämieneinnahme sind getrennte Größen.</p></> : <><p>{trace.source_decisions?.map(item => ruleNames[item.strategy_id] ?? item.strategy_id).join("; ") || "Deklarierter Quellenplan"}.</p><p>{sector === "life" ? "Der Anlagesatz wirkt auf die tatsächlichen Anfangsaktiva der Periode. Die Garantien und der Altbestand bleiben erhalten." : "Der Krankenbeitrag wirkt auf die Anfangspolicen; Neugeschäft und Abgänge verändern den Bestand für die Folgeperiode."}</p></>}
      </li>
      <li><h3>Wie entscheiden die Kunden?</h3>
        {trace.group_decisions ? <><p>{period === 1 ? "Der erklärte Anfangsvertrag gilt." : "Die ausgewiesene Kundenregel prüft die Versicherungsschwelle und wählt bei Beste Information das günstigste aktive Angebot. Gleiche Preise entscheidet die aufsteigende VU-ID."}</p>
          <ul>{trace.group_decisions.map(group => <li key={group.group_id}>{group.group_id} · {ruleNames[group.strategy_id ?? ""] ?? group.strategy_id}: {group.chosen_insurer_id === null ? "unversichert" : `gewählt VU ${group.chosen_insurer_id}`} · erklärte Exposition {shown(group.declared_exposure ?? "–")} · bei VU {result.insurer_id} gebucht {amountText(group.booked_premium)}.</li>)}</ul></> : <p>{sector === "life" ? "Dieser Lebensfall enthält keine ausgeführte Kundennachfrageregel." : "Neugeschäft und Abgänge sind deklarierte Größen, keine ausgeführte Preisnachfrage."}</p>}
      </li>
      <li><h3>Was wird tatsächlich gebucht?</h3>
        {trace.quoted_price !== undefined ? <><p data-testid="explained-premium">Preis {amountText(trace.quoted_price)} × gedeckte Exposition {amountText(trace.covered_exposure!)} = Prämie {amountText(trace.premium_income!)}.</p><p>Zusätzlicher Werbeaufwand: {amountText(trace.advertising_expense!)}. Schäden und Schadenleistungen bleiben exogene Eingaben, auch wenn Kunden wechseln.</p></> : <dl className="explanation-values">{Object.entries(trace.generated_period_source ?? {}).filter(([name]) => !["period", "start_period", "end_period"].includes(name)).map(([name, value]) => <div key={name}><dt>{({ opening_backing_assets: "Anfangsaktiva", investment_result: "Anlageertrag", opening_policies: "Anfangspolicen", premium_income: "Beitragseinnahme", new_business: "Neugeschäft", exits: "Abgänge", benefits_paid_exogenous: "Exogene Leistungszahlung", ...parameterNames } as Record<string, string>)[name] ?? name}</dt><dd>{shown(value)}</dd></div>)}</dl>}
      </li>
      <li><h3>Wie kommt die Buchung in die Bilanz?</h3>
        <p>Anfangs-Eigenkapital {amountText(balance.opening_equity)} + Periodenergebnis {amountText(balance.period_profit)} + Kapitalzuführung {amountText(balance.capital_contribution)} − Ausschüttung {amountText(balance.capital_distribution)} = Schluss-Eigenkapital {amountText(balance.closing_equity)}.</p>
        <p>Aktiva {amountText(balance.closing_assets)} = Passiva {amountText(balance.closing_liabilities)} + Eigenkapital {amountText(balance.closing_equity)}.</p>
        <p>Carryover heißt Fortschreibung: Schlussaktiva {amountText(balance.closing_assets)} {next ? `werden Anfangsaktiva ${amountText(next.opening_assets)} in P${period + 1}.` : "bilden den Anschlusswert für eine mögliche Folgeperiode; der geprüfte Lauf endet hier."}</p>
      </li>
    </ol>
    <div className="reconciliation" data-testid="profit-reconciliation"><h3>Variante gegenüber Baseline bis P{period}</h3>
      {comparison.constant && <p>Gebuchte Ergebnisdifferenz je veränderter Periode: {amountText(comparison.firstDifference, true)}. P{comparison.changed[0].period}–P{comparison.changed.at(-1)!.period}: <strong>{amountText(comparison.firstDifference, true)} × {comparison.changed.length} = {amountText(comparison.totalProfit, true)}</strong>.</p>}
      {!comparison.constant && <p>Summe der tatsächlichen Periodenergebnisdifferenzen: {amountText(comparison.totalProfit, true)}.</p>}
      <p>Differenz der Nettokapitalflüsse: {amountText(comparison.totalCapital, true)}. Tatsächliche Eigenkapitaldifferenz in P{period}: {amountText(amountUnits(result.sides.variant.total_rows[period - 1].closing_equity) - amountUnits(result.sides.baseline.total_rows[period - 1].closing_equity), true)}.</p>
      <p>Dies ist eine Abstimmung der Buchungswerte. Bei mehreren gleichzeitigen Änderungen weist sie allein noch keine einzelne Ursache oder Wechselwirkung nach.</p>
    </div>
    <details><summary>Technische Herkunft und Grenzen</summary><p>Preis/Werbung: IMS.E Vrvu01; Kundenwahl: IMS.E Vrvn06. Moderne AP3-Abrechnung und Vier-Sparten-Bilanz prüfen gemeinsame Anfangsperioden und Fortschreibung. Alte Begriffe und moderne Modellkanäle sind in der <a href="/api/seminar/handbook/management_ap4.html" target="_blank" rel="noreferrer">Einsteigeranleitung</a> erklärt.</p><p>Geprüfter Ergebnisnachweis <code>{result.content_digest}</code>. Nur diese VU wird bilanziert; konkurrierende Angebote sind keine weiteren Unternehmensbilanzen. Kein gesetzlicher Bilanz-, SCR/MCR- oder DORA-Konformitätsnachweis.</p></details>
  </section>;
}
