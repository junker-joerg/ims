# PR138: Gespeicherte Periodenkette read-only freigeben

Stand: 2026-09-11
Umsetzungsstand: PR138 umgesetzt

## Ziel

PR138 nimmt nur Ketten-ID und erwarteten SHA-256-Volldigest als
autoritative Kettenidentitaet an. Die gespeicherte PR137-Kette wird read-only
aufgeloest. Dabei werden Kettenstruktur, relationale Metadaten, gespeicherter
Digest und der vollstaendige erwartete Digest erneut geprueft.

Ein positives `release_ready` ist noch keine Starterlaubnis. Der Check legt
keine Queue und keine Freigabeakte an, veraendert weder Kette noch Kandidaten
und ruft keinen Carryover- oder Periodenrunner auf.

## Historischer und technischer Bezug

| Quelle | Belegte Aussage | Folge fuer PR138 |
| --- | --- | --- |
| `IMSDATA.C:14` | `SIMLAENGE = 100` | der erneut gepruefte Kettenhorizont bleibt auf hoechstens 100 lokale Perioden begrenzt |
| `ESS.C:71-75` | Lauf beginnt bei Periode 1 und schreitet periodisch fort | die PR137-Pruefung muss weiterhin die lueckenlose Reihenfolge bestaetigen |
| PR129-Kandidatenfreigabe | ID, Volldigest und geschlossene Grenzen werden read-only geprueft | PR138 verwendet dasselbe kontrollierte Muster fuer die ganze Kette |
| PR137-Kettenablage | Kettenpayload und relationale Metadaten werden bei jedem Abruf erneut verifiziert | PR138 baut auf diesem read-only Abruf auf und vergleicht zusaetzlich die erwartete Identitaet |

Digest und Freigabecheck besitzen keine historische C-Entsprechung. PR138
portiert keine historische Fachregel und aendert keine VU-/VN-Semantik.

## Request-Vertrag

`POST /api/run-control/strategy-period-chain-release-check` akzeptiert exakt:

- `schema_version`;
- `chain_id`;
- `expected_content_digest`;
- `idempotency_key`;
- `explicit_run_control_release = true`;
- `released_by`;
- `released_at` als UTC-Zeitpunkt mit `Z`;
- `release_reason`.

Kettenpayload, Kandidatenpayloads, freie Datenbank-, Fixture- oder
Ausgabepfade sowie Queue-, Run- und Ausfuehrungsfelder sind verboten. Die
Auditangaben werden nur geprueft und zurueckgegeben; PR138 speichert keine
Freigabeakte und authentisiert keine Benutzeridentitaet.

## Atomare Prueffolge

1. Requestfelder, Formate und ausdrueckliche Freigabe pruefen.
2. Ketten-ID aus dem erwarteten Volldigest ableiten.
3. Kette ueber den read-only PR137-Abruf laden.
4. Gespeichertes Payload, relationale Metadaten, ID und Digest erneut
   verifizieren.
5. Den vollstaendigen erwarteten Digest vergleichen, nicht nur das in der
   Ketten-ID enthaltene Praefix.
6. Horizont und weiterhin geschlossene Ausfuehrungsgrenzen bestaetigen.
7. Nur eine knappe Kettenzusammenfassung und die einzelnen Checks liefern.

Ein Fehler blockiert das Gesamtergebnis. Es gibt kein Teil-`release_ready`
und keinen Schreibzugriff.

## API

- `GET /api/run-control/strategy-period-chain-contract` beschreibt die
  read-only Grenze.
- `POST /api/run-control/strategy-period-chain-release-check` fuehrt nur die
  atomare Pruefung aus.

Ein unbekannter Datensatz ergibt `404`, ein Digest- oder Integritaetskonflikt
`409` und ein ungueltiger Request oder eine fehlende SQLite-Konfiguration
`400`.

## Validierung

- exakte Parserfelder, ID-/Digestformate, UTC-Zeit und Freigabeflag;
- positiver Check einer wirklich gespeicherten Zwei-Perioden-Kette;
- Volldigestkonflikt trotz gleichem ID-Praefix;
- unbekannte und nachtraeglich beschaedigte Kette;
- unveraenderte SQLite-Datei vor und nach dem Check;
- kein Aufruf von Carryover, Periodenrunner oder Simulation;
- Methoden- und Statuscodes fuer FastAPI und Starlette-Fallback;
- Dokumentations- und Gesamtregressionstests.

## Restplanung

- **PR138 (umgesetzt):** read-only Freigabecheck fuer gespeicherte
  Ketten-ID und Volldigest.
- **PR139 (umgesetzt):** isolierte, fluechtige Zwei-Perioden-Wirkungsprobe
  aus einer erneut freigegebenen Kette; exakte Carryover-Flags, atomarer
  Fehlerstopp und keine Ergebnisablage.
- **PR140 (naechster Schritt):** kontrollierter Workbench-Start fuer die
  Zwei-Perioden-Probe mit
  dauerhafter Idempotenz und unveraenderlichem Ergebnisverlauf.
- **PR141+:** Browserabnahme und danach schrittweise Horizonte bis 100
  Perioden, ohne daraus fachliche Produktionsreife abzuleiten.

## Schutzgrenzen

- keine neue oder geaenderte Fachlogik;
- keine erneute Materialisierung oder Aenderung gespeicherter Kandidaten;
- keine Queue, Freigabepersistenz oder Ergebnisablage;
- kein Carryover-Aufruf, Runnerstart, Scheduler oder Simulation;
- kein Legacy-Vergleich und keine historische RNG- oder
  Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.
