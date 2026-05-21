# Deterministischer Agrsich-Replay-Runner

## Ziel

Dieser Schritt fuehrt einen kleinen deterministischen Replay-Runner fuer Agrsich-Validierung
ein. Er liest explizite Perioden-Snapshots, laedt daraus echten Python-Domaenenzustand und
fuehrt die vorhandene BAV-/Agrsich-Record-Erzeugung sowie den bestehenden Export-Writer aus.

Der Runner schreibt dadurch ueber mehrere Perioden dieselben Exportdateien fort und kann ein
kleines Fenster gegen vorhandene echte Legacy-Versichererdateien vergleichen.
Neben dem aelteren Einzelziel `legacy_window` kann der Runner auch mehrere
`legacy_targets` fuer Versicherer- oder VN-Exporttabellen vergleichen und bei
gesetztem `legacy_report_name` denselben JSON-/CSV-Reportpfad wie die neueren
VN- und expliziten VU/VN-Laeufe schreiben.

Vor der Exportbildung fuehrt der Runner je Snapshot den bereits portierten
VU-Periodenschritt aus. Dadurch werden explizite VU-Regel-Snapshots aus dem
Fixture in den Agrsich-Exportzustand uebernommen, ohne eine automatische
historische Regelauswahl zu behaupten. Optional kann
`carry_forward_insurer_state=True` gesetzt werden; alternativ akzeptiert das
Fixture das streng als JSON-Boolean validierte Feld
`carry_forward_insurer_state`. Bei aktivem Carryover muessen die Replay-
Perioden strikt steigen; doppelte oder rueckwaerts angeordnete Perioden werden
vor dem ersten VU-Schritt und vor jeder Dateiausgabe abgelehnt.
Der Runner berichtet die lokale und globale Periodenfolge getrennt:
`processed_local_periods` enthaelt die lokalen `context.period`-Werte,
`processed_global_periods` die Export- und Validierungsachse.

## Anschluss an die bestehende Legacy-Validierung

Die bisherigen Legacy-Vergleiche pruefen einzelne echte Referenzzeilen und kleine tabellenweite
Vergleiche. Der Replay-Runner verbindet diesen Referenzpfad nun mit einem reproduzierbaren
End-to-End-Pfad aus geladenem Domaenenzustand:

- Snapshot laden
- expliziten VU-Periodenschritt anwenden
- Agrsich-Records mit vorhandener Modelllogik erzeugen
- Exporttabellen mit vorhandenem Exportpfad schreiben
- geschriebenes Fenster gegen Legacy-Dateien vergleichen
- optional mehrere geschriebene Exporttabellen gegen Legacy-Ziele vergleichen
- lokale und globale Periodendiagnosen fuer mehrlaeufige Replay-Fixtures
  bereitstellen

Die neuen Fixtures `replay_vu14_window.json` und `replay_vusk1_window.json` sind bewusst
explizite Validierungszustande. Sie reproduzieren kleine zusammenhaengende Fenster aus
`VU14L1.DAT` und `VUSK1L4.DAT`.

## Grenzen

Dies ist noch kein vollstaendiger historischer Simulationslauf. Die Periodenzustande werden
nicht aus Verhalten, Scheduling oder wirtschaftlicher Dynamik hergeleitet, sondern als
explizite Snapshots vorgegeben. Der Runner behauptet daher keine historische Vollgleichheit
des Modells.

Bewusst nicht enthalten sind:

- automatische Herleitung der Periodenzustande aus echter Regellogik
- automatische historische Auswahl von VU-Regeln
- lange historische Vollsimulationen
- neue fachliche Agrsich-Semantik
- UI oder ein konkurrierender Exportpfad

## Naechster sinnvoller Schritt

Ein Folge-PR sollte eine kleine, reproduzierbare Erzeugung solcher Periodenzustande aus
portierter Regel- und Scheduling-Logik anschliessen. Erst danach ist eine breitere Pipeline
aus Altinitialdaten ueber laengere historische Fenster sinnvoll belastbar.
