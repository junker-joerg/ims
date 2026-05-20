# VU-Regel Vrvu03: Mark-Up I

## Ziel

Dieser Schritt portiert einen weiteren eng abgegrenzten VU-Regelkern aus dem historischen Modell:
`Vrvu03`, die Mark-Up-I-Regel.

Die Regel ist deterministisch. Sie vergleicht die Vorperiodenreserven eines Versicherers je Sparte mit
einem Anspruchsniveau und multipliziert daraus Praemien- und Werbewerte mit explizit geladenen
Regelparametern.

## Ursprung im Altcode

Der fachliche Ursprung liegt in `IMS.E`:

- `act Vrvu03`
- Kommentar: `Verhaltensregel: Mark-Up I`
- Abschnitt: Praemien- und Werbefortschreibung anhand von Reservenschwellen

Der portierte Ausschnitt uebernimmt:

- zwei Sparten
- Normal- und Aenderungsschock-Parameter
- Reservenverzinsung je Periode
- Startperiodenverhalten: Praemie und Werbung bleiben erhalten, Reserven werden verzinst
- die historische Aenderungsschock-Asymmetrie: Im Schockfall wird gegen `0.0` statt gegen das
  Anspruchsniveau verglichen

## Python-Abbildung

Der neue Rechenkern liegt in `python_port/ims/model/vu_rules.py`.

Ergaenzt wurden:

- `VUReserveMarkupRuleParameters`
- `VUReserveMarkupRuleSnapshot`
- `VUReserveMarkupRuleResult`
- `VUReserveMarkupRuleApplication`
- `apply_vu_reserve_markup_rule`
- `apply_vu_reserve_markup_rule_to_insurer`
- `apply_vu_reserve_markup_rule_snapshots`
- `load_vu_reserve_markup_rule_snapshots_from_mapping`

Szenarien koennen optional das Feld `vu_reserve_markup_rule_snapshots` enthalten. Der bestehende
VU-Periodenrunner laedt diese Snapshots und wendet sie nach dem bereits vorhandenen
VU-Frmdinf-Snapshot-Pfad an.

## Grenzen

Bewusst nicht enthalten sind:

- keine Vrvu01-/Vrvu02-Zufallsregeln
- keine Vrvu04-/Vrvu05-/Vrvu06-Regeln
- keine automatische historische Auswahl von Regelarten
- kein Scheduler-Anschluss
- keine Herleitung der Parameter aus historischen Initialdaten
- keine Vollsimulation
- keine Aussage ueber historische Vollgleichheit

## Naechster sinnvoller Schritt

Der naechste fachliche Schritt kann Vrvu04, Vrvu05 oder Vrvu06 portieren, sofern die jeweils
benoetigten Vorperiodenfelder explizit und testbar im Python-Modell abgebildet werden.
