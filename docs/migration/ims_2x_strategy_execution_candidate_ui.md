# PR128: Kandidatenreife in der Workbench

Stand: 2026-09-08

## Einordnung

PR127 hat vollstaendig gebaute Einperioden-Ausfuehrungskandidaten
unveraenderlich in der lokalen SQLite-Ablage gespeichert. PR128 ergaenzt eine
rein lesende Beobachtungsschicht fuer diese Datensaetze.

## C-zu-Python-Mapping

| Historischer Bezug | Python-Ziel | Fachliche Entsprechung |
| --- | --- | --- |
| gemeinsamer Zustand fuer `Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06` in `IMS.E` | `ims.api.strategy_execution_candidate_store` | erneut digestgepruefte Uebersicht des bereits gebauten und gespeicherten Einperiodenzustands |
| implizite Herkunft eines historischen Laufs | Kandidaten-, Entwurfs- und Profilidentitaet in der Workbench | sichtbare moderne Provenienz ohne historische Gleichheitsbehauptung |
| kein historischer UI-Speicherstatus | Tab `Kandidaten` in `frontend/src/main.tsx` | read-only Reife-, Digest- und Ablageanzeige |

PR128 portiert keine historische Regel und behauptet keine historische UI-
Entsprechung.

## Umsetzung

Der neue Uebersichtsabruf oeffnet eine vorhandene SQLite-Datei read-only und
legt bei leerer Ablage weder Datei noch Tabelle an. Vor der Aufnahme eines
Datensatzes in die Antwort wird die PR127-Integritaetspruefung fuer
Kandidatenpayload, Digest und relationale Metadaten wiederverwendet.

Die Workbench zeigt den Ablagezustand, die belegten Reifestufen, die Herkunft
aus Entwurf und Marktprofil, Akteurs- und Snapshotzahlen, Speicherzeitpunkt
sowie den vollstaendigen SHA-256-Digest. Die Run-Control-Stufe bleibt sichtbar
gesperrt. `Aktualisieren` fuehrt nur denselben GET-Abruf erneut aus.

## Grenzen

- Der angezeigte Digest belegt technische Inhaltsidentitaet, keine fachliche
  oder historische Vollgleichheit.
- Ein fehlender Speicher wird als nicht konfigurierter Zustand behandelt.
- Beschaedigte Kandidaten werden nicht teilweise angezeigt oder repariert.
- Es gibt in der neuen Ansicht keinen POST-, Speicher-, Freigabe- oder
  Startpfad.
- Runner, Scheduler, Carryover, Ergebnisexport und Simulation bleiben
  unberuehrt.

## Validierung

Store- und API-Tests pruefen leere sowie gefuellte Ablagen und erkennen
veraenderte Metadaten. Ein Frontend-Grenztest belegt den GET-only Abruf,
sichtbare Provenienz, Reife und Sperrstatus. Der Produktionsbuild und ein
Browser-Smoke pruefen die Darstellung auf Desktop und schmalem Viewport.

## Offene Punkte

- PR129 verbindet Kandidaten-ID und erneut geprueften Digest mit der
  Run-Control-Freigabegrenze, ohne bereits zu starten.
- PR130 bleibt der erste geplante, eng kontrollierte Einperioden-Aufruf auf
  einer isolierten Kopie.
- Mehrperiodenfolge, Carryover und fachliche Regulierungsszenarien gehoeren
  nicht zu PR128.
