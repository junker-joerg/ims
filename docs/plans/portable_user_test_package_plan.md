# Plan: Portables Windows-Anwender-Testpaket

Stand: 2026-09-01
Status: umgesetzt

## Ziel

Ein fachlicher Anwender soll die IMS Workbench auf einem anderen Windows-
Rechner ohne Checkout, Git, Node.js oder Frontend-Build testen koennen. Das
Artefakt bleibt ein lokales Testpaket und ist kein nativer Installer.

## Umsetzung

- Das vorhandene, gepruefte Repo-Bundle bleibt die Quellgrenze.
- Das portable Staging erzeugt `install-workbench.cmd`, `check-workbench.cmd`,
  `start-workbench.cmd` und `BITTE-ZUERST-LESEN.txt`.
- Die Installation legt eine lokale `.venv` an und installiert nur die
  versionierten Web-Anforderungen; der fertige Frontend-Build liegt bereits im Paket.
- Check und Start bevorzugen automatisch die lokale `.venv` und fallen fuer
  bestehende Release-Smokes konservativ auf `python` zurueck.
- `build-user-test-package.ps1` baut ein finales ZIP mit eigenem Rootordner,
  den beiden PDF-Handbuechern und ohne lokale Metadaten, Logs oder Caches.

## Anwenderumfang

Das Paket erlaubt Start, Navigation, Lesen vorbereiteter Szenarien und Runs,
Einordnung der historischen Validierung sowie Beurteilung des kontrollierten
Bedienpfads. Es erlaubt keinen freien Datenimport, keinen Szenarioeditor und
keine beliebige Simulation.

## Grenzen

- Windows 10/11 und Python 3.12+ werden vorausgesetzt.
- Die erste Installation benoetigt Internetzugang fuer FastAPI und Uvicorn.
- Das Paket bindet nur an Loopback und richtet keinen Dienst ein.
- Keine Simulation, keine neue Fachlogik und keine historische
  Vollgleichheitsbehauptung.
- `incomming/` bleibt ausgeschlossen.

## Einordnung in die Restplanung

Dieser Auslieferungsschritt ist ein paralleler HB3a-Schnitt und ersetzt PR102
nicht. PR102 schliesst weiterhin den 6.300-Zeilen-Korpus als diagnostischen
Legacy-Benchmark gemaess der am 2026-09-01 angenommenen IMS-2.x-Empfehlung ab.
Linux-Nachweis, iOS/Juno-Entscheidung und Handbuchkonsolidierung bleiben HB4 bis
HB6.
