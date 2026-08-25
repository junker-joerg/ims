# Plan: Abschlussbericht Produktionsfreigabekorpus fuer PR 69

## Ziel

PR 69 fasst den belegten Stand des ersten Produktionsfreigabekorpus zusammen.
Der Bericht trennt technische Workbench-Reife, historische Referenzabdeckung
und unabhaengige berechnete Alt-/Neu-Validierung. Er darf einen technisch
gruenen Demo-/Betriebsstand nicht als fachliche Produktionsfreigabe ausgeben.

## Vorhandene Nachweise

| Nachweis | Aussage |
| --- | --- |
| `legacy_validation_bundle.json` | 19 historische Kernreferenzen und 6.300 eingetragene Vergleichsperioden |
| `legacy_validation_coverage.py` | vorhandene Referenzen, Coverage und Dateiluecken |
| `legacy_calculated_deviation_report.py` | 15 erforderliche berechnete Exporte und blockierende Inputluecken |
| PR 60 | enger berechneter VU14-Aggregat-/Export-Slice fuer vier Perioden |
| PR 66 bis PR 68 | Browser-Demo, Release-Smoke und Metadaten-Recovery |

Die 6.300 ausgerichteten Referenzzeilen pruefen Parser, Header, Fenster,
Selektoren und Reportbildung. Sie sind kein unabhaengiger berechneter
Alt-/Neu-Vollvergleich.

## Umsetzung

1. Ein read-only Bericht baut die bestehende Coverage-Matrix fuer den
   Kernkorpus.
2. Derselbe Bericht baut die bestehende Abweichungsdiagnose ohne erfundene
   berechnete Exporttabellen.
3. Fehlende Kernexporte bleiben als konkrete Blocker sichtbar.
4. Vorhandene Workbench-, Packaging- und Recovery-Dokumente werden nur als
   technische Betriebsnachweise inventarisiert.
5. Eine Migrationsnotiz dokumentiert Freigabeentscheidung, Teststand,
   Bedienpfad, bekannte Abweichungen und offene Voraussetzungen.
6. Die CLI-Uebersicht und das lokale ZIP nehmen Bericht beziehungsweise
   Berichtsdokumentation in ihre bestehenden Grenzen auf.

## Freigabeentscheidung

Der erwartete Stand fuer PR 69 ist:

- Referenzabdeckung vollstaendig fuer den abgegrenzten Kernkorpus;
- technische Workbench-Nachweise dokumentiert;
- unabhaengiger berechneter Kernkorpusvergleich unvollstaendig;
- fachliche Produktionsfreigabe `false`;
- reviewbare lokale Demo weiterhin nutzbar;
- historische Vollgleichheit nicht behauptet.

## Tests

- positiver Bericht fuer den aktuellen 19-/6.300-Korpus;
- exakt 15 fehlende berechnete Exporte als Blocker;
- Negativtest fuer fehlende Referenz oder fehlenden Betriebsnachweis;
- stabile CLI-JSON-Form ohne Schreib- oder Ausfuehrungsflag;
- Doku- und Packaging-Erwartungen;
- vollstaendige Python-Tests und Frontend-Build;
- keine Simulation.

## Grenzen

- keine neuen Referenzdateien und kein Zugriff auf `incomming/`;
- keine neuen Exporttabellen aus Legacy-Zeilen konstruieren;
- keine Simulation, kein Runner- oder Adapterstart;
- keine Fachlogikaenderung;
- keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung;
- keine Produktionsfreigabe trotz technischer Release-Bereitschaft.

## Danach

PR 70 haertet den Abschlussstand als CI-/Windows-Freigabegate fuer Python-
Tests, Frontend-Build, read-only Korpusbericht und Release-Smoke. Die fachliche
Produktionsfreigabe bleibt unabhaengig davon blockiert, bis die 15 berechneten
Kernexporte aus einer belegten Quelle vorliegen und verglichen wurden.
