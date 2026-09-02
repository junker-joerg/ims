# IMS 2.x: Snapshot-Bauplaene in der Workbench

Stand: PR111, 2026-09-02

## Ziel

PR111 macht die PR110-Uebersetzung als fuenften Tab `Bauplaene` im
Strategiearbeitsbereich sichtbar. Die Ansicht beantwortet fuer einen lokal
erfassten Strategieentwurf drei Fragen:

1. Welcher vorhandene VU- oder VN-Regel-Snapshottyp ist das Ziel?
2. Welche Felder stammen bereits eindeutig aus dem Entwurf?
3. Welche Laufzeitwerte fehlen vor einer spaeteren Materialisierung?

Die Anzeige ist eine zustandslose Vorschau. Sie erzeugt keine Snapshotobjekte
und startet weder Regelkern noch Simulation.

## Historische und technische Bindung

| Grundlage | Workbench-Anzeige | Grenze |
| --- | --- | --- |
| `IMSDATA.C`, `ACTION.st` | VU-/VN-Ziel und Zeitbindung | keine neue Wechselplanung |
| `IMS.E`, `Vrvu01`-`Vrvu10` | vorhandener VU-Snapshottyp | keine neuen VU-Regeln |
| `IMS.E`, `Vrvn01`-`Vrvn06` | `VNInsuranceRuleSnapshot` und Regelvariante | keine neuen VN-Regeln |
| PR108/109-Entwurf | Ziel, Strategie und Parameter | nur lokaler Browserzustand |
| PR110-Uebersetzung | vorbereitete und offene Snapshotfelder | keine Materialisierung |

## Bedienung

Der Anwender erfasst im Tab `Entwurf` weiterhin einzelne Zuordnungen und
prueft den gesamten Entwurf serverseitig. Erst ein erfolgreicher, seitdem
unveraenderter Pruefbericht schaltet im Tab `Bauplaene` die Aktion
`Bauplaene anzeigen` frei.

Die Workbench sendet denselben Entwurf an
`POST /api/strategies/assignment-snapshot-translation`. Der Bericht wird nur
im React-Zustand gehalten. Aendert der Anwender Entwurfs-ID, Bezeichnung oder
eine uebernommene Zuordnung, verwirft die Workbench sowohl den Pruefbericht als
auch eine vorhandene Bauplanvorschau.

## Darstellung

Die Kopfzeile zeigt Vertragsversion, Zahl der 16 Regel-Mappings, Zahl der
erzeugten Bauplaene und die Summe der offenen Felder. Jeder Bauplan zeigt:

- VU/VN und Strategie;
- vorhandenen Snapshottyp und Zielcontainer;
- Aktivierungsperiode, Laufgrenze und logische Zeit;
- aus dem Entwurf vorbereitete Felder;
- vor Materialisierung noch erforderliche Felder.

Die offenen technischen Feldnamen werden fuer Anwender ergaenzt, etwa als
Zufallsziehungen, Zinssatz der Periode, Schockstatus, Reserveschwellen, aktive
Versicherer, Schadenwahrscheinlichkeiten oder VU-Marktwerte. Der originale
Feldname bleibt klein sichtbar, damit Bericht und Python-Vertrag eindeutig
aufeinander bezogen werden koennen.

## Grenzen

- keine Datei-, `localStorage`- oder Datenbankspeicherung;
- keine Anwendung technischer Loader-Defaults;
- keine Snapshot-Materialisierung;
- keine Uebergabe an Run-Control oder Runner;
- keine Simulation;
- keine historische Vollgleichheitsbehauptung.

Die sichtbaren Abschlusswerte bleiben deshalb `Defaults: nein`, `Snapshots:
nein`, `Ausfuehrung: nein` und `Simulation: nein`.

## Naechster Schritt

PR112 soll einen versionierten, weiterhin rein validierenden Kontextvertrag
fuer Periode, Ziehungen, Zinssatz, Schockstatus, Markt- und Vorperiodenwerte
definieren. Erst danach kann ein eigener PR die vollstaendigen Bauplaene in
vorhandene Snapshot-Dataclasses materialisieren. Eine Runner-Kopplung bleibt
eine weitere, separate Freigabe.
