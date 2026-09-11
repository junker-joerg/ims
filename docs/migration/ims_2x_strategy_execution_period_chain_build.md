# PR136: Kanonische fluechtige Periodenkette und Gesamtdigest

Stand: 2026-09-11

## Einordnung

PR134 prueft das vollstaendige Kettenformat. PR135 loest die genannten
Kandidaten aus der serverseitigen SQLite-Ablage auf und prueft Inhalt,
Digest, Kontext und Akteursidentitaeten erneut. PR136 baut erst nach diesem
vollstaendigen Erfolg ein kanonisches Kettenobjekt im Speicher.

Die Kette ist identifizierbar, aber noch nicht gespeichert oder ausfuehrbar.

## C-zu-Python-Mapping

| Historischer Ursprung | Python-Ziel | Bedeutung |
| --- | --- | --- |
| `IMSDATA.C:14`, `SIMLAENGE = 100` | Kettenabschnitt `horizon` | expliziter lokaler Laufhorizont von Periode 1 bis hoechstens 100 |
| Periodenschleife in `ESS.C:71-75` | geordnete `period_candidates` und `transitions` | lueckenlose Folge mit Schrittweite eins |
| periodenindizierte VU-/VN-Strukturen in `IMSDATA.C` | serverbestaetigte Kandidatenreferenzen | jeder Kettenschritt verweist auf einen bereits geprueften Periodenkandidaten |

PR136 portiert keine neue C-Funktion. Es fuehrt keine VU-/VN-Regel und keine
historische Zufallsziehung aus.

## Umsetzung

`ims.api.strategy_execution_period_chain_build` liefert:

- `ims.strategy-execution-period-chain-build-contract.v1`;
- `ims.strategy-execution-period-chain-build.v1`;
- eine erneute atomare PR135-Aufloesung als zwingende Vorbedingung;
- ein unveraenderliches, fluechtiges Kettenobjekt mit den Abschnitten
  `identity`, `horizon`, `period_candidates`, `transitions`, `provenance` und
  `execution_boundaries`;
- serverbestaetigte Kandidatenreferenzen ohne eingebettete Kandidatenpayloads;
- einen kanonischen SHA-256-Gesamtdigest;
- eine stabile `strategy-period-chain-...`-ID aus den ersten 24 Hexzeichen
  des vollstaendigen Digests.

FastAPI und der Starlette-Fallback stellen bereit:

- `GET /api/strategies/execution-period-chain-build-contract`;
- `POST /api/strategies/execution-period-chain-build`.

Die Datenbankquelle bleibt serverseitig konfiguriert. Der Request kann keinen
Pfad und weder einen Kandidateninhalt noch einen bereits erzeugten
Aufloesungsbericht einschleusen.

## Digestbasis

Der Digest wird aus ASCII-JSON mit `sort_keys=True`, kompakten Trennzeichen
und `allow_nan=False` gebildet. Er umfasst:

- Kettenschema und `Vdefmd6`;
- Horizont und Laufindex;
- Kandidaten-ID, neu verifizierten Kandidatendigest und Periode;
- explizite VU-/VN-Carryover-Flags je Uebergang;
- Version und Ergebnisgrenzen der PR135-Aufloesung;
- die geschlossenen Ausfuehrungsgrenzen.

Ausgeschlossen sind die daraus abgeleiteten Identitaetsfelder `chain_id` und
`content_digest`, Datenbankpfad, Speicherzeitpunkt und vollstaendige
Kandidateninhalte. Deshalb bleibt dieselbe fachlich und technisch definierte
Kette bei einem geaenderten Speicherzeitpunkt identisch, waehrend ein
geaendertes Uebergangsflag einen anderen Digest ergibt.

## Validierung

Die Tests sichern:

- deterministischen Kettenbau aus zwei echt materialisierten und gespeicherten
  Periodenkandidaten;
- unabhaengige Nachrechnung von Gesamtdigest und Ketten-ID;
- stabile Identitaet trotz geaendertem `stored_at`;
- Digest-Aenderung bei einem geaenderten expliziten Carryover-Flag;
- atomare Blockade ohne Teilkette und ohne Digest bei ungueltigem Eingang oder
  manipuliertem Kandidaten;
- unveraenderte SQLite-Datei und ausbleibende Carryover- und Runneraufrufe;
- Methoden-, Pfad- und Konfigurationsgrenzen beider API-Implementierungen.

## Bewusste Grenzen

PR136 speichert die Kette nicht und erzeugt keine Ergebnisprovenienz.
Spaetere Periodenergebnisse muessen als getrennte Laufdatensaetze auf
Ketten-ID und Kettendigest verweisen; die unveraenderliche Kette wird dafuer
nicht erweitert. Carryover, Periodenrunner, UI-Start und Ergebnisexport
bleiben gesperrt.

Der Kettendigest belegt die Identitaet des modernen, expliziten
Kettendokuments. Er ist kein Nachweis gleicher historischer Zufallszahlen oder
historischer Vollgleichheit.

## Naechster Schritt

PR137 legt die kanonische Kette inzwischen nur nach ausdruecklicher Freigabe
unveraenderlich und idempotent ab und prueft ihren Digest vor und nach der
Speicherung. PR138 prueft die gespeicherte Identitaet inzwischen an einer
read-only Freigabegrenze erneut. PR139 erprobt inzwischen genau zwei
Perioden auf isolierten Kopien fluechtig. PR140 soll den dauerhaften Start
kontrollieren; der Ausbau des Horizonts bleibt weiteren getrennten PRs
vorbehalten.
