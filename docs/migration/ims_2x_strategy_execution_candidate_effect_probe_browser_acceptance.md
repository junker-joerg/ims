# PR132: Einperioden-Bedienpfad im Browser abnehmen

Stand: 2026-09-11

## Einordnung

PR132 ergaenzt den vorhandenen PR131-Start um Abnahme, reproduzierbaren
Smoke-Aufbau und Benutzerbelege. Kandidatenbau, Digestpruefung,
Einperioden-Runner, Idempotenz und Ergebnisablage bleiben fachlich und
technisch unveraendert.

## C-zu-Python-Mapping

| Historischer Bezug | Python-/UI-Ziel | Bedeutung |
| --- | --- | --- |
| Einperiodenwirkung der Aktionen `Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06` in `IMS.E` | vorhandener PR130/PR131-Pfad | unveraenderte Wirkung auf einer isolierten Kandidatenkopie |
| historisch manueller Programmstart | Workbench-Freigabeformular | sichtbare Person, Begruendung und ausdrueckliche Einperiodenbestaetigung |
| unmittelbare Terminal- und Dateiausgaben | Ergebnis- und Verlaufsansicht | digestgepruefter Nachweis ohne neue Ergebnisdatei |

PR132 portiert keine C-Regel. Der Smoke prueft die Bedienoberflaeche um den
bereits vorhandenen Kernanschluss.

## Umsetzung

Der neue Loopback-Smoke erzeugt eine frische SQLite-Datei, baut den
versionierten gemeinsamen VU-/VN-Kandidaten serverseitig neu und speichert
ihn ueber den unveraenderten PR127-Vertrag. Danach liefert er das regulaere
gebaute Frontend und die regulaeren PR131-Endpunkte aus.

Stabile `data-testid`-Anker decken Tab, Kandidatenauswahl, Freigabefelder,
Bestaetigung, Start, Fehler, Ergebnis, Verlauf und Mehrperiodengrenze ab. Sie
aendern weder Text noch Verhalten der Workbench.

## Sichtbare Abnahme

Chrome wurde mit dem gebauten Frontend gegen die isolierte Smoke-Instanz
geprueft:

- `1440 x 1000`: Ergebnis, sechs Wirkungskennzahlen, Ergebnisdigest,
  erfolgreicher Verlauf und PR133-Grenze gleichzeitig sichtbar;
- `390 x 844`: einspaltiger Umbruch ohne horizontales Abschneiden,
  Ueberlagerung oder unlesbare Schaltflaechen;
- vor der Checkbox ist `Wirkungsprobe starten` deaktiviert;
- nach dem erfolgreichen Start ist ein erneuter Start sichtbar gesperrt.

Die datierten PNG-Dateien liegen unter `docs/handbook/images/` und werden im
Bedienhandbuch fachlich eingeordnet.

## Automatisierte Abnahme

Die Tests pruefen:

- frische Datenbank, vorhandenen Frontend-Build und Loopback-Bindung;
- einen echten erfolgreichen Einperiodenaufruf mit einem Ergebnis und einem
  Verlaufseintrag;
- idempotente Wiederholung ohne zweiten Runneraufruf;
- fehlende Ausfuehrungsfreigabe ohne Schreiben;
- falschen Digest ohne Runneraufruf;
- deterministischen Runnerfehler ohne Ergebnis, aber mit Fehlerverlauf;
- Vorhandensein aller Browseranker und Lesbarkeit beider PNG-Dateien.

## Grenzen und naechster Schritt

Die Browserabnahme belegt einen kontrolliert bedienbaren technischen und
fachlichen Einperiodenpfad. Sie belegt keinen 100-Periodenlauf, keine
Regulierungssimulation und keine Reproduktion eines historischen RNG-Laufs.

PR133 hat den versionierten Periodenketten- und Carryover-Vertrag festgelegt.
PR134 prueft den vollstaendigen Ketteneingang zustandslos. PR135 soll als
naechstes die Kandidatenreferenzen serverseitig aufloesen; auch dieser Schritt
schaltet noch keinen Mehrperiodenstart frei.
