# Periodenfortschreibung

Dieses Dokument beschreibt die kleine explizite Fortschreibung von `period` und `logtime` sowie eine technische Zwei-Schritt-Orchestrierung.
Beides ist bewusst minimal und noch keine historische IMS/ESS-Periodensimulation.

## Was die explizite Fortschreibung leistet

- erzeugt aus einem bestehenden `SimulationContext` einen neuen Kontext
- schreibt `period` und `logtime` explizit fort
- erlaubt optional einen Reset von `logtime` für den Start eines neuen Periodenblocks

## Wie die Zwei-Schritt-Orchestrierung arbeitet

- lädt ein Szenario genau einmal
- initialisiert optional das RNG im Kontext
- führt einen ersten BAV-Update-Schritt aus
- erzeugt danach explizit einen zweiten Kontext
- führt genau einen zweiten BAV-Update-Schritt mit denselben geladenen Entitäten aus

## Was ausdrücklich noch nicht enthalten ist

- keine historische Vollsimulation
- keine Scheduler-gesteuerte Ablaufsteuerung
- keine UI
- keine komplexe Marktlogik oder vollständige Fachregeln
- keine Behauptung fachlicher Gleichwertigkeit

## Warum dies noch keine historische Periodensimulation ist

Die Fortschreibung bleibt auf zwei technische Schritte begrenzt und modelliert keine historischen Reihenfolgen oder Mehrperiodenlogik.
Weitergehende Simulationsabläufe müssen später separat validiert und portiert werden.
