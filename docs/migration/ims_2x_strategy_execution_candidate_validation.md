# PR125: Gemeinsamen Kandidateneingang pruefen

Stand: PR125, 2026-09-08

## Ergebnis

PR125 stellt mit `ims.strategy-execution-candidate-input.v1` erstmals eine
gemeinsame Eingabeform fuer den geplanten Einperioden-Ausfuehrungskandidaten
bereit. Der zustandslose Validator liefert
`ims.strategy-execution-candidate-validation.v1` und akzeptiert den Eingang
nur, wenn alle Quellen und Querbeziehungen zusammen passen.

Ein positiver Bericht ist noch kein Kandidat und keine Ausfuehrungsfreigabe.

## Gemeinsame Quellen

| Quelle | Pruefung | Ergebnisverwendung in PR125 |
| --- | --- | --- |
| `assignment_draft` | vorhandener Strategieentwurfsvertrag | nur validiert |
| `snapshot_context` | PR115 fuer VN, PR119 fuer VU | nur inspiziert |
| `vu_input_policy` | feste PR119-Policy-IDs | intern zum Pruefrequest zusammengesetzt |
| `vu_state_provenance` | PR120 | nur abgeglichen |
| `scenario_profile_reference` | stabile ID, Periode, erwartete Population | nicht aufgeloest |
| `vn_process_input` | strikte explizite Schadenprozessform | keine Snapshots erzeugt |

Entwurf und Kontext werden nicht fuer die VU- und VN-Seite dupliziert. Die
vorhandenen Validatoren erhalten dieselben Objektinhalte. PR125 vergleicht
anschliessend Entwurfs-ID, Periode, gemeinsamen Schockstatus und Akteursziele
noch einmal ueber die Teilberichte hinweg.

## Szenarioprofil-Referenz

Die Referenzversion
`ims.strategy-execution-scenario-profile-reference.v1` verlangt:

- `profile_id` ohne freien Pfad;
- Source-Policy `server-known-local-scenario-profile-v1`;
- eine positive Periode und erwartete BAV-ID;
- eindeutige positive VU- und VN-IDs;
- exakte Uebereinstimmung dieser erwarteten Population mit dem Entwurf.

Die Existenz und der Inhalt des lokalen Profils werden erst in PR126
serverseitig geprueft. Deshalb bleibt `scenario_profile_resolved = false`.

## Expliziter VN-Prozess

Der Prozesseingang
`ims.strategy-execution-vn-process-input.v1` verlangt je VN genau einen
kombinierten Schaden-/Abrechnungseintrag. Vier zweispartige Parametervektoren,
Schadenschwellen, Vorvermoegen und die beiden zweispartigen Normalziehungen
liegen explizit vor. Der Schockstatus muss zum VN-Kontext passen.

Die Policy `server-rematerialized-vn-rule-snapshots-v1` legt fest, dass die
Versicherungsentscheidungen spaeter aus PR116 stammen. Entsprechend stammt
auch die Informationskostenwirkung aus `vn-rule-application-v1`. PR125 nimmt
keine Browserentscheidung als alternative Quelle an.

Reine `vn_settlement_snapshots` bleiben fuer diesen ersten Pfad gesperrt. Der
heutige Runner wuerde ihre Entscheidungen nicht mit der vorbereiteten
VN-Strategie verbinden. Diese Grenze vermeidet eine nur scheinbar gemeinsame
Strategiewirkung; sie fuegt keine Fachregel hinzu.

## Atomaritaet und Fehler

Der Bericht trennt VN-Kontext, VU-Eingang, VU-Zustand, Profilreferenz,
VN-Prozess und gemeinsame Identitaet. Mehrere unabhaengige Fehler werden in
einem Bericht gesammelt. Trotzdem entsteht weder bei Teil- noch bei
Gesamterfolg ein Kandidat.

`partial_candidate_returned`, `snapshots_created`,
`server_side_rematerialization_performed`, `digest_calculation_performed`,
`candidate_created`, `candidate_persisted`, `run_control_connected`,
`runner_invocation_performed`, `execution_performed` und
`simulation_performed` bleiben immer `false`.

## API

`GET /api/strategies/execution-candidate-validation-contract` beschreibt die
Pruefung. `POST /api/strategies/execution-candidate-validation` fuehrt sie
in-memory aus. Der Endpunkt schreibt nichts und erlaubt keine freien Fixture-
oder Outputpfade.

## Altcodebezug und Grenzen

Die Werte bleiben den bereits dokumentierten historischen Aktionen `Vrvu01`
bis `Vrvu10` und `Vrvn01` bis `Vrvn06` aus `IMS.E` zugeordnet. PR125 aendert
keine Regelwirkung, aktiviert keinen Scheduler und trifft keine neue Aussage
zur historischen RNG-Folge oder Vollgleichheit.

## Naechster Schritt

PR126 loest einen gueltigen Profilbezeichner serverseitig auf, wiederholt die
VU-/VN-Materialisierung aus den Originalquellen und baut einen kanonischen,
weiterhin nicht ausgefuehrten Kandidaten mit Inhaltsdigest.
