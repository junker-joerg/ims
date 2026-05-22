# VN-Regel Vrvn01: Pflichtversicherung

Dieser Slice portiert den Versicherungsentscheidungsanteil der historischen
VN-Regel `Vrvn01`. Der bereits portierte Schadenskern und die Abrechnung bleiben
unveraendert; neu ist ein wiederverwendbarer Baustein, der die initialen
Startentscheidungen oder die Pflichtversicherung ab Periode 2 in
`VNInsuranceDecision`-Objekte uebersetzt.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`, etwa Zeilen 2185 bis 2263

In Periode 1 verwendet Vrvn01 die Startwerte:

- `Rk[1].l.Vs[1]` und `Rk[2].k.Vs[1]` fuer den Versicherungsstatus
- `Rk[1].l.Vu[1]` und `Rk[2].k.Vu[1]` fuer den Versicherer

In Perioden nach der Startperiode setzt Vrvn01 beide Sparten auf versichert:

- `vr1 = 1`
- `vr2 = 1`

Danach wird fuer jede Sparte ein aktiver Versicherer zufaellig ausgewaehlt.

## Python-Abbildung

Der Kern liegt in `python_port/ims/model/vn_insurance_rules.py`.

Wichtige Typen und Funktionen:

- `VNCompulsoryInsuranceRuleDraws`
- `VNCompulsoryInsuranceRuleResult`
- `apply_vn_compulsory_insurance_rule`
- `vn_compulsory_insurance_rule_draws_from_mapping`

Fuer Periode 1 erwartet der Python-Kern explizite `initial_decisions`. Fuer
Perioden nach 1 erwartet er aktive Versicherer und explizite
`insurer_choice_draws`. Die VU-Auswahl nutzt wie der Vrvn02-Slice die sortierte
aktive VU-Menge und Draws im Intervall `[0.0, 1.0)`.

## Validierung

Die Tests decken ab:

- Uebernahme initialer Startentscheidungen in Periode 1
- Pflichtversicherung und aktive VU-Auswahl ab Periode 2
- Validierung fehlender Startentscheidungen, Draws und aktiver Versicherer
- Loader-Validierung fuer VU-Auswahldraws
- direkte Weitergabe der erzeugten Entscheidungen in den bestehenden
  VN-Schaden-/Abrechnungspfad

## Grenzen

- Keine historische Modulo-RNG-Gleichheit wird behauptet.
- Keine automatische historische Scheduler- oder Regelwahl.
- Keine Praeferenz-, Such- oder Beste-Regel.
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit.
