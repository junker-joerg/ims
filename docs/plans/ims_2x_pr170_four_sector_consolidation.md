# PR170: Vier-Sparten-Konsolidierung

Stand: 2026-09-18

## Ziel und Grenze

Vier explizite IMS-2.x-Eingaben fuer denselben VU und dasselbe lueckenlose
Periodenfenster werden serverseitig erneut berechnet und zu einer einfachen
Modell-Gesamtbilanz zusammengefuehrt: Kfz, Sach-Haftpflicht, Leben und Kranken.
Die bisherige Zwei-Sparten-API bleibt unveraendert. Es gibt weder Speicherung
noch einen gemeinsamen Mehrsparten-Runner; die Zusammengehoerigkeit der
Nicht-Kranken-Eingaben zu einem Szenario wird vom Aufrufer deklariert, nicht
historisch bewiesen.

## Herkunft und Abbildung

| Ursprung | IMS-2.x-Rechnung | Konsolidierte Position |
| --- | --- | --- |
| `IMSDATA.C` mit zwei historischen Schadenpositionen `LV`/`KV` | `non_life_model_balance.py` fuer `motor` und `property_liability` | Cash = Vermoegen; Schadenverbindlichkeit = Verpflichtung |
| Keine historische Lebensposition in den zwei C-Schadenpositionen | `life_period_chain.py`/`life_policy_balance.py` | Deckende Vermoegenswerte = Vermoegen; Garantieverpflichtung = Verpflichtung |
| Keine historische Krankenposition in den zwei C-Schadenpositionen | `health_period_chain.py`/`health_model_balance.py` | Cash = Vermoegen; offene Leistung = Verpflichtung |

Die vier Eigenkapitalpositionen, Periodenergebnisse sowie explizite
Kapitalzufuehrungen/-ausschuettungen werden addiert. Schaden-/Leistungsfluesse,
Garantiegutschriften, Police- und Bestandszahlen bleiben spartenspezifisch;
sie werden **nicht** als vermeintlich einheitliche Kennzahl addiert. Es gibt
keine konzerninternen Forderungen oder Transfers in diesem einfachen Modell.

## Abnahme

- Eingang: versioniert, genau vier verschiedene Sparten, gleicher VU,
  gleicher Horizont aus 1, 2, 5, 10, 25, 50 oder 100 Perioden; bei Kranken muessen `scenario_id`/`variant_id`
  zum aeusseren Szenario passen.
- Jede Sparte wird aus ihrer Eingabe neu berechnet. Ungueltige Eingabe,
  anderer VU, andere Periode oder nicht stimmende Bilanz liefert atomar
  keine Spartenzahl und keine Gesamtzeile.
- Ergebnis: je Sparte und Periode eine normalisierte Allokation sowie
  die Gesamtbilanz mit `Vermoegen = Verpflichtung + Eigenkapital`,
  Eigenkapitalbewegung und Carryover; exakte Dezimaltexte und Digests.
- Reproduzierbarkeit und stabiler Prefix, einschliesslich 100 Perioden,
  werden getestet. API und bestehende Zwei-Sparten-API werden getrennt getestet.

## Offene Punkte

- PR170a ist der unmittelbar naechste kleine Schnitt: eine lesbare
  Vier-Sparten-Bilanzansicht in der Workbench mit gezielter Uebernahme der
  vier Szenarioeingaben, Fehleranzeige und Browserabnahme. Der vorhandene
  Zwei-Sparten-Editor bleibt bis dahin ausdruecklich als Schadenansicht
  beschriftet.
- Ein durchgaengender Vier-Sparten-Runner, ein gemeinsamer Szenarioeditor,
  Speicherung und Export dieser neuen Gesamtbilanz bleiben weitere
  eigene Folgeschritte.
- Die Deklaration eines gemeinsamen Szenarios ersetzt keine fachliche
  Pruefung, ob die vier Teilannahmen wirtschaftlich zusammenpassen.
- Keine aufsichtsrechtliche Bilanz, keine Solvency-II-Aussage und kein
  historischer Vollgleichheitsnachweis.
