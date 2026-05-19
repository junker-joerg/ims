# VU-Frmdinf-Periodenschritt

## Ziel

Dieser Schritt verbindet den portierten BAV-Frmdinf-Kern mit den expliziten VU-Frmdinf-Regelparameter-Snapshots.

Damit entsteht ein kleiner deterministischer Fachlauf:

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
- `run_loaded_vu_foreign_info_period`
- `run_vu_foreign_info_period_from_mapping`
- `run_vu_foreign_info_period_from_fixture`

Der Runner nutzt:

- `compute_extended_foreign_info`
- `apply_vu_foreign_info_rule_snapshots`
- `collect_basic_aggregates`

## Validierung

Die Tests pruefen:

- BAV-Frmdinf wird vor der VU-Regelanwendung berechnet
- Durchschnitts- und Angriffs-Snapshots greifen auf die passenden Frmdinf-Vektoren zu
- Zielversicherer werden aktualisiert
- Diagnoseobjekte halten die angewendeten Regeln fest
- Szenarioausfuehrung funktioniert aus Mapping und Fixture-Datei
- doppelte Snapshot-Ziele werden abgelehnt
- ein Szenario ohne Snapshots bleibt gueltig und berechnet nur BAV-Frmdinf

## Grenzen

Bewusst nicht enthalten sind:

- kein historischer Scheduler-Anschluss
- keine automatische Auswahl von VU-Regelarten
- keine Parameterherleitung aus historischen Tabellen
- keine VN-Regelportierung
- keine Vollsimulation
- keine Aussage ueber historische Vollgleichheit

## Naechster sinnvoller Schritt

Der naechste fachliche Schritt kann entweder einen weiteren eng abgegrenzten VU-/VN-Regelteil portieren oder diesen kleinen Periodenschritt in einen mehrperiodigen Fachlauf mit expliziten Snapshots einbetten.
