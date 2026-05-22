# VN-Regel Vrvn02: Zufallsversicherung

Dieser Slice portiert den Versicherungsentscheidungsanteil der historischen
VN-Regel `Vrvn02`. Der bereits portierte Schadenskern und die Abrechnung bleiben
unveraendert; neu ist ein wiederverwendbarer Baustein, der aus
Status-Schwellen, aktiven Versicherern und expliziten Draws
`VNInsuranceDecision`-Objekte bildet.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn02`

In Perioden nach der Startperiode bestimmt Vrvn02 den Versicherungsstatus mit:

- `vr1 = (e <= myrndf())`
- `vr2 = (f <= myrndf())`

Anschliessend wird fuer jede Sparte ein aktiver Versicherer zufaellig
ausgewaehlt, bevor die Versicherungszweige ausgewertet werden. Der Python-Kern
erzwingt diese Auswahl deshalb auch fuer unversicherte Sparten und legt sie in
`selected_insurer_ids` offen. Bei nicht versicherten Sparten wird sie nicht als
`insurer_id` an den Abrechnungspfad weitergereicht, weil dieser unversicherte
Entscheidungen ohne Versicherer erwartet.

## Python-Abbildung

Der Kern liegt in `python_port/ims/model/vn_insurance_rules.py`.

Wichtige Typen und Funktionen:

- `VNRandomInsuranceRuleParameters`
- `VNRandomInsuranceRuleDraws`
- `VNRandomInsuranceRuleResult`
- `apply_vn_random_insurance_rule`
- `vn_random_insurance_rule_parameters_from_mapping`
- `vn_random_insurance_rule_draws_from_mapping`
- `load_active_insurer_ids_from_mapping`

Die VU-Auswahl nutzt die sortierte aktive VU-Menge und einen Draw im Intervall
`[0.0, 1.0)`. Dadurch ist der Python-Pfad deterministisch und testbar, ohne die
historische Modulo-RNG-Folge als identisch zu behaupten.

## Validierung

Die Tests decken ab:

- Normal- und Schockschwellen
- Randfall `threshold == draw`, der wie im Altcode als versichert gilt
- aktive Versichererauswahl vor dem Statuszweig und Validierung leerer aktiver
  Mengen
- Loader-Normalisierung und Draw-Validierung
- direkte Weitergabe der erzeugten Entscheidungen in den bestehenden
  VN-Schaden-/Abrechnungspfad

## Grenzen

- Keine Startperioden-Sonderlogik.
- Keine automatische historische Scheduler- oder Regelwahl.
- Keine Praeferenz-, Pflichtversicherungs-, Such- oder Beste-Regel.
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit.
