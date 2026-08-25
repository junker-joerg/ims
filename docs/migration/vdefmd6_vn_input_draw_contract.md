# Vdefmd6-VN-Eingabe- und Draw-Vertrag

## Ziel und Ursprung

Der Vertrag `pr77-v1` verbindet die historischen Regelbloecke `Vrvn01` bis
`Vrvn06` in `IMS.E` mit den bereits vorhandenen Python-Oberflaechen in
`vn_insurance_rules.py`, `vn_damage_rules.py`, `vn_rules.py` und
`vn_rule_runner.py`. Er kartiert Herkunft und Grenzen; er fuehrt keine Regel
aus und fuegt keine Fachlogik hinzu.

## Population und Regeln

In den Perioden 1-49 sind 150 VN aktiv:

| Regel | Python-Art | Aktive VN | Zusaetzlicher Bestand ab 50 |
| --- | --- | ---: | ---: |
| `Vrvn01` | `compulsory` | 15 | 0 |
| `Vrvn02` | `random` | 15 | 10 |
| `Vrvn03` | `preference` | 30 | 40 |
| `Vrvn04` | `search_history` | 30 | 0 |
| `Vrvn05` | `sample_search` | 30 | 0 |
| `Vrvn06` | `best_info` | 30 | 0 |

Die regelabhaengigen Eingaben sind im Fixture
`tests/fixtures/vdefmd6_vn_input_draw_contract.json` einzeln festgehalten. Dazu
gehoeren aktive Versicherer, Startentscheidungen, Schwellen, Werbung,
Praemien, Suchhistorie, BAV-Schadenindikator, Informationskosten und die je
Regel erforderlichen expliziten Wahldraws.

## Gemeinsamer Schaden- und Settlement-Pfad

Alle sechs historischen Regeln enthalten dieselbe Form je Sparte:

```c
s1 = (sw1 > normal()) * (a0 + b0 * normal());
s2 = (sw2 > normal()) * (c0 + d0 * normal());
```

Der Vertrag bindet dazu Parameter, aktuelle `Sw`-Schwellen, vier explizite
Normalwerte und den Vorschockstatus. `IMSRND.C` bildet jeden historischen
`normal()`-Wert aus zwoelf `myrndf()`-Ziehungen. Damit sind pro aktivem VN
mindestens 48 und pro Vorschockperiode 7.200 uniforme Basisziehungen allein
fuer den Schaden belegt. Regelabhaengige Wahlziehungen und deren
Wiederholungsschleifen kommen danach hinzu.

Das Settlement schreibt anschliessend je Sparte Versichererreserven,
Schadensumme, Schadenanzahl und Versichertenzahl sowie VN-Versicherer,
Versicherungsstatus, Praemie, Eigen- und Gesamtschaden. Zuletzt wird das
VN-Vermoegen fortgeschrieben.

## Belegte Reihenfolge und offene Grenze

Auf Ebene der C-Anweisungen ist belegt:

1. Schaden Sparte 1;
2. Schaden Sparte 2;
3. Versicherungsentscheidung;
4. Settlement Sparte 1;
5. Settlement Sparte 2;
6. Vermoegensfortschreibung.

Innerhalb einer Schadenformel ist die Reihenfolge der beiden `normal()`-
Funktionsaufrufe wegen der C-Auswertung der Multiplikationsoperanden nicht festgelegt.
Der Python-Port verwendet explizit Trigger und Hoehe fuer Sparte 1,
danach Trigger und Hoehe fuer Sparte 2. Diese moderne Reihenfolge ist
reproduzierbar, aber kein historischer Reihenfolgenachweis.

Ausserdem ist die historische Reihenfolge mehrerer VN im selben logischen
Aktionsslot weiterhin offen. Der PR-75-Vertrag enthaelt nur eine
Darstellungsordnung.

## Runner-Anschluss

Der heutige explizite Runner verarbeitet zuerst
`VNInsuranceRuleSnapshot`, danach `VNDamageSettlementSnapshot`. Das ist fuer
bereits materialisierte Draws und Entscheidungen deterministisch, entspricht
aber nicht automatisch der historischen Zufallsverbrauchsfolge. PR 78 muss
deshalb die Vdefmd6-Snapshotableitung und eine explizite moderne Drawfolge vor
dem Runner bereitstellen. PR 77 markiert den Pfad nur als kartiert:

- `mapping_ready = true`;
- `policyholder_claim_path_mapped = true`;
- `settlement_write_path_mapped = true`;
- `historical_draw_order_fully_bound = false`;
- `independent_periods_2_49_ready = false`;
- `generation_ready = false`.

Die Kartierung ist kein Herkunftsnachweis fuer einen bereits erzeugten
Vollzustand. Es wurden keine Legacy-Ausgaben als Eingabe verwendet, keine
Draws gezogen, kein Runner und keine Simulation gestartet.
Es gibt keine historische Vollgleichheitsbehauptung.
