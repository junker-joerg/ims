# AP8: Bedienkorrektur vor Anwenderabnahme

03.10.2026. Der Auftraggeber meldet zunehmende Orientierungsprobleme und hält
die Oberfläche für nicht vorzeigbar. Korrektur im bestehenden AP8-Paket und
PR #297; keine AP9-Umsetzung oder Mergefreigabe.

## Befund und Umsetzung

Zwölf gleichrangige Modellreiter, drei unabhängige Marktformulare und sechs
vollständig ausgeschriebene Auswertungen erschweren die Orientierung. Der
Einstieg fehlte in der Hauptnavigation; Anleitung und Menüname stimmten nicht
überein. Erfolgreiche Rechentests belegen keine verständliche Bedienung.

* Markt und Familien direkt in der Hauptnavigation, aktueller Ort eindeutig.
* Modellwahl: häufige Fälle direkt, weitere Werkzeuge in benannten Gruppen.
* Markt: Hauptbereich „Markt verstehen“; Schockbearbeitung und Quellen/
  Handfälle erst nach Auswahl. Instanzen bleiben montiert, damit Eingaben,
  geprüfte Ergebnisse und Freigaben beim Wechsel erhalten bleiben.
* Klarer Ablauf: Fall wählen, Vorlage laden, frisch rechnen, Ergebnis erkunden.
  Import getrennt; Laden/Fehler/veralteter Stand sichtbar.
* Jeweils eine von sechs Ansichten; gemeinsame Filter und Buchungsnachweis
  bleiben erhalten. Rollen öffnen die passende Ansicht.
* Einheitliche Abstände, lesbare Formulare, führende Rechenaktion,
  Tastaturbedienung und sichtbare Auswahl in beiden Farbmodi.

## Herkunft und Prüfung

Prinzipien: [NN/G: Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/),
[GOV.UK: Buttons](https://design-system.service.gov.uk/components/button/) und
[W3C: konsistente Navigation](https://www.w3.org/WAI/WCAG22/Understanding/consistent-navigation).
Eigene Anwendung dieser Prinzipien, keine behauptete Zertifizierung oder
Anwenderabnahme. Keine Frameworkmigration.

Kein Simulationskern, Buchungsvertrag oder Modellkanal geändert. Historisches
C-Mapping bleibt die AP8-Projektion aus AP5/AP7; betroffen sind Navigation,
React-Darstellung, CSS und Anleitung. Filter rechnen nicht neu.
Neue ausgelieferte Produktfassung: alpha.9 (AP8-Korrektur, kein AP9).
Historische alpha.8-Belege bleiben erhalten. Die Korrektur braucht eigene
Browser-, Versions- und Installerbelege; Abnahme/Merge bleiben offen.
