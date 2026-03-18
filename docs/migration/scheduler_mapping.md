# Scheduler-Mapping

Dieses Dokument beschreibt, welche Altlogik durch das neue technische Scheduler-Grundgerüst vorbereitet wird.
Es dokumentiert ausdrücklich nur die generische Simulationsmechanik und noch keine IMS-Fachregeln.

## Altcode → neue Dateien

- Vermutete Alt-Scheduler- und Ablaufsteuerung (`inventory_scheduler.c`) → `python_port/ims/engine/scheduler.py`
- Vermutete Initialisierungs- und Laufzeitkontextlogik (`inventory_context.c`) → `python_port/ims/engine/context.py`

## Fachlich vorbereitet

- periodische und logische Zeitsteuerung über `period` und `logtime`
- deterministische Abarbeitungsreihenfolge über eine Priority Queue
- generischer Laufzeitkontext mit Platz für RNG-Seed, Registries und Stores

## Noch NICHT portiert

- IMS-spezifische Fachobjekte oder Regeln
- konkrete Altcode-Events, fachliche Eventtypen oder Business-Entscheidungen
- echte RNG-Strategie außer einem minimalen Seed-Feld im Kontext
- Initialisierung von Domänenregistern, Persistenz oder I/O

## Bekannte Unterschiede zum Altcode

- Die Altdateien sind aktuell nicht im Repository vorhanden; das Mapping bleibt daher vorläufig.
- Der neue Scheduler ist bewusst generisch und koppelt nicht an VU, VN, BAV oder andere IMS-Fachobjekte.
- Die aktuelle Reihenfolge basiert rein technisch auf `period`, `logtime`, `priority` und stabiler Einfüge-Reihenfolge.
