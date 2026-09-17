# PR169c: Kontrollierte Kranken-Ergebnisablage und Export

Stand: 2026-09-17
Startvertrag: `ims.health-result-start.v1`
Liefervertrag: `ims.health-result-delivery.v1`
API-Basis: `/api/accounting/health-period-chain`

## Ursprung und Grenze

| Ursprung | IMS 2.x | Grenze |
| --- | --- | --- |
| `IMSDATA.C`: periodische VU-/VN-Vektoren fuer zwei historische Schadenpositionen | PR169b: getrennte Kranken-Periodenkette | keine belegte Zuordnung von `KV` oder `Rk[2]` zu moderner Krankenversicherung. |
| `IMS.E`: historische Aggregatdateien | PR169c: verifizierter Ergebnisdatensatz und drei Exporte | keine Wiederverwendung historischer Ausgabewerte, Feldgleichheit oder RNG-Folge. |
| PR166: `ims.api.life_result_delivery` | `ims.api.health_result_delivery` und `health_result_exports` | gleiches Speicher-/Digest-Muster, aber eigene Kranken-Tabelle, eigene Ergebnis-ID und eigene API; keine Aenderung an Lebensregeln. |

PR169c fuegt **keine neue Kranken-Fachregel** hinzu. Die Periodenrechnung
bleibt der PR169b-Bibliotheksaufruf; eine gesetzliche Krankenbilanz,
Solvency-II-Bewertung oder historische Vollgleichheit wird nicht
behauptet.

## Bediengrenze der API

| Weg | Wirkung |
| --- | --- |
| `GET /contract` | Versionen, Endpunkte, Zeitgrenze und Freigabepflicht lesen. |
| `POST /preview` | Vollstaendige Kette serverseitig pruefen und fluechtig rechnen; Ergebnis und SHA-256-Digests liefern, **keine** Datei/DB schreiben. |
| `POST /start` | Freigabe, Idempotenzschluessel, Eingabe- und Ergebnis-Digest fordern; serverseitig erneut rechnen und nur bei vollstaendiger Uebereinstimmung atomar speichern. |
| `GET /results` | Hoechstens 100 verifizierte gespeicherte Krankenergebnisse lesen. |
| `GET /result/{result_id}` | Verifizierten Datensatz mit vollstaendigem Eingang, Bericht und Herkunft lesen. |
| `GET /result/{result_id}.csv/.json/.xlsx` | Nur mit `If-Match` des Ergebnis-Digests herunterladen. |

Der Start benoetigt einen explizit konfigurierten SQLite-Pfad. Die
Vorschau funktioniert ohne ihn. Pro App ist nur eine gleichzeitige
Krankenrechnung freigegeben; ein weiterer Versuch liefert `429`.
Eingaben sind auf 2 MB, die Rechnung auf 20 Sekunden begrenzt. Ein
Zeitlimit setzt den Abbruch der reinen Kette; vor erfolgreicher
Neuberechnung wird nichts gespeichert. Ein wiederholter identischer
Start gibt den vorhandenen verifizierten Datensatz zurueck, ohne
nochmals zu rechnen oder zu schreiben. Derselbe Schluessel mit anderen
Digests liefert `409`. SQLite-Transaktion und Unique-Schluessel halten
auch parallele Starts bei genau einem Datensatz.

Abruf, Verlauf und Exporte verifizieren Eingabe-, Ergebnis- und
Datensatz-Digest erneut. Ein manipulierter Datensatz wird als `409`
abgewiesen, nicht teilweise ausgeliefert. Der SHA-256-Digest dient der
Integritaets- und Identitaetskontrolle, **nicht** als Signatur gegen
jemanden mit Schreibzugriff auf die Datenbank.

## Exportsemantik

CSV enthaelt eine Zeile je Periode mit unveraenderten Dezimalstrings
und wiederholter Ergebnis-ID, allen drei Digests, VU, Szenario,
Variante und Horizont. JSON enthaelt den vollstaendigen verifizierten
Datensatz samt Eingabe und Bericht. XLSX enthaelt `Perioden` und
`Herkunft`; Betragszellen sind explizit Text, nicht Excel-Gleitkomma.
Auch CSV selbst traegt die exakten Zeichen, doch Tabellenprogramme
koennen sie beim automatischen Import eigenstaendig als Zahlen deuten.
Alle drei Downloads tragen ETag und verlangen dasselbe `If-Match`.

FastAPI und Fallback-Router haben dieselben Pfade und Fehlergrenzen.
Tests pruefen Vorschau, Freigabe, Replay, Parallelstart, Manipulation,
Abbruch/Timeout, 100 Perioden und die Uebereinstimmung der Exporte.
Die Workbench hat diese API in **PR169d** fuer den Seminarfall bedienbar
gemacht; die Speicher- und Digestgrenzen dieses PR169c bleiben dabei
unveraendert.
