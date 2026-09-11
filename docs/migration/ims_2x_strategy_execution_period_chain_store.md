# PR137: Periodenkette unveraenderlich speichern

Stand: 2026-09-11

## Einordnung

PR134 prueft den vollstaendigen Ketteneingang, PR135 loest alle genannten
Kandidaten serverseitig auf und PR136 baut daraus eine kanonische fluechtige
Kette samt Gesamtdigest. PR137 fuegt die erste schreibende Grenze fuer dieses
Kettendokument hinzu. Die Speicherung ist nur nach ausdruecklicher Freigabe
moeglich und schaltet weder Carryover noch Mehrperiodenausfuehrung frei.

## C-zu-Python-Mapping

| Historischer Ursprung | Python-Ziel | Bedeutung |
| --- | --- | --- |
| `IMSDATA.C:14`, `SIMLAENGE = 100` | persistierter Abschnitt `horizon` | lokaler Laufhorizont bleibt auf hoechstens 100 Perioden begrenzt |
| Periodenschleife in `ESS.C:71-75` | persistierte `period_candidates` und `transitions` | lueckenlose, bei Periode 1 beginnende Reihenfolge |
| periodenindizierte VU-/VN-Strukturen in `IMSDATA.C` | unveraenderliche Kandidatenreferenzen | Kette verweist auf bereits gespeicherte und erneut gepruefte Periodenkandidaten |

PR137 portiert keine neue C-Funktion und fuegt keine VU-/VN-Fachlogik hinzu.

## Umsetzung

`ims.api.strategy_execution_period_chain_store` definiert:

- den Requestvertrag
  `ims.strategy-execution-period-chain-store-request.v1`;
- den Speichervertrag `ims.strategy-execution-period-chain-store.v1`;
- eine SQLite-Tabelle mit eindeutiger `chain_id` und eindeutigem
  `content_digest`;
- insert-only Speicherung oder einen exakten idempotenten Replay;
- einen read-only Abruf mit erneuter Struktur- und Digestpruefung.

FastAPI und der Starlette-Fallback stellen bereit:

- `GET /api/strategies/execution-period-chain-store-contract`;
- `POST /api/strategies/execution-period-chain-store`;
- `GET /api/strategies/execution-period-chains/{chain_id}`.

Der Request enthaelt den vollstaendigen PR134-Eingang, erwartete `chain_id`
und `content_digest`, einen Speicherzeitpunkt mit Zeitzone sowie
`explicit_storage_release = true`. Datenbankpfad und ein vom Browser
geliefertes fertiges Kettenpayload sind nicht zulaessig.

## Pruefreihenfolge

1. Requestform, Schemaversion, Zeitstempel und explizite Freigabe pruefen.
2. Die Kette ueber PR135 und PR136 serverseitig vollstaendig neu bilden.
3. Neu gebaute ID und Volldigest gegen die Freigabe pruefen.
4. Inhalt unmittelbar vor dem Insert nochmals strukturell und kryptografisch
   pruefen.
5. Neue Identitaet einfuegen oder vorhandenen exakt gleichen Inhalt als
   Replay bestaetigen.
6. Die gespeicherte Zeile neu lesen und Ketteninhalt, Metadaten, ID und
   Volldigest erneut pruefen.

Ein vorhandener abweichender oder beschaedigter Datensatz wird abgelehnt,
nicht aktualisiert und nicht repariert. Der erste gespeicherte Zeitstempel
bleibt auch bei einem spaeteren exakten Replay erhalten.

## Validierung

Die Tests sichern:

- Speicherung und read-only Abruf einer serverseitig neu gebauten Kette;
- Digestpruefung vor und nach dem Insert sowie bei jedem Abruf;
- idempotenten Replay ohne zweite Zeile oder geaenderten Zeitstempel;
- Abbruch ohne Kettentabelle bei fehlender Freigabe, falscher erwarteter
  Identitaet oder fehlgeschlagenem Neubau;
- Ablehnung manipulierter Payloads, Ausfuehrungsgrenzen und Metadaten ohne
  Reparatur;
- gleiche Methoden- und Konfigurationsgrenzen in FastAPI und Starlette;
- ausbleibende Carryover-, Runner- und Simulationsaufrufe.

## Bewusste Grenzen

Die gespeicherte Kette ist ein freigegebenes, reproduzierbar identifiziertes
Eingabedokument. Sie ist noch kein Laufauftrag und enthaelt keine
Periodenergebnisse. PR137 fuehrt weder Carryover noch Runner aus und schreibt
keine Ergebnisdateien.

Der Kettendigest belegt die Integritaet des modernen Kettendokuments. Er ist
keine historische RNG- oder Vollgleichheitsbehauptung. `incomming/` bleibt
unversioniert.

## Naechster Schritt

PR138 soll eine gespeicherte Ketten-ID und den erwarteten Volldigest an einer
read-only Freigabegrenze erneut aufloesen und pruefen. Start, Carryover und
Mehrperiodenrunner bleiben dort weiterhin gesperrt.
