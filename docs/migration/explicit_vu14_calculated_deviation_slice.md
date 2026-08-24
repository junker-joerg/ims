# Erster berechneter VU14-Diagnoseslice

## Ziel

PR 60 verbindet erstmals ein Ergebnis des vorhandenen expliziten
Mehrperiodenrunners direkt mit der read-only Abweichungsdiagnose aus PR 59.
Der Slice umfasst `imsvu014.dat` fuer Versicherer 14 und die Perioden `1-4`
der historischen Referenz `VU14L1.DAT`.

Der Runner erhaelt kein Legacyziel. Seine `ExportTable`-Ergebnisse entstehen
zuerst aus den expliziten Zustandsinputs ueber die vorhandene Agrsich-
Aggregation und den Exportaufbau. Erst danach waehlt der neue Adapter den
VU14-Export und uebergibt ihn an die Diagnose.

## Ursprung und Python-Zuordnung

Dieser PR portiert keine neue C-Fachlogik und fuegt keine Regel hinzu.

| Ursprung / Eingabe | Python-Komponente | Rolle in PR 60 |
| --- | --- | --- |
| explizite VU14-Zustandssnapshots | `tests/fixtures/calculated_vu14_explicit_slice.json` | vorgegebene Zustaende fuer Perioden `1-4` |
| vorhandener Mehrperiodenpfad | `run_explicit_multi_period_from_fixture` | Aggregation und Exporttabellen je Periode |
| historische Referenzgrenze | `tests/fixtures/calculated_vu14_validation_slice.json` | `VU14L1.DAT`, Level I, `entity = 14`, Perioden `1-4` |
| neuer Adapter | `explicit_legacy_deviation_adapter.py` | Auswahl, periodische Zusammenfuehrung und PR-59-Diagnose |

Der genaue historische C-Generator, Scheduler und RNG-Lauf wird nicht
rekonstruiert.

## Berechnungs- und Herkunftsgrenze

Die vier Zustandswerte sind explizite, referenzausgerichtete Snapshots. Der
berechnete Umfang ist daher bewusst auf
`agrsich_aggregation_and_export_from_explicit_state_snapshots` begrenzt. Der
Slice belegt keine unabhaengige historische Zustandsentwicklung.

Der Adapter macht diese Grenze maschinenlesbar:

- `source_state_origin_verified = false`;
- `independent_historical_state_evolution_verified = false`;
- `automatic_historical_rule_selection_performed = false`;
- `historical_equivalence_claimed = false`.

Im expliziten Lauf werden keine VU- oder VN-Regeln, Settlements oder
Schadensabrechnungen angewendet. Der Lauf startet keine Vollsimulation und
schreibt ohne `output_dir` keine Dateien.

## Ergebnis des schmalen Slices

Der Runner erzeugt vier Periodenergebnisse und insgesamt 20 einzelne
Exporttabellen. Der Adapter:

- fuehrt die vier `imsvu014.dat`-Tabellen zu einem Ziel zusammen;
- ignoriert fuer diesen engen Slice transparent 16 Tabelleninstanzen aus vier
  anderen Exportidentitaeten;
- vergleicht genau vier VU14-Zeilen;
- meldet `4/4` passende Zeilen und `56/56` exakte Feldvergleiche;
- meldet keine tolerierte, blockierende oder offene Felddifferenz;
- schreibt selbst keine Datei.

Dieser Treffer belegt die Aggregat-/Exportanbindung fuer die vier explizit
vorgegebenen VU14-Zustaende. Er ist kein Vollgleichheitsnachweis fuer
`VU14L1.DAT`, den 19-Dateien-Kernkorpus oder das historische Modell.

## Weiterhin blockierter Kernkorpus

Wird dasselbe schmale Ergebnis gegen das volle Kernbundle geprueft, bleibt die
Diagnose auf `blocked_input`. Es fehlen weitere Exportidentitaeten und
Zielperioden; der Vierperiodenslice wird nicht als Teilvollgleichheit gewertet.

Der Lauf erzeugt außerdem Level-IV-Tabellen mit Laufzeitmetadaten
`selector_kind = "all"`, `selector_value = "all"`. Das historische Kernfixture
verwendet fuer `IMSVUSK1` und `IMSVNSK1` den historischen Selektorwert `SK1`.
Beide Bezeichnungen gehoeren zur dokumentierten `SK1`-/`all`-Grenze, duerfen
aber im strikten Adapter nicht still gleichgesetzt werden.

## Umsetzung in PR 61

PR 61 kanonisiert und testet die Level-IV-Selektormetadaten `all` und `SK1`
nun explizit an einer gemeinsamen technischen Identitaetsgrenze. Die rohe
Laufzeittabelle und die Aggregatstufe bleiben unveraendert. Ein berechneter
SK1-Slice ist damit technisch anschliessbar, aber noch nicht fachlich
validiert.

PR 62 hat den kontrollierten read-only Run-Control-Freigabecheck umgesetzt.
Als naechstes bereitet PR 63 die atomare Backend-Start-/Statusgrenze vor.
Daraus folgt weiterhin keine historische Vollgleichheitsbehauptung.
