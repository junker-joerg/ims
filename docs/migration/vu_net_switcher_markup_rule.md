# VU-Regel Vrvu04: Mark-Up II

## Ziel

Dieser Schritt portiert den deterministischen Kern der historischen VU-Regel `Vrvu04`.
Die Regel nutzt Nettowechsler je Sparte als Vergleichswert fuer die Praemien- und
Werbefortschreibung.

## Ursprung im Altcode

Der fachliche Ursprung liegt in `IMS.E`:

- `act Vrvu04`
- Kommentar: `Verhaltensregel: Mark-Up II`
- Kernformel: Nettowechsler je Sparte als `Vn(t-1) - Vn(t-2)`

Der portierte Ausschnitt uebernimmt:

- zwei Sparten
- Nettowechslerberechnung aus expliziten Vorperiodenwerten
- Vergleich gegen sektorisierte Anspruchsniveaus
- Normal- und Aenderungsschock-Parameter
- Reservenverzinsung je Periode
- Startperiodenverhalten: In den ersten zwei Perioden bleiben die gelieferten Praemie- und Werbewerte erhalten, Reserven werden verzinst

## Python-Abbildung

Der neue Rechenkern liegt in `python_port/ims/model/vu_rules.py`.

Ergaenzt wurden:

- `VUNetSwitcherMarkupRuleParameters`
- `VUNetSwitcherMarkupRuleSnapshot`
- `VUNetSwitcherMarkupRuleResult`
- `VUNetSwitcherMarkupRuleApplication`
- `apply_vu_net_switcher_markup_rule`
- `apply_vu_net_switcher_markup_rule_to_insurer`
- `apply_vu_net_switcher_markup_rule_snapshots`
- `load_vu_net_switcher_markup_rule_snapshots_from_mapping`

Szenarien koennen optional das Feld `vu_net_switcher_markup_rule_snapshots` enthalten.
Der Snapshot muss `previous_policyholders_sector` explizit enthalten, weil der kleine
Replay-/Regelpfad die zweite Vorperiode noch nicht automatisch aus einem vollstaendigen
historischen Zustandslauf herleitet.

## Grenzen

Bewusst nicht enthalten sind:

- keine automatische historische Auswahl von Regelarten
- kein Scheduler-Anschluss
- keine automatische Herleitung von `Vn(t-2)`
- keine Parameterherleitung aus historischen Initialdaten
- keine Vrvu01-/Vrvu02-Zufallsregeln
- keine Vollsimulation
- keine Aussage ueber historische Vollgleichheit

## Naechster sinnvoller Schritt

Der naechste fachliche Schritt kann die noch fehlende automatische Vorperiodenbasis
fuer VU-Regeln verbreitern oder einen weiteren eng belegbaren VU-/VN-Regelausschnitt
portieren.
