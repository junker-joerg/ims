# IMS 2.x: Strategiekatalog und Taxonomie

Stand: 2026-09-02
Vertrag: `ims.strategy-catalog.v1`

## Einordnung

Der Katalog verbindet die historischen Verhaltensregeln mit ihren bereits
portierten expliziten Python-Rechenkernen. Er ist Metadatenvertrag, nicht
Ausfuehrungslogik. Die moderne Familie beschreibt, wie Regeln spaeter in der
Workbench auffindbar und in Analysen gruppierbar werden koennen.

Historische Regelklasse und moderne Familie sind verschiedene Dinge:

- Die Regelklasse stammt aus der Vdefmd6-Population und bleibt unveraendert.
- Die moderne Familie ist eine neue, als `taxonomy_only` markierte Sicht.
- `Vrvu10` ist historisch in `IMS.E` vorhanden, aber nicht Teil von Vdefmd6.

## VU-Regeln

| ID | Historische Regel | Vdefmd6-Klasse | Moderne Familie | Python-Einstieg | Teststatus |
| --- | --- | ---: | --- | --- | --- |
| `vu.vrvu01` | Zufall I | 1 | Zufallsbasiert | `apply_vu_random_uniform_rule` | Unit + Regression |
| `vu.vrvu02` | Zufall II | 1 | Zufallsbasiert | `apply_vu_random_normal_rule` | Unit |
| `vu.vrvu03` | Mark-Up I | 2 | Erfahrungs-Mark-Up | `apply_vu_reserve_markup_rule` | Unit |
| `vu.vrvu04` | Mark-Up II | 2 | Erfahrungs-Mark-Up | `apply_vu_net_switcher_markup_rule` | Unit + Regression |
| `vu.vrvu05` | Mark-Up III | 2 | Erfahrungs-Mark-Up | `apply_vu_market_share_markup_rule` | Unit |
| `vu.vrvu06` | Erwartungsschaden | 2 | Schadenorientiert | `apply_vu_expected_claim_rule` | Unit |
| `vu.vrvu07` | Dumping | 3 | Marktinformation | `apply_vu_foreign_info_rule` | Unit |
| `vu.vrvu08` | Durchschnitt | 3 | Marktinformation | `apply_vu_foreign_info_rule` | Unit + Regression |
| `vu.vrvu09` | Angriff | 3 | Marktinformation | `apply_vu_foreign_info_rule` | Unit |
| `vu.vrvu10` | Frei definierbar | - | Freie Definition | `apply_vu_free_linear_rule` | Unit |

Die drei Fremdinformationsregeln teilen sich im Python-Port einen Rechenkern,
bleiben aber durch die Varianten `dumping`, `average` und `attack` als
historische Einzelregeln identifizierbar.

## VN-Regeln

| ID | Historische Regel | Vdefmd6-Klasse | Moderne Familie | Python-Einstieg | Teststatus |
| --- | --- | ---: | --- | --- | --- |
| `vn.vrvn01` | Zufall I / Pflichtversicherung | 1 | Pflicht und Zufall | `apply_vn_compulsory_insurance_rule` | Unit + Regression |
| `vn.vrvn02` | Zufall II | 1 | Pflicht und Zufall | `apply_vn_random_insurance_rule` | Unit + Regression |
| `vn.vrvn03` | Praeferenz | 2 | Praeferenz und Erfahrung | `apply_vn_preference_insurance_rule` | Unit + Regression |
| `vn.vrvn04` | Totale Erinnerung | 2 | Praeferenz und Erfahrung | `apply_vn_search_insurance_rule` | Unit + Regression |
| `vn.vrvn05` | Suche | 3 | Marktsuche | `apply_vn_sample_search_insurance_rule` | Unit + Regression |
| `vn.vrvn06` | Beste Information | 3 | Marktsuche | `apply_vn_best_info_insurance_rule` | Unit + Regression |

## Parameterfaehigkeit

Der Katalog beschreibt nur vorhandene, explizite Eingaben. Er macht keine
Parameter neu wirksam. Ausgewiesen werden unter anderem:

- getrennte Werte fuer die zwei historischen Sparten;
- Normal- und Aenderungsschockzweige;
- explizite Zufallsziehungen;
- Reserve-, Wechsler-, Marktanteils- und Schadenschwellen;
- Praeferenz, eigene Praemienhistorie, Stichprobengroesse und
  Informationskosten;
- Markt- und Fremdinformationen.

`Vrvn01` besitzt in der heutigen Portierung keinen eigenen strategischen
Parameterblock. Die explizite Versichererauswahl per Draw ist ein
reproduzierbarer Eingang, aber noch keine frei parametrisierbare Strategie.

## Technischer Vertrag

`python_port/ims/strategies/catalog.py` stellt bereit:

- `STRATEGY_FAMILIES` und `STRATEGY_DEFINITIONS`;
- Filterung nach Akteur oder Familie;
- Lookup ueber stabile Strategie-ID;
- eine I/O-freie Integritaetspruefung;
- ein JSON-serialisierbares read-only Payload, das PR105 ueber
  `GET /api/strategies/catalog` in der Workbench anzeigt.

Das Payload traegt ausdruecklich
`historical_full_equality_claim = false`. Es startet weder Regelkern noch
Runner und veraendert keine Population.

## Bedeutung fuer die Regulierungssimulation

Baseline und Intervention koennen spaeter nur sauber verglichen werden, wenn
die eingesetzte VU-/VN-Regel eindeutig und versioniert benannt ist. PR104
liefert diese Identitaets- und Gruppierungsgrenze. Regulatorische Eingriffe,
Strategiewechsel, Bilanzwirkungen und neue Sparten benoetigen weiterhin eigene
Vertraege und Tests.

## Offene Grenze

Die vorhandenen Tests belegen die expliziten Rechenkerne und ausgewaehlte
mehrperiodige Regressionen. Sie belegen keine vollstaendige Gleichheit mit
historischen stochastischen Laeufen und noch keine fachliche Eignung einer
Regel fuer eine konkrete moderne Regulierung.
