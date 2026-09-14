# PR145: Fuenf-Perioden-Start dauerhaft absichern

Stand: 2026-09-14
Status: umgesetzt

## Ziel

Die in PR144 isoliert gepruefte Fuenf-Perioden-Wirkung erhaelt einen
kontrollierten Serverstart. Ein fachlich gleicher Wiederholungsrequest liefert
das einmal gespeicherte Ergebnis, ohne einen weiteren Runneraufruf. Request,
kanonische Kette und Wirkungsergebnis werden gemeinsam durch einen Digest
geschuetzt.

## Historischer Bezug

| Ursprung | Bedeutung fuer PR145 |
| --- | --- |
| `ESS.C:73-75` | belegt die historische aufsteigende Periodenschleife |
| `IMSDATA.C:14` | belegt den historischen Standardhorizont von 100 Perioden, nicht die Freigabe eines freien Runners |
| PR140 | liefert das bewaehrte Muster fuer atomaren Start, Idempotenz und Ergebnisablage |
| PR144 | liefert unveraendert die isolierte Fuenf-Perioden-Wirkungsprobe und den exakten Prefixnachweis 1-2 |

PR145 portiert keine weitere VU-/VN-Regel. Die persistente Steuerung ist eine
technische Ausfuehrungsgrenze um die bereits gepruefte Wirkung.

## Vertrag

Der Startrequest umschliesst den unveraenderten PR144-Request mit:

- kanonischer Ketten-ID und erwartetem Gesamtdigest;
- dauerhaftem Idempotenzschluessel;
- Person, Zeitpunkt und Grund der Freigabe;
- einer zweiten expliziten Freigabe fuer den dauerhaften Start.

Die Ketten-ID wird aus den fuenf gespeicherten Kandidaten neu aufgebaut und
vor dem ersten Runner mit der Freigabe verglichen. Zwischen Vorpruefung und
Ausfuehrung muss die kanonische Kette unveraendert bleiben.

## Dauerhafte Ablage

Zwei getrennte SQLite-Tabellen speichern:

1. jeden begonnenen, fehlgeschlagenen oder abgeschlossenen Startversuch;
2. hoechstens ein erfolgreiches Ergebnis je kanonischer Fuenf-Perioden-Kette.

Der Ergebnisdigest umfasst Ablageidentitaet und -zeitpunkt, den vollstaendigen
Startrequest, eine kanonische Kettenkopie und das vollstaendige
Wirkungsergebnis. Dadurch bleibt der Nachweis read-only pruefbar, auch wenn
sich spaeter Kandidaten- oder Prefixbestaende aendern.

## Atomare und idempotente Grenzen

- Der Idempotenzanspruch wird vor Kettenbau und Runner atomar gespeichert.
- Derselbe Schluessel mit demselben Request liefert das gespeicherte Ergebnis.
- Derselbe Schluessel mit anderem Inhalt wird blockiert.
- Ein zweiter Schluessel darf ein vorhandenes Kettenergebnis nicht ersetzen.
- Fehler speichern den Versuch und seine Aufrufzaehler, aber kein Teilresultat.
- Fehlgeschlagene Versuche werden nicht automatisch wiederholt.
- Read-only Ergebnis- und Verlaufszugriffe erzeugen keine Tabellen.

## API-Schnitt

- `GET /api/run-control/strategy-period-chain-five-period-effect-probe-start-contract`
- `POST /api/run-control/strategy-period-chain-five-period-effect-probe-start`
- `GET /api/run-control/strategy-period-chain-five-period-effect-probe-result/{chain_id}`
- `GET /api/run-control/strategy-period-chain-five-period-effect-probe-history/{chain_id}`

Die Workbench besitzt in PR145 noch keinen Startknopf fuer fuenf Perioden.

## Abnahme

- Erststart: exakt fuenf Runner- und vier Uebergangsfolgen, danach ein Ergebnis;
- Wiederholung: null weitere Runner- oder Carryover-Aufrufe und null Schreibzugriffe;
- Fehler in Periode 4: Versuch protokolliert, kein Ergebnis und kein Teilresultat;
- manipulierte Request-, Ketten- oder Ergebnisdaten: read-only Zugriff blockiert;
- FastAPI und Starlette-Fallback bieten dieselben Methoden und Pfade;
- keine Ausgabedatei, Queue oder automatische Wiederholung;
- `incomming/` bleibt unversioniert und wird nicht gelesen;
- keine historische RNG- oder Vollgleichheitsbehauptung.

## Naechster Schritt

PR146 bindet diesen kontrollierten Fuenf-Perioden-Start an die Workbench an
und nimmt den vollstaendigen Bedienpfad auf breitem und schmalem Viewport,
einschliesslich Fehlerpfaden und Handbuchbild, ab. Der Ausbau auf 10, 25, 50
und 100 Perioden bleibt bis PR147 getrennt gesperrt.
