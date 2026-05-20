# VU-Regel Vrvu10: frei definierbar

## Ziel

Dieser Schritt portiert einen kontrollierten Ausschnitt der historischen VU-Regel
`Vrvu10`. Die Regel ist im Altcode als frei definierbare Verhaltensregel angelegt
und nutzt eine lineare Fortschreibung fuer Praemie und Werbung je Sparte.

## Ursprung im Altcode

Der fachliche Ursprung liegt in `IMS.E`:

- `act Vrvu10`
- Kommentar: `Verhaltensregel: frei definierbar`
- Parameterblock `Pv[0]` bis `Pv[15]`
- Normal- und Aenderungsschockzweige
- Reservenverzinsung mit dem BAV-Zinssatz

Der Python-Slice bildet die lineare Form kontrolliert ab:

- Sparte 1 Praemie: `a + b * previous_premium`
- Sparte 2 Praemie: `c + d * previous_premium`
- Sparte 1 Werbung: `e + f * previous_advertising`
- Sparte 2 Werbung: `g + h * previous_advertising`

Die Normal-/Schockparameter werden explizit im Szenario-Snapshot uebergeben.

## Python-Abbildung

Der Rechenkern liegt in `python_port/ims/model/vu_rules.py`.

Ergaenzt wurden:

- `VUFreeLinearRuleParameters`
- `VUFreeLinearRuleSnapshot`
- `VUFreeLinearRuleResult`
- `VUFreeLinearRuleApplication`
- `apply_vu_free_linear_rule`
- `apply_vu_free_linear_rule_to_insurer`
- `apply_vu_free_linear_rule_snapshots`
- `load_vu_free_linear_rule_snapshots_from_mapping`

Szenarien koennen optional das Feld `vu_free_linear_rule_snapshots` enthalten.
Der VU-Periodenrunner laedt und validiert diese Snapshots gemeinsam mit den
anderen expliziten VU-Regelpfaden.

## Annahmen

Der historische Block ist als freie Eingriffsstelle formuliert. Der Python-Slice
nutzt deshalb die bereits im Python-Modell vorhandenen aktuellen VU-Snapshots als
Vorwertbasis fuer die lineare Formel. Damit bleibt die Regel reproduzierbar und
testbar, ohne eine vollstaendige historische Scheduler- oder Tabellenherleitung
zu behaupten.

## Grenzen

Bewusst nicht enthalten sind:

- keine automatische historische Auswahl von Vrvu10
- kein Scheduler-Anschluss
- keine Parameterherleitung aus historischen Initialdaten
- keine freie Python-Formel- oder Plugin-Auswertung
- keine Vollsimulation
- keine Aussage ueber historische Vollgleichheit
