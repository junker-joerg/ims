# IMS 2.x: Strategiezuordnung und Parameterformen

Stand: 2026-09-02
Vertrag: `ims.strategy-assignment-contract.v1`
API: `GET /api/strategies/assignment-contract`

## Einordnung

PR106 verbindet den Strategiekatalog mit den bereits vorhandenen
Akteursfeldern, Parameter-Dataclasses und der belegten Modellkonfiguration
`Vdefmd6`. Der Vertrag beschreibt nur, was heute vorhanden und zuordenbar
ist. Er ist weder Szenariokonfiguration noch Ausfuehrungsplan.

## C-zu-Python-Mapping

| Historischer Ursprung | Python-Ziel | Bedeutung |
| --- | --- | --- |
| `IMSDATA.C`, `ACTION.st` | `Insurer.rule_id`, `Policyholder.rule_id` | eine historische Regelnummer je Akteur |
| `IMSDATA.C`, `vkrvu` und `vkrvn` | `historical_rule_class` | abgeleitete historische Regelklasse, keine editierbare Strategie |
| `IMS.E`, `Vuauini` und `Vnauini` | `vdefmd6_population.py` | Akteursgruppen, Aktivierung und 16 Quellparameter |
| `IMS.E`, `Vdefmd6` | `build_vdefmd6_strategy_assignment_profiles()` | achtzehn zusammenhaengende Quellprofile |
| vorhandene `*RuleParameters` | `STRATEGY_PARAMETER_SCHEMAS` | dreizehn reale Dataclass-Schemata |
| vorhandene `*_parameters_from_mapping` | Feldvertrag `existing_validation` | heutige Loadergrenzen ohne neue Wertebereiche |

## Zuordnungsgrenze

Der heutige Vertrag kennt zwei Zieltypen:

| Akteur | Zielobjekt | Zulaessige Strategien | Granularitaet |
| --- | --- | ---: | --- |
| VU | `ims.model.entities.Insurer` | `vu.vrvu01` bis `vu.vrvu10` | hoechstens eine Strategie je VU |
| VN | `ims.model.entities.Policyholder` | `vn.vrvn01` bis `vn.vrvn06` | hoechstens eine Strategie je VN |

Die historische Regelklasse bleibt eine aus der Regelnummer abgeleitete
Aggregat- und Analyseinformation. Sie ist kein eigenstaendiges
Zuordnungsziel. `Vrvu10` ist fuer den Akteurstyp VU katalogisiert, kommt aber
in den `Vdefmd6`-Quellprofilen nicht vor.

## Vdefmd6-Quellprofile

| Akteur | IDs | Strategie | Aktivierung |
| --- | --- | --- | ---: |
| VU | 1-2 | `vu.vrvu01` | 1 |
| VU | 3-4 | `vu.vrvu02` | 1 |
| VU | 5-7 | `vu.vrvu03` | 1 |
| VU | 8-10 | `vu.vrvu04` | 1 |
| VU | 11-13 | `vu.vrvu05` | 1 |
| VU | 14 | `vu.vrvu06` | 1 |
| VU | 15-16 | `vu.vrvu06` | 1 |
| VU | 17-19 | `vu.vrvu07` | 1 |
| VU | 20-22 | `vu.vrvu08` | 1 |
| VU | 23-25 | `vu.vrvu09` | 1 |
| VN | 1-15 | `vn.vrvn01` | 1 |
| VN | 16-30 | `vn.vrvn02` | 1 |
| VN | 31-60 | `vn.vrvn03` | 1 |
| VN | 61-90 | `vn.vrvn04` | 1 |
| VN | 91-120 | `vn.vrvn05` | 1 |
| VN | 121-150 | `vn.vrvn06` | 1 |
| VN | 151-190 | `vn.vrvn03` | 50 |
| VN | 191-200 | `vn.vrvn02` | 50 |

VU14 und VU15-16 verwenden dieselbe Regel, aber unterschiedliche belegte
Parameterprofile. Deshalb bleiben sie getrennte Quellprofile. Die
ausfuehrbaren Schleifen des Altmodells belegen VN151-190 und VN191-200; der
bekannte abweichende Bildschirmtext wird nicht als Zuordnungsquelle benutzt.

## Parameterschemata

Zehn VU-Regeln und die VN-Regeln 2-6 besitzen vorhandene
Strategieparameter-Dataclasses. Die VU-Regeln 7-9 teilen sich das Schema
`VUForeignInfoRuleParameters`, behalten aber ihre Variantenidentitaet.
`Vrvn01` besitzt keinen eigenen Strategieparameterblock; seine expliziten
Versichererwahl-Draws sind Laufeingaben und keine editierbaren
Strategieparameter.

Alle Felder sind heute Zweiervektoren fuer die zwei historischen
Sektorpositionen. Die Schemata umfassen:

- Praemien- und Werbeabschnitte beziehungsweise Faktoren;
- Faktoren ober- und unterhalb vorhandener Anspruchsniveaus;
- VN-Versicherungsschwellen;
- Stichprobengroessen der VN-Suchregel.

Die vorhandenen Loader normalisieren numerische Zweiervektoren. Nur die
Stichprobengroessen besitzen bereits eine ausdrueckliche Nichtnegativpruefung.
PR106 erfindet keine weiteren Wertebereiche. Insbesondere sind die 16
historischen VN-Quellwerte nicht vollstaendig Strategieparameter: Die ersten
acht Positionen speisen den separaten Schadenparameterblock.

## Sektorgrenze

`legacy_sector_1` und `legacy_sector_2` sind Positionsbezeichner, keine
fachlichen Spartennamen. Eine spaetere Abbildung auf Kfz und
Sach-Haftpflicht sowie eine Erweiterung um Leben oder Kranken benoetigen
eigene Sparten-, Zustands- und Regelvertraege. Der heutige Vertrag erlaubt
weder unterschiedliche Strategien je Position noch mehr als zwei Positionen.

## Read-only- und Ausfuehrungsgrenze

Das Payload setzt Auswahl, Zuordnungsbearbeitung, Parameterbearbeitung,
Gruppenbearbeitung, sektorweise Strategie, geplante Strategiewechsel,
Schreiben und Ausfuehrung auf `false`. Es fuehrt keinen Regelkern aus, startet
keinen Runner und keine Simulation. Parameterwerte werden nicht ausgegeben;
Fingerabdruecke dienen nur der Identitaet vorhandener Quellprofile.

Die API besitzt nur eine GET-Route. `POST`, `PUT` und `DELETE` werden
abgewiesen. Der Vertrag behauptet keine historische Vollgleichheit.

## Anschluss

PR107 kann diese Informationen in der Workbench lesbar machen. Ein danach
moegliches Entwurfsformat muss Strategie-ID, Ziel-ID, Gueltigkeit und
Parameterwerte versionieren und zunaechst ohne Ausfuehrung validieren.
