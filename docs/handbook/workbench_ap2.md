# Die Workbench bedienen

Stand: 06.10.2026. Die Oberfläche ist in sechs Hauptbereiche gegliedert. Der gemeinsame Markt liegt unter **Markt und Strategien → Markt verstehen**; seine [aktuelle Anleitung](market_ap8.md) erklärt den Ablauf. Am großen Bildschirm wechseln
Sie links, am Smartphone über die untere Navigation. Eingaben, berechnete
Ergebnisse und noch nicht verwendete Freigaben bleiben beim Wechsel erhalten.
Neuladen der Seite beginnt eine neue Sitzung; gespeicherte Fälle bleiben in der
lokalen Ablage.

| Bereich | Zweck |
| --- | --- |
| Übersicht | Modellfall öffnen, Szenario vorbereiten, Ergebnisse oder Hilfe erreichen; Systemstatus lesen. |
| Markt und Strategien | Gemeinsamer Modellmarkt, Vorstandsstrategien, äußere Ereignisse und sechs verknüpfte Auswertungen; Modellwelt, Unternehmen und Laufwiedergabe. |
| Fallablage | Vorhandene lokale Szenario- und Laufmetadaten ansehen, filtern und bearbeiten. Rechenannahmen stehen im Modellfall. |
| Modellwerkzeuge | Kfz/Sach, Leben, Kranken, Gesamtbilanz und Kapitalwirkung berechnen. Strategien und Ausführung sind gesonderte Expertenansichten. |
| Ergebnisse | Tatsächlich berechnete Ergebnisse und lokale Lebens-/Krankenverläufe prüfen, ausdrücklich speichern und exportieren. |
| Hilfe | Bedienhinweise und Modellgrenzen lesen; Diagnose- und Vertragsdetails bei Bedarf aufklappen. |

## Ein Modell prüfen

1. In der Übersicht **Modellfall öffnen** wählen oder unter **Modellwerkzeuge**
   eine Sparte öffnen.
2. Baseline und Variante eingeben. Die sichtbaren Herkunftsangaben erklären,
   ob Beispielwerte oder geprüfte Spartenquellen vorliegen.
3. Berechnen. Während einer laufenden Anfrage zeigt die Aktion ihren
   Ladezustand. Ungültige Eingaben lösen eine sichtbare Fehlermeldung aus;
   korrigieren und im selben Formular erneut berechnen.
4. Diagramm und genaue Tabellenwerte vergleichen. Breite Tabellen lassen sich
   innerhalb ihrer Fläche horizontal und vertikal scrollen. Mit Tabulator auf
   die Tabelle wechseln und die Pfeiltasten verwenden.
5. Unter **Ergebnisse** weiterarbeiten. Lebens-/Krankenfälle werden erst nach
   ausdrücklicher Speicherfreigabe persistiert; die vorhandenen Exporte stehen
   danach am geprüften Fall. Die Kapitalwirkung bietet geprüfte JSON-/XLSX-
   Exporte. Die Kfz-/Sachbilanz bietet den vorhandenen XLSX-Export.

Geänderte Annahmen entwerten Ergebnisse, abhängige Gesamtbilanzen und Freigaben
wie bisher. Eine Navigation ersetzt keine Prüfung. Gesamtbilanz setzt geprüfte
Kfz-, Sach-, Lebens- und Krankenquellen voraus; Kapitalwirkung benötigt die
geprüfte Gesamtbilanz und ihre eigene Bestätigung.

## Darstellung und Grenzen

Oben schalten Sie Hell-/Dunkelmodus um. Die Auswahl wird lokal gespeichert,
soweit der Browser dies erlaubt; ohne gespeicherte Wahl gilt die Systemwahl.
Tabulator und Umschalt+Tabulator bedienen die Oberfläche; der Fokus ist sichtbar.
**Zum Inhalt** überspringt die Navigation. Reduzierte Bewegung des Betriebssystems
wird berücksichtigt. Aufklappbare Details bleiben zunächst geschlossen.

Historische Direktlinks wie `#health`, `#capital`, `#scenarios`, `#runs` und
`#validation` funktionieren weiter. Zurück/Vorwärts wechselt zwischen Bereichen.

Die Berechnungen sind weiterhin explizite Seminar- und Bilanzmodelle. Sie
behaupten keine historische Vollgleichheit, gesetzliche Bilanz oder berechneten
regulatorischen SCR/MCR. Technische Ausführungssperren und ausdrücklich zu
erteilende Freigaben gelten weiter. Der geführte 100-Perioden-Ablauf ist AP3
zugeordnet und wird hier nicht als verfügbare Aktion angeboten.

## Bilder und Browserprüfung

| Darstellung | Vor AP2 | Nach AP2 |
| --- | --- | --- |
| 1440×900, Übersicht | [Vorher](images/ap2_before_overview_1440x900.png) | [Hell](images/ap2_after_overview_light_1440x900.png), [Dunkel](images/ap2_after_overview_dark_1440x900.png) |
| 1024×768, Übersicht | [Vorher](images/ap2_before_overview_1024x768.png) | [Hell](images/ap2_after_overview_light_1024x768.png), [Dunkel](images/ap2_after_overview_dark_1024x768.png) |
| 390×844, Übersicht | [Vorher](images/ap2_before_overview_390x844.png) | [Hell](images/ap2_after_overview_light_390x844.png), [Dunkel](images/ap2_after_overview_dark_390x844.png) |
| Kranken, 390×844 | [Vorher](images/ap2_before_health_390x844.png) | [Hell](images/ap2_after_health_light_390x844.png), [Dunkel](images/ap2_after_health_dark_390x844.png) |
| Gespeichertes Ergebnis, 390×844 | — | [Hell](images/ap2_after_results_light_390x844.png), [Dunkel](images/ap2_after_results_dark_390x844.png) |

Für Entwickler: im Checkout `.venv` mit editable install von `python_port[web]` einrichten,
`npm.cmd ci --prefix frontend`, `frontend\node_modules\.bin\playwright.cmd install chromium`,
`npm.cmd run build --prefix frontend`, dann `npm.cmd run test:browser --prefix frontend`.
Der Test startet den vorhandenen Launcher mit einer eigenen temporären Ablage.
`IMS_BASE_URL` prüft alternativ einen bereits gestarteten Server; der Installer-
Test nutzt damit die installierte EXE. `IMS_CAPTURE=1` aktualisiert die
Handbuchbilder. Die JSON-Berichte liegen unter `.tmp-pr-ap2`, Fehler zusätzlich
als Screenshot und Browser-Trace. CI archiviert die Nachweise.
