# Zwei-Event-Sequenz

Dieses Dokument beschreibt eine kleine technische Eventsequenz mit genau zwei geplanten `bav_update`-Events.
Die Sequenz bleibt bewusst minimal und ist noch keine historische Eventkette des IMS/ESS-Modells.

## Was diese kleine Eventsequenz leistet

- plant genau zwei technische `bav_update`-Events
- prüft ihre relevante Reihenfolge über den Scheduler
- dispatcht beide Events nacheinander
- gibt die beiden Dispatch-Ergebnisse strukturiert zurück

## Warum dies ein Fortschritt gegenüber dem Einzel-Event-Slice ist

Die Sequenz verbindet erstmals explizite Scheduler-Reihenfolgeprüfung mit sequentieller Dispatcher-Ausführung über mehr als ein Event.
Trotzdem bleibt der Ablauf klein genug, um klar testbar und technisch nachvollziehbar zu sein.

## Was ausdrücklich noch nicht enthalten ist

- keine historische Eventkette
- keine allgemeine Event-Semantik des Altmodells
- keine Mehr-Event-Logik über zwei Schritte hinaus
- keine UI
- keine komplexe Marktlogik oder vollständige Fachregeln

## Warum dies noch keine historische Eventkette ist

Es werden genau zwei technische `bav_update`-Events mit festem Schema erzeugt und ausgeführt.
Historische Aktionspläne, fachliche Event-Typen und komplexe Ablaufsteuerung müssen später separat validiert und portiert werden.
