# IMS 2.x: Strategie- und Parameterplan je Sparte

Stand: 2026-09-16
Entwurf: `ims.sector-strategy-plan.v1`
Validierung: `ims.sector-strategy-plan-validation.v1`

## Wofuer der Vertrag dient

Ein Plan kann fuer VU und VN der bekannten Vdefmd6-Population unterschiedliche
Katalogstrategien je **benannter** Nichtleben-Sparte und Periode vorsehen.
Parameterwerte sind dabei skalar: ein Wert fuer die jeweils bezeichnete
Sparte. Das ist ein Entwurf fuer IMS 2.x, noch keine wirksame Laufkonfiguration.

Die positive, synthetische Beispielstruktur liegt unter
`tests/fixtures/sector_strategy_plan_v1.json`. Sie zeigt fuer denselben
Versicherer eine andere Strategie in Kfz als in Sach-Haftpflicht. Die Werte
sind Testdaten, keine fachliche Empfehlung.

## Historischer Ursprung und neue Grenze

| Ursprung | Bestehender Python-Port | PR154 |
| --- | --- | --- |
| `IMSDATA.C`: `classVU.Vr/Pv/Ac` und `classVN.Vr/Pv/Ac` je Akteur | eine Katalogstrategie je Akteur im bisherigen Entwurf | geplanter Strategiewechsel je Akteur, Ziel-Sparte und inklusivem Periodenfenster |
| `IMSDATA.C`: VU `Sp[1/2]`, VN `Rk[1/2]` | Parameter als historische Zweiervektoren | skalare Parameter je benannter Ziel-Sparte, **nicht** in den Altvektor geschrieben |
| `ims.strategies.catalog` und `assignment_contract` | bestehende VU-/VN-Regel- und Parameterschema-IDs | dieselben IDs und Feldtypen zur strukturellen Validierung |

Historisch ist `Vr` ein einzelnes Regelfeld je Akteur. Der Altcode belegt
**keine** unterschiedliche Regel je Sparte. Auch PR153 bindet seine neutralen
IDs `legacy.damage_1/2` nicht an Kfz oder Sach-Haftpflicht. Deshalb
materialisiert PR154 keine alten Snapshots und startet keinen Runner.

## Format und Pruefung

Der Dokumentkopf bindet Versionen von Spartentaxonomie und Strategiekatalog,
die Vdefmd6-Akteurspopulation und `historical_mapping_status = unresolved`.
Jeder Eintrag nennt `actor_type`, `target_id`, `sector_id`, `strategy_id`,
`period_from`, `period_through`, `parameter_schema` und `parameter_values`.

- `motor` und `property_liability` sind **Planungsziele**, keine historisch
  nachgewiesenen Namen fuer `Sp[1/2]` oder `Rk[1/2]`.
- `life` und `health` sind bereits Taxonomie-IDs, haben aber noch keine
  zulaessige Strategie aus dem heutigen Schadenregel-Katalog.
- VU-IDs sind auf 1-25 und VN-IDs auf 1-200 der Vdefmd6-Population begrenzt.
- Zeitfenster sind inklusiv und liegen innerhalb der Perioden 1-100.
  Fenster desselben Akteurs und derselben Sparte duerfen nicht ueberlappen;
  Luecken sind in einem Teilentwurf erlaubt.
- `parameter_schema` muss exakt zum Katalogeintrag passen. Alle deklarierten
  Parameterfelder sind erforderlich, weitere Felder nicht erlaubt. Werte
  sind endliche Zahlen; historische Stichprobengroessen sind nichtnegative
  Ganzzahlen. Parameterlose Regeln verlangen zweimal `null`.

Die Validierung ist atomar: Ein ungueltiger Plan meldet Fehlerpfade,
akzeptiert aber **keine** seiner Zuordnungen teilweise.

`GET /api/strategies/sector-plan-contract` beschreibt die Form und Grenzen.
`POST /api/strategies/sector-plan-validation` prueft JSON ausschliesslich
im Speicher. Fachlich ungueltige Plaene erhalten HTTP 200 mit
`valid = false`; unlesbares JSON HTTP 400. Es gibt keine Speicherung,
Snapshot-Erzeugung, Ausfuehrung oder Simulation.

## Offen

Die Akteursregel im bisherigen Kern wird nicht je Sparte umgestellt.
Weder per-Sparte-Ziehungen und Marktinformationen noch die Wirkung eines
Zeitfensterwechsels sind hier festgelegt. Dafuer braucht es spaeter einen
eigenen fachlichen Laufzeitvertrag und deterministische Falltests.
Leben und Kranken benoetigen eigene Strategie- und Zustandsmodelle.
Eine historische Vollgleichheit wird nicht behauptet.
