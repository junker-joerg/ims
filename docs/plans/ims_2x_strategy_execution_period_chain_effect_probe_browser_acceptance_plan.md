# PR141: Browserabnahme der Zwei-Perioden-Wirkungsprobe

Stand: 2026-09-14
Umsetzungsstand: PR141 umgesetzt

## Ziel

PR141 nimmt den in PR140 bedienbar gemachten Zwei-Perioden-Pfad auf einem
breiten und einem schmalen Browser-Viewport ab. Die sichtbare Freigabe,
beide Periodenwirkungen, der Carryover, der unveraenderliche Ergebnisnachweis
und der Verlauf werden mit einer reproduzierbaren Loopback-Instanz geprueft
und im Benutzerhandbuch belegt.

Der Schnitt fuegt keine Fachlogik hinzu. Er oeffnet weder einen allgemeinen
Kettenrunner noch einen 100-Perioden-Lauf.

## Historischer Bezug

| Quelle | Bereits belegte Semantik | Folge fuer PR141 |
| --- | --- | --- |
| `ESS.C:71-75` | historischer periodischer Ablauf | sichtbar bleibt nur der in PR139/PR140 belegte Ausschnitt 1 nach 2 |
| `IMSDATA.C:14` | `SIMLAENGE = 100` | der historische Zielhorizont bleibt geschlossen |
| PR139 | isolierte Wirkung fuer Periode 1 und 2 mit VU-/VN-Carryover | der Browser-Smoke nutzt diesen Pfad unveraendert |
| PR140 | dauerhafte Idempotenz und unveraenderliche Ergebnisablage | Ergebnis und Verlauf werden im Browser abgenommen |

PR141 portiert keine C-Regel. Viewportpruefung, Loopback-Smoke und
Screenshots sind moderne Abnahme- und Dokumentationsmittel.

## Isolierter Smoke-Aufbau

`ims.api.strategy_execution_period_chain_effect_probe_browser_smoke`
erzeugt je Abnahme:

- eine frische SQLite-Metadatenquelle;
- zwei serverseitig neu gebaute und unveraenderlich gespeicherte Kandidaten
  fuer Periode 1 und 2;
- eine daraus serverseitig neu gebaute und unveraenderlich gespeicherte
  Periodenkette;
- das regulaere gebaute Workbench-Frontend;
- einen ausschliesslich an Loopback gebundenen Webserver.

Bestehende Datenbanken, nicht frische Profilverzeichnisse, fehlende
Frontend-Builds und Nicht-Loopback-Adressen werden abgewiesen.
`incomming/` bleibt unversioniert und wird nicht gelesen.

## Browsermatrix

| Sicht | Viewport | Abnahmekriterien |
| --- | --- | --- |
| breit | 1440 x 1000 | Kettenidentitaet, beide Periodenwirkungen, Carryover, Ergebnisdigest, Verlauf und geschlossene Mehrperiodengrenze sind lesbar |
| schmal | 390 x 844 | einspaltiger Aufbau ohne horizontales Abschneiden, Ueberlagerung oder unlesbare Bedienfelder |

## Bedienfolge

1. `Strategien` und den Tab `Periodenkette` oeffnen.
2. Horizont 1-2, zwei Kandidaten, Digest und beide Carryover-Flags pruefen.
3. Person und konkreten Grund der Freigabe erfassen.
4. Periode 1 und 2 mit gespeichertem Carryover ausdruecklich bestaetigen.
5. `Zwei Perioden starten` ausloesen.
6. beide Periodenwirkungen und den Uebergang 1 nach 2 lesen.
7. Ergebnisdigest, unveraenderliche Speicherung und Verlauf pruefen.
8. den gesperrten Wiederholungs- und Mehrperiodenpfad kontrollieren.

## Fehlerpfade

- Ohne ausdrueckliche Checkbox bleibt der Startknopf deaktiviert.
- Eine fehlende Ausfuehrungsfreigabe wird vor Schreiben oder Runner mit
  `400` abgewiesen.
- Ein falscher Kettendigest wird atomar mit `409` abgewiesen.
- Ein Runnerfehler in Periode 2 liefert kein Teilresultat und keinen
  Ergebnisdatensatz; der fehlgeschlagene Versuch bleibt im Verlauf sichtbar.
- Eine identische erfolgreiche Wiederholung liest das vorhandene Ergebnis
  ohne weitere Runner- oder Carryover-Aufrufe.

## Restplanung

- **PR141 (umgesetzt):** Browserabnahme, Fehlerpfade und datierte
  Handbuch-Screenshots fuer den Zwei-Perioden-Bedienpfad.
- **PR142 (umgesetzt):** read-only Vertrag fuer einen Kettenrunner mit zwei
  bis fuenf Perioden und exakter fachlicher Prefixprojektion 1-2.
- **PR143 (umgesetzt):** kanonische Fuenf-Perioden-Kette gebaut und atomar
  validiert, weiterhin ohne Runner.
- **PR144 (umgesetzt):** isolierte Fuenf-Perioden-Wirkungsprobe und
  exakter fachlicher Prefixnachweis 1-2.
- **PR145+:** Horizonte in getrennten, deterministisch geprueften Stufen
  ausfuehren; Bedienung und Ergebnisvertrag jeweils mitziehen.
- **100-Perioden-Gate:** erst nach Prefix-, Laufzeit-, Abbruch-, Ergebnisbundle-
  und eigener Browserabnahme oeffnen.

## Schutzgrenzen

- keine neue oder geaenderte VU-/VN-Fachlogik;
- exakt zwei Perioden und ein gespeicherter Uebergang;
- keine freie Kandidaten-, Ketten-, Datenbank-, Fixture- oder
  Ausgabepfaduebergabe aus dem Browser;
- keine fachlichen Ausgabedateien und kein Legacy-Vergleich;
- keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.
