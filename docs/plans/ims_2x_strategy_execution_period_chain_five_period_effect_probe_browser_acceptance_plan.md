# PR146: Browserabnahme der Fuenf-Perioden-Wirkungsprobe

Stand: 2026-09-16
Umsetzungsstand: PR146 umgesetzt

## Ziel

PR146 macht den in PR145 dauerhaft abgesicherten Fuenf-Perioden-Start in der
Workbench bedienbar. Ein vorhandenes Zwei-Perioden-Ergebnis dient sichtbar
als Prefixreferenz. Nach ausdruecklicher Freigabe zeigt die Workbench die
Wirkung in Periode 1 bis 5, vier VU-/VN-Carryover-Uebergaenge, den exakten
Prefixnachweis 1-2 sowie das unveraenderlich gespeicherte Ergebnis und den
Versuchsverlauf.

Der Schnitt fuegt keine VU-/VN-Regel und keinen neuen Runner hinzu. Horizonte
ab zehn Perioden, fachliche Ausgabedateien und ein freier Simulationsstart
bleiben geschlossen.

## Historischer Bezug

| Quelle | Bereits belegte Semantik | Folge fuer PR146 |
| --- | --- | --- |
| `ESS.C:71-75` | Perioden werden historisch in aufsteigender Folge bearbeitet | sichtbar ist der bereits in PR144/PR145 belegte Ausschnitt 1 bis 5 |
| `IMSDATA.C:14` | `SIMLAENGE = 100` | fuenf Perioden sind eine kontrollierte Vorstufe, kein historischer Gesamtlauf |
| PR140 | unveraenderliches Zwei-Perioden-Ergebnis | die Workbench akzeptiert nur einen vorhandenen erfolgreichen Prefixnachweis |
| PR145 | atomarer Start, Idempotenz und Ergebnisablage fuer fuenf Perioden | die UI verwendet diesen Serverpfad unveraendert |

PR146 portiert keine C-Regel. Workbench, Loopback-Smoke, Viewportpruefung und
Screenshots sind moderne Bedien- und Abnahmemittel.

## Kleiner technischer Schnitt

Der bereits verifizierte kanonische Kettensatz wird read-only und verlustfrei
auf den versionierten Ketteneingang projiziert. Dadurch muss die Workbench
weder Kettenfelder erraten noch einen freien Payload erfassen. Die
Kettenuebersicht weist getrennt aus, ob genau zwei oder genau fuenf Perioden
fuer ihren jeweiligen kontrollierten Pfad bereit sind.

`ims.api.strategy_execution_period_chain_five_period_effect_probe_browser_smoke`
erzeugt je Abnahme:

- eine frische SQLite-Metadatenquelle und frische lokale Profilverzeichnisse;
- ein erfolgreich gespeichertes Zwei-Perioden-Ergebnis als Prefixreferenz;
- eine unveraenderlich gespeicherte Fuenf-Perioden-Kette;
- das regulaere gebaute Workbench-Frontend;
- einen ausschliesslich an Loopback gebundenen Webserver.

Bestehende Datenbanken, nicht frische Profilverzeichnisse, fehlende
Frontend-Builds und Nicht-Loopback-Adressen werden abgewiesen. `incomming/`
wird nicht gelesen und bleibt unversioniert.

## Browsermatrix

| Sicht | Viewport | Abnahmekriterien |
| --- | --- | --- |
| breit | 1440 x 1000 | Prefixnachweis, alle fuenf Perioden, vier Uebergaenge, Ergebnisdigest, Verlauf und Folgegrenze sind lesbar |
| schmal | 390 x 844 | einspaltige Zeitlinie ohne horizontales Abschneiden, Ueberlagerung oder unlesbare Bedienfelder |

Beide Sichten wurden am 2026-09-16 mit dem regulaeren Produktionsbuild
aufgenommen. `scrollWidth` entspricht jeweils exakt der Viewportbreite; die
Browserkonsole meldet keine Warnung und keinen Fehler.

## Bedienfolge

1. `Strategien` und den Tab `Periodenkette` oeffnen.
2. die gespeicherte Kette `Periode 1-5` und ihre vier Uebergaenge pruefen.
3. den erfolgreichen Vergleich fuer Periode 1-2 waehlen.
4. Person und konkreten Zweck der Freigabe erfassen.
5. die Ausfuehrung von Periode 1 bis 5 ausdruecklich bestaetigen.
6. `Fuenf Perioden starten` ausloesen.
7. fuenf Periodenwirkungen, vier Carryover-Uebergaenge und den exakten
   Prefixnachweis lesen.
8. Ergebnisdigest, unveraenderliche Speicherung, Verlauf und gesperrte
   Folgegrenze kontrollieren.

## Fehlerpfade

- Ohne ausdrueckliche Checkbox bleibt der Startknopf deaktiviert.
- Ohne gespeichertes Zwei-Perioden-Ergebnis bleibt der Start sichtbar
  blockiert.
- Eine fehlende Startfreigabe wird ohne Versuch und ohne Runner abgewiesen.
- Ein falscher Kettendigest erreicht keinen Runner und speichert kein
  Ergebnis; ein auditierbarer Fehlversuch darf erhalten bleiben.
- Ein deterministischer Runnerfehler in Periode 4 liefert weder Teilergebnis
  noch Ergebnisdatensatz; der Fehler bleibt im Verlauf sichtbar.
- Eine identische erfolgreiche Wiederholung liest das vorhandene Ergebnis
  ohne weitere Runner-, Carryover- oder Schreibaufrufe.

## Restplanung

- **PR146 (umgesetzt):** Workbench-Start, Browserabnahme, Fehlerpfade und
  datierte Handbuch-Screenshots fuer den Fuenf-Perioden-Pfad.
- **PR147 (naechster Schritt):** read-only Horizontvertrag fuer 10, 25, 50
  und 100 Perioden mit Laufzeit-, Ressourcen-, Abbruch- und Fehlergrenzen.
- **PR148:** kontrollierte Ausfuehrung fuer 10, 25 und 50 Perioden mit
  stabilen Prefixen und deterministischem Replay.
- **PR149:** kontrollierte Ausfuehrung fuer 100 Perioden.
- **PR150:** versioniertes Ergebnisbuendel in CSV, JSON und XLSX.
- **PR151:** Ergebnisarbeitsplatz fuer Zeitreihen und Baseline-/Variantenvergleich.

## Schutzgrenzen

- keine neue oder geaenderte VU-/VN-Fachlogik;
- exakt fuenf Perioden und vier gespeicherte Uebergaenge;
- keine freie Kandidaten-, Ketten-, Datenbank-, Fixture- oder
  Ausgabepfaduebergabe aus dem Browser;
- keine fachlichen Ausgabedateien und kein Legacy-Vergleich;
- keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.
