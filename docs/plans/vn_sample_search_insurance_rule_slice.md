# Slice-Plan: VN-Stichprobensuche

## Ziel

Portierung des Vrvn05-Versicherungsentscheidungskerns als isolierter
Python-Baustein. Der Slice soll aus einem Marktschadenindikator, aktiven
aktuellen VU-Praemien, Stichprobengroessen und expliziten Draws
`VNInsuranceDecision`-Objekte erzeugen.

## Nicht-Ziele

- keine automatische Regelwahl ueber historische Menues oder Scheduler
- keine Vollsimulation
- keine Behauptung historischer Modulo-RNG-Gleichheit
- keine Aenderung am bestehenden Schaden- oder Abrechnungskern

## Umsetzung

- neue Dataclasses fuer Parameter, Draws, aktive Praemieneingaben und Ergebnis
- Loader fuer Parameter, Draws und aktive VU-Praemien mit kontrollierten
  `ValueError`s
- Vrvn05-Stichprobenlogik:
  - Periode 1 uebernimmt explizite Startentscheidungen
  - Perioden danach verwenden `Dg[0] <= threshold`
  - je Sparte wird eine Draw-gesteuerte Stichprobe aktiver VU gezogen
  - gewaehlt wird die niedrigste beobachtete aktuelle Praemie
  - Informationskosten werden diagnostisch ausgewiesen

## Validierung

- fokussierte Unit-Tests fuer Vrvn05
- Loader- und Fehlerfalltests
- Kopplungstest in den bestehenden VN-Schaden-/Abrechnungspfad
- voller Pytest-Lauf vor PR und nach Merge
