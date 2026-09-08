# PR126: Kanonischer gemeinsamer Ausfuehrungskandidat

Stand: 2026-09-08

## Ergebnis

PR126 verbindet die vorhandenen Validierungs- und Materialisierungsbausteine
erstmals zu einem vollstaendigen, aber weiterhin fluechtigen
Einperioden-Kandidaten. Nur ein fehlerfreier PR125-Eingang kann einen
Kandidaten erzeugen.

Der neue Pfad ruft keine Regelanwendung und keinen Runner auf. Er setzt nur
die Datenstrukturen zusammen, die ein spaeterer kontrollierter Lauf verwenden
koennte.

## Herkunft und Entsprechung

| Ursprung oder Vorarbeit | Heutige Komponente | Verwendung in PR126 |
| --- | --- | --- |
| `IMS.E`, `Vrvu01` bis `Vrvu10` | `assignment_vu_snapshot_materialization.py` | VU-Regelsnapshots neu erzeugen |
| `IMS.E`, `Vrvn01` bis `Vrvn06` | `assignment_snapshot_materialization.py` | VN-Regelsnapshots neu erzeugen |
| PR125-Gesamtvalidator | `execution_candidate_validation.py` | alle Quellen vor dem Bau atomar pruefen |
| Szenarioeinlesung | `scenario_loader.py` | Population und Snapshotreferenzen gemeinsam pruefen |
| neuer Orchestrator | `execution_candidate_build.py` | Profil, Snapshots, Kanonisierung und Digest verbinden |

Es wurde keine VU-, VN-, Schaden- oder Abrechnungsregel geaendert.

## Lokales Profil

Die stabile ID `synthetic-joint-single-period-v1` ist serverseitig genau der
versionierten Paketdatei
`python_port/ims/strategies/profiles/strategy_execution_candidate_profile_v1.json`
zugeordnet.
Der Request kennt nur die ID und keinen Dateipfad.

Das Profil liefert ausschliesslich:

- `SimulationContext` fuer Periode 2;
- einen BAV-Zustand;
- ein synthetisches VU und ein synthetisches VN;
- Vorperioden- und aktuelle Marktwerte.

Es liefert keine VU-/VN-Regelsnapshots. Damit koennen alte oder vom Browser
eingeschleuste Snapshotlisten die serverseitige Neu-Materialisierung nicht
umgehen.

Vor der Verwendung werden Profil-ID, Schema, Basismodell, Periode, Horizont,
BAV-ID und beide Populationen gegen die PR125-Referenz geprueft. Die
registrierte Datei muss innerhalb des festgelegten Paket-Profilverzeichnisses
liegen und wird auch in Python-Pakete und portable Workbench-Bundles
aufgenommen.

## Kandidatenbau

Der Builder arbeitet in dieser Reihenfolge:

1. gesamten Eingang mit PR125 pruefen;
2. registriertes Profil laden und als Marktgrundzustand validieren;
3. VU-Snapshots mit PR121 aus den Originalquellen neu materialisieren;
4. VN-Snapshots mit PR116 aus denselben Originalquellen neu materialisieren;
5. explizite VN-Schadenprozesswerte aus dem PR125-Eingang ergaenzen;
6. das Gesamtmapping mit dem bestehenden Szenarioloader als
   `LoadedScenario` laden;
7. Entitaeten und Snapshot-Sammlungen nach ihren Ziel-IDs ordnen;
8. Quelldokumente, Vertragsversionen, Marktgrundzustand, Snapshots und feste
   Ausfuehrungsgrenzen kanonisch serialisieren;
9. den SHA-256-Inhaltsdigest und daraus die deterministische Kandidaten-ID
   bilden.

Bei jedem Fehler ist `candidate = null` und
`partial_candidate_returned = false`. Intern bereits erzeugte Snapshots
werden nicht als Teilresultat veroeffentlicht.

## Digestvertrag

Die Digestbasis enthaelt:

- Kandidatenschema, Entwurfs-ID und Periode;
- alle relevanten Upstream-Vertragsversionen;
- die normalisierten Original-Quelldokumente;
- den geladenen Marktgrundzustand und dessen eigenen Profildigest;
- alle elf kanonischen `LoadedScenario`-Snapshot-Sammlungen;
- die fest geschlossenen Ausfuehrungsgrenzen.

JSON-Objektschluessel werden sortiert, Sammlungen nach Akteurs-ID geordnet,
Nicht-Endlich-Werte abgelehnt und kompakte ASCII-JSON-Trennzeichen verwendet.
`candidate_id` und `content_digest` selbst sind nicht Teil der Digestbasis.

Der Digest belegt die Identitaet dieses modernen Eingabekandidaten. Er ist
kein Nachweis einer historischen RNG- oder Ergebnisgleichheit.

## API

- `GET /api/strategies/execution-candidate-build-contract`
- `POST /api/strategies/execution-candidate-build`

Der POST-Endpunkt liefert den Kandidaten nur in der Antwort. Er schreibt
weder Datei noch Datenbank.

## Weiterhin gesperrt

- Kandidatenpersistenz und spaetere Wiederauflosung;
- Run-Control, Queue und Freigabe;
- Regelanwendung, Einperiodenrunner und Mehrperiodenlauf;
- Carryover, Ergebnisdateien und Legacy-Vergleich;
- Simulation sowie historische RNG- oder Vollgleichheitsbehauptung.

## Naechster Schritt

PR127 soll einen erfolgreichen PR126-Kandidaten nur nach eigener expliziter
Speicherfreigabe unveraenderlich ablegen. Vor und nach der Ablage wird sein
Digest erneut geprueft. Runner und Simulation bleiben weiterhin gesperrt.
