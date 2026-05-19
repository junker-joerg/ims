# VU-Fremdinformations-Regelkern

## Ziel

Dieser Schritt portiert einen kleinen gemeinsamen Rechenkern aus den historischen VU-Regeln, die direkt BAV-Fremdinformationen verwenden.

Der neue Python-Ausschnitt ist bewusst eng begrenzt: Er berechnet spartengetrennte Praemien- und Werbezielwerte aus bereits vorhandenen BAV-Frmdinf-Vektoren und schreibt Reserven periodisch mit dem uebergebenen Zinssatz fort.

## Ursprung im Altcode

Der Slice bezieht sich auf die gemeinsamen Formelteile in `legacy_c/IMS.E`:

- `Vrvu07` fuer Dumpingverhalten
- `Vrvu08` fuer Durchschnittsverhalten
- `Vrvu09` fuer Angriffsverhalten

Diese Regeln unterscheiden sich im gelesenen Fremdinformationsvektor:

- Dumping: `Pm` und `Wm`
- Durchschnitt: `Dp` und `Dw`
- Angriff: `Mp` und `Mw`

Die lineare Berechnung der Zielwerte ist fuer diesen Ausschnitt gleichartig.

## Python-Abbildung

Der Rechenkern liegt in `python_port/ims/model/vu_rules.py`.

Ergaenzt wurden:

- `VUForeignInfoRuleKind`
- `VUForeignInfoRuleParameters`
- `VUForeignInfoRuleResult`
- `VUForeignInfoRuleSnapshot`
- `VUForeignInfoRuleApplication`
- `apply_vu_foreign_info_rule`
- `apply_vu_foreign_info_rule_to_insurer`
- `apply_vu_foreign_info_rule_snapshots`
- `load_vu_foreign_info_rule_snapshots_from_mapping`

Damit der Ausschnitt spartengetrennt testbar bleibt, fuehrt `Insurer` zusaetzlich kleine aktuelle Vektoren fuer Praemie und Werbung:

- `premiums_current_sector`
- `advertising_current_sector`

Der Szenario-Lader liest diese Felder optional. Bei alten Skalarwerten bleibt die bisherige Kompatibilitaet erhalten, indem der Skalar konservativ fuer beide Sparten verwendet wird.

## Explizite Parameter-Snapshots

Nach dem ersten Regelkern-Slice kann ein Szenario optional explizite VU-Frmdinf-Regelparameter-Snapshots enthalten.

Das Feld `vu_foreign_info_rule_snapshots` ist bewusst kein Scheduler und keine historische Regelauswahl. Es verbindet nur einen bekannten Versicherer, eine der drei bereits portierten Frmdinf-Quellen und einen vollstaendig angegebenen Parameterblock:

- `insurer_id`
- `rule_kind`
- `interest_rate`
- `change_shock`
- `parameters`

Der Loader macht daraus `VUForeignInfoRuleSnapshot`-Objekte. `apply_vu_foreign_info_rule_snapshots` wendet diese Snapshots deterministisch auf passende Versicherer an und liefert pro Anwendung eine kleine Diagnose zurueck.

## Validierung

Die neuen Tests pruefen:

- Auswahl der richtigen BAV-Frmdinf-Quelle fuer Dumping, Durchschnitt und Angriff
- Normal- und Aenderungsschockparameter
- period-1-Verhalten mit unveraenderten Startwerten
- Fortschreibung der Reserven mit Zinssatz
- Aktualisierung des VU-Snapshots
- Loader-Kompatibilitaet fuer neue Vektorfelder und alte Skalarfelder
- Agrsich-Auswertung der neuen aktuellen VU-Spartenfelder
- Laden expliziter VU-Frmdinf-Regelparameter-Snapshots aus In-Memory-Szenarien
- deterministische Anwendung dieser Snapshots auf passende Versicherer
- Fehlerfall fuer unbekannte Versicherer und unvollstaendige Parameterbloecke

## Grenzen

Dies ist noch keine vollstaendige VU-Regelportierung.

Bewusst nicht enthalten sind:

- kein Scheduling der historischen VU-Regeln
- keine automatische Aktivierung der Regeln aus dem Periodenlauf
- keine Zufalls- oder Marktmechanik
- keine Herleitung der Parameter aus vollstaendigen historischen Regeltabellen
- keine automatische Auswahl von Regelkindern aus historischen Ablaufbedingungen
- keine Aussage ueber historische Vollgleichheit

## Naechster sinnvoller Schritt

Der naechste fachliche Schritt kann weitere klar abgegrenzte VU-/VN-Regelausschnitte portieren oder auf dem kleinen Periodenschritt in `vu_foreign_info_period_runner.md` aufbauen, ohne bereits eine vollstaendige historische Simulation zu behaupten.
