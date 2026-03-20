# Prioritäts-Slice: Zwei Events mit gleichem Zeitpunkt

## Ziel dieses Dokuments

Dieses Dokument beschreibt einen kleinen technischen Slice, in dem zwei
`bav_update`-Events mit gleichem `period` und `logtime`, aber
unterschiedlicher `priority` geplant, entnommen und dispatcht werden.

## Was dieser Slice leistet

Der Slice zeigt explizit:

- zwei technisch gleichartige Events
- gleicher Ereigniszeitpunkt
- Unterschied nur über `priority`
- Scheduler-Entnahme in Prioritätsreihenfolge
- anschließende Dispatcher-Ausführung in genau dieser Reihenfolge

Zusätzlich wird testbar gemacht, dass die Planungsreihenfolge nicht
zwingend der Ausführungsreihenfolge entsprechen muss.

## Warum dies ein sinnvoller Schritt nach PR 11 ist

PR 11 zeigte bereits eine kleine Zwei-Event-Sequenz mit unterschiedlichem
Zeitpunkt. Der jetzige Slice isoliert zusätzlich den Fall, dass der
Zeitpunkt identisch ist und die Reihenfolge daher explizit durch
`priority` bestimmt werden muss.

Damit wird ein weiterer technischer Ordnungsaspekt des Schedulers
sichtbar, ohne schon historische Eventsemantik nachzubilden.

## Was ausdrücklich noch nicht enthalten ist

- keine historische Prioritätssemantik des Altmodells
- keine unterschiedlichen Fach-Eventtypen
- keine komplexen Dispatcher-Regeln
- keine allgemeine Mehr-Event-Simulation
- keine vollständige ESS/IMS-Aktionsplanung

## Warum dies noch keine historische Prioritätssemantik ist

In diesem Slice wird nur gezeigt, dass der technische Scheduler zwei
Events mit gleichem Zeitpunkt anhand ihrer numerischen `priority`
ordnet. Welche fachliche Bedeutung Prioritäten im historischen Modell
später haben, wird hier noch nicht behauptet.

## Nächste sinnvolle Schritte

1. kleinen Mehr-Event-Loop kontrolliert erweitern
2. Priorität und Zeitpunkt gemeinsam in etwas reicheren Sequenzen testen
3. zweite Event-Art nur mit klarer Altcode-Basis ergänzen
4. fachliche Semantik weiterhin testbasiert und schrittweise vertiefen
