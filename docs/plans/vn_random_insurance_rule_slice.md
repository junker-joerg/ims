# VN-Zufallsversicherungsregel

## Ziel

Dieser Slice portiert den Vrvn02-Baustein, der je Sparte den
Versicherungsstatus zufaellig bestimmt und bei Versicherungsschutz einen
aktiven Versicherer auswaehlt.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn02`

Historisch gilt fuer Perioden nach der Startperiode:

- `vr1 = (e <= myrndf())`
- `vr2 = (f <= myrndf())`
- fuer jede Sparte wird ein aktiver VU zufaellig ausgewaehlt

## Umsetzung

- neuer reiner Regelkern `python_port/ims/model/vn_insurance_rules.py`
- Parameter fuer Normal- und Schockschwellen
- explizite Gleichverteilungsziehungen fuer Status und VU-Auswahl
- Ergebnis als vorhandene `VNInsuranceDecision`-Liste fuer den bestehenden
  VN-Schaden-/Abrechnungspfad

## Annahmen und Grenzen

- Die VU-Auswahl nutzt die sortierte aktive VU-Menge und reproduzierbare
  Python-Draws; das behauptet keine identische historische Modulo-RNG-Folge.
- Startperiodenlogik, Scheduler-Regelwahl, Praeferenzlogik und
  Pflichtversicherung bleiben ausserhalb dieses Slices.
