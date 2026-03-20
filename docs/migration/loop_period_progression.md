# Loop mit expliziter Perioden-/Logtime-Fortschreibung

Dieses Dokument beschreibt eine kleine technische Erweiterung des kontrollierten Mehr-Event-Loops.
Sie ergänzt explizite Fortschreibung über Perioden- und Logtime-Grenzen hinweg, bleibt aber bewusst keine historische Vollsimulation.

## Was diese Fortschreibung leistet

- erzeugt mehrere technische `bav_update`-Events ausgehend vom Initialkontext
- verwendet explizite Kontext-Fortschreibung über `advanced(...)`
- setzt bei Erreichen der Logtime-Grenze auf die nächste Periode mit `logtime = 0`
- hält die Abarbeitung weiterhin über `max_events` klein und testbar

## Warum dies ein sinnvoller Schritt nach PR 13 ist

Der vorhandene kontrollierte Mehr-Event-Loop kann damit nicht nur mehrere Events,
sondern auch einen kleinen, expliziten Übergang zwischen Perioden abbilden.
Das macht den technischen Slice etwas näher an späteren Ablaufmustern, ohne bereits allgemeine historische Semantik einzuführen.

## Was ausdrücklich noch nicht enthalten ist

- keine historische Vollsimulation
- keine allgemeine Event-Semantik des Altmodells
- keine komplexe Marktlogik oder vollständige Fachregeln
- keine UI
- keine unbegrenzte Eventverarbeitung

## Warum dies noch keine historische Periodenschleife ist

Die Erweiterung verarbeitet weiterhin nur technische `bav_update`-Events mit festem Schema.
Periodenwechsel entstehen allein aus einer kleinen technischen Fortschreibungsregel und nicht aus portierter historischer Ablaufsteuerung.
