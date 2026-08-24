# Technische Level-IV-Selektorkanonisierung

## Ziel

PR 61 schliesst eine rein technische Metadatengrenze im berechneten
Legacy-Vergleich. Laufzeitexporte der Aggregatstufe IV verwenden
`selector_kind = "all"` und `selector_value = "all"`. Das historische
Validierungsbundle bezeichnet dasselbe unterstuetzte SK1-Gesamtaggregat mit
`selector_kind = "all"` und `selector_value = "SK1"`.

Die beiden belegten Werte werden nur fuer die Exportidentitaet des
Legacy-Vergleichs kanonisiert. Exporttabellen, Aggregatbildung und historische
Zielmetadaten werden nicht umgeschrieben.

## Ursprung und Mapping

| Ursprung | Python-Ziel | Bedeutung |
| --- | --- | --- |
| Level-IV-Aggregatkey `all` aus der bestehenden Agrsich-Aggregation | `python_port/ims/model/agrsich_export.py` | Laufzeitmetadatum des Gesamtaggregats |
| Historischer Bundlewert `all = SK1` fuer `IMSVUSK1` und `IMSVNSK1` | `tests/fixtures/legacy_validation_bundle.json` | belegte historische Bezeichnung desselben Gesamtaggregats |
| Technische Vergleichsidentitaet | `python_port/ims/model/legacy_export_identity.py` | kanonisiert ausschliesslich diese beiden Werte auf `SK1` |
| Berechneter Vergleich, Abweichungsdiagnose und expliziter Adapter | `legacy_calculated_comparison.py`, `legacy_calculated_deviation_report.py`, `explicit_legacy_deviation_adapter.py` | verwenden dieselbe kanonische Identitaet |

Es wird keine neue C-Fachlogik portiert. Die Aenderung betrifft nur die
Zuordnung bereits vorhandener Exportmetadaten zu bereits dokumentierten
historischen Zielen.

## Enge Grenze

Eine Kanonisierung findet nur statt, wenn alle drei Bedingungen exakt gelten:

- `level == "IV"`;
- `selector_kind == "all"`;
- `selector_value` ist exakt `"all"` oder `"SK1"`.

Andere Stufen, Selektorarten, Werte und Schreibweisen bleiben verschieden.
Insbesondere werden `ALL`, `sk1`, numerische Werte oder Level III nicht
stillschweigend akzeptiert.

Die rohe Laufzeittabelle behaelt `selector_value = "all"`. Die kanonische
Identitaet dient nur Gruppierung, Auswahl und Vergleich; ihr Wert ist `SK1`.

## VUSK1-Zeitfenster

`VUSK1L1.DAT` bis `VUSK1L5.DAT` bleiben die fuenf aufeinanderfolgenden
Zeitfenster desselben `SK1`-/`all`-Aggregats auf der unterstuetzten
Aggregatstufe IV. Die Kanonisierung erzeugt weder neue Aggregatebenen noch
unterschiedliche SK1-Aggregate.

## Validierung und Grenzen

Die Tests belegen:

- die positive `all`-/`SK1`-Zuordnung fuer Level IV;
- die strikte Ablehnung aehnlicher Werte ausserhalb der engen Grenze;
- den berechneten Vergleich ueber beide Metadatenbezeichnungen;
- die Auswahl einer rohen Level-IV-Laufzeittabelle durch den PR-60-Adapter.

Es wurde keine Vollsimulation gestartet. Die Tests verwenden kontrollierte
Vertragsdaten beziehungsweise den vorhandenen expliziten Periodenpfad. Aus der
technischen Identitaetszuordnung folgt keine historische Vollgleichheit und
kein Nachweis einer unabhaengigen historischen Zustandsentwicklung.

## Naechster Schritt

PR 62 hat den kontrollierten read-only Run-Control-Freigabecheck fuer den
lokalen Adapter umgesetzt. PR 63 bereitet die atomare Backend-Start-/Status-
und Ergebnisgrenze vor. Freier Browser-Upload und unbegrenzte Simulation
bleiben gesperrt.
