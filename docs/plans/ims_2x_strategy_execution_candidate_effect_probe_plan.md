# PR130: Kontrollierte Einperioden-Wirkungsprobe

Stand: 2026-09-09

## Ziel

PR130 fuehrt einen in PR129 erneut geprueften Strategie-
Ausfuehrungskandidaten genau einmal durch den vorhandenen expliziten
Einperioden-Runner. Die Ausfuehrung erfolgt auf einem neu geladenen,
isolierten Objektgraphen und liefert ein fluechtiges Vorher/Nachher-Ergebnis.

Die Probe ist kein Mehrperiodenlauf und keine vollstaendige Simulation. Sie
schreibt weder Ergebnis- noch Legacy-Dateien und veraendert den gespeicherten
Kandidaten nicht.

## Historischer Bezug

Die historischen Aktionen `Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06`
in `IMS.E` wirkten innerhalb eines gemeinsamen Periodenzustands. Der bereits
vorhandene Python-Anker `run_loaded_explicit_period` bildet die portierte
Reihenfolge fuer explizit geladene VU-, VN-Regel-, Schaden- und
Abrechnungssnapshots ab.

PR130 portiert keine weitere C-Regel. Er verbindet den in PR126 kanonisierten
und in PR127 gespeicherten Einperiodenzustand erstmals mit diesem vorhandenen
Kernanker. Daraus folgt keine historische RNG- oder Vollgleichheitsbehauptung.

## Zweite Ausfuehrungsfreigabe

`POST /api/run-control/strategy-candidate-effect-probe` akzeptiert exakt:

- die eigene `schema_version`;
- den vollstaendigen PR129-`release`-Request;
- `explicit_effect_probe_execution = true`.

Die PR129-Freigabe allein startet weiterhin nichts. Kandidatenpayloads, freie
Datenbank-, Fixture- oder Outputpfade sowie Carryover- und Legacy-Felder sind
im PR130-Request verboten.

## Kontrollierte Ausfuehrungsfolge

1. PR130-Request und ausdrueckliche Ausfuehrungsfreigabe validieren;
2. PR129-Freigabecheck fuer ID, Volldigest und SQLite-Integritaet ausfuehren;
3. gespeicherten Kandidaten in ein neues Mapping tief kopieren;
4. Marktgrundzustand und elf Snapshot-Sammlungen in einen neuen
   `LoadedScenario`-Objektgraphen laden;
5. `run_loaded_explicit_period` genau einmal mit `output_dir=None` aufrufen;
6. Periode und leere `written_files` defensiv pruefen;
7. fluechtige Vorher/Nachher-Projektion und Anwendungshaeufigkeiten liefern;
8. gespeicherten Kandidaten und die Ablage unveraendert lassen.

## Technische Loader-Normalisierung

PR126 speichert bei einem VN-Schaden-Snapshot ohne vorgegebene
Versicherungsentscheidung `insurance_decisions: null`. Fachlich sollen diese
Entscheidungen aus der zuvor angewendeten VN-Regel kommen. Der vorhandene
Loader akzeptiert diesen Zustand beim erneuten Laden als fehlendes optionales
Feld, nicht als `null`.

PR130 entfernt deshalb ausschliesslich dieses `null`-Feld aus der isolierten
Loaderkopie. Es wird keine Entscheidung ergaenzt und der gespeicherte
Kandidat samt Digest bleibt unveraendert.

## Fluechtiges Ergebnis

Das Ergebnis enthaelt:

- lokale und globale Periode;
- Haeufigkeiten der acht VU- und drei VN-Anwendungsarten;
- fokussierte VU- und VN-Zustaende vor und nach der Periode;
- IDs der geaenderten VU und VN;
- Anzahl der im Speicher gebildeten Exporttabellen und -zeilen.

Die Exporttabellen werden nicht geschrieben. Das Ergebnis selbst wird in
PR130 nicht gespeichert. Der mitgefuehrte `idempotency_key` ist daher noch
keine dauerhafte Wiederholungssperre; diese Einbindung folgt in PR131.

## API und Workbench

- `GET /api/run-control/strategy-candidate-effect-probe-contract` beschreibt
  den Vertrag read-only.
- `POST /api/run-control/strategy-candidate-effect-probe` fuehrt die
  ausdruecklich freigegebene Backend-Probe aus.
- Die Workbench zeigt nur die Verfuegbarkeit der Backend-Probe. Sie erhaelt in
  PR130 keinen Startbutton und zeigt noch kein Probenergebnis an.

## Validierung

- Parser- und Methodenbegrenzung fuer den verschachtelten PR129-Request;
- positiver Einperiodentest mit exakt einem Runneraufruf;
- bytegleicher SQLite-Inhalt und unveraenderter Kandidat vor und nach der
  Probe;
- deterministisch identisches Ergebnis bei erneutem fluechtigen Aufruf;
- Negativtests fuer fehlende Freigabe, falschen Digest, unbekannten Kandidaten
  und Runnerfehler;
- belegte VU-/VN-Anwendung sowie Vorher/Nachher-Aenderung;
- Frontend-Build und Gesamtsuite.

## Schutzgrenzen

- keine neue oder geaenderte VU-/VN-Fachlogik;
- genau eine Periode und genau ein Runneraufruf je erfolgreichem Request;
- keine Queue-Anlage, kein Preflight und kein vorhandener Fixture-Adapter;
- keine Ergebnis- oder Idempotenzpersistenz;
- kein Carryover, Scheduler oder Mehrperiodenlauf;
- keine Ausgabedatei und kein Legacy-Vergleich;
- keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.

## Restplanung

- **PR131:** manuellen Workbench-Start und read-only Ergebnisansicht an eine
  dauerhafte Freigabe-, Idempotenz- und Verlaufskette anbinden.
- **PR132:** Browser-Smoke, Fehlerpfade und Handbuch-Screenshots fuer den eng
  benannten Einperiodenpfad abschliessen.

Nach PR130 verbleiben zwei kleine PRs bis zur kontrolliert bedienbaren
Einperioden-Wirkungsprobe. Mehrperiodenlauf, Carryover und
Regulierungssimulation bleiben eigene spaetere Ausbaubloecke.

## Naechster Schritt

PR131 macht den Einperiodenpfad kontrolliert bedienbar. Ein Workbench-Start
darf erst nach expliziter Freigabe erfolgen, muss den Idempotenzschluessel
dauerhaft sichern und Ergebnis sowie Versuchshistorie read-only anzeigen.
