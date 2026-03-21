# Gemischter kontrollierter Mehr-Event-Loop

Dieses Dokument beschreibt einen kleinen technischen Mehr-Event-Loop mit `bav_update` und `bav_snapshot`.
Der Loop bleibt bewusst kontrolliert, hat eine feste Obergrenze und ist keine historische Vollsimulation.

## Was dieser gemischte Loop leistet

- erzeugt kleine gemischte Sequenzen aus `bav_update` und `bav_snapshot`
- plant alle Events in denselben Scheduler ein
- verarbeitet die Sequenz kontrolliert bis zur festen Obergrenze `max_events`
- hält mutierende und lesende technische Schritte explizit unterscheidbar

## Warum die Trennung von mutierendem und lesendem Schritt wichtig ist

`bav_update` bleibt der schreibende technische Schritt.
`bav_snapshot` bleibt lesend und sammelt nur Aggregationen.
Damit lässt sich die Dispatcher-Erweiterung testen, ohne bereits fachlich reichere Mehrtyp-Semantik einzuführen.

## Was ausdrücklich noch nicht enthalten ist

- keine historische Vollsimulation
- keine allgemeine Event-Semantik des Altmodells
- keine komplexe Marktlogik oder vollständige Fachregeln
- keine UI
- keine offene Mehrtyp-Orchestrierung über viele fachliche Event-Arten

## Warum dies noch keine historische Mehrtyp-Eventschleife ist

Der Loop verarbeitet nur zwei kleine technische Event-Typen mit festem Verhalten und fester Obergrenze.
Historische Ablaufsteuerung und breitere fachliche Eventlandschaften bleiben weiterhin außerhalb dieses Slices.
