# PR144: Fuenf-Perioden-Wirkungsprobe mit Prefixnachweis

Stand: 2026-09-14
Umsetzungsstand: PR144 umgesetzt

## Ziel

PR144 fuehrt die in PR143 atomar gebaute Kette erstmals fuer genau fuenf
Perioden aus. Die Ausfuehrung arbeitet ausschliesslich auf isolierten Kopien
der gespeicherten Kandidaten und liefert nur ein fluechtiges Gesamtergebnis.

Vor den Perioden 3 bis 5 muss die fachliche Projektion aus Periode 1,
Uebergang 1->2 und Periode 2 kanonisch bytegleich mit einem bereits
gespeicherten und erneut geprueften PR140-Zwei-Perioden-Ergebnis sein.

## Historischer Bezug

| Quelle | Belegte Semantik | Grenze fuer PR144 |
| --- | --- | --- |
| `ESS.C:73-75` | streng aufsteigende historische Periodenschleife | genau fuenf explizite Aufrufe, keine freie Schleife |
| `IMSDATA.C:14` | historischer Zielhorizont `SIMLAENGE = 100` | fuenf Perioden sind nur eine moderne Freigabestufe |
| `compute_global_period` | `run_index * max_periods + period` | Referenz und Probe muessen fuer den Prefix dieselben Globalperioden liefern |
| PR139/PR140 | Zwei-Perioden-Wirkung und unveraenderliches Ergebnis | gespeichertes PR140-Ergebnis ist die unabhaengige Prefixreferenz |
| PR142/PR143 | Prefixvertrag und kanonische Fuenf-Perioden-Kette | werden ohne neue VU-/VN-Regel wiederverwendet |

## Ausfuehrungsgrenze

Der neue Request enthaelt:

- den unveraenderten PR143-Ketteneingang fuer genau fuenf Perioden;
- Ketten-ID und erwarteten Kettendigest der gespeicherten
  Zwei-Perioden-Referenz;
- den erwarteten Ergebnisdigest dieser Referenz;
- eine explizite Freigabe nur fuer die fluechtige Fuenf-Perioden-Probe.

Vor Periode 1 werden die vollstaendige Kette, alle fuenf Kandidatenkopien
und das gespeicherte Referenzergebnis geprueft. Nach Periode 2 werden beide
Prefixprojektionen als kanonisches JSON verglichen. Die erste Abweichung
blockiert die Perioden 3 bis 5 und gibt kein Teilresultat zurueck.

## Validierung

Unit- und API-Tests belegen:

- exakt fuenf Perioden und vier geordnete Uebergaenge;
- autoritative VU-/VN-Carryover-Flags und acht Aufrufe im Vollfall;
- semantisch und byteweise gleiche Prefixprojektionen ohne Toleranz;
- deterministisch identische Wiederholung;
- Abbruch nach Periode 2 bei abweichender Globalperiode;
- Abbruch vor Periode 1 bei fehlender Prefixreferenz;
- kein Teilresultat nach einem spaeteren Runnerfehler;
- unveraenderte Kandidaten und unveraenderte SQLite-Datei;
- gleiche Semantik in FastAPI und Starlette-Fallback.

## Restplanung

- **PR144 (umgesetzt):** isolierte fluechtige Fuenf-Perioden-Wirkungsprobe
  mit exaktem Prefixnachweis fuer Perioden 1 und 2.
- **PR145 (naechster Schritt):** kontrollierter Start, dauerhafte
  Idempotenz und unveraenderliche Ergebnisablage fuer fuenf Perioden.
- **PR146:** Workbench- und Browserabnahme auf breitem und schmalem Viewport
  samt Fehlerpfaden und Handbuch-Screenshot.
- **PR147-PR151:** gestufter Horizont bis 100 Perioden, Ergebnisbuendel und
  auswertbarer Ergebnisarbeitsplatz gemaess Produkt-Roadmap.

## Schutzgrenzen

- keine neue oder geaenderte VU-/VN-Fachlogik;
- kein freier oder allgemeiner Simulationsrunner;
- keine Speicherung, Queue, Workbench-Freigabe oder Ausgabedatei;
- kein Legacy-Vergleich und keine historische RNG- oder
  Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert und wird nicht gelesen.
