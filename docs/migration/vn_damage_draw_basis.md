# VN-Schadendraw-Basis

Dieser Slice verbindet den portierten VN-Schadenerzeugungskern mit der
reproduzierbaren Python-RNG-Basis. Explizite `draws` in
`vn_damage_settlement_snapshots` bleiben gueltig; wenn sie fehlen, erzeugt der
VN-Periodenrunner die benoetigten Normalziehungen aus `SimulationContext`.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`

Die historische Formel nutzt pro Sparte zwei Normalziehungen: eine fuer den
Schadeneintritt und eine fuer die Schadenhoehe.

## Python-Abbildung

- `python_port/ims/model/vn_rules.py`
  - `VNDamageSettlementSnapshot.draws` ist optional.
  - `apply_vn_damage_settlement_snapshot` akzeptiert bei fehlenden Draws eine
    explizite Draw-Quelle.
- `python_port/ims/engine/vn_rule_runner.py`
  - fehlende Draws werden ueber `ensure_context_rng` und
    `rand_normal_standard` erzeugt.
  - die Ziehungsreihenfolge ist Trigger Sparte 0, Hoehe Sparte 0, Trigger
    Sparte 1, Hoehe Sparte 1.
  - Mehrperiodenlaeufe verwenden fuer fehlende Draws einen gemeinsamen
    RNG-Strom, wenn alle geladenen Perioden denselben `rng_seed` tragen.
    Dadurch starten solche Szenarien nicht in jeder Periode wieder bei
    derselben Normalfolge.
  - Wenn Periodenkontexte unterschiedliche `rng_seed`-Werte tragen, bleibt der
    jeweilige Perioden-Seed erhalten und die fehlenden Draws werden aus dem
    lokalen Periodenkontext erzeugt.

## Validierung

Die Tests decken ab:

- Laden von VN-Schaden-/Abrechnungs-Snapshots ohne explizite Draws.
- Direkte Anwendung mit expliziter Draw-Quelle.
- Runner-Anwendung mit reproduzierbaren Draws aus `rng_seed`.
- Mehrperioden-Runner mit fortlaufendem Draw-Strom ueber Periodengrenzen bei
  gleichem Seed.
- Mehrperioden-Runner mit periodenspezifischen Draws bei unterschiedlichen
  Seeds.

## Grenzen

- Keine historische RNG-Kompatibilitaet wird behauptet.
- Die VN-Wahl-, Praeferenz- und Pflichtversicherungspfade bleiben weiterhin
  explizite Eingaben oder spaetere Migrationsschritte.
- Der reine Schadenskern in `vn_damage_rules.py` bleibt ohne versteckte
  RNG-Nutzung.
