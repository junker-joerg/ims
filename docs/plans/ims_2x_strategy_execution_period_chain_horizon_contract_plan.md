# PR147: Horizontvertrag fuer 10, 25, 50 und 100 Perioden

Stand: 2026-09-16
Umsetzungsstand: PR147 umgesetzt; PR148 naechster Schritt

## Ziel und Grenze

Ein versionierter, rein lesender Vertrag beschreibt vier kontrollierte
Folgehorizonte, bevor einer von ihnen gestartet werden darf. Die bestehenden
Zwei- und Fuenf-Perioden-Pfade bleiben unveraendert. PR147 baut keine laengere
Kette, speichert keinen Kandidaten, startet keinen Runner und erzeugt keine
fachlichen Ausgaben.

## Historische Einordnung

`ESS.C:71-75` setzt die lokale Periode auf 1 und durchlaeuft sie in
aufsteigender Folge. `IMSDATA.C:14` begrenzt mit `SIMLAENGE = 100` einen
historischen Einzellauf. Die aus mehreren Laeufen stammenden 300-/500-Zeilen-
Fenster sind kein Anlass, einen Einzellauf auf mehr als 100 zu verlaengern.
Der neue Vertrag ist eine technische Schutzschicht, keine portierte C-Regel.

## Entscheidungen

| Horizont | Kandidaten | Uebergaenge | Runner hoechstens | Carryover hoechstens | Gesamtzeit hoechstens |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 10 | 9 | 10 | 18 | 180 s |
| 25 | 25 | 24 | 25 | 48 | 450 s |
| 50 | 50 | 49 | 50 | 98 | 900 s |
| 100 | 100 | 99 | 100 | 198 | 1.800 s |

Die Zeiten sind obere Sicherheitsbudgets, keine Laufzeitprognose. Je Periode
sind hoechstens 30 s vorgesehen. Fuer jeden Horizont gelten vorlaeufig
1.024 MiB maximale Worker-RSS, 64 MiB fuer den kanonischen Ketten-Payload,
64 MiB fuer das komplette serialisierte Ergebnis und mindestens 256 MiB
freier Platz vor dem Start. Diese Grenzen sind *nicht* durch PR147
durchgesetzt; reale Messungen und ein isolierbarer Worker sind zwingende
Freigabebedingungen in PR148/PR149. Werden sie nicht belegt, bleibt der
jeweilige Horizont gesperrt; Aenderungen der Limits benoetigen einen neuen
versionierten Vertrag.

Vor dem ersten Runner sind alle Kandidaten und Kontexte erneut aufzulosen,
Digests zu pruefen, Folge und Uebergaenge vollstaendig zu validieren sowie
ein gespeicherter erfolgreicher Fuenf-Perioden-Nachweis nachzuweisen. Dessen
Perioden 1-5 samt vier Uebergaengen muessen vor Periode 6 semantisch und als
kanonisches JSON bytegleich bleiben; der gespeicherte Nachweis enthaelt
seinerseits den exakten Zwei-Perioden-Prefix. Huellenfelder des neuen
Horizonts werden nicht als fachliche Prefixwirkung verglichen.

## Abbruch und Fehler

- Der harte Zeit- und Speicherabbruch setzt einen isolierten, abbrechbaren
  Worker voraus; ein Python-Thread wird nicht als sicher abbrechbar angesehen.
- Ein manueller Abbruch wird zwischen Perioden angenommen. Ein harter
  Budgetabbruch kann den isolierten Worker auch innerhalb einer Periode
  beenden, ohne Zustand des gespeicherten Kandidaten zu veraendern.
- Der erste Fehler stoppt weitere Perioden. Kein Teilergebnis und kein
  Checkpoint werden zur Wiederaufnahme angeboten oder persistiert.
- Nur der vollstaendige Erfolg darf mit erneut geprueftem Ergebnisdigest
  atomar gespeichert werden. Ein fehlgeschlagener Versuch darf als Audit
  sichtbar bleiben; ein erneuter Versuch braucht eine neue explizite Freigabe.
- Gleicher Idempotenzschluessel und identischer Request lesen nach Erfolg
  nur das vorhandene Ergebnis; unterschiedliche Inhalte werden abgewiesen.

## Umsetzung und Pruefung

- Neues `ims.strategies.execution_period_chain_horizon_contract` mit
  unveraenderlichem, parameterlosem Payload; GET in FastAPI und Starlette.
- Exakte Tests fuer vier Horizonte, Budgets, Prefix, Freigabe-Flags und
  verbotene HTTP-Methoden; keine Datenbank und kein Runner im Vertragsaufruf.
- Migrationsnotiz mit C-zu-Python-Mapping, offenen Implementierungsfragen
  und der Grenze zur historischen Vergleichbarkeit.

## Folge

- PR148 implementiert und misst die isolierte Ausfuehrung fuer 10/25/50,
  jeweils mit eigener Freigabe und den hier definierten Grenzen.
- PR149 uebertraegt dieselben Invarianten nach eigenen Lasttests auf 100.
- PR150/151 liefern erst danach Exporte und Ergebnisarbeitsplatz.

`incomming/` bleibt unversioniert. Kein historischer RNG- oder
Vollgleichheitsnachweis wird behauptet.
