# Periodenplan-Eingabevalidierung

## Ziel

Die Periodenplan-Adapter weisen ungueltige Entity-Update-Felder jetzt
kontrolliert als Validierungsfehler zurueck. Dadurch bleibt der Vertrag der
Plan-Lader stabil: fehlerhafte Nutzereingaben fuehren zu `ValueError` statt zu
rohen Python-Typfehlern.

## Ursprung im Altcode

Dieser Slice portiert keine weitere C-Funktion. Er schuetzt die expliziten
Python-Eingaben fuer bereits portierte VU-/VN-Kernlogik, deren fachlicher
Anschluss in den `Vrvu*`-Slices sowie `Vrvn01` bis `Vrvn03` dokumentiert ist.

## Python-Abbildung

Betroffen sind die vorhandenen Plan-Lader:

- `ims.engine.replay_plan`
- `ims.engine.vn_agrsich_replay_plan`
- `ims.engine.explicit_period_plan`

Alle drei pruefen `insurers` und `policyholders` in Periodenupdates explizit als
Listen, bevor sie die Daten weiterverarbeiten.

## Annahmen und Grenzen

- Fehlende Felder bleiben erlaubt und bedeuten eine leere Update-Liste.
- Nichtlisten sind ungueltig, auch `null`.
- Die eigentliche Fachlogik, Carryover-Semantik und Exportlogik bleiben
  unveraendert.
