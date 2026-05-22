# Slice-Plan: VN-Beste-Information

## Ziel

Portierung des Vrvn06-Versicherungsentscheidungskerns als isolierter
Python-Baustein. Der Slice soll aus einem Marktschadenindikator und aktiven
aktuellen VU-Praemien `VNInsuranceDecision`-Objekte erzeugen.

## Nicht-Ziele

- keine automatische Regelwahl ueber historische Menues oder Scheduler
- keine Vollsimulation
- keine Behauptung historischer Modulo-RNG-Gleichheit
- keine Aenderung am bestehenden Schaden- oder Abrechnungskern

## Umsetzung

- neue Dataclasses fuer Parameter und Ergebnis
- Loader fuer Parameter mit kontrollierten `ValueError`s
- Vrvn06-Vollinformationslogik:
  - Periode 1 uebernimmt explizite Startentscheidungen
  - Perioden danach verwenden `Dg[0] <= threshold`
  - je Sparte werden alle aktiven VU-Praemien betrachtet
  - gewaehlt wird die niedrigste aktuelle aktive Praemie
  - Informationskosten werden diagnostisch ausgewiesen
- Begleitfix fuer Vrvn05: Minimumsuche nutzt `float("inf")` statt `1000.0`

## Validierung

- fokussierte Unit-Tests fuer Vrvn06
- Regressionstest fuer hohe Vrvn05-Praemienskalen
- Loader- und Fehlerfalltests
- Kopplungstest in den bestehenden VN-Schaden-/Abrechnungspfad
- voller Pytest-Lauf vor PR und nach Merge
