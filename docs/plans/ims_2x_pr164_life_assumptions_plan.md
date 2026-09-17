# PR164: Deterministische Lebens-Annahmequellen

Stand: 2026-09-17
Status: umgesetzt als separater, zustandsloser Resolver

## Ziel und Grenze

Ein kleiner vollstaendig enumerierter Lebensfall kann je VU und
Modellperiode Anlageergebnis und Todesfallauswahl aus expliziten
Quellen oder aus festgelegten Kurven ableiten. Der Resolver nimmt den
geprueften Anfangsbestand einer Periode entgegen und liefert nur
Quellwerte. Er fuehrt keine Lebensbilanz, Periodenkette, Speicherung,
API oder Workbench aus. PR163-Eingang und -Rechnung bleiben unveraendert;
PR165 verbindet die aufgeloesten Werte kontrolliert mit ihnen.

## Entscheidungen

- Eigene Ein-/Ergebnisversion und VU-ID. Ein Plan umfasst 1 bis 100
  Perioden; seine Anlage- und Mortalitaetsquelle sind unabhaengig je
  genau einer von zwei exklusiven Modi. Explizite Werte oder
  Kurvenfenster decken alle Perioden lueckenlos und ohne Ueberlappung.
- Anlage: `explicit_scenario` liefert einen signierten Betrag je
  Periode. `insurer_rule_on_opening_backing_assets` multipliziert
  **Anfangsaktiva** mit einem signierten Satz von -1 bis 1 und rundet
  mit `ROUND_HALF_EVEN` auf `0.0001`. Neue Praemien und Kapitalzufuhr
  erhalten in dieser Periode keinen rueckwirkenden Ertrag. Dies ist
  eine einfache VU-Anlageregel, keine Anlageoptimierung.
- Mortalitaet: `explicit_death_policy_ids` nennt betroffene IDs je
  Periode. `exogenous_deterministic_rate_curve` rundet je fachlicher
  Kohorte `Anfangsstueckzahl * Satz` mit `ROUND_HALF_UP` auf ganze
  Todesfaelle und waehlt die lexikografisch ersten aktiven Policen-IDs
  dieser Kohorte. Keine RNG-Ziehung, Alters- oder Produkttafel und
  keine VN-Strategie. Die Auswahlregel ist ein transparenter,
  moeglicherweise verzerrender Workshop-Default, kein Sterblichkeitsmodell.
- Die Eingabe nennt alle aktiven Anfangspolicen mit ID und Kohorte,
  hoechstens 100, sowie Anfangsaktiva. Doppelte IDs, unbekannte
  explizite Todesfaelle und unvollstaendige Quellen werden atomar
  abgelehnt. Todesfallleistungen bleiben separate explizite
  Szenariowerte; der Resolver setzt weder Leistungen noch Bilanzwerte.
- Ein laengerer Plan mit gleichem Anfangsfenster muss fuer dieselbe
  Periode dieselben Werte liefern. Eingabelistenreihenfolge,
  Decimal-Kontext und Wiederholung aendern das Ergebnis nicht.

## Herkunft, Risiken und Abnahme

`IMSDATA.C` enthaelt `MAXSPARTEN 2` und `BAV.Zs` fuer die Verzinsung
der **Schadenreserven**; `IMS.E` nutzt `Zs[gperiod]` fuer die beiden
VU-Sparten. Das belegt einen periodischen Zinsinput im Altmodell,
nicht die neue Lebens-Anlage- oder Mortalitaetsregel. Es gibt keine
historische Vollgleichheitsbehauptung. Tests pruefen beide Modi,
Fenstergrenzen, Rundung, VU-Bindung, Policenauswahl, Fehler ohne
Teilwerte und exakte Prefixstabilitaet. Die Lebensrechnung und der
alte Nichtleben-Runner bleiben unveraendert.

Offen fuer PR165: Uebergabe der aufgeloesten Anlage- und Todesfallwerte
an die periodische Lebensrechnung, explizite Todesfallleistung pro
ausgewaehlter Police, Carryover und Runner-Budget. PR166-167 bringen
Ergebnisablage/Export und Workbench.
