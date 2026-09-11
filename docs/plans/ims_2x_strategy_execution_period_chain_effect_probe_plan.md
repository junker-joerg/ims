# PR139: Isolierte Zwei-Perioden-Wirkungsprobe

Stand: 2026-09-11
Umsetzungsstand: PR139 umgesetzt

## Ziel

PR139 fuehrt aus einer durch PR138 erneut geprueften, gespeicherten
Periodenkette genau die Perioden 1 und 2 aus. Die beiden Kandidaten werden
vor dem ersten Runneraufruf erneut read-only geladen, auf Digest, Kontext und
Akteursidentitaet geprueft und anschliessend nur als tiefe Kopien verwendet.

Der einzige Uebergang wird exakt nach den in der Kette gespeicherten
`carry_forward_vu_state`- und `carry_forward_vn_state`-Flags ausgefuehrt. Die
Probe schreibt weder Ergebnis noch Idempotenzdaten und ist keine allgemeine
Mehrperiodensimulation.

## Historischer und technischer Bezug

| Quelle | Belegte Aussage | Folge fuer PR139 |
| --- | --- | --- |
| `ESS.C:71-75` | Der historische Lauf schreitet periodisch fort | PR139 prueft erstmals kontrolliert die Reihenfolge 1 nach 2 |
| `IMSDATA.C:14` | `SIMLAENGE = 100` | Zwei Perioden sind nur der kleinste Testausschnitt, nicht der historische Gesamthorizont |
| vorhandene VU-/VN-Runner | Explizite Snapshots koennen eine Periode deterministisch ausfuehren | PR139 orchestriert nur vorhandene Fachbausteine |
| vorhandene Carryover-Funktionen | VU- und VN-Zustand koennen getrennt fortgeschrieben werden | die gespeicherten Uebergangsflags werden einzeln und unveraendert beachtet |

Der historische C-Code kennt weder Ketten-ID noch SHA-256-Freigabe. Diese
Elemente sind moderne Kontrollgrenzen und keine portierte Fachlogik.

## Kontrollierter Ablauf

1. Exakten PR139-Request und ausdrueckliche Probenfreigabe pruefen.
2. PR138-Freigabecheck fuer Ketten-ID und Volldigest erneut ausfuehren.
3. Genau zwei Perioden und genau den Uebergang 1 nach 2 verlangen.
4. Beide Kandidaten vor dem ersten Runneraufruf vollstaendig neu aufloesen.
5. Kandidatenkopien laden und Kontexte sowie Akteursidentitaeten abgleichen.
6. Periode 1 ohne Ausgabepfad ausfuehren.
7. VU-/VN-Carryover exakt nach den gespeicherten Flags anwenden.
8. Periode 2 ohne Ausgabepfad ausfuehren.
9. Nur fluechtige Wirkungs- und Carryover-Diagnosen zurueckgeben.

Jeder Fehler vor Schritt 6 verhindert beide Runneraufrufe. Ein Fehler waehrend
der Ausfuehrung beendet die Probe ohne Teilresultat und ohne Speicherung.

## Schutzgrenzen

- genau zwei lokale Perioden, keine freie Horizontwahl;
- keine freie Kandidaten-, Fixture-, Datenbank- oder Ausgabepfaduebergabe;
- keine Queue, keine dauerhafte Freigabe und keine Ergebnisablage;
- keine Aenderung gespeicherter Ketten oder Kandidaten;
- keine neue oder geaenderte VU-/VN-Fachlogik;
- kein Legacy-Vergleich und keine historische RNG- oder
  Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.

## Restplanung

- **PR139 (umgesetzt):** isolierte, fluechtige Zwei-Perioden-
  Wirkungsprobe mit atomarem Fehlerstopp.
- **PR140 (naechster Schritt):** kontrollierter Workbench-Start mit
  dauerhafter Idempotenz und
  unveraenderlicher Ergebnisablage fuer genau diese Zwei-Perioden-Probe.
- **PR141:** Browserabnahme auf breitem und schmalem Viewport sowie
  Handbuch-Screenshots fuer den Zwei-Perioden-Bedienpfad.
- **PR142+:** Horizonte schrittweise erweitern und jeweils gesondert
  validieren, bis 100 Perioden reviewbar und stabil bedienbar sind.
