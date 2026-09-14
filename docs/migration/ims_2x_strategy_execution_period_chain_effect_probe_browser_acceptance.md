# PR141: Zwei-Perioden-Bedienpfad im Browser abnehmen

Stand: 2026-09-14

## Einordnung

PR141 schliesst die in PR140 geoeffnete Zwei-Perioden-Bediengrenze mit einer
reproduzierbaren Browserabnahme ab. Kettenbau, Kandidatenbau, Digestpruefung,
Runner, Carryover, Idempotenz und Ergebnisablage bleiben fachlich und
technisch unveraendert.

## C-zu-Python-Mapping

| Historischer Bezug | Python-/UI-Ziel | Bedeutung |
| --- | --- | --- |
| Periodenschleife in `ESS.C:71-75` | vorhandener PR139/PR140-Pfad | isolierter Ausschnitt aus Periode 1 und 2 mit genau einem Uebergang |
| VU-/VN-Vorperiodenzustand | sichtbarer VU-/VN-Carryover | gespeicherte Uebergangsflags werden unveraendert angewandt |
| `SIMLAENGE = 100` in `IMSDATA.C:14` | gesperrte Mehrperiodengrenze | Browserabnahme belegt noch keinen historischen Gesamthorizont |
| historischer manueller Programmstart | Workbench-Freigabeformular | sichtbare Person, Begruendung und ausdrueckliche Zwei-Perioden-Bestaetigung |

PR141 portiert keine C-Regel. Loopback-Smoke, Viewportpruefung und
Screenshots sind moderne Abnahme- und Dokumentationsmittel.

## Reproduzierbarer Smoke-Aufbau

`ims.api.strategy_execution_period_chain_effect_probe_browser_smoke`
erzeugt eine frische SQLite-Datei, zwei periodenspezifische lokale
Marktprofile sowie daraus zwei serverseitig neu gebaute Kandidaten. Die
Kandidaten werden unveraenderlich gespeichert und zu einer ebenfalls
serverseitig neu gebauten Kette fuer Periode 1 und 2 verbunden.

Der Webserver liefert das regulaere Produktions-Frontend und die regulaeren
PR140-Endpunkte ausschliesslich ueber Loopback aus. Bestehende Datenbanken,
nicht frische Profilverzeichnisse, fehlende Frontend-Builds und externe
Bindeadressen werden abgewiesen.

## Sichtbare Abnahme

Der gebaute Workbench-Stand wurde mit Browser-Locators und expliziten
Viewports geprueft:

- `1440 x 1000`: Kettenstatus, Freigabe, beide Periodenwirkungen,
  VU-/VN-Carryover, Ergebnisdigest, Verlauf und geschlossene
  Mehrperiodengrenze sind lesbar;
- `390 x 844`: einspaltige Ergebnis- und Nachweiszeilen ohne horizontale
  Ueberbreite, abgeschnittene Woerter oder Ueberlagerung;
- vor der ausdruecklichen Checkbox ist `Zwei Perioden starten` deaktiviert;
- nach dem erfolgreichen Start ist der Startknopf entfernt;
- nach einem Browser-Neuladen bleiben Ergebnis und Verlauf sichtbar;
- der Browser meldet keine Warnung oder Fehlermeldung in der Konsole.

Die Strategie-Tabs wurden fuer die inzwischen zehn Ansichten auf stabile
Zeilen mit fuenf, vier, zwei beziehungsweise einer Spalte verteilt. Auf dem
schmalen Viewport stehen Bezeichner und Werte der Ergebnisnachweise
untereinander, damit insbesondere `ausgefuehrt` nicht innerhalb des Wortes
umbricht.

## Automatisierte Abnahme

Die Tests pruefen:

- frische Datenbank, frisches Profilverzeichnis, vorhandenen Frontend-Build
  und Loopback-Bindung;
- einen echten erfolgreichen Zwei-Periodenaufruf mit zwei Runner- und zwei
  Carryover-Aufrufen;
- beide Periodenwirkungen, Uebergang 1 nach 2 und beide Carryover-Arten;
- idempotente Wiederholung ohne weitere Runner-, Carryover- oder
  Schreibaufrufe;
- fehlende Ausfuehrungsfreigabe ohne Schreiben;
- falschen Digest ohne Runneraufruf;
- deterministischen Runnerfehler in Periode 2 ohne Teilresultat und ohne
  Ergebnisdatensatz, aber mit Fehlerverlauf;
- Vorhandensein der Browseranker sowie Format und Abmessungen beider PNGs.

## Grenzen und naechster Schritt

Die Abnahme belegt genau den kontrollierten Bedienpfad fuer Periode 1 und 2.
Sie belegt keinen freien Mehrperiodenlauf, keinen 100-Periodenlauf, keine
Regulierungssimulation und keine Reproduktion eines historischen RNG-Laufs.
Es entstehen keine fachlichen Ausgabedateien; `incomming/` wird nicht gelesen
und bleibt unversioniert.

PR142 hat inzwischen den read-only Vertrag fuer einen kleinen, bis fuenf
Perioden begrenzten gemeinsamen Kettenrunner festgelegt. Der bereits belegte
Prefix 1-2 bleibt als exakte fachliche Projektion geschuetzt. PR143 hat die
Fuenf-Perioden-Kette ohne Runner gebaut und validiert. PR144 fuehrt sie als
naechstes fluechtig aus; der 100-Perioden-Horizont bleibt eine spaetere,
separat abzunehmende Grenze.
