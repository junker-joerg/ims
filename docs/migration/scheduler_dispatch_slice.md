# Scheduler-Dispatcher-Slice: erste technische Kopplung

## Ziel dieses Dokuments

Dieses Dokument beschreibt die erste vorsichtige Kopplung zwischen
geplantem Event, kleinem Dispatcher und technischem BAV-Update-Schritt.

## Was in diesem PR eingeführt wird

In diesem PR werden drei Dinge verbunden:

1. ein einzelnes geplantes Event im bestehenden Scheduler
2. ein kleiner Dispatcher für genau eine unterstützte Event-Art
3. die Ausführung eines technischen BAV-Update-Schritts

## Unterstützte Event-Art

In diesem PR wird bewusst nur genau eine Event-Art unterstützt:

- `action == "bav_update"`

Andere Event-Arten werden nicht stillschweigend ignoriert, sondern mit
einem klaren Fehler abgelehnt.

## Was diese Kopplung leistet

Der neue Ablauf ist bewusst klein:

1. Szenario laden
2. Kontext optional mit RNG initialisieren
3. genau ein `bav_update`-Event erzeugen
4. Event in den Scheduler einplanen
5. Event wieder entnehmen
6. Event per Dispatcher ausführen
7. Ergebnisobjekt zurückgeben

## Warum dieser Schritt sinnvoll ist

Damit entsteht erstmals eine explizite Brücke zwischen:
- technischer Planung,
- technischer Entnahme aus dem Scheduler,
- kleiner fachnaher Ausführung.

Der Schritt bleibt dennoch klein genug, um klar testbar zu sein.

## Was ausdrücklich noch nicht enthalten ist

- kein allgemeiner Event-Loop
- keine Mehr-Event-Verarbeitung
- keine historischen Aktionspläne
- keine vollständige Scheduler-Semantik des Altmodells
- keine Portierung komplexer fachlicher Event-Arten

## Warum dies noch keine historische Event-Semantik ist

Der Dispatcher unterstützt derzeit genau eine Event-Art und führt nur eine
bereits vorbereitete technische Aktualisierung aus. Dies ist eine kleine
technische Kopplung und kein Nachbau des historischen ESS/IMS-Ablaufs.

## Nächste sinnvolle Schritte

1. zweiten kleinen Event-Typ nur mit klarer Altcode-Basis ergänzen
2. Mehr-Event-Ablauf vorsichtig strukturieren
3. Scheduler-Reihenfolge mit Dispatcher-Ausführung kombinieren
4. fachliche Semantik nur schrittweise und testbasiert vertiefen
