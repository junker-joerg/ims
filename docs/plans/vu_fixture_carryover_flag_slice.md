# Plan: VU-Fixture-Carryover-Flag

## Ziel

Der explizite VU-Mehrperiodenrunner kann Versichererzustand bereits
programmatisch in die Folgeperiode uebertragen. Dieser Slice macht dieselbe
Steuerung in Mehrperioden-Fixtures verfuegbar und validiert das Flag strikt.

## Ursprung im Altmodell

- `IMS.E`, `act Vrvu01` bis `Vrvu10`
- bereits portierter VU-Mehrperiodenrunner fuer explizite Periodenszenarien
- kontrollierter VU-State-Carryover als konservative Zustandsfortschreibung

## Umsetzungsschritte

1. Fixture-Feld `carry_forward_insurer_state` fuer Objekt-Fixtures einfuehren.
2. Das Feld strikt als JSON-Boolean validieren.
3. Die Validierung auch bei extern gesetztem Override ausfuehren.
4. Tests fuer Fixture-Flag, Listen-Fixture, falsche Typen und Override-Fall
   ergaenzen.

## Grenzen

- Keine neue VU-Regel, keine automatische historische Regelauswahl.
- Kein Scheduler-Anschluss und keine Vollsimulation.
- Listen-Fixtures bleiben kompatibel und koennen Carryover weiterhin nur ueber
  den expliziten Funktionsparameter aktivieren.
