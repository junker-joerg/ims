# PR132: Browserabnahme der Einperioden-Wirkungsprobe

Stand: 2026-09-11
Umsetzungsstand: PR132 umgesetzt

## Ziel

PR132 schliesst den in PR131 bedienbar gemachten Einperiodenpfad mit einer
reproduzierbaren Browserabnahme ab. Geprueft werden ein breiter und ein
schmaler Viewport, die sichtbare Freigabe- und Ergebniskette sowie atomare
Fehlerpfade. Die belegten Ansichten werden in das Benutzerhandbuch
uebernommen.

Der Schnitt fuegt keine Fachlogik hinzu. Er startet keinen Mehrperiodenlauf
und leitet aus dem Ergebnis keine historische Vollgleichheit ab.

## Historischer Bezug

Die fachliche Wirkung bleibt der in PR130 angebundene, bereits portierte
Einperiodenanker fuer `Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06` aus
`IMS.E`. PR132 portiert keine weitere C-Funktion. Der historische
100-Perioden-Horizont aus `IMSDATA.C` ist nur die Grenze des folgenden
Planungsblocks und wird in diesem PR nicht ausgefuehrt.

## Isolierter Smoke-Start

`ims.api.strategy_execution_candidate_effect_probe_browser_smoke` erzeugt
fuer jede Abnahme:

- eine frische SQLite-Metadatenquelle;
- genau einen serverseitig neu gebauten Kandidaten aus dem versionierten
  PR125-Fixture;
- das gebaute Workbench-Frontend;
- einen ausschliesslich an Loopback gebundenen Webserver.

Bestehende Datenbanken, fehlende Frontend-Builds und Nicht-Loopback-Adressen
werden abgewiesen. `incomming/` wird weder gelesen noch versioniert.

## Browsermatrix

| Sicht | Viewport | Gepruefter Inhalt |
| --- | --- | --- |
| breit | 1440 x 1000 | Ergebnisstatus, Wirkungskennzahlen, Digest, Verlauf und geschlossene Mehrperiodengrenze |
| schmal | 390 x 844 | einspaltiger Ergebnisaufbau, lesbare Kennzahlen, keine horizontale Ueberlagerung |

Der Browserpfad lautet:

1. `Strategien` und den Tab `Kandidaten` oeffnen;
2. gespeicherten und digestgeprueften Kandidaten lesen;
3. Person und Grund der Freigabe erfassen;
4. genau eine isolierte Periode ausdruecklich bestaetigen;
5. `Wirkungsprobe starten` ausloesen;
6. gespeichertes Ergebnis, Digest und Versuchsverlauf lesen;
7. gesperrten Wiederholungs- und Mehrperiodenpfad kontrollieren.

## Fehlerpfade

- Ohne ausdrueckliche Checkbox bleibt der Browserstart deaktiviert.
- Eine fehlende Ausfuehrungsfreigabe wird vor jedem Schreib- oder Runnerpfad
  mit `400` abgewiesen.
- Ein nicht zur Kandidaten-ID passender Digest wird atomar mit `409`
  abgewiesen.
- Ein Runnerfehler erzeugt keinen Ergebnisdatensatz, bleibt aber als
  fehlgeschlagener Versuch im read-only Verlauf sichtbar.
- Eine identische erfolgreiche Wiederholung liest das vorhandene Ergebnis
  ohne zweiten Runneraufruf.

## Restplanung

- **PR132 (umgesetzt):** Browser-Smokes, Fehlerpfade und datierte
  Handbuch-Screenshots fuer die Einperioden-Wirkungsprobe.
- **PR133 (umgesetzt):** versionierten Periodenketten- und Carryover-Vertrag
  fuer eine spaetere kontrollierte Folge von bis zu 100 Perioden festlegen;
  weiterhin ohne neuen Runner- oder UI-Startpfad.
- **PR134 (umgesetzt):** den versionierten Ketteneingang zustandslos und
  atomar validieren.
- **PR135 (umgesetzt):** Kandidatenreferenzen und -kontexte serverseitig
  aufloesen und atomar abgleichen.
- **PR136 (umgesetzt):** kanonische fluechtige Kette und Gesamtdigest bilden.
- **PR137 (umgesetzt):** Kette unveraenderlich und idempotent speichern;
  Carryover und Runner bleiben gesperrt.
- **PR138 (umgesetzt):** gespeicherte Ketten-ID und Volldigest an einer
  read-only Freigabegrenze erneut pruefen.
- **PR139 (naechster Schritt):** isolierte fluechtige Zwei-Perioden-
  Wirkungsprobe; Ergebnisablage bleibt gesperrt.

Die Einperioden-Wirkungsprobe ist nach PR132 kontrolliert bedienbar und
dokumentiert. Ein nutzbarer 100-Periodenlauf, Ergebnisbloecke, XLSX-Export und
Regulierungsszenarien bleiben getrennte Ausbaustufen.

## Schutzgrenzen

- keine neue oder geaenderte VU-/VN-Fachlogik;
- genau eine isolierte Periode je erfolgreichem Erststart;
- keine freie Kandidaten-, Datenbank-, Fixture- oder Ausgabepfaduebergabe
  aus dem Browser;
- kein Carryover, Scheduler oder Mehrperiodenlauf;
- keine Ausgabedateien und kein Legacy-Vergleich;
- keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.
