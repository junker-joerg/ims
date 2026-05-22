# Slice-Plan: VN-Suchversicherungsregel

## Ziel

Portierung des Vrvn04-Versicherungsentscheidungskerns als isolierter
Python-Baustein. Der Slice soll aus subjektiven Schadenwahrscheinlichkeiten,
historischen VN-Versicherungsstaenden und optionalen Fallback-Draws
`VNInsuranceDecision`-Objekte erzeugen.

## Nicht-Ziele

- keine automatische Regelwahl ueber historische Menues oder Scheduler
- keine Vollsimulation
- keine Behauptung historischer Modulo-RNG-Gleichheit
- keine Aenderung am bestehenden Schaden- oder Abrechnungskern

## Umsetzung

- neue Dataclasses fuer Parameter, Draws, Historieneintraege und Ergebnis
- Loader fuer Parameter, Draws und Historie mit kontrollierten `ValueError`s
- Vrvn04-Suchlogik:
  - Periode 1 uebernimmt explizite Startentscheidungen
  - Perioden danach verwenden `sw > threshold`
  - VU-Auswahl sucht die niedrigste fruehere versicherte Praemie je Sparte
  - Fallback nutzt aktive VU und explizite Draws
- Haertung des typisierten Vrvn03-VU-Eingabepfads

## Validierung

- fokussierte Unit-Tests fuer Vrvn04
- Regressionstest fuer typisierte Vrvn03-Inputs
- Kopplungstest in den bestehenden VN-Schaden-/Abrechnungspfad
- voller Pytest-Lauf vor PR und nach Merge
