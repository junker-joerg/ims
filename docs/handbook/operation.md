# Workbench bedienen

Stand: 2026-09-01
Gilt fuer: lokale IMS-Workbench, Handbuchstand HB2

## Vor dem Bedienpfad

Die Workbench muss bereits lokal gestartet und im Browser erreichbar sein.
Der gepruefte Windows-Installations- und Startweg wird in HB3 als eigener
Kurzstart dokumentiert. Linux ist noch nicht verifiziert; iOS/Juno ist noch
eine offene Machbarkeitsfrage.

Beginne nur, wenn im `Dashboard` mindestens Folgendes sichtbar ist:

- Backend `bereit`;
- Frontend `gebaut`;
- eine nachvollziehbare Metadatenquelle;
- keine unerwartet aktiven Schreib- oder Simulationspfade.

Steht das Backend auf `nicht erreichbar`, das Frontend auf `nicht gebaut` oder
ist die Datenquelle unerwartet, brich den Bedienpfad ab. Die spaetere
Fehlerhilfe wird diese Faelle in HB6 zusammenfassen.

## 1. Szenario auswaehlen

1. Waehle in der Navigation `Szenarien`.
2. Suche in der `Szenario-Uebersicht` nach Name oder ID.
3. Grenze die Liste bei Bedarf ueber Status, Quelle oder Umfang ein.
4. Waehle eine Zeile und pruefe im `Metadaten-Detail` Name, ID, Umfang und
   Validierungsangabe.
5. Pruefe in der `Auswahlzusammenfassung`, ob Szenario und Quelle zur Aufgabe
   passen.

Die Szenarioansicht ist kein Editor. Es gibt im aktuellen Bedienpfad keinen
Browser-Upload und keine freie Aenderung historischer Eingaben.

## 2. Run auswaehlen

1. Waehle in der Navigation `Runs`.
2. Suche in der `Run-Uebersicht` nach Name oder ID.
3. Filtere bei Bedarf nach Status, Szenario oder Quelle.
4. Waehle den Run und pruefe Periodenfenster, Szenariozuordnung und
   Ausfuehrungsstatus.
5. Wechsle zur `Run-Control-Uebersicht` und kontrolliere den ausgewaehlten
   Queue-Eintrag oder den Hinweis, dass noch keiner vorhanden ist.

Der oben sichtbare Knopf `Neuer Lauf` gehoert in HB2 nicht zum freigegebenen
Bedienpfad. Fuer kontrollierte Aktionen ist ausschliesslich der nachfolgende
Run-Control-Ablauf massgeblich.

## 3. Validierungsstatus lesen

1. Waehle in der Navigation `Validierung`.
2. Pruefe den `Kernvalidierungsueberblick` und den `Validierungsstatus`.
3. Unterscheide technische Bereitschaft von fachlicher Freigabe.
4. Bei `blocked_calculated_core_validation` darf die Workbench technisch
   funktionieren; der historische Kernvergleich ist dann noch nicht als
   vollstaendig bewertet freigegeben.
5. Lies offene Hinweise, bevor du Queue- oder Freigabeaktionen ausfuehrst.

Die Bedeutung der Feld- und Zeilentreffer steht in
[Ergebnisse und historische Validierung verstehen](results_and_validation.md).

## 4. Dry-Run pruefen

1. Vergewissere dich, dass das richtige Szenario und der richtige Run
   ausgewaehlt sind.
2. Waehle im `Run-Control-Dry-Run-Vertrag` die Aktion `Dry-Run pruefen`.
3. Pruefe im Ergebnis insbesondere Request, Preflight, Szenariozuordnung,
   Schreibgrenzen und Ausfuehrungsstatus.
4. Fahre nur fort, wenn keine unerwarteten Blocker oder Zuordnungsfehler
   angezeigt werden.

Der Dry-Run prueft den Request. Er startet keinen Adapter und keine
Simulation.

## 5. Queue vormerken

1. Waehle `Queue vormerken` erst nach einem erfolgreichen Dry-Run.
2. Pruefe Queue-ID, Run-ID, Szenario-ID und Status in der angezeigten
   Vormerkung.
3. Lies danach den `Run-Control-Aktionsplan`.
4. Kontrolliere in der `Run-Control-Uebersicht`, welcher naechste Schritt fuer
   den Queue-Eintrag ausgewiesen wird.

Die Queue-Vormerkung ist ein ausdruecklicher Schreibvorgang in die konfigurierte
lokale Metadatenquelle. Sie startet keinen Queue-Worker und keine Simulation.

## 6. Explizite Freigabe pruefen

Dieser Schritt ist nur fuer einen bereits vorab validierten Queue-Eintrag
vorgesehen.

1. Pruefe im `Run-Control-Ausfuehrungsflow` die Reihenfolge
   `Preflight -> explizite Freigabe -> Ausfuehren`.
2. Trage unter `Freigegeben von` eine nachvollziehbare Person ein.
3. Trage unter `Begruendung` den konkreten Zweck ein.
4. Aktiviere `Ausfuehrung explizit freigeben`.
5. Waehle `Freigabe pruefen`.
6. Fahre nur fort, wenn der Freigabecheck den Start explizit zulaesst und der
   ausgewaehlte Queue-Eintrag unveraendert ist.

Eine Freigabe ist an Queue-Eintrag, Person und Begruendung gebunden. Aenderst
du diese Angaben, muss sie erneut geprueft werden.

## 7. Kontrollierten Adapter starten

`Adapter starten` wird erst aktiv, wenn die serverseitigen Vorbedingungen
erfuellt sind. Der Start ist manuell und idempotent. Er startet den eng
freigegebenen kontrollierten Adapter, keinen automatischen Worker und keine
historische Simulation.

1. Waehle `Adapter starten` nur fuer den geprueften Queue-Eintrag.
2. Warte auf den aktualisierten Queue- und Ergebnisstatus.
3. Wiederhole den Start nicht als Fehlerbehandlung; lies zuerst Status und
   Verlauf.

## 8. Ergebnis und Verlauf lesen

1. Oeffne die `Run-Control-Ergebnisanzeige`.
2. Pruefe Queue, Run, Szenario, Summary-Modus und Persistenzzeitpunkt.
3. Lies den `Run-Control-Ausfuehrungsverlauf` fuer Freigabe-, Start- und
   Fehlerhinweise.
4. Waehle `Ergebnis neu laden`, wenn sich der Serverstatus geaendert hat.
5. Ordne das Ergebnis anschliessend mit dem `Kernvalidierungsueberblick` ein.

Ein persistiertes Adapter-Resultat belegt, dass der kontrollierte technische
Pfad funktioniert hat. Es belegt fuer sich allein weder einen historischen
Modelllauf noch historische Vollgleichheit oder Produktionsfreigabe.

## Schreib- und Stopgrenzen

| Aktion | Schreibt | Startet Ausfuehrung |
| --- | --- | --- |
| Szenario/Run waehlen und filtern | nein | nein |
| `Dry-Run pruefen` | nein | nein |
| `Queue vormerken` | Queue-Metadaten | nein |
| `Freigabe pruefen` | Freigabe-/Auditkontext gemaess Serververtrag | nein |
| `Adapter starten` | Status, Audit und Adapter-Resultat | kontrollierter Adapter, keine Simulation |
| `Ergebnis neu laden` | nein | nein |

Bei unklarer Quelle, unerwartetem Schreibpfad, geaendertem Queue-Eintrag oder
einem fachlichen Blocker wird nicht weiter freigegeben. Der Browser darf nicht
dazu verwendet werden, historische Referenzen zu ueberschreiben oder lokale
Dateien aus `incomming/` zu importieren.
