# PR124: Gemeinsamen Ausfuehrungskandidaten als Vertrag beschreiben

Stand: 2026-09-08

## Ziel

PR124 versioniert die Form des spaeteren gemeinsamen Einperioden-
Ausfuehrungskandidaten fuer vorbereitete VU- und VN-Snapshots. Der Vertrag
benennt Pflichtabschnitte, kanonische `LoadedScenario`-Sammlungen, offene
Anschlussarbeiten und feste Sperrfelder.

Der Schritt nimmt keinen Kandidateneingang entgegen, validiert und erzeugt
keinen Kandidaten, berechnet keinen Digest, speichert nichts und startet
keinen Runner.

## Grundlage

- PR108 bis PR116 liefern versionierte Strategieentwuerfe, Kontextwerte und
  die atomare VN-Snapshot-Materialisierung.
- PR118 bis PR121 liefern VU-Bestand, Eingang, Zustandsbeleg und atomare
  VU-Snapshot-Materialisierung.
- PR123 entscheidet, dass nur eine serverseitige Neumaterialisierung aus den
  Quelldokumenten autoritativ sein darf.
- `ims.io.scenario_loader.LoadedScenario` stellt die heutige technische
  Sammlungskante bereit.
- `ims.engine.explicit_period_runner.run_loaded_explicit_period` bleibt ein
  lediglich benannter spaeterer Anschlussanker.

## Umsetzung

1. Eigenes Schema `ims.strategy-execution-candidate.v1` beschreiben.
2. Acht Pflichtabschnitte fuer Identitaet, Vertragsversionen,
   Quelldokumente, Marktgrundzustand, VU-/VN-Regeln, VN-Prozess und
   Ausfuehrungsgrenzen festlegen.
3. Acht VU-Regelsammlungen, eine VN-Regelsammlung und zwei disjunkte
   VN-Prozesssammlungen explizit auffuehren.
4. Die vorhandenen Upstream-Vertragsversionen lesend einbetten.
5. Sechs offene Anforderungen den PRs 125, 126, 127, 129 und 130 zuordnen.
6. Den Vertrag nur ueber
   `GET /api/strategies/execution-candidate-contract` bereitstellen.

## Schutzgrenzen

- kein Kandidateneingang und keine Kandidatenvalidierung;
- keine Aufloesung eines Szenarioprofils;
- keine Snapshotloader oder erneute Materialisierung;
- keine Digestberechnung oder Kandidatenerzeugung;
- keine Speicherung, Run-Control-Kopplung oder Runnerausfuehrung;
- kein Carryover, keine Ausgabedateien und kein Legacy-Vergleich;
- keine Simulation und keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.

## Validierung

- Pflichtabschnitte und Upstream-Versionen werden als stabile Vertragsform
  geprueft.
- Die elf Sammlungen werden gegen die vorhandenen VU-Ziele und
  `LoadedScenario` abgeglichen.
- Alle offenen Anschlussarbeiten und Sperrfelder werden geprueft.
- Der API-Test erlaubt nur `GET`.
- Ein Grenztest belegt, dass Materialisierer und Runner nicht aufgerufen
  werden.

## Naechster Schritt

PR125 hat einen zustandslosen, atomaren Validator fuer den gemeinsamen
Kandidateneingang eingefuehrt. PR126 darf als naechstes nur einen gueltigen
Eingang verwenden, das bekannte lokale Szenarioprofil serverseitig aufloesen,
VU und VN neu materialisieren sowie ein kanonisches `LoadedScenario` samt
Digest bauen. Speicherung und Ausfuehrung bleiben gesperrt.
