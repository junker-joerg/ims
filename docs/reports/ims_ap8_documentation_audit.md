# Aktualitätsprüfung der Repository-Dokumentation

Stand: 06.10.2026, AP8 alpha.11. Auftrag umfasst aktuelle Benutzerführung, Eingaben und Rechenkern-Dokumentation. Die Prüfung unterscheidet heutige Einstiegstexte von historischen Nachweisen und angenommenen Plänen.

## Prüfmethode

`scripts/documentation/audit_repository_docs.py` inventarisiert alle versionierten und neuen nicht ignorierten Textdokumente unter docs sowie README/AGENTS. Es prüft lokale Markdown-/HTML-Verweise auf vorhandene Ziele. Das [maschinenlesbare Inventar](ims_ap8_documentation_inventory.json) enthält jede Datei mit ihrer Einordnung und den geprüften Verweisen. Es behauptet keine erneute manuelle fachliche Vollprüfung aller historischen Berichte.

Die aktuellen Handbuch-Einstiege, Menüwege, Releasehinweise und Aussagen zum gemeinsamen Markt wurden mit den tatsächlich vorhandenen UI-Komponenten und AP5-/AP6-/AP7-Verträgen verglichen. Originalherkunft und Abweichungen sind in [Rechenkern](../handbook/rechenkern.md) erläutert. Der frühere Gesamt-C-Gleichlauf wird nicht aus aktuellen modernen Prüfungen abgeleitet.

## Notwendige Korrekturen

| Fund | Aktualisierung |
| --- | --- |
| Handbuchindex verwies primär auf AP2/AP3 und fünf alte Bereiche | Heutiger gemeinsamer Markt zuerst; sechs Hauptbereiche; aktuelle AP8-, Eingabe- und Rechenkernlinks |
| „Simulation“ und „Szenario“ als Hauptmenüs | Bedienwege zu Modellwerkzeuge bzw. Fallablage korrigiert; Markt und Strategien mit eigenem Einstieg |
| AP6-Datenanforderung als scheinbar aktueller Lieferstand | Als historischer Anforderungsstand markiert und auf gelieferten BaFin-Referenzfall verwiesen; deutsche Direktmarkttore bleiben offen |
| Installer-/Kurzstarttexte ohne heutigen Umfang | Aktuelle Produktnummer und getrennte Prüfung; alter AP1-Abnahmebeleg bleibt auf AP1 begrenzt |
| Frühe „kein 100er-Markt“-Aussagen ohne Paketbezug | Heutigen deklarierten AP5-/AP7-Markt unterscheiden von historisch nicht belegtem Vollmodell |
| Migrationseinstieg ohne gemeinsame Marktübersicht | Neue Übersicht mit tatsächlichen Originalstellen, moderner Prozessbrücke und Grenzen |
| Neues Bild mit Pause und fiktiven Kennzahlen | Anzeige-Wiedergabe klar kennzeichnen; kein Kerncheckpoint, keine SCR-/Solvenz-/Auszahlungswirkung erfinden |
| Keine systematische Eingabeliste | 37 fachliche Gruppen sowie AST-Nachweis jeder bestehenden input/select/textarea-Deklaration |
| Historische Bilder neben aktuellem Text | Ursprüngliche alpha.8/alpha.10-Versionen erhalten und benennen; sechs neue alpha.11-Browserbilder separat |

## Erhaltene Historie und Restgrenzen

Angenommene Planumfänge, menschliche Abnahmen, ursprüngliche Testzahlen, Produktpunkte und frühere Ergebnisdigests bleiben unverändert. Das aktuelle Manifest führt die erneute AP8-Erweiterung getrennt. Vorgängerberichte sind keine Prüfung der neuen UI. Bei alten komponentenbezogenen Migrationsnotizen dient eine heutige Einordnung dem Lesen; ihr damals beschriebener Vertrag wird nicht rückwirkend erweitert.

`installer_windows.html` wird im Installer als `help.html` an die Ressourcenwurzel kopiert. Seine PDF-/Handbuchlinks werden deshalb gegen diesen Auslieferungspfad geprüft, nicht gegen das Quellenverzeichnis docs/handbook. HTTP-Links zu Rechenkern, Eingaben und den drei SVGs werden zusätzlich im Browser geprüft. Historische Berichte und Migrationslinks in neu gerendertem HTML erhalten explizite Repository-Links, da diese Berichtssammlung nicht vollständig als HTTP-Handbuchroute ausgeliefert wird.

Dokumentationsaktualität ist keine fachliche Kalibrierung der BaFin-Gruppe, kein Beleg eines deutschen Direktmarktes und keine Erweiterung der bisherigen AP7-Verträge. Anwenderabnahme, AP8-Merge, öffentliches Release und AP9–AP14 bleiben offen beziehungsweise nicht beauftragt.
