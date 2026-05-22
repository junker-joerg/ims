# VN-Regel Vrvn03: Praeferenzversicherung

Dieser Slice portiert den Versicherungsentscheidungsanteil der historischen
VN-Regel `Vrvn03`. Der bereits portierte Schadenskern und die Abrechnung bleiben
unveraendert; neu ist ein Baustein, der aus subjektiven
Schadenwahrscheinlichkeiten, aktiven VU-Werbewerten und optionalen
Fallback-Draws `VNInsuranceDecision`-Objekte bildet.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn03`, etwa Zeilen 2627 bis 2805

In Periode 1 verwendet Vrvn03 die Startwerte:

- `Rk[1].l.Vs[1]` und `Rk[2].k.Vs[1]` fuer den Versicherungsstatus
- `Rk[1].l.Vu[1]` und `Rk[2].k.Vu[1]` fuer den Versicherer

In Perioden nach der Startperiode bestimmt Vrvn03 den Versicherungsstatus aus
subjektiven Schadenwahrscheinlichkeiten:

- `vr1 = (sw1 > e*)`
- `vr2 = (sw2 > f*)`

Anschliessend wird je Sparte der aktive Versicherer mit dem hoechsten relativen
Werbeanteil gewaehlt. Wenn keine aktive Werbung vorhanden ist, faellt der
Altcode auf eine zufaellige aktive VU-Auswahl zurueck.

## Python-Abbildung

Der Kern liegt in `python_port/ims/model/vn_insurance_rules.py`.

Wichtige Typen und Funktionen:

- `VNPreferenceInsuranceRuleParameters`
- `VNPreferenceInsuranceRuleDraws`
- `VNPreferenceInsurerInput`
- `VNPreferenceInsuranceRuleResult`
- `apply_vn_preference_insurance_rule`
- `vn_preference_insurance_rule_parameters_from_mapping`
- `vn_preference_insurance_rule_draws_from_mapping`
- `load_vn_preference_insurer_inputs_from_mapping`

Die VU-Auswahl nutzt die sortierten aktiven VU-Eingaben. Bei gleichen
Praeferenzwerten bleibt wie im C-Loop der erste gefundene Versicherer erhalten,
also der kleinste aktive `insurer_id` in der Python-Abbildung. Der Zufallsfallback
nutzt explizite Draws im Intervall `[0.0, 1.0)`.

Der historische Risiko-2-Block addiert beim Normalisieren sichtbar `pf1[i]` in
den Nenner, obwohl `pf2[i]` kommentiert und ausgewertet wird. Fuer die Auswahl
des Maximums bleibt der gewaehlte Versicherer dadurch unveraendert; die
diagnostischen `preference_scores` im Python-Kern werden jedoch je Sparte aus
dem eigenen Werbevektor gebildet.

## Validierung

Die Tests decken ab:

- Uebernahme initialer Startentscheidungen in Periode 1
- Statusbildung mit Normal- und Schockschwellen
- Praeferenzwahl nach maximalem Werbeanteil je Sparte
- deterministische Tie-Breaks ueber aufsteigende Versicherer-IDs
- Zufallsfallback bei Null-Werbung
- Loader- und Eingabevalidierung
- direkte Weitergabe der erzeugten Entscheidungen in den bestehenden
  VN-Schaden-/Abrechnungspfad

## Grenzen

- Keine historische Modulo-RNG-Gleichheit wird behauptet.
- Die diagnostischen Praeferenzscores bilden die fachliche
  Sektor-Normalisierung ab; sie behaupten keine 1:1-Abbildung der
  Risiko-2-Nenner-Eigenheit im C-Code.
- Keine automatische historische Scheduler- oder Regelwahl.
- Die spaeteren Such- und Beste-Regeln bleiben ausserhalb dieses Slices.
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit.
