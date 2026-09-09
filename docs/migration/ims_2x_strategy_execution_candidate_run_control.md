# PR129: Run-Control-Freigabecheck fuer Ausfuehrungskandidaten

Stand: 2026-09-08

## Einordnung

PR127 speichert gemeinsame VU-/VN-Ausfuehrungskandidaten unveraenderlich;
PR128 macht Herkunft, Digest und Speicherstatus sichtbar. PR129 verbindet
diese Ablage mit einer eigenen Run-Control-Pruefgrenze, ohne einen Lauf zu
starten.

## C-zu-Python-Mapping

| Historischer Bezug | Python-Ziel | Fachliche Entsprechung |
| --- | --- | --- |
| gemeinsamer Laufzustand fuer `Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06` in `IMS.E` | `ims.api.strategy_execution_candidate_run_control` | technische Aufloesung eines bereits gebauten Zustands ueber stabile ID und erneut geprueften Digest |
| implizite Programm- und Globalzustandsgrenze | `StrategyExecutionCandidateRunControlRequest` | explizite Identitaets- und Auditangaben vor einer spaeteren Ausfuehrung |
| kein historischer Freigabedigest | `check_strategy_execution_candidate_run_control_release` | moderne Integritaetsgrenze ohne Behauptung historischer Entsprechung |

Es wird keine historische Regel, kein Scheduler und keine historische
Startsemantik portiert.

## Umsetzung

Der Requestparser akzeptiert nur Kandidaten-ID, erwarteten Volldigest und
explizite Auditfelder. Vor dem SQLite-Zugriff wird geprueft, ob die ID aus dem
erwarteten Digest ableitbar ist. Danach verwendet der Resolver den
read-only Abruf aus `ims.api.strategy_execution_candidate_store`, der Payload,
Digest und relationale Metadaten erneut prueft.

Der Check vergleicht ausserdem den vollstaendigen Digest und bestaetigt, dass
die im gespeicherten Kandidaten festgeschriebenen Grenzen fuer Run-Control,
Runner, Carryover, Ausgabedateien und Legacy-Vergleich weiterhin geschlossen
sind.

Die API liefert nur eine kurze Kandidatenzusammenfassung. Der vollstaendige
Kandidatenpayload kann dadurch nicht ueber den Freigabecheck ersetzt oder
eingeschleust werden.

## Ergebnisgrenze

`release_ready = true` belegt:

- konsistente Kandidaten-ID und erwarteten SHA-256-Digest;
- einen vorhandenen, unveraenderten SQLite-Datensatz;
- erneut bestaetigte Kandidaten- und Metadatenintegritaet;
- geschlossene Ausfuehrungsgrenzen im Kandidaten.

Der Wert belegt keine Benutzeridentitaet, schreibt keinen Freigabedatensatz,
legt keine Queue an und ist keine Starterlaubnis. Die bestehenden
fixture-basierten Run-Control-Endpunkte werden nicht umgedeutet oder
automatisch verwendet.

## API

- `GET /api/run-control/strategy-candidate-contract`
- `POST /api/run-control/strategy-candidate-release-check`

Ein unbekannter Kandidat ergibt `404`, ein Integritaets- oder Digestkonflikt
`409` und ein ungueltiger Request oder eine fehlende SQLite-Konfiguration
`400`. Alle Antworten weisen Queue, Preflight, Start, Schreiben, Ausfuehrung
und Simulation explizit als nicht erfolgt aus.

## Grenzen und offene Punkte

- Die Workbench zeigt die verfuegbare Pruefgrenze nur read-only an.
- Autorisierung, dauerhafte Freigabeakte, Start-Idempotenz und Ergebnisverlauf
  werden erst mit dem kontrollierten Ausfuehrungspfad konkretisiert.
- PR130 fuehrt den ersten kontrollierten Runneraufruf auf einer isolierten
  Kandidatenkopie aus und bleibt auf eine Periode begrenzt.
- PR131 ergaenzt die dauerhafte Idempotenz- und Ergebnisgrenze fuer die
  bedienbare Workbench.
- Mehrperiodenlauf, Carryover, Ergebnisexport und Regulierungsszenarien sind
  nicht Teil dieses PRs.
- Es gibt keine historische RNG- oder Vollgleichheitsbehauptung.
