# Plan: VN-Mehrperiodenrunner

## Ziel

Fuehre einen kleinen deterministischen Mehrperiodenrunner fuer explizite
VN-Schaden- und VN-Settlement-Szenarien ein. Der Runner soll mehrere bereits
ausformulierte Periodenszenarien geordnet ausfuehren und Diagnosen sammeln,
ohne daraus einen historischen PlanVN-Scheduler oder eine Vollsimulation zu
machen.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`
- historische VN-Periodenaktionen im PlanVN-Umfeld

Die historischen Aktionen laufen periodisch ueber VN-Subjekte. Der Python-Slice
bildet nur den expliziten, bereits portierten Schaden-/Abrechnungspfad ueber
mehrere Perioden ab.

## Umsetzung

1. Geladene Szenarien direkt ueber den VN-Periodenrunner ausfuehren.
2. In-Memory- und Fixture-Einstiege fuer Einzelperioden ergaenzen.
3. Mehrperiodenlauf fuer Listen oder Fixture-Feld `periods` einfuehren.
4. Periodenfolge auf nichtleer, eindeutig und streng steigend validieren.
5. Pro Periode doppelte oder konfligierende VN-Ziele zwischen
   Schaden-Abrechnungs- und direkten Settlement-Snapshots ablehnen.

## Grenzen

- keine automatische Zustandsfortschreibung zwischen Perioden
- keine historische Versichererwahl oder Praeferenzlogik
- keine versteckte RNG-Nutzung
- keine Vollsimulation und keine Gleichheitsbehauptung gegen historische Laeufe
