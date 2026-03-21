# Modularisierung der Event-Builder

Dieses Dokument beschreibt einen kleinen Architektur-Schritt: reine technische Event-Erzeugung wurde aus `simulation.py` in ein eigenes Modul verschoben.
Die bestehenden Loops und ihre beobachtbare technische Semantik bleiben dabei bewusst unverändert.

## Was modularisiert wurde

- reine Builder-Funktionen für technische BAV-Eventfolgen
- sequenzielle Update-Events
- fortgeschriebene Update-Events
- gemischte Update-/Snapshot-Sequenzen und deren Fortschreibungsvariante

## Was bewusst unverändert blieb

- gleiche Event-Arten
- gleiche Reihenfolge der erzeugten Events
- gleiche Payload-Struktur
- gleiche technische Fortschreibungslogik
- keine Änderungen an Dispatcher- oder Ausführungslogik

## Warum das ein sinnvoller Architektur-Schritt ist

Die Event-Erzeugung ist nun an einer Stelle gebündelt und separat testbar.
Das reduziert Duplikate in `simulation.py`, ohne neue fachliche Semantik einzuführen.

## Warum dies keine neue fachliche Semantik einführt

Die Builder erzeugen weiterhin dieselben kleinen technischen Events wie zuvor.
Dies ist nur ein Modularisierungsschritt und keine Erweiterung des fachlichen oder historischen Verhaltens.
