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
- Vollständige AP8-Browserprüfung mit vier übernommenen 100er-Digests läuft.
  Vollständige neue Produkt-CI und Installerbelege folgen am eingefrorenen Produktpunkt.

Die alpha.9-CI am Commit 392efe7 war nicht vollständig erfolgreich:
sechs Browserfälle scheiterten an verdeckten Werkzeuglinks beziehungsweise dem
nach Reload noch nicht gewählten Schockbereich. Diese tatsächlichen Wege sind
jetzt in den Prüfungen berücksichtigt; keine Fälle wurden entfernt. Die neue
alpha.10 benötigt eigene vollständige Nachweise. Frühere alpha.8-Abnahmen werden
nicht auf diese Fassung übertragen. Technische Prüfung ersetzt keine menschliche
Verständlichkeitsabnahme.

Nächster Schritt: echte Produkt-CI einschließlich Installer und installierter
Browserprüfungen auswerten, Paketbeschreibung und Abschlussbelege aktualisieren.
