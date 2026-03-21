# Gemischter Loop mit Perioden-/Logtime-Fortschreibung

Dieses Dokument beschreibt eine kleine technische Erweiterung des gemischten kontrollierten Mehr-Event-Loops.
`bav_update` und `bav_snapshot` werden kontrolliert verarbeitet und nun auch über kleine Perioden- und Logtime-Grenzen hinweg fortgeschrieben.

## Was dieser gemischte Fortschreibungs-Loop leistet

- erzeugt kleine gemischte Paare aus `bav_update` und `bav_snapshot`
- nutzt explizite technische Fortschreibung über `period` und `logtime`
- bleibt über `max_events` bewusst begrenzt und testbar
- hält mutierende und lesende technische Schritte weiterhin getrennt

## Warum dies ein sinnvoller Schritt nach PR 16 ist

Der vorhandene gemischte kontrollierte Loop kann damit nicht nur mehrere Event-Typen,
sondern auch kleine Übergänge über Perioden- und Logtime-Grenzen ausdrücken.
So wird der technische Slice etwas vollständiger, ohne bereits historische Vollsemantik zu behaupten.

## Was ausdrücklich noch nicht enthalten ist

- keine historische Vollsimulation
- keine allgemeine Event-Semantik des Altmodells
- keine komplexe Marktlogik oder vollständige Fachregeln
- keine UI
- keine offene historische Mehrtyp-Orchestrierung

## Warum dies noch keine historische Mehrtyp-Periodenschleife ist

Der Loop verarbeitet weiterhin nur zwei kleine technische Event-Typen mit festem Verhalten.
Periodenwechsel folgen nur einer kleinen technischen Fortschreibungsregel und nicht einer portierten historischen Ablaufsteuerung.
