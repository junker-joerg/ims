# VN-Regel Vrvn04: Suchversicherung

Dieser Slice portiert den Versicherungsentscheidungsanteil der historischen
VN-Regel `Vrvn04`. Der bestehende Schadenskern und die Abrechnung bleiben
unveraendert; neu ist ein Baustein, der aus subjektiven
Schadenwahrscheinlichkeiten und der VN-Versicherungshistorie
`VNInsuranceDecision`-Objekte bildet.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn04`, etwa Zeilen 2948 bis 3222

In Periode 1 verwendet Vrvn04 die Startwerte:

- `Rk[1].l.Vs[1]` und `Rk[2].k.Vs[1]` fuer den Versicherungsstatus
- `Rk[1].l.Vu[1]` und `Rk[2].k.Vu[1]` fuer den Versicherer

In Perioden nach der Startperiode bestimmt Vrvn04 den Versicherungsstatus aus
subjektiven Schadenwahrscheinlichkeiten:

- `vr1 = (sw1 > e*)`
- `vr2 = (sw2 > f*)`

Anschliessend durchsucht der Altcode je Sparte die frueheren Perioden des VN.
Beruecksichtigt werden nur Perioden, in denen die jeweilige Sparte versichert
war. Gewaehlt wird der Versicherer mit der niedrigsten historisch gezahlten
Praemie; bei gleicher Praemie bleibt durch den C-Loop die fruehere gefundene
Periode erhalten. Wenn keine versicherte Historie existiert, faellt Vrvn04 auf
eine zufaellige aktive VU-Auswahl zurueck.

## Python-Abbildung

Der Kern liegt in `python_port/ims/model/vn_insurance_rules.py`.

Wichtige Typen und Funktionen:

- `VNSearchInsuranceRuleParameters`
- `VNSearchInsuranceRuleDraws`
- `VNSearchInsuranceHistoryEntry`
- `VNSearchInsuranceRuleResult`
- `apply_vn_search_insurance_rule`
- `vn_search_insurance_rule_parameters_from_mapping`
- `vn_search_insurance_rule_draws_from_mapping`
- `load_vn_search_insurance_history_from_mapping`

Die Suche nutzt normalisierte Historieneintraege mit `period`, `sector_index`,
`insured`, `insurer_id` und `premium`. Eintraege aus der aktuellen oder einer
spaeteren Periode werden nicht fuer die Auswahl verwendet. Bei fehlender
versicherter Historie braucht der Fallback explizite Draws im Intervall
`[0.0, 1.0)` und eine aktive VU-Menge.

## Begleitende Haertung

Der Slice haertet ausserdem den typisierten Vrvn03-Eingabepfad:
`load_vn_preference_insurer_inputs_from_mapping` normalisiert und validiert nun
auch bereits erzeugte `VNPreferenceInsurerInput`-Objekte. Damit gelten fuer
Mapping- und Dataclass-Eingaben dieselben Zwei-Sparten- und
Nichtnegativitaetsgarantien.

## Validierung

Die Tests decken ab:

- Uebernahme initialer Startentscheidungen in Periode 1
- Statusbildung mit Normal- und Schockschwellen
- Suche nach niedrigster frueherer versicherter Praemie je Sparte
- deterministisches Beibehalten des frueheren Treffers bei gleicher Praemie
- Zufallsfallback ohne versicherte Historie
- Loader- und Eingabevalidierung fuer Historie, Parameter und Draws
- direkte Weitergabe der erzeugten Entscheidungen in den bestehenden
  VN-Schaden-/Abrechnungspfad
- Normalisierung und Validierung typisierter Vrvn03-VU-Eingaben

## Grenzen

- Keine historische Modulo-RNG-Gleichheit wird behauptet.
- Der Slice waehlt keine Regel automatisch aus einem historischen Scheduler.
- Die spaeteren VN-Regelvarianten bleiben ausserhalb dieses Slices.
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit.
