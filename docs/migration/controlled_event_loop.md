# Kontrollierter Mehr-Event-Loop

Dieses Dokument beschreibt einen kleinen technischen Mehr-Event-Loop mit fester Obergrenze.
Der Loop bleibt bewusst minimal und ist noch keine historische Eventschleife des IMS/ESS-Modells.

## Was dieser kleine Loop leistet

- erzeugt mehrere technische `bav_update`-Events
- plant sie in denselben Scheduler ein
- dispatcht sie sequentiell in Scheduler-Reihenfolge
- begrenzt die Abarbeitung explizit über `max_events`
- gibt geplante Events, ausgeführte Ergebnisse und den Restzustand strukturiert zurück

## Warum die feste Obergrenze wichtig ist

Die feste Obergrenze hält den Ablauf klein, vorhersagbar und testbar.
Sie verhindert, dass aus diesem technischen Slice bereits stillschweigend ein offener Mehr-Event-Loop wird.

## Was ausdrücklich noch nicht enthalten ist

- keine historische Vollsimulation
- keine allgemeine Event-Semantik des Altmodells
- keine komplexe Marktlogik oder vollständige Fachregeln
- keine UI
- keine unbegrenzte Eventverarbeitung

## Warum dies noch keine historische Eventschleife ist

Der Loop verarbeitet nur technische `bav_update`-Events mit festem Schema und fester Obergrenze.
Historische Aktionspläne, fachliche Eventtypen und offene Ablaufsteuerung müssen später separat validiert und portiert werden.
