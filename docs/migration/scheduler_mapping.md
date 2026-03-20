# Scheduler-Mapping

Dieses Dokument beschreibt das minimale technische Grundgerüst für periodische und logische Ereignissteuerung im Python-Port.
Es dokumentiert bewusst nur eine generische technische Basis und behauptet keine Gleichwertigkeit zum historischen IMS/ESS-Code.

## Dieses Grundgerüst bereitet vor

- einen kleinen `SimulationContext` mit Basislaufparametern
- generische `Event`-Objekte ohne harte Kopplung an IMS-Domänenklassen
- einen `Scheduler` mit expliziter Ordnung nach `period`, `logtime`, `priority` und stabiler Einfügereihenfolge
- erste Referenztests für Reihenfolge, Stabilität und leeren Zustand

## Noch nicht enthalten

- IMS-Fachlogik, VU/VN/BAV-Regeln oder Marktverhalten
- fachliche Registries oder komplexe Zustandscontainer
- RNG-Integration, Simulationsteuerung oder Ergebnisverarbeitung
- Ableitungen aus konkreten historischen Funktionen oder Datenstrukturen
