# PR164: Deterministische Anlage- und Mortalitaetsquellen

Stand: 2026-09-17
Eingang: `ims.life-assumptions-input.v1`
Ergebnis: `ims.life-assumptions-result.v1`
Python: `ims.accounting.life_assumptions.resolve_life_period_assumptions`

## Herkunft und Grenze

| Ursprung | Python-Ziel | Fachliche Grenze |
| --- | --- | --- |
| `IMSDATA.C`: `MAXSPARTEN 2`, `BAV.Zs[SIMLAENGE+1]` zur Verzinsung der VU-Schadenreserven; `IMS.E`: `Zs[gperiod]` und Verzinsung beider Spartenreserven | Versionierter Perioden-Satz als Eingangsform | Der C-Zins ist kein Beleg fuer eine Lebens-Anlageregel oder gleiche Ergebniswerte. |
| PR160-v3-Zielvertrag | Exklusive Quellenmodi fuer Anlage und Mortalitaet | Die hier festgelegte Zaehl- und Auswahlregel ist eine neue IMS-2.x-Annahme, keine historische Sterblichkeitsregel. |
| PR163: vollstaendig enumerierte Policen | Aktive Policen-IDs und Kohorten als Anfangsbasis | Der Resolver liefert nur Anlagebetrag und Todesfall-IDs; er veraendert weder PR163-Eingabe noch -Rechnung. |

Es gibt keine historische Vollgleichheit, RNG-Nachbildung,
gesetzliche Bilanz oder Solvency-II-Aussage. Die Funktion startet
keinen Runner, schreibt keine Daten und erstellt keine Bilanz.

## Versionierter Plan

Das vollstaendige Beispiel liegt in
`tests/fixtures/life_assumptions_v1.json`. Der Plan verlangt
`schema_version`, `life_sector_contract_schema_version =
"ims.life-sector-contract.v3"`, `sector_taxonomy_schema_version`,
`source_kind = "versioned_assumption_plan"`,
`historical_mapping_status = "unresolved"`, `sector_id = "life"`,
`insurer_id` von 1 bis 25, `period_count` von 1 bis 100 sowie
`investment` und `mortality`. Unbekannte Felder sind unzulaessig.

Jede Quelle hat **genau einen** Modus:

| Quelle | Modus | Eingabe |
| --- | --- | --- |
| Anlage | `explicit_scenario` | `periods` mit genau einem signierten `investment_result` je Periode |
| Anlage | `insurer_rule_on_opening_backing_assets` | `windows` mit `start_period`, `end_period`, signiertem `rate_per_period` von -1 bis 1 |
| Mortalitaet | `explicit_death_policy_ids` | `periods` mit `death_policy_ids` je Periode, auch als leere Liste |
| Mortalitaet | `exogenous_deterministic_rate_curve` | `windows` mit nichtnegativem `rate_per_period` von 0 bis 1 |

Betrag und Saetze sind Dezimalstrings mit hoechstens vier bzw. sechs
Nachkommastellen. Fenster duerfen in der Eingabeliste beliebig
geordnet sein, muessen nach Sortierung aber den Horizont 1 bis N
**lueckenlos und ueberlappungsfrei** abdecken. Explizite
Periodenwerte decken denselben Horizont genau einmal ab. Ein
`periods`-Feld im Kurvenmodus oder ein `windows`-Feld im expliziten
Modus wird abgelehnt; Quellen werden nie addiert.

## Periodenauflosung

Der zweite Funktionsparameter ist der Anfangsbestand **einer**
Periode: `insurer_id`, `period`, `opening_backing_assets` und eine
vollstaendige `opening_policies`-Liste aus `policy_id` und
`cohort_id`. Hoechstens 100 aktive Policen sind erlaubt. VU-ID muss
zum Plan passen, und die Periode muss im Plan liegen. PR165 muss
diese Anfangsbasis aus dem geprueften Anfangs-/Vorperiodenbestand
bereitstellen; PR164 leitet keine Folgeperioden selbst ab.

Die einfache VU-Anlageregel berechnet
`investment_result = ROUND_HALF_EVEN(opening_backing_assets *
rate_per_period, 0.0001)`. Laufende Praemien, Neugeschaeft und
Kapitalbewegungen dieser Periode erhalten keinen rueckwirkenden
Anlageertrag. Ein negativer Satz erlaubt einen Verlust, aber keine
Anlageoptimierung oder Portfoliowahl.

Die Mortalitaetskurve berechnet **je Kohorte**
`deaths = ROUND_HALF_UP(active_opening_policies * rate_per_period)`
auf eine ganze Zahl. Sie waehlt die lexikografisch ersten aktiven
Policen-IDs dieser Kohorte. Das ist eine dokumentierte,
reproduzierbare Auswahl ohne Zufallsziehung, aber keine
altersabhaengige Sterbetafel; eine dauerhafte ID-Verzerrung ist
moeglich. Explizite Todesfall-IDs muessen im aktiven Anfangsbestand
liegen. Das Ergebnis zeigt IDs, Kohorten-Stueckzahlen, Quellenmodi,
Satz und Anlagebetrag; ungueltige Eingaben liefern **keine**
aufgeloesten Teilwerte.

Todesfallleistungen, Garantieverpflichtung, Praemien, Ablauf und
Bilanz bleiben explizit beziehungsweise Aufgabe des separaten
Lebens-Rechners. Der Resolver darf aus einer gezogenen Todesfall-ID
keine Todesfallleistung erfinden. PR165 muss die Wertuebergabe,
Leistung, Carryover, Budget und den unveraenderten Nichtleben-Pfad
kontrolliert pruefen. PR166-167 folgen mit Ablage/Export und
Workbench.
