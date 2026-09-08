# PR126: Gemeinsamen Ausfuehrungskandidaten kanonisch bauen

Stand: 2026-09-08

## Ziel

PR126 nimmt ausschliesslich einen vollstaendig gueltigen PR125-Eingang,
loest dessen stabile Szenarioprofil-ID serverseitig auf, materialisiert die
VU- und VN-Regelsnapshots erneut und baut daraus atomar ein kanonisches
`LoadedScenario` samt reproduzierbarem Inhaltsdigest.

Der Kandidat bleibt fluechtig. Speicherung, Run-Control, Runner und
Simulation werden nicht angebunden.

## Bestehende Grundlage

- PR116 materialisiert gueltige VN-Kontexte in vorhandene
  `VNInsuranceRuleSnapshot`-Objekte.
- PR121 materialisiert gueltige VU-Kontexte in die acht vorhandenen
  VU-Snapshot-Sammlungen.
- PR124 beschreibt die Pflichtabschnitte und Sammlungen des gemeinsamen
  Kandidaten.
- PR125 prueft Entwurf, Kontext, VU-Zustandsbeleg, Profilreferenz und
  VN-Prozesseingang gemeinsam und ohne Seiteneffekte.
- `ims.io.scenario_loader.load_scenario_from_mapping` prueft Population,
  Referenzen und die disjunkten VN-Prozesssammlungen beim Aufbau eines
  `LoadedScenario`.

Historische fachliche Herkunft bleiben die bereits dokumentierten Aktionen
`Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06` aus `IMS.E`. PR126 veraendert
keine ihrer Regeln.

## Profilentscheidung

Der Request enthaelt weiterhin keinen Pfad. Eine feste serverseitige Registry
ordnet eine stabile Profil-ID genau einer versionierten JSON-Datei im
auslieferbaren Python-Paket zu.

Die Aufloesung prueft vor jeder Materialisierung:

1. Pfad bleibt innerhalb des vertrauenswuerdigen Paket-Profilverzeichnisses;
2. Profil-ID, Schema, Basismodell und Periode stimmen;
3. BAV-, VU- und VN-IDs entsprechen exakt der PR125-Referenz;
4. die Datei enthaelt nur Marktgrundzustand, keine vorgegebenen
   Regelsnapshots;
5. der Grundzustand kann mit dem vorhandenen Szenarioloader geladen werden.

## Atomarer Bau

1. PR125-Eingang erneut vollstaendig validieren.
2. Bekanntes lokales Profil aufloesen und seinen Inhalt pruefen.
3. PR121-VU-Eingang aus gemeinsamem Entwurf, Kontext, Policy und
   Zustandsbeleg zusammensetzen und serverseitig materialisieren.
4. PR116-VN-Eingang aus demselben Entwurf und Kontext materialisieren.
5. Materialisierte Regel-Snapshots und explizite VN-Prozesswerte in das
   Profil-Mapping einordnen.
6. Das Gesamtmapping mit `load_scenario_from_mapping` als ein
   `LoadedScenario` laden und damit Referenzen und Sammlungen gemeinsam
   pruefen.
7. Entitaeten und Snapshot-Sammlungen stabil nach Ziel-ID ordnen.
8. Versionen, Quelldokumente, Marktgrundzustand, alle Snapshots und feste
   Ausfuehrungsgrenzen als kanonisches JSON serialisieren.
9. `sha256` ueber genau dieses JSON bilden und daraus die deterministische
   Kandidaten-ID ableiten.

Erst nach Schritt 9 wird ein Kandidat veroeffentlicht. Jeder Fehler liefert
einen vollstaendigen Fehlerbericht ohne Teilkandidat.

## API

- `GET /api/strategies/execution-candidate-build-contract` beschreibt
  Profilquelle, Digestbasis und geschlossene Grenzen.
- `POST /api/strategies/execution-candidate-build` baut genau einen
  fluechtigen Kandidaten in-memory.
- Freie Profil- und Ausgabepfade sowie andere HTTP-Methoden bleiben gesperrt.

## Schutzgrenzen

- keine neue oder geaenderte VU-/VN-Fachregel;
- keine vom Browser gelieferten Materialisierungsberichte;
- keine RNG-Ziehung und kein Fallback fuer fehlende Draws;
- keine Kandidatenablage und keine Metadatenbank-Aenderung;
- kein Run-Control-, Runner-, Carryover- oder Exportanschluss;
- keine Simulation und kein Legacy-Vergleich;
- keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.

## Validierung

- deterministischer Positivfall mit wiederholbar identischem Digest;
- unbekannte Profil-ID und abweichende Profilpopulation sperren vor der
  Materialisierung;
- Materialisierungs- und finaler Szenarioladefehler liefern keinen
  Teilkandidaten;
- Listenreihenfolgen werden im Kandidaten kanonisch geordnet;
- Grenztest verhindert Speicherung, Runner und Simulation;
- API- und Invalid-JSON-Tests;
- Gesamtregression ohne neuen Simulationsstart.

## Naechster Schritt

PR127 ergaenzt fuer vollstaendige PR126-Kandidaten eine gesondert
freizugebende, unveraenderliche Ablage mit erneuter Digest-Pruefung. Ein Start
oder Runneraufruf bleibt auch dort gesperrt.
