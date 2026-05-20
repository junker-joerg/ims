# VU-Frmdinf-Periodenschritt

## Ziel

Dieser Schritt verbindet den portierten BAV-Frmdinf-Kern mit den expliziten VU-Frmdinf-Regelparameter-Snapshots.

Damit entsteht ein kleiner deterministischer Fachlauf fuer eine oder mehrere explizite Perioden:

1. Szenario laden
2. BAV-Fremdinformationen aus Vorperiodenwerten berechnen
3. explizite VU-Regelparameter-Snapshots anwenden
4. einen einfachen Aggregat-Snapshot zurueckgeben

## Ursprung im Altcode

Der fachliche Bezug bleibt eng:

- `legacy_c/IMS.E`: `Vrvu07`, `Vrvu08`, `Vrvu09`
- bereits portierte BAV-Frmdinf-Vektoren fuer Versicherer
- bereits portierter linearer VU-Frmdinf-Rechenkern

Dieser Schritt portiert keine neue historische Regelentscheidung. Er haengt nur die schon portierten Bausteine in einer kontrollierten Reihenfolge zusammen.

## Python-Abbildung

Der neue Einstieg liegt in `python_port/ims/engine/vu_rule_runner.py`.

Ergaenzt wurden:

- `VUForeignInfoPeriodRunResult`
- `VUForeignInfoCarryover`
- `VUForeignInfoMultiPeriodRunResult`
- `run_loaded_vu_foreign_info_period`
- `run_vu_foreign_info_period_from_mapping`
- `run_vu_foreign_info_period_from_fixture`
- `run_vu_foreign_info_multi_period_from_mappings`
- `run_vu_foreign_info_multi_period_from_fixture`

Der Runner nutzt:

- `compute_extended_foreign_info`
- `apply_vu_foreign_info_rule_snapshots`
- `apply_vu_reserve_markup_rule_snapshots`
- `apply_vu_net_switcher_markup_rule_snapshots`
- `apply_vu_expected_claim_rule_snapshots`
- `apply_vu_market_share_markup_rule_snapshots`
- `collect_basic_aggregates`

Der Mehrperiodenpfad verarbeitet eine Liste expliziter Periodenszenarien oder ein Fixture mit dem Feld `periods`. Die Periodennummern muessen eindeutig und streng steigend sein. Das ist eine Reproduzierbarkeitspruefung, keine historische Ablaufherleitung.

Optional kann `carry_forward_insurer_state=True` gesetzt werden. Dann schreibt der Runner fuer Versicherer, die in zwei aufeinanderfolgenden Periodenszenarien dieselbe `entity_id` haben, die berechneten aktuellen VU-Werte der Vorperiode kontrolliert in die Vorperioden- und Startwerte der naechsten Periode:

- Praemienvektor
- Werbevektor
- Reservenvektor
- Vorperiodenaktivitaet

Dieser Carryover ist bewusst eng und diagnostiziert die betroffenen Versicherer ueber `VUForeignInfoCarryover`.

Zusaetzlich kann ein Szenario explizite `vu_reserve_markup_rule_snapshots` enthalten. Diese Snapshots
bilden den portierten `Vrvu03`-/Mark-Up-I-Regelkern ab und werden nach den Frmdinf-Snapshots
angewendet. Die Details und Grenzen stehen in `vu_markup_reserve_rule.md`.

Explizite `vu_net_switcher_markup_rule_snapshots` bilden den portierten `Vrvu04`-/Mark-Up-II-
Regelkern ab. Sie werden nach den Mark-Up-I-Snapshots angewendet und benoetigen die
Versicherungsnehmerzahlen der zweiten Vorperiode explizit im Snapshot. Details und Grenzen stehen
in `vu_net_switcher_markup_rule.md`.

Explizite `vu_expected_claim_rule_snapshots` bilden den portierten `Vrvu06`-/Erwartungsschaden-
Regelkern ab. Sie werden nach den Frmdinf- und Mark-Up-I-Snapshots angewendet. Details und Grenzen
stehen in `vu_expected_claim_rule.md`.

Explizite `vu_market_share_markup_rule_snapshots` bilden den portierten `Vrvu05`-/Mark-Up-III-
Regelkern ab. Sie werden nach den Frmdinf-, Mark-Up-I- und Erwartungsschaden-Snapshots angewendet.
Details und Grenzen stehen in `vu_market_share_markup_rule.md`.

## Validierung

Die Tests pruefen:

- BAV-Frmdinf wird vor der VU-Regelanwendung berechnet
- Durchschnitts- und Angriffs-Snapshots greifen auf die passenden Frmdinf-Vektoren zu
- Zielversicherer werden aktualisiert
- Diagnoseobjekte halten die angewendeten Regeln fest
- Szenarioausfuehrung funktioniert aus Mapping und Fixture-Datei
- Mehrperioden-Fixtures funktionieren als Liste und als Objekt mit `periods`
- doppelte oder unsortierte Perioden werden abgelehnt
- optionaler Carryover schreibt passende Versichererwerte in die Folgeperiode
- nicht passende Versicherer werden beim Carryover ignoriert
- explizite Vrvu03-/Mark-Up-I-Snapshots koennen im Periodenrunner angewendet werden
- explizite Vrvu04-/Mark-Up-II-Snapshots koennen im Periodenrunner angewendet werden
- explizite Vrvu06-/Erwartungsschaden-Snapshots koennen im Periodenrunner angewendet werden
- explizite Vrvu05-/Mark-Up-III-Snapshots koennen im Periodenrunner angewendet werden
- doppelte Snapshot-Ziele werden abgelehnt
- ein Szenario ohne Snapshots bleibt gueltig und berechnet nur BAV-Frmdinf

## Grenzen

Bewusst nicht enthalten sind:

- kein historischer Scheduler-Anschluss
- keine automatische Auswahl von VU-Regelarten
- keine breite automatische Zustandsfortschreibung zwischen Perioden
- kein Carryover fuer VN-Zustand, Vertraege, Schaeden oder Marktmechanik
- keine Parameterherleitung aus historischen Tabellen
- keine VN-Regelportierung
- keine Vollsimulation
- keine Aussage ueber historische Vollgleichheit

## Naechster sinnvoller Schritt

Der naechste fachliche Schritt kann entweder einen weiteren eng abgegrenzten VU-/VN-Regelteil portieren oder den Carryover schrittweise auf klar belegte weitere Zustandsfelder ausweiten.
