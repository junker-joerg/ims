# Abschlussstand Fachlogik-Migration im engeren Sinn

Diese Notiz fasst den kontrollierten Stand der Python-Migration im
Simulationskern zusammen. Sie markiert keinen historischen Vollsimulationslauf
und keine Behauptung historischer Vollgleichheit. Gemeint ist: Die bisher
priorisierten fachlichen Kernbausteine fuer BAV, VU und VN sind als explizit
steuerbare Python-Pfade vorhanden, validiert und im Scheduler ansprechbar.

## Enthaltene Fachlogik

- BAV-/Aggregatbasis mit sparten- und risikogetrennten Fremdinformationswerten
- VU-Regelkerne fuer Zufallspreise, Fremdinformation, Reserveaufschlag,
  Nettowechsler, erwartete Schaeden, Marktanteilsbasis und freie lineare
  Fortschreibung
- VN-Schadenerzeugung, VN-Abrechnung und die Kopplung von Schaden und
  Abrechnung
- VN-Versicherungsregeln fuer Pflichtversicherung, Zufallsentscheidung,
  Praeferenzwahl, Suchwahl, Stichprobensuche und beste Information
- expliziter VN-Regeldispatch fuer periodische Schaden-/Abrechnungspfade
- mehrperiodige VU-, VN- und kombinierte VU/VN-Runner mit kontrolliertem
  Carryover, globaler Periodenordnung und Periodendiagnosen
- deterministische Periodenplaene fuer VU/VN-Laeufe mit Kontext-Overrides,
  Entity-Updates und optionalen Legacy-Zielen
- Agrsich-Export, Replay-Pfade und Legacy-Fenstervergleiche fuer kontrollierte
  Validierungslaeufe
- Scheduler-Dispatch fuer explizite VU/VN-Periodenereignisse

## Validierungsstand

Der Abschlussstand stuetzt sich auf Unit- und Regressionstests fuer die
portierten Regelkerne, Loader-Validierung, Carryover-Verhalten,
Periodenreihenfolgen, Replay-Pfade, Legacy-Zielvergleiche und Scheduler-
Dispatch. Beim Abschluss dieses Statusdokuments lief die vollstaendige lokale
Testsuite mit 540 erfolgreichen Tests.

Die Tests pruefen kontrollierte Szenarien und kleine Referenzfenster. Sie
ersetzen keine vollstaendige historische IMS/ESS-Simulation und keine
umfassende Gleichheitsvalidierung ueber alle historischen Laufvarianten.

## Bewusste Grenzen

- keine Portierung der historischen Terminal-UI
- keine Backend- oder Frontend-Modernisierung in dieser Migrationsphase
- keine automatische Rekonstruktion aller historischen PlanVU-/PlanVN-
  Schedulerpfade
- keine spekulative Fachlogik ausserhalb der dokumentierten portierten
  Bausteine
- keine Aussage historischer Vollgleichheit ausserhalb konkret getesteter
  Referenzfenster

## Naechste Arbeitsbloecke

Die Fachlogik-Migration im engeren Sinn ist damit als abgeschlossen
dokumentiert. Anschliessende Arbeiten sollten getrennt priorisiert werden:

1. staerkere historische Validierung ueber zusaetzliche Referenzfenster und
   Laufpfade
2. Modernisierung von Backend/API und danach Frontend/UI auf Basis der nun
   abgegrenzten Python-Fachlogik

Beide Folgephasen sollten eigene PR-Serien bleiben, damit fachliche
Validierung, technische Architektur und UI-Entscheidungen nachvollziehbar
getrennt bleiben.
