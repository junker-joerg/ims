# Vdefmd6-VU-Snapshotvertrag

## Ziel

Der Vertrag `pr79-v1` bindet alle 25 VU der typisierten
`Vdefmd6Population` an die vorhandenen Python-Snapshottypen. Der Builder
`build_vdefmd6_vu_snapshot_batch` liest einen expliziten Vorperiodenzustand,
die 16 Regelparameter und die drei Anspruchsniveaus je Sparte. Er schreibt
keinen Modellzustand fort.

## Regelabbildung

| Historische Regel | Python-Snapshot | VU |
| --- | --- | ---: |
| `Vrvu01` | `VURandomUniformRuleSnapshot` | 2 |
| `Vrvu02` | `VURandomNormalRuleSnapshot` | 2 |
| `Vrvu03` | `VUReserveMarkupRuleSnapshot` | 3 |
| `Vrvu04` | `VUNetSwitcherMarkupRuleSnapshot` | 3 |
| `Vrvu05` | `VUMarketShareMarkupRuleSnapshot` | 3 |
| `Vrvu06` | `VUExpectedClaimRuleSnapshot` | 3 |
| `Vrvu07-09` | `VUForeignInfoRuleSnapshot` | 9 |

Die geraden Parameterpositionen bilden den Vorschockfall, die ungeraden den
Schockfall. Anspruchsniveau 1 bindet Reserven, Anspruchsniveau 2
Nettowechsler und Anspruchsniveau 3 Marktanteile. Fuer `Vrvu04` wird die
zweite Vorperiode separat als `policyholders_t_minus_2` gehalten.

## BAV-Vorperiodeninputs

Der Batch haelt pro VU Praemie, Werbung, Reserve, VN-Zahlen, Schadenanzahl und
Schadensumme fuer `t-1` sowie die VN-Zahlen fuer `t-2`. Pro aktivem VN wird der
Versicherungsstatus aus `t-1` festgehalten. Diese Felder reichen als explizite
Eingangsoberflaeche fuer den vorhandenen `Frmdinf`-Kern, ohne ihn in PR 79
auszufuehren.

## Informationskosten

In den historischen Regeln `Vrvn05` und `Vrvn06` lautet das Vermoegensende
sinngemaess `Vm(t-1) - Schaden - Praemien - ik`. Der Python-Regelkern liefert
`information_cost`, der heutige `VNDamageSettlementSnapshot` akzeptiert diesen
Wert jedoch noch nicht. Daher gilt:

- `information_cost_origin_evidenced = true`;
- `information_cost_application_ready = false`;
- `independent_periods_2_49_ready = false`.

PR 80 muss die Kosten explizit und getestet an das Settlement anbinden, bevor
der Mehrperiodenpfad als geschlossen gelten kann.

## Fortschreibung durch PR 80

PR 80 hat diese Luecke mit einem nichtnegativen `information_cost`-Feld
geschlossen. Die Kosten werden genau einmal vom kumulierten VN-Vermoegen
abgezogen. Der kontrollierte Vorschockpfad erzeugt VU14 fuer Perioden 1-49 und
klassifiziert 236/686 Feldtreffer; die historische Reihenfolge bleibt offen.

## Grenzen

Der Bericht materialisiert 8 uniforme und 8 normale moderne RNG-Werte. Er
fuehrt weder BAV-Service noch VU-/VN-Runner aus, verwendet keine Legacy-Zeile
als Erzeugungsinput und startet keine Simulation. Die moderne Reihenfolge ist
kein historischer RNG-Nachweis. Es gibt keine historische Vollgleichheitsbehauptung.
