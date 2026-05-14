# Agrsich-Slice: erster substanzieller Kern mit Aggregatstufen I-IV

Dieser PR portiert einen ersten echten, aber weiterhin kontrollierten Agrsich-Slice nach Python.
Er bleibt bewusst ein in-memory Fachschnitt ohne historische Dateiausgabe und ohne Behauptung
historischer Vollgleichheit.

## Substanziell portiert

- expliziter Aggregatzustand im BAV-Servicezustand
- aktuelle Aktivitätsmengen für Versicherer und Versicherungsnehmer als Basis von Agrsich
- Aggregatstufen I-IV für beide Subjektklassen
- In-Memory-Records für einen ersten portierten Agrsich-Kern
- Mittelwert- und Modusbildung für ausgewählte Versicherer- und Versicherungsnehmermetriken

## Direkt adressierte historische Agrsich-Aspekte

- Aggregation aktuell aktiver Subjekte in mehreren Stufen
- Gruppierung nach Einzelsubjekt, Verhaltensregel, Verhaltensregelklasse und Gesamtklasse
- getrennte Aggregatideen für Versicherer und Versicherungsnehmer
- persistenter BAV-Zustand, der die letzte kleine Agrsich-Aggregation nachvollziehbar hält

## Bewusst noch nicht portiert

- keine Ausgabe in historische Tabellen-/Dateiformate
- keine vollständige Altvektorportierung
- keine Schadenzahl-/Schadenhöhenportierung
- keine vollständige Operatorauswahl für alle Aggregatarten
- keine Vollsimulation
- keine Behauptung historischer Vollgleichheit

## Nächster sinnvoller Schritt für PR 25

PR 25 sollte den portierten Agrsich-Kern an weitere direkt belegbare Aggregatarten anbinden,
zusätzliche Operatoren und Metrikfamilien quellenbasiert ergänzen und erst danach mögliche
Anbindungen an historische Ausgabe- oder Speicherstrukturen prüfen.
