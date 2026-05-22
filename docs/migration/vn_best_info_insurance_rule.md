# VN-Regel Vrvn06: Beste Information

Dieser Slice portiert den Versicherungsentscheidungsanteil der historischen
VN-Regel `Vrvn06`. Der bestehende Schadenskern und die Abrechnung bleiben
unveraendert; neu ist ein Baustein, der aus einem Marktschadenindikator und den
aktuellen aktiven VU-Praemien `VNInsuranceDecision`-Objekte bildet.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn06`, etwa Zeilen 3517 bis 3786

In Periode 1 verwendet Vrvn06 die Startwerte:

- `Rk[1].l.Vs[1]` und `Rk[2].k.Vs[1]` fuer den Versicherungsstatus
- `Rk[1].l.Vu[1]` und `Rk[2].k.Vu[1]` fuer den Versicherer

In Perioden nach der Startperiode bestimmt Vrvn06 den Versicherungsstatus aus
dem BAV-Schadenindikator:

- `vr1 = (Dg[0] <= e*)`
- `vr2 = (Dg[0] <= f*)`

Anschliessend liest der Altcode je Sparte die aktuellen Praemien aller VU,
beruecksichtigt bei der Minimumsuche aber nur aktive VU. Gewaehlt wird der
aktive Versicherer mit der niedrigsten aktuellen Praemie. Fuer jede gelesene
Praemieninformation werden Informationskosten addiert.

## Python-Abbildung

Der Kern liegt in `python_port/ims/model/vn_insurance_rules.py`.

Wichtige Typen und Funktionen:

- `VNBestInfoInsuranceRuleParameters`
- `VNBestInfoInsuranceRuleResult`
- `apply_vn_best_info_insurance_rule`
- `vn_best_info_insurance_rule_parameters_from_mapping`

Die VU-Auswahl nutzt dieselben aktiven VU-Praemieneingaben wie der Vrvn05-Slice.
Bei gleicher Praemie bleibt durch die aufsteigende Auswertung der kleinste
aktive `insurer_id` erhalten. Das ist die deterministische Python-Abbildung des
historischen Minimum-Loops ueber aufsteigende VU-Indizes.

Die Informationskosten werden als `2 * len(active_insurer_inputs) *
information_cost_per_insurer` diagnostisch ausgewiesen. Der historische Code
liest zwar technisch alle `MAXVU`-Praemien, waehlt aber nur aktive VU; der
Python-Kern arbeitet bewusst mit der expliziten aktiven Eingabemenge.

## Begleitende Haertung

Der Slice ersetzt im Vrvn05-Stichprobenkern die feste Praemien-Sentinel `1000.0`
durch `float("inf")`. Dadurch bleiben hohe, aber gueltige Praemienskalen
auswaehlbar und fuehren nicht zu einem irrefuehrenden Stichprobengroessenfehler.

## Validierung

Die Tests decken ab:

- Uebernahme initialer Startentscheidungen in Periode 1
- Statusbildung mit Normal- und Schockschwellen
- Minimumauswahl nach aktueller aktiver Praemie je Sparte
- Diagnose betrachteter Versicherer und Informationskosten
- Loader- und Eingabevalidierung
- direkte Weitergabe der erzeugten Entscheidungen in den bestehenden
  VN-Schaden-/Abrechnungspfad
- Regression fuer Vrvn05-Praemien groesser als `1000.0`

## Grenzen

- Keine historische Modulo-RNG-Gleichheit wird behauptet.
- Die Informationskosten werden in diesem Slice nur diagnostisch geliefert und
  noch nicht automatisch in den Settlement-Vermoegenspfad eingebucht.
- Keine automatische historische Scheduler- oder Regelwahl.
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit.
