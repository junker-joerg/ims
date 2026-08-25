# Plan: Workbench-Release-Smoke fuer PR 67

## Ziel

PR 67 wiederholt die vorhandenen Packaging-, Staging- und Startskript-Pruefungen
fuer den nach PR 66 freigegebenen lokalen Workbench-Stand. Die bisherige
Release-Checkliste wird als fester, maschinenpruefbarer Ablauf dokumentiert.

Der PR erweitert weder Simulationskern noch Fachlogik. Er liefert keinen
historischen Vollgleichheitsnachweis und erzeugt kein versioniertes
Release-Artefakt.

## Ursprung und vorhandene Bausteine

| Bestehender Baustein | Verwendung in PR 67 |
| --- | --- |
| `workbench_bundle_build.py` | erzeugt ein explizites lokales ZIP fuer den Smoke |
| `workbench_bundle_smoke.py` | prueft ZIP-Inhalt, Ausschluesse, Metadaten und CRC rein lesend |
| `workbench_portable_staging.py` | staged das gepruefte ZIP in einen leeren lokalen Zielordner |
| `workbench_portable_staging_smoke.py` | prueft Backend, Frontend und portable Skripte rein lesend |
| `workbench_portable_readiness.py` | prueft die portable Pfadstruktur rein lesend |
| `scripts/workbench/check-workbench.cmd` | prueft den Repo-Startkontext ohne Serverstart |
| `scripts/workbench/start-workbench.cmd` | startet ausschliesslich `ims.api.app:app` |

Der isolierte PR-66-Smoke unter `run_control_browser_demo_smoke.py` bleibt eine
separate Testschale. Er darf weder im Repo- noch im portablen Produktionsstart
referenziert werden.

## Umsetzung

1. Ein read-only Release-Smoke fasst ZIP-Smoke und portablen Staging-Smoke fuer
   explizite Pfade zusammen.
2. Er prueft die Repo- und portablen Startskripte auf den normalen
   Produktionsendpunkt `ims.api.app:app`.
3. Er blockiert Referenzen auf den PR-66-Fake-Adapter, den Browser-Demo-Smoke
   oder einen freien Adapterstart in diesen Produktionsskripten.
4. Er meldet stabile JSON-Felder fuer Checklistenstatus, Einzelpruefungen,
   Grenzen und Issues.
5. Der Release-Smoke selbst schreibt nicht und startet keinen Server. ZIP-Build
   und Staging bleiben vorgelagerte, explizite Schritte.

## Verifikation

- positiver Test fuer ein geprueftes ZIP und ein korrekt gestagtes Artefakt;
- Negativtest fuer einen PR-66-Demo-Adapter im Produktionsstartskript;
- Negativtest fuer fehlendes oder fehlerhaftes ZIP/Staging;
- CLI-/JSON-Test fuer den read-only Sammelcheck;
- realer lokaler Frontend-Build, ZIP-Build, ZIP-Smoke, Staging-Smoke und
  Readiness gegen ein temporaeres, nicht versioniertes Ziel;
- kurzlebiger normaler Workbench-Start auf Loopback mit GET auf `/api/health`,
  ohne Run-Control-Aktion und ohne Simulation.

## Grenzen und Risiken

- kein Installer, Release-Tag oder veroeffentlichtes ZIP;
- kein Browser-Upload und kein Queue-Worker;
- kein Start von `controlled_execution_adapter` oder eines Engine-Runners;
- keine neue Fachlogik und keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung;
- lokale Startfaehigkeit belegt nur die technische Auslieferungsgrenze.

## Danach

PR 68 prueft Backup/Restore sowie Update/Rollback fuer lokale Metadaten mit
einem bereits validierten Ergebnisstand. Diese Datenbetriebsprobe bleibt von
der hier eingefrorenen Packaging- und Startgrenze getrennt.
