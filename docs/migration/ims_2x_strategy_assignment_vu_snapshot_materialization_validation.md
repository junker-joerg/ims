# PR119: VU-Materialisierungseingang pruefen

Stand: PR119, 2026-09-07

## Ergebnis

PR119 fuehrt einen versionierten VU-Eingang und eine zustandslose,
atomare Validierung fuer alle zehn katalogisierten VU-Strategien ein. Der
Eingang kapselt einen unveraenderten PR108-Entwurf und PR112-Kontext und
deklariert zusaetzlich drei feste Herkunftsrichtlinien.

Der Bericht beantwortet nur, ob die gelieferten offenen Snapshotwerte nach
diesen Richtlinien vollstaendig und streng genug sind. Er erzeugt keinen
Snapshot und gibt keine Ausfuehrung frei.

## Schwellenwertquelle

Die drei Mark-Up-Regeln lesen ihre Anspruchsniveaus im Altcode direkt aus dem
Ziel-VU:

| Feld | `IMS.E` | Python-Entsprechung |
| --- | --- | --- |
| `reserve_thresholds` | `A1[1]`, `A2[1]` in `Vrvu03` | Position 0 von `aspiration_sector_1/2` |
| `net_switcher_thresholds` | `A1[2]`, `A2[2]` in `Vrvu04` | Position 1 von `aspiration_sector_1/2` |
| `market_share_thresholds` | `A1[3]`, `A2[3]` in `Vrvu05` | Position 2 von `aspiration_sector_1/2` |

Der Eingang muss deshalb `threshold_source_policy =
insurer-aspiration-profile-v1` deklarieren und je Schwellenfeld zwei
explizite endliche Werte liefern. Die Werte werden in PR119 noch nicht gegen
ein mitgeliefertes VU-Anspruchsprofil verglichen. Der Bericht weist dies mit
`threshold_values_cross_checked_against_actor_state = false` aus.

## Ziehungen

`draw_source_policy = explicit-context-draws-v1` legt fest:

- `Vrvu01` erhaelt genau vier explizite endliche Werte in `[0.0, 1.0)`;
- `Vrvu02` erhaelt genau vier explizite endliche Normalziehungswerte;
- die Werte werden auch fuer einen eingereichten Startperiodenkontext
  verlangt, weil der heutige Python-Regelkern sie vor seiner Periodengrenze
  normalisiert;
- es wird weder ein Seed noch eine historische RNG-Folge rekonstruiert.

## Keine stillen Fallbacks

`fallback_policy = reject-loader-and-runner-fallbacks-v1` schliesst alle in
PR118 inventarisierten technischen Ersatzpfade fuer diesen Eingang aus.
Insbesondere sind nicht zulaessig:

- `null` mit spaeterer RNG-Ziehung im Runner;
- fehlende Schwellen mit Loader-Nullwerten;
- `null` fuer `previous_policyholders_sector` mit VU-State-Fallback;
- `null` fuer `active_policyholder_count` mit BAV-State-Fallback;
- stiller Zins `0.0` oder Schockstatus `false` durch den Loader.

Explizit gelieferte Werte `0.0`, `0` und `false` bleiben gueltige Werte. Die
aktive VN-Zahl und die beiden Vorperiodenbestaende duerfen nicht negativ
sein. Schwellenwerte werden mangels weitergehender historischer
Bereichsbelegung nur auf ihre bereits durch PR112 gesicherte endliche
Zweierform geprueft.

## API

`GET
/api/strategies/assignment-vu-snapshot-materialization-validation-contract`
liefert Schema, Policy-IDs, Validierungsreihenfolge und Grenzen.

`POST /api/strategies/assignment-vu-snapshot-materialization-validation`
akzeptiert:

- `schema_version`;
- `threshold_source_policy`;
- `draw_source_policy`;
- `fallback_policy`;
- `draft`;
- `context`.

Die Grundform wird zuerst mit dem unveraenderten PR112-Validator geprueft.
Danach werden ausschliesslich die enthaltenen VU-Eintraege bewertet. Ein
ungueltiger Eintrag verhindert die Gesamtfreigabe; Teilakzeptanz gibt es
nicht.

## Schutzgrenze

Kein VU-Snapshotloader wird aufgerufen. Kontextwerte werden inspiziert, aber
nicht konsumiert oder aufbewahrt. Es entstehen keine Snapshots und keine
Schreibvorgaenge. Runner, Ausfuehrung und Simulation bleiben gesperrt.

PR119 behauptet weder historische RNG-Gleichheit noch historische
Vollgleichheit und veraendert keine vorhandene VU-Regel.

## Naechster Schritt

Vor einer VU-Materialisierung ist zu entscheiden, ob ein Folge-PR die
Schwellen- und Vorperiodenwerte gegen einen expliziten VU-Zustandsblock
abgleicht oder die feste Herkunftsdeklaration fuer den ersten atomaren
Materialisierungsschnitt ausreicht.
