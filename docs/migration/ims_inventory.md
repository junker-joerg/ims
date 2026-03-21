# Inventar der historischen IMS/ESS-Quellen

Stand: initiale Bestandsaufnahme  
Status: unvollständig, wird in späteren PRs verfeinert

## Ziel dieses Dokuments

Dieses Dokument sammelt die zentralen Altdateien, beschreibt ihren vermuteten Zweck und ordnet sie grob einer künftigen Python-Zielstruktur zu.

## Bestandsliste

### `IMS.E`
Vermutete Rolle:
- zentrale Modellspezifikation
- Definition von Klassen, Aktionen und Simulationsabläufen
- fachlicher Kernbezug

Vorläufige Zielzuordnung:
- `python_port/ims/model/`
- teilweise `python_port/ims/engine/`

Unsicherheiten:
- genaue Trennung zwischen fachlicher Klassenbeschreibung und technischer Ablaufsteuerung noch offen

### `IMSVN.E`
Vermutete Rolle:
- VN-bezogene Logik
- Regeln oder Zustandsfortschreibung für Versicherungsnehmer

Vorläufige Zielzuordnung:
- `python_port/ims/model/`
- später evtl. `python_port/ims/model/rules.py`

Unsicherheiten:
- Granularität der späteren Regelobjekte noch offen

### `IMSVU.E`
Vermutete Rolle:
- VU-bezogene Logik
- Verhaltensregeln, Entscheidungen, Zustandsänderungen auf Versichererseite

Vorläufige Zielzuordnung:
- `python_port/ims/model/`
- später evtl. `python_port/ims/model/rules.py`

Unsicherheiten:
- Trennung zwischen Entität, Regel und Marktinteraktion noch offen

### `IMSSURFE.C`
Vermutete Rolle:
- UI-/Oberflächen- und Dialoghilfen
- terminalnahe Ein-/Ausgabe

Vorläufige Zielzuordnung:
- keine direkte 1:1-Portierung vorgesehen
- nur dokumentationsrelevant
- ggf. minimale CLI-Ersatzschicht in `python_port/ims/io/`

Unsicherheiten:
- welche Teile davon indirekt doch für Inputformate relevant sind, muss später geprüft werden

### `ESS.C`
Vermutete Rolle:
- generischer Simulationskern
- Zeit-/Ereignissteuerung, Scheduling, Listenverwaltung, Aktivierungsmechanik

Vorläufige Zielzuordnung:
- `python_port/ims/engine/`

Unsicherheiten:
- welche Teile rein technisch und welche bereits fachlich aufgeladen sind, muss später genauer kartiert werden

### `IMSRND.C`
Vermutete Rolle:
- Zufallszahlen und Verteilungen
- Grundlage für reproduzierbare Simulation

Vorläufige Zielzuordnung:
- `python_port/ims/engine/rng.py`

Unsicherheiten:
- ob der historische RNG exakt nachgebaut werden muss oder zunächst nur funktional angenähert wird, ist offen

## Grobe Zuordnung nach Themen

### Domäne / Fachlogik
- `IMS.E`
- `IMSVN.E`
- `IMSVU.E`

### Scheduler / Engine / Zeitlogik
- `ESS.C`

### RNG / Stochastik
- `IMSRND.C`

### UI / Terminal / Bedienung
- `IMSSURFE.C`

## Vorläufige Migrationsentscheidung

Die Migration beginnt nicht mit UI-Code, sondern mit:
1. Zielarchitektur
2. Python-Paketgerüst
3. Scheduler-Grundgerüst
4. Zustandscontainer
5. RNG und Reproduzierbarkeit
6. ersten fachlichen Slices

## Offene Punkte

- exaktes Mapping einzelner Altfunktionen zu Python-Modulen
- Abgrenzung von Engine- und Fachlogik in `ESS.C`
- Umfang eines historisch kompatiblen RNG
- spätere Referenzszenarien für Regressionstests
