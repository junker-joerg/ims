# PR120: VU-Zustand und Herkunft pruefen

Stand: PR120, 2026-09-07

## Ergebnis

PR120 fuehrt einen versionierten VU-Zustandsbeleg und eine atomare
Herkunftspruefung ein. Die Anfrage besteht aus einem unveraenderten, bereits
durch PR119 pruefbaren `input` und einem neuen `state`-Dokument. Nur wenn beide
Teile gueltig sind und alle belegten Werte uebereinstimmen, meldet der Bericht
`valid = true`.

Der Zustandsbeleg dient ausschliesslich dem Konsistenznachweis. Seine Werte
werden weder in Snapshots uebernommen noch gespeichert oder ausgefuehrt.

## C-zu-Python-Zuordnung

| Kontextwert | Historischer Ursprung | Zustandsbeleg / Python-Entsprechung |
| --- | --- | --- |
| `interest_rate` | `IMS.E`: `Zins[gperiod]` | `period_state.interest_rate` / `Vdefmd6VUPeriodInput.interest_rate` |
| `change_shock` | `IMS.E`: `aenderung` | `period_state.change_shock` / `Vdefmd6VUPeriodInput.change_shock` |
| `reserve_thresholds` | `Vrvu03`: `A1[1]`, `A2[1]` | `aspiration_sector_1/2[0]` |
| `net_switcher_thresholds` | `Vrvu04`: `A1[2]`, `A2[2]` | `aspiration_sector_1/2[1]` |
| `previous_policyholders_sector` | `Vrvu04`: `Vn[gperiod-2]` | `policyholders_t_minus_2` / `Insurer.policyholders_prev_sector` |
| `market_share_thresholds` | `Vrvu05`: `A1[3]`, `A2[3]` | `aspiration_sector_1/2[2]` |
| `active_policyholder_count` | `Vrvu05`: `akvn` | `period_state.active_policyholder_count` / BAV-Aktivitaetszustand |

Damit wird die in PR119 noch offene Schwellenherkunft nun gegen die beiden
expliziten Anspruchsprofile des Ziel-VU geprueft. Fuer `Vrvu04` wird der
Bestand `t-2` bewusst von den laufenden Bestandswerten getrennt.

## Zustandsformat

Das Dokument verwendet
`schema_version = ims.strategy-assignment-vu-snapshot-state.v1` und bindet
sich mit `input_schema_version` an den PR119-Eingang. Es enthaelt:

- `draft_id` und `period` als exakte Bindung an Entwurf und Kontext;
- `period_state` mit Zinssatz, Schockstatus und aktiver VN-Zahl;
- genau einen `entries`-Eintrag je VU im validierten Eingang;
- je VU nur die fuer den Herkunftsabgleich benoetigten `values`.

Fuer `Vrvu03` und `Vrvu05` sind dies die beiden dreistelligen
Anspruchsprofile. `Vrvu04` ergaenzt den zweistelligen Bestand `t-2`. Die
anderen sieben Regeln verlangen einen leeren Werteblock. Unbekannte Felder,
fehlende VU und abweichende Strategiezuordnungen werden abgewiesen.

## Pruefreihenfolge

1. PR119-Eingang einschliesslich seiner Policy- und Fallbackgrenzen pruefen.
2. Zustandsdokument und alle verschachtelten Feldformen exakt pruefen.
3. VU-Zuordnung gegen den validierten Entwurf abgleichen.
4. Gemeinsamen Periodenzins und Schockstatus je VU vergleichen.
5. Regelabhaengige Schwellen, `t-2`-Bestand und aktive VN-Zahl vergleichen.
6. Nur den vollstaendigen, fehlerfreien Gesamtbeleg akzeptieren.

Die Vergleiche sind Identitaetspruefungen eingereichter Werte. Deshalb wird
keine fachliche Toleranz angewendet. Ein abweichender Wert wird mit seinem
Kontextpfad und der Herkunftskategorie gemeldet.

## API

`GET /api/strategies/assignment-vu-snapshot-state-contract` liefert
Schemafelder, sieben Herkunftsdefinitionen, regelabhaengige Zustandsfelder
und die geschlossenen Funktionsgrenzen.

`POST /api/strategies/assignment-vu-snapshot-state-validation` prueft ein
Objekt mit den Feldern `input` und `state`. Ungueltiges JSON wird mit Status
400 beantwortet; fachliche Vertragsabweichungen bleiben ein strukturierter
Validierungsbericht mit Status 200.

## Aussagegrenzen

Der `state`-Block ist ein explizit eingereichter Konsistenzbeleg. PR120 laedt
ihn nicht aus einer VU-Population oder einem Runner und kann daher seine
externe Authentizitaet nicht beweisen. Ebenso werden die Ziehungen nicht gegen
einen Seed oder Draw-Plan geprueft; der Bericht weist
`draw_values_cross_checked_against_draw_plan = false` aus.

Kein VU-Snapshotloader wird aufgerufen. Es werden keine Kontext- oder
Zustandswerte konsumiert, keine Snapshots erzeugt und keine Daten gespeichert.
Runner, Ausfuehrung und Simulation bleiben gesperrt. PR120 behauptet weder
historische RNG-Gleichheit noch historische Vollgleichheit.

## Naechster Schritt

PR121 kann ausschliesslich vollstaendig gueltige PR120-Anfragen atomar in die
vorhandenen VU-Snapshottypen materialisieren. Speicherung, Runner und
Simulation bleiben auch in diesem Folgeschritt ausserhalb des Umfangs.
