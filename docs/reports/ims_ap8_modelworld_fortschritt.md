# AP8 alpha.11 · Modellwelt und Dokumentation

Stand 06.10.2026. Fortsetzung im bestehenden Paket-PR #297, Branch `codex/ims-market-visualizations`. Auftrag: vier neue Bilder berücksichtigen, notwendige Eingaben erfassen, Rechenkern samt Abweichungen zum ursprünglichen IMS grafisch erklären, Dokumentation auf Aktualität prüfen.

Modellwelt, Unternehmensportfolio und Wiedergabe vorhandener Perioden sind im gemeinsamen Marktexperiment eingebaut. Fokus führt in denselben Vorstandseditor; Suche, Mehrfachvergleich und Wiedergabe ändern keinen Modelllauf. Die vier bestehenden Arbeitsschritte und sechs Auswertungen bleiben erhalten. Pause/Fortsetzen aus dem Mockup wird ausdrücklich als Anzeigesteuerung eingeordnet. Keine neuen Kernkanäle.

37 fachliche Eingabegruppen und ein AST-Inventar aller 191 Eingabedeklarationen in 19 TSX-Komponenten erstellt. Drei deterministisch erzeugte SVG-Grafiken und ein lesbares Rechenkern-Handbuch mit Originalstellen, Periodenablauf, Buchungsgleichungen, Abweichungen und Prüfgrenzen ergänzt. Offline-HTML und kontrolliertes Installer-Staging erweitert.

Aktuelle Einstiegstexte und Menüpfade korrigiert. Historische Abnahmen, Ergebnisse und Planumfänge werden nicht umgeschrieben. Das vollständige Dokumenten-/Linkinventar liegt separat. Erste lokale Browserproben in Hell/Dunkel bestanden; aktuelle vollständige Produkt- und Installerprüfung noch ausstehend. Frühere alpha.10-Nachweise bleiben historisch.

Responsive Hell-/Dunkelproben, Tastatur/AXE und grafische Sichtprüfung der sechs neuen Browserbilder sowie drei SVGs sind erfolgt. Lokaler Build, 44 Markt-/Planprüfungen, vier Seminar-API-Prüfungen und fünf Handbuchprüfungen bestanden. Dokumentationsinventar: 533 Textdateien, 612 lokale Verweise, kein fehlendes Ziel.

Der erste Windows-Release-Gate-Lauf am Produktpunkt f9e6b05 meldete 2.763 bestandene Tests/14 Subtests und eine veraltete Handbuchindex-Erwartung („Handbuchstand: PR178a“). Die Prüfung wurde auf die aktuellen Menüwege und die vorhandenen Eingabe-/Rechenkernziele aktualisiert; alle fünf Handbuchprüfungen bestehen lokal. [Unveränderter Fehlerbeleg](https://github.com/junker-joerg/ims/actions/runs/37422825328/job/112135769482). Ein neuer Produktpunkt erhält die vier vollständigen CI-Prüfungen. Die Produktfassung alpha.11 ist noch nicht ausgeliefert.

Nächster Schritt: vier reale CI-Checks, vollständige Browser-/Digestnachweise und authentischen Windows-Installer am korrigierten Produktpunkt prüfen. AP8-Anwenderabnahme und Merge bleiben offen. AP9–AP14 nicht beauftragt.
