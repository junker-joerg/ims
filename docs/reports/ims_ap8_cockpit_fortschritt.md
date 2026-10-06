# AP8: gemeinsames Marktexperiment, Produkt alpha.10

04.10.2026. [Auftrag und Umsetzungsplan](../plans/ims_ap8_experiment_cockpit.md).
Im bestehenden [Paket-PR #297](https://github.com/junker-joerg/ims/pull/297).
Anwenderabnahme und Merge bleiben offen. Kein AP9-Auftrag und kein öffentliches Release.

Die neue Benutzerführung verbindet den geladenen Markt, endogene Anbieter-
und Nachfrageparameter, exogene Ereignisse und Ergebnis in einer Sitzung.
Anbieteränderungen erzeugen bestehende ausführbare Maßnahmen; Gegenmaßnahmen
und Vergleichsachse verwenden den AP7-Vertrag. Jede Quellenänderung entwertet
Ergebnis und Export. Schritt-/Ansichtswechsel erhalten Sitzung und Auswahl.
Die direkt gebundene BaFin-Abbildung wird nicht durch freie Modelländerungen
entkoppelt. Eigene Änderungen erfolgen in den bestehenden abgeleiteten Fällen.

Die gesamte Oberfläche verwendet gemeinsame Gestaltung: dunkle Navigation,
Hell-/Dunkelflächen, klare Typografie, türkis bezeichnete Strategien und
bernsteinfarbene Umwelt. Fallablage und Modellwerkzeuge werden deutlich benannt.
Ergebnisse zeigen den zuletzt geöffneten Modellfall. Rollenwechsel öffnet den
jeweiligen Aufgabenpfad. Kennzahlen kommen aus tatsächlichen Buchungen; das
Providerdiagramm zeigt deklarierte Kanten und reale Modell-Ausfallzeilen.

## Bisherige Prüfungen

- TypeScript/Vite-Build erfolgreich; bestehende Warnung zum Gesamtbundle über 500 kB.
- 44 Python-Tests und 14 Subtests erfolgreich, einschließlich AP8-Projektion und
  Planung; eine bestehende Starlette-Deprecation-Warnung.
- Neun aktuelle Browserfälle erfolgreich: neue Maßnahmen samt einmaliger P6-
  Buchung und frischem JSON-Export; eigener ICT-Ausfall/Ersatzpfad/Vergleich,
  ungültige Intensität sperrt Ergebnis/Export; sechs Kombinationen aus drei
  Bildschirmgrößen und Hell/Dunkel mit Tastatur, AXE und erhaltenen Zuständen;
  wieder geprüfter Rollenweg im AP5-Peer-Fall. Keine übersprungenen/flaky Fälle.
- 19 weitere Browserfälle im ersten Lauf erfolgreich (globale Navigation,
  alle bisherigen Modellbereiche, 44-Pixel-Ziele, Kontrast einschließlich großer
  Schrift, Speicherung/Exporte und AP5-Quellen). Ein zusätzlich verdeckter
  Rollenpfad wurde durch automatisches Öffnen beim Rollenwechsel korrigiert und
  anschließend in den neun Fällen erfolgreich nachgeprüft.
- Vollständige lokale AP8-Browserprüfung: 13 Fälle erfolgreich in 12,6 Minuten,
  einschließlich aller vier übernommenen 100er-Digests, 25er-Prefixe, frischem
  JSON-/Excel-Export, 22 Offline-Anleitungsbildern und sechs Hell/Dunkel-/ICT-
  Kombinationen. Keine übersprungenen, flaky oder wiederholten Testfälle.
- Der neue Vorstandseditor erhält bestehende Parametermaßnahmen statt sie zu
  überlappen. Neue Board-Maßnahmen vor P6 werden im geführten Vergleich abgewiesen;
  bestehende Rechenverträge und historische Handfälle bleiben unverändert.
  Die gezielte Browserprüfung des neuen Eingabewegs und der sechs Darstellungen wurde danach erneut ausgeführt: neun Fälle erfolgreich in 64,2 Sekunden.
- Vollständige neue Produkt-CI und Installerbelege folgen am eingefrorenen Produktpunkt.

Die alpha.9-CI am Commit 392efe7 war nicht vollständig erfolgreich:
sechs Browserfälle scheiterten an verdeckten Werkzeuglinks beziehungsweise dem
nach Reload noch nicht gewählten Schockbereich. Diese tatsächlichen Wege sind
jetzt in den Prüfungen berücksichtigt; keine Fälle wurden entfernt. Die neue
alpha.10 benötigt eigene vollständige Nachweise. Frühere alpha.8-Abnahmen werden
nicht auf diese Fassung übertragen. Technische Prüfung ersetzt keine menschliche
Verständlichkeitsabnahme.

Nächster Schritt: echte Produkt-CI einschließlich Installer und installierter
Browserprüfungen auswerten, Paketbeschreibung und Abschlussbelege aktualisieren.

## Vollständiger technischer Abschluss

04.10.2026: Vier Produktchecks an `11384cf69f14f52d3c0f0ae72537986a94484e57` erfolgreich.
2764 Python-Tests/14 Subtests, 91 Checkout- und 91 installierte Browserfälle,
14 Lifecycle-Prüfungen, 409 Ressourcen und geprüfter alpha.10-Installer.
[Produktprüfung](ims_ap8_cockpit_produktpruefung.md),
[Verifikation](ims_ap8_cockpit_verification.json),
[Abschluss](ims_ap8_cockpit_abschlussbericht.md).
Vorstehende offene Prüfstände sind historisch. Anwenderabnahme und Merge offen.
