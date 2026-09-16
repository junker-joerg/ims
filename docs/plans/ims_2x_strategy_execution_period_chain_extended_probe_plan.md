# PR148: Kontrollierte Wirkungsprobe fuer 10, 25 und 50 Perioden

Stand: 2026-09-16

## Ziel und Schnitt

Ein ausdruecklich freigegebener, fluechtiger Pfad fuehrt genau 10, 25 oder
50 Perioden in einem isolierten, hart abbrechbaren Prozess aus. Die gesamte
Kette, alle Kandidaten und ein gespeicherter erfolgreicher Fuenf-Perioden-
Nachweis werden vor dem ersten Runner geprueft. Vor Periode 6 wird dessen
fachlicher Prefix 1-5 semantisch und als kanonisches JSON exakt verglichen.

## Grenzen und Abnahme

- Der PR147-Vertrag bleibt massgeblich: Zeit, Peak-RSS, Ketten- und
  Ergebnispayload sowie freier Plattenplatz sind gemessene harte Grenzen.
- Ein erster Fehler, Timeout, fehlende Messung oder Abbruch liefert kein
  Teilergebnis. Der Worker darf keinen Zustand im Serverprozess halten.
- Pro Horizont: echter deterministischer Lauf, unveraenderter Prefix,
  gepruefte Carryover-Zaehler und atomare Negativpfade. Reale Lastmesswerte
  und Testumgebung werden in der Migrationsnotiz festgehalten.
- Kein UI-Start, keine Speicherung oder Wiederaufnahme, keine Aenderung von
  VU-/VN-Regeln. PR149 prueft und oeffnet 100 gesondert.

## Herkunft und Unsicherheit

`ESS.C:71-75` gibt die aufsteigende lokale Periodenfolge vor;
`IMSDATA.C:14` begrenzt den historischen Einzellauf auf 100. Laufzeit-
und Speicherlimits sind neue technische Sicherheitsentscheidungen, keine
historische Fachlogik. Gleiche alte Zufallsfolgen werden nicht behauptet.
