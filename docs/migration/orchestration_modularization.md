# Vereinheitlichung der Orchestrierungslogik

Dieses Dokument beschreibt einen kleinen Architektur-Schritt in `simulation.py`.
Wiederkehrende technische Lade-, Scheduler- und Dispatch-Schritte wurden in kleine Hilfsfunktionen gebündelt.

## Was vereinheitlicht wurde

- Laden und optionale RNG-Initialisierung eines Szenarios
- Planen und Dispatchen geplanter Events in Scheduler-Reihenfolge
- technischer Aufbau der Ergebnisobjekte für kleine Sequenzen und kontrollierte Loops

## Was bewusst unverändert blieb

- öffentliche Dataclasses und öffentliche Funktionssignaturen
- Event-Arten, Reihenfolge und Payloads
- bestehendes Fehlerverhalten
- beobachtbares Limit- und Dispatch-Verhalten der bisherigen Loops

## Warum dies ein sinnvoller Architektur-Schritt ist

Die technische Orchestrierung ist nun weniger dupliziert und zentraler nachvollziehbar.
Das erleichtert spätere kleine Refactorings und Regressionstests, ohne die fachliche Bedeutung zu erweitern.

## Warum dies keine neue fachliche Semantik einführt

Die Hilfsfunktionen bündeln nur vorhandene technische Ablaufmuster.
Sie führen keine neuen Event-Typen, keine neue Fachlogik und keine historische Semantik ein.
