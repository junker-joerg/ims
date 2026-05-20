# Plan: VN-Abrechnungskern

## Ziel

Portiere den deterministischen Abrechnungskern der historischen VN-Regeln als
expliziten Python-Slice. Der Slice verarbeitet vorgegebene Entscheidungen und
Schadenwerte je Sparte, ohne die noch nicht portierte VN-Wahl-, Praeferenz- oder
Zufallslogik vorwegzunehmen.

## Altcode-Bezug

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`

Diese Regeln unterscheiden sich in Wahl- und Zufallslogik, nutzen danach aber
denselben Abrechnungsblock fuer versicherte und eigenversicherte Schaeden.

## Umsetzung

1. Neuen `vn_rules.py`-Kern mit Dataclasses fuer Sektorentscheidung,
   Settlement-Snapshot und Anwendung anlegen.
2. Versicherer- und VN-Snapshots deterministisch aktualisieren:
   Reserven, Schadenanzahl, Schadensumme, Versichertenzahl, Praemie,
   Eigen-/Fremdschaden und Vermoegen.
3. Optionales Szenariofeld fuer explizite VN-Settlement-Snapshots laden.
4. Tests fuer Fremdversicherung, Eigenversicherung, Vermoegensfortschreibung,
   Loader und Validierungsfehler ergaenzen.

## Bewusst nicht enthalten

- keine Portierung der VN-Zufalls- oder Praeferenzwahl
- keine automatische historische Regelauswahl
- keine Scheduler-Kopplung
- keine Vollsimulation
- keine Behauptung historischer Vollgleichheit
