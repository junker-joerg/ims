# PR165: Kontrollierte Lebens-Periodenkette

Stand: 2026-09-17
Eingang: `ims.life-period-chain-input.v1`
Ergebnis: `ims.life-period-chain-result.v1`
Python: `ims.accounting.life_period_chain.run_life_policy_period_chain`

## Herkunft und Grenze

| Ursprung | Python-Ziel | Fachliche Grenze |
| --- | --- | --- |
| `IMSDATA.C` (`MAXSPARTEN 2`, `BAV.Zs`) und `IMS.E` (Periodenfolge und Verzinsung beider Schadenreserven) | Separater Lebens-Periodenpfad | Kein historischer Lebensbestand, keine Sterblichkeitsregel und keine historische Vollgleichheit belegt. |
| PR163: `build_life_policy_balance` | Jeder wachsende Prefix wird unveraendert als vollstaendiger Policenfall berechnet und geprueft | PR163-Eingang, Rundung, Abgangsfolge und Bilanzformeln bleiben unveraendert. |
| PR164: `resolve_life_period_assumptions` | Aufloesung von Anlagebetrag und Todesfall-IDs auf dem jeweiligen Anfangsbestand | Keine zweite Anlage- oder Todesfallquelle in der Kettenperiode. Mortalitaet erfindet keine Leistung. |

Dieser Schnitt fuehrt eine deterministische Lebensprojektion aus, nicht
den historischen IMS-Nichtleben-Runner. Er schreibt nichts, startet
keinen App-Runner und behauptet weder gesetzliche Bilanz noch
Solvency-II-Wert oder historische Vollgleichheit.

## Versionierte Eingabe

`tests/fixtures/life_period_chain_v1.json` enthaelt einen vollstaendigen
Zwei-Perioden-Fall. Die Huelle verlangt `schema_version`,
`life_sector_contract_schema_version`, `sector_taxonomy_schema_version`,
`source_kind = "versioned_life_period_chain"`,
`historical_mapping_status = "unresolved"`, `insurer_id` (1 bis 25),
`sector_id = "life"`, `opening`, `assumptions` und 1 bis 100
lueckenlose `periods`. `opening` ist der vollstaendig enumerierte
PR163-Anfangsbestand. `assumptions` ist ein kompletter PR164-Plan mit
derselben VU-ID und genau demselben Horizont.

Jede Kettenperiode hat `period`, `policy_flows`, `new_business`,
`operating_expense_paid`, `capital_contribution` und
`capital_distribution`. Ein Policenfluss enthaelt `policy_id`,
`renewal_premiums_collected`, `renewal_liability_allocation`,
`death_benefit_if_death` und `maturity_benefit_if_due`.
Alle Betragsfelder sind nichtnegative Dezimalstrings mit maximal vier
Nachkommastellen. `death_benefit_if_death` ist der **Szenariobetrag im
Todesfall**, kein aus der Sterblichkeitskurve berechneter Wert.
`maturity_benefit_if_due` ist der **Szenariobetrag bei faelligem
Ueberleben**. Bei Tod wird er null; Todesfall geht vor Ablauf.
Bei ueberlebender Faelligkeit gilt weiterhin die PR163-
Garantieuntergrenze. Die Perioden duerfen keine eigenen Felder
`investment_result`, `death` oder `death_benefits_paid` tragen;
andernfalls waeren Quellen doppelt oder widerspruechlich.

## Ablauf und Nachweis

Fuer Periode 1 kommen `opening_backing_assets` und aktive Policen
aus `opening`.
Ab Periode 2 kommen sie ausschliesslich aus dem **geprueften Schluss**
der Vorperiode. PR164 loest darauf je Periode Anlagebetrag und
Todesfall-IDs auf. Nur ausgewaehlte Policen erhalten ihre explizite
Todesfallleistung; ihr moeglicher Ablaufbetrag wird nicht ausgezahlt.
Die daraus materialisierte Periode wird an PR163 angehaengt, und
der gesamte Prefix wird erneut mit PR163 berechnet. Sein Schluss
ist die einzige Basis fuer den naechsten Schritt. Zeilen, Kohorten,
Policen und vier Bilanz-/Bestandswerte muessen exakt durchgetragen
werden. Das Ergebnis zeigt PR163-Zeilen und die PR164-Quellenwerte
je Periode. Ein Fehler in irgendeiner Periode oder ein Abbruch
**zwischen** Perioden liefert atomar null Zeilen und null
Quellenwerte. Es gibt kein teilweise persistiertes Ergebnis.

Die Eingabe ist auf 100 Perioden, 100 aktive Policen an jedem
Periodenrand, 100 Neupolicen je Periode und insgesamt 10.000 aktive
Policen-Perioden begrenzt. Der Extremtest mit 100 Policen ueber
100 Perioden lief auf dem lokalen Windows-Rechner in rund 46 Sekunden.
Das erneute Pruefen wachsender Prefixe ist bewusst konservativ,
aber quadratisch im Horizont; vor einem interaktiven API-Start muss
PR166 Laufzeit, Abbruch und gegebenenfalls einen gleichwertigen
inkrementellen Rechenpfad gesondert absichern. Die reine Funktion
hat keine eigene Wandzeitfrist; der optionale Abbruch wird vor jeder
neuen Periode geprueft.

## Offen

PR166 hat gespeicherte, digestgebundene Ergebnisse,
Idempotenz, API und XLSX ergaenzt; siehe
`ims_2x_life_result_delivery.md`. PR167 fuehrt einen nichttechnischen
Workbench-Bedienweg ein. Rueckkauf, Bonus, unveraenderliche
individuelle Ausgabeterm-Ablaufleistung und historische RNG-Folgen
sind weiter ausgeschlossen. Der bestehende Nichtleben-Pfad bleibt
unveraendert.
