# VU-Regel Vrvu05: Mark-Up III

## Ziel

Dieser Schritt portiert den deterministischen Kern der historischen VU-Regel `Vrvu05`.
Die Regel nutzt Marktanteile je Sparte als Vergleichswert fuer die Praemien- und
Werbefortschreibung.

## Ursprung im Altcode

Der fachliche Ursprung liegt in `IMS.E`:

- `act Vrvu05`
- Kommentar: `Verhaltensregel: Mark-Up III`
- Kernformel: Marktanteil je Sparte als `Vn / akvn` mit Nullschutz

Der portierte Ausschnitt uebernimmt:

- zwei Sparten
- Marktanteilsberechnung aus sektorisierten Versicherungsnehmerzahlen
- Nullschutz bei `akvn == 0`
- Normal- und Aenderungsschock-Parameter
- Reservenverzinsung je Periode
- Startperiodenverhalten: Praemie und Werbung bleiben erhalten, Reserven werden verzinst

## Python-Abbildung

Der neue Rechenkern liegt in `python_port/ims/model/vu_rules.py`.

Ergaenzt wurden:

- `VUMarketShareMarkupRuleParameters`
- `VUMarketShareMarkupRuleSnapshot`
- `VUMarketShareMarkupRuleResult`
- `VUMarketShareMarkupRuleApplication`
- `apply_vu_market_share_markup_rule`
- `apply_vu_market_share_markup_rule_to_insurer`
- `apply_vu_market_share_markup_rule_snapshots`
- `load_vu_market_share_markup_rule_snapshots_from_mapping`

Der `Insurer`-Zustand fuehrt nun optional `policyholders_current_sector`, damit der
Vrvu05-Slice die historischen `Vn`-Werte je Sparte ausdruecken kann. Der Loader bleibt
abwaertskompatibel: Liegt nur `policyholders_current` vor, wird der Skalar konservativ
auf beide Sparten gespiegelt.

Szenarien koennen optional das Feld `vu_market_share_markup_rule_snapshots` enthalten.
Der bestehende VU-Periodenrunner laedt diese Snapshots und wendet sie nach den bereits
vorhandenen Frmdinf-, Mark-Up-I- und Erwartungsschaden-Snapshots an.

`active_policyholder_count` kann im Snapshot weiterhin explizit angegeben werden. Fehlt
der Wert, verwendet der VU-Periodenrunner den zuvor ueber `compute_extended_foreign_info`
aktualisierten BAV-Aktivitaetszaehler als kontrollierte `akvn`-Basis. Die direkte
Snapshot-Anwendung ausserhalb des Runners verlangt weiterhin eine solche Zaehlerquelle,
damit kein impliziter Nenner entsteht.

## Grenzen

Bewusst nicht enthalten sind:

- keine automatische historische Auswahl von Regelarten
- kein Scheduler-Anschluss
- keine Parameterherleitung aus historischen Initialdaten
- keine automatische Herleitung von `akvn` ausserhalb des BAV-Aktivitaetszustands
- keine Vrvu01-/Vrvu02-Zufallsregeln
- keine Vrvu04-Portierung
- keine Vollsimulation
- keine Aussage ueber historische Vollgleichheit

## Naechster sinnvoller Schritt

Der naechste fachliche Schritt kann Vrvu04 portieren. Dafuer muessen die
Versicherungsnehmerzahlen aus zwei Vorperioden kontrolliert als explizite
Snapshot-Felder verfuegbar gemacht werden.
