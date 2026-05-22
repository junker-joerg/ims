# VN-Regel Vrvn05: Stichprobensuche

Dieser Slice portiert den Versicherungsentscheidungsanteil der historischen
VN-Regel `Vrvn05`. Der bestehende Schadenskern und die Abrechnung bleiben
unveraendert; neu ist ein Baustein, der aus einem Marktschadenindikator,
aktiven aktuellen VU-Praemien, Stichprobengroessen und expliziten Draws
`VNInsuranceDecision`-Objekte bildet.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn05`, etwa Zeilen 3225 bis 3514

In Periode 1 verwendet Vrvn05 die Startwerte:

- `Rk[1].l.Vs[1]` und `Rk[2].k.Vs[1]` fuer den Versicherungsstatus
- `Rk[1].l.Vu[1]` und `Rk[2].k.Vu[1]` fuer den Versicherer

In Perioden nach der Startperiode bestimmt Vrvn05 den Versicherungsstatus aus
dem BAV-Schadenindikator:

- `vr1 = (Dg[0] <= e*)`
- `vr2 = (Dg[0] <= f*)`

Anschliessend zieht der Altcode je Sparte eine Stichprobe aus aktiven VU. Die
Ziehung erfolgt mit Wiederholung; die beobachteten aktuellen Praemien werden in
einen Suchvektor geschrieben. Danach wird der niedrigste beobachtete
Praemienwert gewaehlt. Fuer jede Stichprobenziehung werden Informationskosten
addiert.

## Python-Abbildung

Der Kern liegt in `python_port/ims/model/vn_insurance_rules.py`.

Wichtige Typen und Funktionen:

- `VNSampleSearchInsuranceRuleParameters`
- `VNSampleSearchInsuranceRuleDraws`
- `VNSampleSearchInsurerInput`
- `VNSampleSearchInsuranceRuleResult`
- `apply_vn_sample_search_insurance_rule`
- `vn_sample_search_insurance_rule_parameters_from_mapping`
- `vn_sample_search_insurance_rule_draws_from_mapping`
- `load_vn_sample_search_insurer_inputs_from_mapping`

Die VU-Auswahl nutzt sortierte aktive VU-Eingaben und explizite Draws im
Intervall `[0.0, 1.0)`. Bei gleicher beobachteter Praemie bleibt durch die
aufsteigende Auswertung der kleinste aktive `insurer_id` erhalten. Das ist die
deterministische Python-Abbildung des historischen Minimum-Loops ueber
aufsteigende VU-Indizes.

Die Informationskosten werden als `sum(sample_sizes) *
information_cost_per_sample` diagnostisch ausgewiesen. Der bestehende
VN-Abrechnungskern bleibt unveraendert; eine spaetere Integration kann diese
Kosten in den Vermoegenspfad einhaengen.

## Validierung

Die Tests decken ab:

- Uebernahme initialer Startentscheidungen in Periode 1
- Statusbildung mit Normal- und Schockschwellen
- Stichprobenziehung mit Wiederholung aus aktiven VU
- Minimumauswahl nach aktueller Praemie je Sparte
- Diagnose der gezogenen Versicherer, verwendeten Draws und Informationskosten
- Loader- und Eingabevalidierung fuer Parameter, Draws und aktive Praemien
- direkte Weitergabe der erzeugten Entscheidungen in den bestehenden
  VN-Schaden-/Abrechnungspfad

## Grenzen

- Keine historische Modulo-RNG-Gleichheit wird behauptet.
- Die Informationskosten werden in diesem Slice nur diagnostisch geliefert und
  noch nicht automatisch in den Settlement-Vermoegenspfad eingebucht.
- Keine automatische historische Scheduler- oder Regelwahl.
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit.
