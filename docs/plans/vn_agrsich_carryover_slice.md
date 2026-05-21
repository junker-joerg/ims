# Plan: VN-Agrsich-Replay mit Carryover

## Ziel

Binde den bereits portierten optionalen VN-State-Carryover an den
VN-Agrsich-Replay-Pfad an. Explizite VN-Mehrperiodenlaeufe koennen dadurch
nach jedem Periodenschritt Agrsich-Exports aus dem fortgeschriebenen Zustand
schreiben.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`
- historische VN-Agrsich-Ausgaben wie `IMSVNR*.DAT` und `IMSVNSK1.DAT`

## Umsetzung

1. VN-State-Carryover als wiederverwendbaren Engine-Baustein oeffnen.
2. `VNAgrsichReplayRunResult` um Carryover-Diagnose erweitern.
3. `run_vn_agrsich_replay_from_mappings(..., carry_forward_vn_state=True)` und
   Fixture-Feld `carry_forward_vn_state` ergaenzen.
4. Fixture-Flag strikt als Boolean validieren.
5. Tests fuer Exportwirkung und Fixture-Validierung ergaenzen.

## Grenzen

- Carryover bleibt standardmaessig deaktiviert.
- Keine VN-Wahl-, Praeferenz-, RNG- oder Schedulerlogik.
- Keine Erzeugung fehlender Folgeentitaeten.
- Keine Behauptung historischer Vollgleichheit.
