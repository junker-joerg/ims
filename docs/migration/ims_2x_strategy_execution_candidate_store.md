# PR127: Unveraenderliche Ablage des Ausfuehrungskandidaten

Stand: 2026-09-08

## Einordnung

PR126 konnte aus gemeinsamem Strategieentwurf, Kontext, VU-Herkunft,
VN-Prozesseingang und registriertem Marktgrundprofil einen kanonischen
Einperioden-Kandidaten samt SHA-256-Digest bauen. Dieser Zustand war bisher
nur die Antwort eines einzelnen API-Aufrufs.

PR127 ergaenzt die kontrollierte lokale Ablage. Der Kandidat wird dadurch
wiederauffindbar, aber noch nicht ausfuehrbar.

## C-zu-Python-Mapping

| Historischer Bezug | Python-Ziel | Fachliche Entsprechung |
| --- | --- | --- |
| gemeinsamer Laufzustand fuer `Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06` in `IMS.E` | `ims.strategies.execution_candidate_build` | bereits in PR126 kanonisch gebauter Einperiodenzustand |
| keine eigenstaendige historische Persistenzgrenze | `ims.api.strategy_execution_candidate_store` | moderne, explizit freizugebende und unveraenderliche Ablage |
| implizite Identitaet eines gestarteten Laufs | Kandidaten-ID plus SHA-256-Digest | reproduzierbare technische Identitaet vor jeder spaeteren Freigabe |

Es wird keine historische Speichersemantik behauptet und keine Fachregel
veraendert.

## Umsetzung

`strategy_execution_candidates` speichert Kandidaten-ID, Quellidentitaet,
Periode, Profilbezug, Digest, Speicherzeitpunkt und den kanonischen JSON-
Payload. Es gibt absichtlich keinen Update- oder Delete-Pfad.

Der Schreibpfad akzeptiert nicht den im Browser sichtbaren Kandidaten. Er
nimmt die urspruenglichen versionierten Dokumente entgegen, baut damit den
Kandidaten serverseitig neu und vergleicht das Ergebnis mit der explizit
freigegebenen ID und dem Digest. Vor dem `INSERT` und nach dem Wiederlesen
wird der Inhaltsdigest berechnet. Der read-only Abruf wiederholt dieselbe
Integritaetspruefung.

Eine identische Wiederholung liefert den vorhandenen Datensatz ohne
Schreibzugriff. Jede Abweichung in Payload oder relationalen Metadaten ist
ein Konflikt und wird nicht still durch ein Upsert geheilt.

## Grenzen

- Die Ablage ist lokal und verwendet die konfigurierte Workbench-SQLite-
  Datei.
- Der Speicherzeitpunkt gehoert zur Ablagehuelle und nicht zum fachlichen
  Kandidatendigest.
- Ein SHA-256-Digest belegt technische Inhaltsidentitaet, keine historische
  oder fachliche Vollgleichheit.
- PR127 startet weder Run-Control noch den Einperioden-Runner.
- Mehrperiodenzustand, Carryover, RNG-Fortschreibung und Ergebnisexport sind
  nicht enthalten.

## Validierung

Unit-Tests decken Neuanlage, read-only Abruf, exakte Wiederholung,
Freigabesperre, Erwartungsabweichungen, atomare Baufehler sowie erkannte
Datenbeschaedigung ab. API-Tests pruefen Vertrag, Statuscodes, Methoden und
die Bindung an eine explizite SQLite-Quelle. Ein eigener Grenztest ersetzt
den Runner durch eine fehlschlagende Attrappe und belegt, dass keine
Ausfuehrung erfolgt.

## Offene Punkte

- PR128 visualisiert Reife, Herkunft, Digest und Speicherstatus eines
  gespeicherten Kandidaten read-only.
- PR129 darf Run-Control nur ueber Kandidaten-ID plus erneut geprueften
  Digest anbinden.
- PR130 stellt den eng kontrollierten Einperioden-Aufruf auf einer isolierten
  Kopie bereit; PR131 bindet Ergebnisablage und Idempotenz an.
