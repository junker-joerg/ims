# Read-only Abweichungsdiagnose fuer berechnete Legacy-Vergleiche

## Ziel

PR 59 setzt auf dem strikten Eingangsvertrag aus PR 58 auf. Das neue Modul
`python_port/ims/model/legacy_calculated_deviation_report.py` prueft gelieferte
berechnete `ExportTable`-Ergebnisse und erzeugt eine rein lesende Diagnose.

Der Bericht startet keinen Runner, schreibt keine Artefakte und startet keine
Simulation. Er behauptet weder historische Vollgleichheit noch eine fachliche
Ursache fuer beobachtete Zahlenunterschiede.

## Ursprung und Python-Zuordnung

Dieser PR portiert keine neue C-Fachlogik. Er ordnet vorhandene technische
Vergleichsergebnisse ein:

| Bestehende Grenze | Python-Komponente | Rolle in PR 59 |
| --- | --- | --- |
| PR-58-Sollplan | `build_calculated_legacy_comparison_plan` | benoetigte Exportidentitaeten und Perioden |
| PR-58-Vergleich | `compare_calculated_export_tables_to_legacy_fixture` | Feld- und Zeilenvergleich mit bestehender Toleranz |
| Legacy-Report | `LegacyValidationReport` | Treffer-, Zeilen- und Feldabweichungsdaten |
| neue Diagnose | `build_calculated_legacy_deviation_report` | Inputblocker und technische Abweichungskategorien |

Historischer Scheduler, RNG, automatische Regelwahl und C-Laufkontext werden
durch die Diagnose nicht rekonstruiert. Die deklarierte `calculation_origin`
bleibt eine Aufruferangabe und ist kein automatisch verifizierter
Provenienznachweis.

## Inputgate vor jedem Vergleich

Vor dem Feldvergleich prueft die Diagnose:

- deklarierte Berechnungsherkunft;
- alle benoetigten Exportidentitaeten;
- fehlende, doppelte und unerwartete Tabellen;
- fehlende, doppelte, unsortierte und unerwartete Perioden;
- lesbare globale Periodenwerte.

Bei einer Luecke lautet der Status `blocked_input`. Dann bleiben
`comparison_performed = false`, `matches = null` und alle Vergleichszaehler auf
null beziehungsweise null Zeilen. Eine Inputluecke wird nicht als fachliche
Abweichung umgedeutet.

## Technische Kategorien

Nur bei vollstaendig bestandenem Inputgate werden Felder klassifiziert:

| Kategorie | Technische Bedeutung | Fachliche Aussage |
| --- | --- | --- |
| exakter Treffer | normalisierte Werte stimmen exakt ueberein | keine Vollgleichheitsbehauptung |
| `tolerated_numeric_difference` | numerische Differenz ist groesser null, bleibt aber innerhalb der bestehenden Vergleichstoleranz | keine Ursachenklassifikation |
| `blocking_numeric_difference` | numerische Differenz liegt ausserhalb der bestehenden Vergleichstoleranz | blockierender Befund, Ursache offen |
| `open_field_question` | nichtnumerischer Unterschied, zum Beispiel Header-/Strukturfrage | Feldklaerung erforderlich |

Die Kategorien verwenden ausschließlich vorhandene Vergleichswerte und die
bereits etablierte Toleranz. PR 59 fuehrt keinen neuen fachlichen Schwellenwert
ein.

## Aktueller Kernkorpus-Befund

Der read-only Aufruf fuer
`tests/fixtures/legacy_validation_bundle.json` ohne gelieferte berechnete
Tabellen ergibt:

- Status `blocked_input`;
- 19 historische Ziele und 6.300 Zielperioden;
- 15 benoetigte berechnete Exporttabellen;
- 0 gelieferte Exporttabellen;
- 15 Issues mit Code `required_export_missing`;
- kein ausgefuehrter Vergleich und keine Gleichheitsaussage.

Das ist ein Inputbereitschaftsbefund, kein Ergebnis eines Neu-/Alt-Laufs.
ZINS000 bleibt außerhalb dieses Kernkorpusberichts.

## Validierung in PR 59

Kontrollierte In-Memory-Tests belegen:

- die 15 blockierenden Kerninputluecken;
- einen Bericht mit ausschließlich exakten Treffern;
- eine numerische Differenz innerhalb der bestehenden Toleranz;
- eine blockierende numerische Differenz;
- eine nichtnumerische Headerfrage;
- Abbruch vor dem Vergleich bei fehlender Periode oder Herkunftsangabe;
- `writes_performed = false`, `execution_performed = false`,
  `simulation_performed = false` und
  `historical_equivalence_claimed = false`.

Die Testwerte sind keine historischen Berechnungsergebnisse und liefern keinen
fachlichen Gleichheitsnachweis.

## Naechster Schritt

PR 60 hat einen ersten schmalen Aggregat-/Export-Output aus vier expliziten
VU14-Zustaenden angebunden. PR 61 hat die technische Level-IV-Selektorgrenze
`all` gegen `SK1` explizit und eng kanonisiert. PR 62 bereitet als naechstes
die kontrollierte Run-Control-Ausfuehrungsfreigabe vor; ein fachlich
validierter berechneter SK1-Slice bleibt davon getrennt. Modellkorrekturen
bleiben gesperrt, bis eine konkrete berechnete Abweichung aus vergleichbaren
Zustaenden belegt ist.
