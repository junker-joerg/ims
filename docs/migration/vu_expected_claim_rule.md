# VU-Regel Vrvu06: Erwartungsschaden

## Ziel

Dieser Schritt portiert den deterministischen Kern der historischen VU-Regel `Vrvu06`.
Die Regel nutzt den erwarteten Schaden je Sparte als Vergleichswert fuer die
Praemien- und Werbefortschreibung.

## Ursprung im Altcode

Der fachliche Ursprung liegt in `IMS.E`:

- `act Vrvu06`
- Kommentar: `Verhaltensregel: Erwartungsschaden`
- Kernformel: `s = Sh / Sa` mit Nullschutz

Der portierte Ausschnitt uebernimmt:

- zwei Sparten
- erwarteten Schaden aus Schadensumme und Schadenanzahl
- Nullschutz bei `Sa == 0`
- Normal- und Aenderungsschock-Parameter
- Reservenverzinsung je Periode
- Startperiodenverhalten: Praemie und Werbung bleiben erhalten, Reserven werden verzinst

## Python-Abbildung

Der neue Rechenkern liegt in `python_port/ims/model/vu_rules.py`.

Ergaenzt wurden:

- `VUExpectedClaimRuleParameters`
- `VUExpectedClaimRuleSnapshot`
- `VUExpectedClaimRuleResult`
- `VUExpectedClaimRuleApplication`
- `apply_vu_expected_claim_rule`
- `apply_vu_expected_claim_rule_to_insurer`
- `apply_vu_expected_claim_rule_snapshots`
- `load_vu_expected_claim_rule_snapshots_from_mapping`

Szenarien koennen optional das Feld `vu_expected_claim_rule_snapshots` enthalten.
Der bestehende VU-Periodenrunner laedt diese Snapshots und wendet sie nach den
bereits vorhandenen Frmdinf- und Mark-Up-I-Snapshots an.

## Grenzen

Bewusst nicht enthalten sind:

- keine automatische historische Auswahl von Regelarten
- kein Scheduler-Anschluss
- keine Parameterherleitung aus historischen Initialdaten
- keine Portierung der Schadenentstehung selbst
- keine Vrvu01-/Vrvu02-Zufallsregeln
- keine Vrvu04-/Vrvu05-Portierung
- keine Vollsimulation
- keine Aussage ueber historische Vollgleichheit

## Naechster sinnvoller Schritt

Der naechste fachliche Schritt kann Vrvu04 oder Vrvu05 portieren. Beide benoetigen
weitere klar kontrollierte Vorperiodenfelder fuer Versicherungsnehmerzahlen bzw.
Marktanteile.
