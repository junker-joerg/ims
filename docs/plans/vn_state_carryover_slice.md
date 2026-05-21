# Plan: VN-State-Carryover

## Ziel

Ergaenze den expliziten VN-Mehrperiodenrunner um einen optionalen,
kontrollierten Zustandstransfer zwischen aufeinanderfolgenden Periodenszenarien.
Damit koennen bereits portierte VN-Schaden-/Abrechnungsschritte mehrere Perioden
lang auf mutierten VU- und VN-Zustaenden aufbauen, ohne einen historischen
PlanVN-Scheduler oder eine Vollsimulation zu behaupten.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`
- periodische VN-Aktionen im historischen PlanVN-Umfeld

Die historischen VN-Aktionen schreiben pro Periode aktuelle VN- und VU-Werte
fort. Der Python-Slice nutzt weiterhin nur explizite Periodenszenarien und
uebertraegt optional die bereits berechneten aktuellen Werte in die naechste
geladene Periode.

## Umsetzung

1. Neues Diagnoseobjekt fuer VN-State-Carryover.
2. Periodenergebnis haelt die mutierten VU-/VN-Listen als Rueckgabekontext.
3. Mehrperiodenrunner erhaelt `carry_forward_vn_state=False` als opt-in.
4. Fixture-Runner kann denselben Schalter explizit aus dem Fixture lesen.
5. Tests pruefen Carryover, Nicht-Carryover und fehlende Folgeentitaeten.

## Grenzen

- Keine neue VN-Wahl-, Praeferenz- oder RNG-Logik.
- Keine automatische Erzeugung fehlender Folgeentitaeten.
- Keine Aussage historischer Vollgleichheit.
