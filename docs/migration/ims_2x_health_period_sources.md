# PR169a: Kranken-Bestands- und Quellenvertrag

Stand: 2026-09-17
Eingang: `ims.health-period-sources-input.v1`
Pruefergebnis: `ims.health-period-sources-result.v1`
Schnittstelle: `ims.accounting.health_period_sources.validate_health_period_sources`

## Ursprung und Grenze

| Ursprung | IMS 2.x | Grenze |
| --- | --- | --- |
| `IMSDATA.C`: `MAXSPARTEN 2`, VU `Sp[1/2]`, VN `Rk[1/2]` | eigener `health`-Quellenplan je VU | `KV`, `Sp[2]` und `Rk[2]` sind **kein** belegtes historisches Krankenmodell. |
| `IMS.E`: Vorperiodenpraemien und Marktaggregate der zwei alten Positionen | explizite Periodenfenster und Bestandszahlen | keine automatische Uebernahme alter Preis-/Wechselregeln. |
| PR169: `ims.accounting.health_model_balance` | exakte Dezimalform und atomare Fehlerbefunde | der bisherige geschlossene Ein-/Zweiperiodenfall bleibt unveraendert. |

Der Quellenplan ist eine **neue IMS-2.x-Annahme**, nicht die Rekonstruktion
eines historischen Laufs. Ein `scenario_id` verbindet spaeter Baseline
und Varianten; `variant_id` benennt den einzelnen Plan. Der Pruefer
vergleicht Varianten noch nicht miteinander und erzeugt weder Bilanz
noch Ergebniszeilen.

## Eingabe

Das feste Beispiel steht in `tests/fixtures/health_period_sources_v1.json`.
Ein Plan nennt Vertragsversionen, `source_kind =
versioned_health_period_sources`, `historical_mapping_status = unresolved`,
`insurer_id` 1-25, `sector_id = health`, ASCII-Kennungen mit 1-40 Zeichen,
`period_count` 1-100 und `opening_active_policies` 0-1 Milliarde. Eine
Periode ist eine **IMS-Modellperiode**, kein Kalenderjahr.

| Feld | Akteur und Modus | Wert und zeitliche Wirkung |
| --- | --- | --- |
| `new_business` | `market`, `explicit_scenario_counts` | Genau eine nichtnegative ganze Zahl je Periode; Neugeschaeft wird am Periodenende aktiv. |
| `exits` | `policyholder`, `explicit_scenario_counts` | Genau eine nichtnegative ganze Zahl je Periode; nur zu Beginn aktive Vertraege duerfen am Periodenende abgehen. Dies ist eine Szenariozahl, keine ausgefuehrte VN-Strategie. |
| `pricing` | `insurer`, `explicit_insurer_price_windows` | Lueckenlose, ueberlappungsfreie Fenster mit Beitrag je Anfangsvertrag. Eine explizite VU-Entscheidung, kein automatisch ausgefuehrter Preisalgorithmus. |
| `benefits` | `exogenous`, `explicit_benefit_cost_windows` | Lueckenlose, ueberlappungsfreie Fenster mit angefallener Leistung je Anfangsvertrag. **Kein** frei abschaltbarer VU-Strategiehebel. |

Zu Periodenbeginn aktive Vertraege sind der Bezugsbestand fuer Beitrag und
Leistungsanfall der laufenden Periode, auch wenn ein Vertrag am Ende
abgeht. Neue Vertraege wirken erst in der Folgeperiode auf diese Fluesse.
Der rechnerische Schlussbestand ist `Anfang - Abgang + Neugeschaeft` und
liegt zwischen 0 und einer Milliarde. Ein Fensterbetrag ist ein
nichtnegativer Dezimalstring mit hoechstens 12 Vor- und vier
Nachkommastellen. Auch `Anfang * Stueckbetrag` muss in 12+4 Stellen
passen. Es gibt keine implizite Rundung oder Stochastik.

## Pruefung und offene Arbeit

Unbekannte, fehlende oder widerspruechliche Felder, Luecken, doppelte
Perioden, ueberlappende Fenster, falsche Akteure/Modi, Abgaenge ueber dem
Anfangsbestand und Grenzverletzungen erzeugen Befunde. Bei irgendeinem
Fehler ist `validated_period_count = 0`; der Bericht enthaelt **keine**
teilweise geprueften Perioden. Auch ein gueltiger Bericht enthaelt keine
berechneten Ergebnisse. Ein-/100-Perioden-Plaene sind lediglich
validierbar, nicht startbar.

PR169b muss diesen Plan mit einem getrennt geprueften Bilanzanfang sowie
Auszahlungs-, Anlage-, Aufwands- und Kapitalwerten verbinden und erst
dann die Periodenkette rechnen. Besonders `benefits_paid` ist die
Begleichung einer vorhandenen Leistungsverpflichtung, **keine** zweite
Leistungsannahme. Bestand, Bilanz und exakte Prefixe muessen gemeinsam
geprueft werden. PR169c fuegt kontrollierte Ablage/Exporte hinzu, PR169d
erst den Workbench-Start. Kein Runner, keine Speicherung, keine
gesetzliche Alterungsrueckstellung, keine Solvency-II-Aussage und keine
historische Vollgleichheitsbehauptung in PR169a.
