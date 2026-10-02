# Bestandsprüfung zur Vorstandsplanung

Tatsächliche Läufe am 02.10.2026 mit Python 3.12, eigener editable Umgebung.
Produktbasis: main `81146aa8657e2d507cc51c921207e80895f78340`.
Keine neue Simulationsfunktion. [Eingaben, Digests, Replay und Ergebniszeilen](ims_board_baseline_2026_10.json)
wurden mit `scripts/planning/probe_board_baseline.py` erzeugt.

## Ausführbarer Umfang

Sechs ICT-Vertragsläufe mit dem vorhandenen synthetischen Zwei-VU-Preset:
100 Tagesperioden à 24 Stunden, zwei Tage gemeinsamer Ausfall ab Stunde 1176.
Je Haus vier unabhängige Prozesswarteschlangen mit Nachfrage 10/h und Kapazität
12/h. Bestehender Restart/Fallback-Wert 0,5, Zeitraum 1188–1224, Kosten 1/h.
Restart betrifft den gemeinsamen Asset und teilt 36 Kosten auf beide Häuser;
der skalare Fallback gilt nur für Portal 1 und kostet Haus 1 insgesamt 36.
**Das sind Capability-Proben mit unterschiedlichen Kostenträgern, kein fairer
Vergleich von drei Vorsorgestrategien.** Die No-shock-Proben behalten bezahlte
Maßnahmen; die eingebaute ICT-Baseline allein würde alle Maßnahmenkosten entfernen.

| Tatsächlicher Lauf | Ergebnis Haus 1 / Haus 2 über 100 Perioden | Maßnahmenkosten Haus 1 / Haus 2 |
| --- | ---: | ---: |
| Kein Schock, keine Maßnahme | 10000 / 10000 | 0 / 0 |
| Ausfall, keine Maßnahme | 9769,60 / 9769,60 | 0 / 0 |
| Ausfall, deklarierter Restart | 9893,68 / 9893,68 | 18 / 18 |
| Kein Schock, bezahlter Restart | 9982 / 9982 | 18 / 18 |
| Ausfall, skalarer Fallback Portal 1 | 9881,44 / 9769,60 | 36 / 0 |
| Kein Schock, bezahlter Fallback | 9964 / 10000 | 36 / 0 |

Einheit: Modellwährung. Der vorhandene `operational_impact` der Bilanzzeile
enthält bereits Maßnahmenkosten; diese dürfen nicht ein zweites Mal addiert
werden. Rückstände werden aufgeholt, damit ist temporär entgangene Marge kein
automatischer endgültiger Verlust. Alle sechs Eingaben wurden identisch
wiederholt und lieferten gleiche vollständige Ergebnisse und Digests.

AP3-Preisfall frisch gerechnet und wiederholt: 100 Perioden, Schluss-Eigenkapital
Baseline 116015,7633, Variante 87325,7633, Differenz −28690 = −302 × 95.
Das ist die vorhandene Fokus-VU-Abrechnung, kein gemeinsam bilanzierter Markt.

## Verträge und Herkunft

| Geprüfte Quelle | Bestehende Leistung | Grenze für den neuen Fall |
| --- | --- | --- |
| `ESS.C:88–149`, `IMS.E:1087/3521`, `IMSDATA.C`, bestehende AP3-Mappings | Perioden/Aktionen, VU-Angebote und VN-Auswahl als kartierte Regelkerne | Neue ICT-, Cash- und Rivalenverträge sind moderne Erweiterungen; historische Spartenidentität bleibt ungeklärt |
| `ims.strategies.modern_bridge` | Vollständige Draws, inklusive Zeitfenster, Kundenwahl und Fokus-VU-Abrechnung | Maximal 25 Anbieter; keine gemeinsamen Rivalenbilanzen, begrenzte Regeln, Schäden bleiben exogen |
| `ims.ict.contract/simulation/presets` | Transitive Abhängigkeiten, Ereigniszeiten, Original/Nacharbeit, Carryover, einmalige Maßnahmenallokation | Maximal 25 Versicherer; unabhängige Queues; kein Kundenmarkt oder Cash-Ledger |
| ICT-Restart | Deklarierte Verkürzung verbleibender Ausfalldauer | Kein Nachweis getesteter Wiederherstellung; dokumentiert/verfügbar/getestet fehlen |
| ICT-Fallback | Kapazitätsuntergrenze nach Abhängigkeitsauswertung | Keine Ersatzpfad-Topologie oder Prüfung gemeinsamer Unterlieferanten |
| `ims.accounting.life_period_chain` | Policen, Garantien, Prämien, exogene Todes-/Ablaufzahlungen, Bestands-Carryover | Kein vollständiger Vertrauens-/Rückkaufvertrag; keine stille Gleichsetzung mit Kündigungslogik |

Vorhandene Cash-ähnliche Policen-/Bilanzflüsse sind wiederzuverwenden, ergeben
aber keinen bereits verfügbaren Cash-Vertrag für den gekoppelten Drei-VU-Markt.
Eigenmittel-Proxies sind keine regulatorischen SCR/MCR-Ausgaben. Die angenommenen
AP5/AP7-Verträge liefern erst künftig Mehr-VU- und Markt-/ICT-Grundlagen.

Der [neue Handfall](../plans/ims_dora_reference_case.md) ist ausschließlich
spezifiziert. Keine Behauptung, sein unabhängiger Fallback, Kunden-/Risikotransfer,
Cash oder reagierende Rivalen seien mit diesen Läufen bereits validiert.

## Wiederholen

Im jeweiligen Checkout mit eigener Umgebung:

```powershell
.\.venv\Scripts\python.exe scripts\planning\probe_board_baseline.py --out .tmp-pr-board-plan\baseline-replay.json
.\.venv\Scripts\python.exe -m pytest tests\test_ict_workshop.py tests\test_api_ict_workshop.py tests\test_api_seminar.py -q
```

Der Runner schreibt ausschließlich die angegebene Berichtdatei. 27 bestehende
ICT-/API-/Seminarprüfungen bestanden in 155,80 Sekunden; eine vorhandene
Starlette-Testclient-Deprecation-Warnung. 35 Planprüfungen bestanden ebenfalls.
CI-Stand und PR #292 stehen im Handoff; ein erfolgreicher Bestandslauf ersetzt
keine Benutzerabnahme oder eine fachliche Freigabe der neuen Modellkanäle.
