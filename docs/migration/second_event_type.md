# Zweiter technischer Event-Typ

Dieses Dokument beschreibt einen kleinen zweiten technischen Event-Typ im Dispatcher.
Neben dem schreibenden `bav_update` gibt es nun den lesenden Schritt `bav_snapshot`.

## Was der zweite Event-Typ leistet

- erweitert den kleinen Dispatcher um genau einen zweiten unterstützten Event-Typ
- trennt einen mutierenden technischen Schritt (`bav_update`) von einem lesenden Schritt (`bav_snapshot`)
- erlaubt kleine gemischte Sequenzen aus Update und Snapshot im selben Scheduler

## Warum `bav_snapshot` bewusst lesend ist

`bav_snapshot` führt kein `update_bav_central_state(...)` aus.
Der Schritt sammelt nur `collect_basic_aggregates(...)` und verändert den `BAV`-Zustand nicht.
Damit bleibt die Trennung zwischen technischem Schreiben und technischem Lesen in diesem Slice explizit.

## Was ausdrücklich noch nicht enthalten ist

- keine historische Vollsimulation
- keine allgemeine Event-Semantik des Altmodells
- keine komplexe Marktlogik oder vollständige Fachregeln
- keine UI
- keine allgemeine Mehrtyp-Orchestrierung über viele Fach-Event-Arten

## Warum dies noch keine historische Mehrtyp-Eventsemantik ist

Die Erweiterung unterstützt nur zwei kleine technische Event-Arten mit festem Verhalten.
Sie bildet noch keine historische Ablaufsteuerung oder offene fachliche Eventlandschaft des Altmodells nach.
