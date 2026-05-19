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
- `apply_vu_foreign_info_rule`
- `apply_vu_foreign_info_rule_to_insurer`

Damit der Ausschnitt spartengetrennt testbar bleibt, fuehrt `Insurer` zusaetzlich kleine aktuelle Vektoren fuer Praemie und Werbung:

- `premiums_current_sector`
- `advertising_current_sector`

Der Szenario-Lader liest diese Felder optional. Bei alten Skalarwerten bleibt die bisherige Kompatibilitaet erhalten, indem der Skalar konservativ fuer beide Sparten verwendet wird.

## Validierung

Die neuen Tests pruefen:

- Auswahl der richtigen BAV-Frmdinf-Quelle fuer Dumping, Durchschnitt und Angriff
- Normal- und Aenderungsschockparameter
- period-1-Verhalten mit unveraenderten Startwerten
- Fortschreibung der Reserven mit Zinssatz
- Aktualisierung des VU-Snapshots
- Loader-Kompatibilitaet fuer neue Vektorfelder und alte Skalarfelder
- Agrsich-Auswertung der neuen aktuellen VU-Spartenfelder

## Grenzen

Dies ist noch keine vollstaendige VU-Regelportierung.

Bewusst nicht enthalten sind:

- kein Scheduling der historischen VU-Regeln
- keine automatische Aktivierung der Regeln aus dem Periodenlauf
- keine Zufalls- oder Marktmechanik
- keine Herleitung der Parameter aus vollstaendigen historischen Regeltabellen
- keine Aussage ueber historische Vollgleichheit

## Naechster sinnvoller Schritt

Der naechste fachliche Schritt sollte diesen Regelkern entweder mit einem kleinen, expliziten VU-Regelparameter-Snapshot verbinden oder einen weiteren klar abgegrenzten VU-/VN-Regelausschnitt portieren, der bereits durch vorhandene Zustandsfelder und Tests abgesichert werden kann.
