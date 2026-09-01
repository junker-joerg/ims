# Portables Windows-Anwender-Testpaket

## Ziel

Der bestehende ZIP-/Staging-Vertrag wird als einfach weitergebbares
Windows-Testpaket abgeschlossen. Ein Anwender benoetigt auf dem Zielrechner nur
Python 3.12+, beim ersten Installieren Internetzugang und einen Browser.

## Ursprung und Zuordnung

| Ursprung | Umsetzung | Bedeutung |
| --- | --- | --- |
| `workbench_portable_staging.py` | generiertes Installationsskript und `.venv`-Auswahl | lokale Web-Abhaengigkeiten ohne globale Installation |
| `frontend/dist` | unveraendert ins portable Layout | kein Node.js-Build auf dem Zielrechner |
| `python_port/requirements-web.txt` | Installation in `.venv` | FastAPI-/Uvicorn-Laufzeit fuer die lokale Workbench ohne Paket-Build |
| Handbuchquellen | zwei PDF-Dateien im Paket | 2 Seiten Installation und 10 Seiten Bedienung mit 8 Modell-, Dissertations- und UI-Abbildungen |
| `build-user-test-package.ps1` | finales ZIP mit Rootordner | ein Artefakt zum Kopieren und Entpacken |

Es wird keine historische C-Logik portiert oder geaendert. Der Schnitt betrifft
ausschliesslich Packaging, lokale Laufzeitwahl und Anwenderdokumentation.

## Validierung

- Unit-Tests pruefen generierte Skripte, `.venv`-Auswahl und Erstlesedokument.
- Der bestehende Staging-Smoke importiert weiterhin Backendmodule aus dem
  portablen Root und startet keinen Server.
- Das finale ZIP wird nach dem Bau erneut geoeffnet und auf Pflichtdateien
  geprueft.
- Der lokale Abnahmelauf prueft Installation, Check und Loopback-Health ohne
  Queue-Aktion, Adapterstart oder Simulation.

## Offene Punkte

Das Paket enthaelt keine Python-Laufzeit und kein Offline-Wheelhouse. Ein
nativer Installer, Codesignierung, automatisches Update, Linux und iOS/Juno
bleiben getrennte Schritte. Die fachliche Produktionsfreigabe bleibt von der
technischen Portabilitaet unabhaengig.

## Lokaler Nachweis vom 2026-09-01

- finales ZIP: 909.712 Bytes;
- SHA-256: `a420b33098c641fc52cca033c8a52e1af36189a5f954176b5f108b42ec8e0973`;
- Entpacken und Installation in einem neuen Pfad mit Leerzeichen erfolgreich;
- lokale `.venv` mit Python 3.13 und Web-Anforderungen erfolgreich aufgebaut;
- portable Diagnose und Readiness jeweils `status = ok`;
- normaler Start auf `127.0.0.1:8000`, `GET /api/health` mit HTTP 200 und
  `frontend_available = true`;
- Server danach beendet und Port wieder geschlossen;
- keine Queue-Aktion, kein Adapterstart und keine Simulation.
