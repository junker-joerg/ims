# PR140: Kontrollierter Workbench-Start fuer zwei Perioden

Stand: 2026-09-14
Umsetzungsstand: PR140 umgesetzt

## Ziel

PR140 macht die in PR139 eingefuehrte Zwei-Perioden-Wirkungsprobe
kontrolliert bedienbar. Eine gespeicherte Kette wird in der Workbench
read-only ausgewaehlt, ausdruecklich freigegeben und hoechstens einmal
ausgefuehrt. Startversuch und vollstaendiges Ergebnis werden in der
konfigurierten SQLite-Metadatenquelle nachweisbar abgelegt.

Der Schnitt bleibt auf Periode 1 und 2 sowie genau einen gespeicherten
Uebergang begrenzt. Er ist keine freie Mehrperiodensimulation.

## Historischer und technischer Bezug

| Quelle | Belegte Aussage | Folge fuer PR140 |
| --- | --- | --- |
| `ESS.C:71-75` | Der historische Lauf schreitet periodisch fort | PR140 bedient weiterhin nur den kleinsten Ausschnitt 1 nach 2 |
| `IMSDATA.C:14` | `SIMLAENGE = 100` | 100 Perioden bleiben ein spaeterer Ausbau, nicht Teil dieses PRs |
| PR139 | Zwei Kandidatenkopien und gespeicherte Carryover-Flags koennen atomar wirken | PR140 ruft diesen Pfad unveraendert auf |
| PR131 | Einperiodenstarts besitzen Idempotenz und Ergebnisnachweis | dasselbe Kontrollmuster wird kettenspezifisch fortgefuehrt |

Ketten-ID, SHA-256-Digests und SQLite-Nachweise sind moderne
Kontrollgrenzen. Sie haben keine direkte C-Entsprechung und aendern keine
historische Fachregel.

## Kontrollierter Ablauf

1. Gespeicherte Ketten read-only auflisten und beim Lesen verifizieren.
2. Exakten PR139-Request mit Person, Grund und Zeitstempel bilden.
3. PR138-Freigabecheck vor dem atomaren Startanspruch wiederholen.
4. Ketten-ID und Idempotenzschluessel mit `BEGIN IMMEDIATE` reservieren.
5. Parallele, abweichende oder bereits erfolgreich ausgefuehrte Starts
   blockieren.
6. PR139 mit zwei isolierten Kandidatenkopien ausfuehren.
7. Nur das vollstaendige Ergebnis samt eigenem Digest speichern.
8. Fehler ohne Teilresultat als fehlgeschlagenen Versuch festhalten.
9. Identische erfolgreiche Wiederholung ohne Runner aus der Ablage lesen.

Nach einem fehlgeschlagenen Versuch ist ein neuer manueller Start mit neuem
Idempotenzschluessel moeglich. Automatische Wiederholungen bleiben gesperrt.

## Workbench

Der neue Tab `Periodenkette` zeigt:

- alle verifiziert gespeicherten Ketten und ihren Horizont;
- Ketten-, Kandidaten- und Carryover-Status;
- Freigabeperson, Grund und ausdrueckliche Zwei-Perioden-Bestaetigung;
- Wirkung und Regelanwendungen fuer Periode 1 und 2;
- den dazwischen ausgefuehrten VU-/VN-Carryover;
- Speicherzeit, Ergebnisdigest und read-only Versuchsverlauf.

Ketten mit einem anderen Horizont bleiben sichtbar, koennen an dieser Grenze
aber nicht gestartet werden.

## Schutzgrenzen

- exakt zwei Perioden und genau ein gespeicherter Uebergang;
- keine Aenderung der PR139-Runner- oder Carryover-Logik;
- keine freie Ketten-, Kandidaten-, Datenbank- oder Pfaduebergabe;
- keine Queue, kein Worker und kein automatischer Retry;
- keine fachlichen Ausgabedateien;
- kein Legacy-Vergleich und keine historische RNG- oder
  Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.

## Restplanung

- **PR140 (umgesetzt):** kontrollierter Workbench-Start, dauerhafte
  Idempotenz, unveraenderliche Ergebnisablage und read-only Verlauf fuer
  genau zwei Perioden.
- **PR141 (umgesetzt):** Browserabnahme auf breitem und schmalem
  Viewport, Fehlerpfade und Handbuch-Screenshots fuer den Zwei-Perioden-Pfad.
- **PR142 (umgesetzt):** read-only Vertrag fuer zwei bis fuenf Perioden und
  exakte fachliche Prefixprojektion 1-2.
- **PR143 (umgesetzt):** kanonische Fuenf-Perioden-Kette gebaut und atomar
  validiert, weiterhin ohne Runner.
- **PR144 (umgesetzt):** isolierte Fuenf-Perioden-Wirkungsprobe und
  exakter fachlicher Prefixnachweis 1-2.
- **PR145+:** Horizonte in getrennten, getesteten Stufen ausfuehren;
  Bedienung und Ergebnisvertrag jeweils mitziehen.
- **100-Perioden-Gate:** erst nach deterministischer Prefix-Pruefung,
  Laufzeit-/Abbruchtest, Ergebnisbundle und eigener Browserabnahme oeffnen.

Die Zahl der dafuer noetigen PRs bleibt eine Planungsannahme. Neue Fachlogik,
Bilanz, XLSX und Regulierungsszenarien werden nicht still in die
Horizonterweiterung aufgenommen.
