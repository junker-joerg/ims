# Agrsich-Exportslice: historisch orientierte Exportrepräsentation mit breiteren Messgrößen

Dieser PR erweitert den bisherigen Agrsich-Slice substanziell um eine erste,
historisch orientierte Exportrepräsentation. Der Stand bleibt bewusst konservativ:
keine echte Dateischreibpflicht, keine Vollsimulation und keine Behauptung historischer Vollgleichheit.

## Substanziell erweitert

- breitere Agrsich-Messgrößen für Versicherer und Versicherungsnehmer
- erste Exportrepräsentation mit Dateispezifikation, Kopfzeilen und Datenzeilen
- historisch orientierte Dateibenennung für Aggregatstufen I-IV
- fortlaufende Periodennummer über Wiederholungsläufe als konservative Näherung

## Historische Exportaspekte jetzt adressiert

- Annäherung an historische Dateinamenmuster für VU- und VN-Agrsich-Tabellen
- explizite Tabellenköpfe für Versicherer und konsistente Python-Kopfzeilen für Versicherungsnehmer
- Überführung der in-memory Agrsich-Aggregate in exportnahe Tabellenobjekte

## Bewusst noch nicht portiert

- noch kein echtes Schreiben auf Disk im finalen historischen Dateifluss
- noch keine vollständige Vollabdeckung aller Altgrößen
- noch keine vollständige Tabellen-/Formatkompatibilität bis auf letzte Stelle
- keine Vollsimulation
- keine Behauptung historischer Vollgleichheit

## Nächster sinnvoller Schritt für PR 26

PR 26 sollte die Exportrepräsentation an weitere direkt belegbare historische Messgrößen und
Selektoren anbinden, die Formatannäherung weiter schärfen und erst danach mögliche echte
Schreibpfade oder zusätzliche historische Ausgabevarianten prüfen.
