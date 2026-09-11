# PR131: Kontrollierter Workbench-Start fuer die Einperioden-Wirkungsprobe

Stand: 2026-09-09

## Ziel

PR131 macht die in PR130 eingefuehrte Einperioden-Wirkungsprobe kontrolliert
bedienbar. Ein ausdruecklich freigegebener Workbench-Start reserviert den
Idempotenzschluessel dauerhaft, fuehrt den vorhandenen PR130-Pfad hoechstens
einmal aus und speichert Ergebnis sowie Versuchshistorie in der konfigurierten
SQLite-Metadatenquelle.

Der Schnitt bleibt auf genau eine isolierte Kandidatenkopie und eine Periode
begrenzt. Er ist kein Mehrperiodenlauf und keine vollstaendige Simulation.

## Historischer Bezug

Die fachliche Wirkung bleibt unveraendert im bereits portierten
Einperiodenanker fuer `Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06`.
PR131 portiert keine C-Regel. Er ergaenzt ausschliesslich die kontrollierte
Bedien-, Freigabe- und Nachweiskette um den PR130-Kernaufruf.

## Startvertrag

`POST /api/run-control/strategy-candidate-effect-probe-start` akzeptiert
unveraendert den vollstaendigen PR130-Request. Darin muessen sowohl
`explicit_run_control_release = true` als auch
`explicit_effect_probe_execution = true` gesetzt sein.

Der Browser darf keine Kandidateninhalte, Datenbankpfade, Fixtures,
Ausgabepfade, Carryover-Werte oder Legacy-Ziele uebergeben. Autoritative
Identitaet bleiben Kandidaten-ID und erwarteter SHA-256-Digest.

## Atomare Ablaufgrenze

1. Request, Kandidaten-ID, Digest und Speicherintegritaet pruefen;
2. Kandidat und Idempotenzschluessel mit `BEGIN IMMEDIATE` reservieren;
3. parallele oder inhaltlich abweichende Wiederholungen blockieren;
4. Kandidat unmittelbar vor dem Runner erneut serverseitig pruefen;
5. PR130 genau einmal auf einer isolierten Kopie ausfuehren;
6. Ergebnisdigest, Ergebnis und erfolgreichen Versuch gemeinsam speichern;
7. Runnerfehler als fehlgeschlagenen Versuch ohne Ergebnis festhalten;
8. identische erfolgreiche Wiederholung ohne Runner aus der Ablage lesen.

Je Kandidat wird hoechstens ein erfolgreiches Ergebnis gespeichert. Nach
einem fehlgeschlagenen Versuch ist eine neue manuelle Freigabe mit neuem
Idempotenzschluessel erlaubt. Automatische Wiederholungen und Queue-Worker
bleiben gesperrt.

## Ablage und Beobachtung

Eigene Tabellen trennen Strategie-Kandidaten von der aelteren
Fixture-Adapter-Queue:

- `strategy_execution_candidate_effect_probe_attempts` fuer Freigabe,
  Idempotenz, Zeitpunkte und Fehlerstatus;
- `strategy_execution_candidate_effect_probe_results` fuer das
  unveraenderliche PR130-Ergebnis samt eigenem SHA-256-Digest.

Read-only Endpunkte liefern Ergebnis und Verlauf, ohne Tabellen anzulegen
oder Daten zu veraendern:

- `GET /api/run-control/strategy-candidate-effect-probe-result/{candidate_id}`;
- `GET /api/run-control/strategy-candidate-effect-probe-history/{candidate_id}`.

## Workbench

Die Kandidatenansicht erhaelt:

- Freigabefelder fuer Person und Grund;
- eine ausdrueckliche Bestaetigung fuer genau eine Periode;
- einen klar benannten Startbutton;
- Ergebniskennzahlen zu Periode, VU-/VN-Anwendungen und geaenderten Akteuren;
- den read-only Verlauf mit Freigabe-, Start-, Abschluss- und Fehlerstatus.

Nach vorhandenem Ergebnis ist der Start in der Workbench gesperrt. Die
serverseitige Idempotenzgrenze bleibt auch bei direktem API-Aufruf wirksam.

## Validierung

- erster Start ruft den Runner genau einmal und speichert Versuch und Ergebnis;
- identische Wiederholung liefert das Ergebnis ohne zweiten Runneraufruf;
- gleicher Idempotenzschluessel mit anderem Inhalt wird abgewiesen;
- paralleler Doppelstart wird atomar blockiert;
- ein Runnerfehler wird ohne Ergebnis im Verlauf sichtbar;
- neuer manueller Versuch nach Fehler ist moeglich;
- Ergebnismanipulation wird durch den gespeicherten Digest erkannt;
- reine Lesezugriffe erzeugen keine Tabellen;
- API-Methoden, Statuscodes und Workbench-Grenzen sind getestet.

## Schutzgrenzen

- keine neue oder geaenderte VU-/VN-Fachlogik;
- genau eine Periode auf einer isolierten Kandidatenkopie;
- keine freie Pfad- oder Payloaduebergabe aus der UI;
- keine Queue, kein Queue-Worker und kein automatischer Retry;
- kein Carryover, Scheduler oder Mehrperiodenlauf;
- keine Ergebnisdateien und kein Legacy-Vergleich;
- keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.

## Restplanung

- **PR131 (umgesetzt):** kontrollierter Workbench-Start, dauerhafte Idempotenz,
  Ergebnisablage und read-only Verlauf.
- **PR132 (umgesetzt):** Browser-Smoke, Fehlerpfade und Handbuch-Screenshots
  fuer den bedienbaren Einperiodenpfad abschliessen.
- **PR133 (umgesetzt):** Periodenketten- und Carryover-Vertrag fuer einen
  spaeteren kontrollierten 100-Periodenpfad festlegen.
- **PR134 (umgesetzt):** den Ketteneingang zustandslos und atomar validieren.
- **PR135 (umgesetzt):** Kandidatenreferenzen und -kontexte serverseitig
  aufloesen und atomar abgleichen.
- **PR136 (umgesetzt):** kanonische fluechtige Kette und Gesamtdigest bilden.
- **PR137 (umgesetzt):** Kette unveraenderlich und idempotent speichern,
  weiterhin ohne Carryover oder Runner.
- **PR138 (umgesetzt):** gespeicherte Ketten-ID und Volldigest read-only
  erneut pruefen.
- **PR139 (naechster Schritt):** isolierte fluechtige Zwei-Perioden-
  Wirkungsprobe; Ergebnisablage bleibt gesperrt.

Nach PR132 ist die Einperioden-Wirkungsprobe kontrolliert bedienbar und
dokumentiert. Mehrperiodenlauf, Carryover und Regulierungssimulation bleiben
eigene spaetere Ausbaubloecke.

## Naechster Schritt

PR134 validiert den versionierten Ketteneingang. PR135 loest die
Kandidatenreferenzen auf. PR136 bildet inzwischen die kanonische fluechtige
Kette. PR137 speichert sie inzwischen unveraenderlich und schaltet noch keinen
Mehrperiodenstart frei. PR138 fuegt inzwischen den read-only Freigabecheck
hinzu. PR139 erprobt als Naechstes genau zwei Perioden fluechtig.
