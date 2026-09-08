# PR124: Vertrag fuer den gemeinsamen Ausfuehrungskandidaten

Stand: PR124, 2026-09-08

## Ergebnis

PR124 stellt die spaetere Verbindung der gemeinsam vorbereiteten VU- und
VN-Snapshots erstmals als versionierten, rein lesenden Vertrag dar. Der
Vertrag beschreibt noch keinen vorhandenen Kandidaten. Er legt fest, welche
Teile vor einer spaeteren Freigabe gemeinsam und unveraenderlich vorliegen
muessen.

Das Vertragsschema lautet
`ims.strategy-execution-candidate-contract.v1`; die geplante Kandidatenform
lautet `ims.strategy-execution-candidate.v1`.

## Pflichtabschnitte

| Abschnitt | Inhalt | Spaetere Herkunft |
| --- | --- | --- |
| Identitaet | Kandidaten-ID, Entwurfs-ID, Periode, Inhaltsdigest | serverseitiger Builder |
| Vertragsversionen | Versionen aller Quell- und Materialisierungsvertraege | versionierte Quellen |
| Quelldokumente | Entwurf, Kontext, VU-Eingang und -Zustand, VN-Prozess, Szenarioprofil-ID | Originaldokumente |
| Marktgrundzustand | vollstaendiger Kontext, BAV, VU und VN | bekanntes lokales Szenarioprofil |
| VU-Regeln | acht VU-Snapshot-Sammlungen | erneute PR121-Materialisierung |
| VN-Regeln | `vn_insurance_rule_snapshots` | erneute PR116-Materialisierung |
| VN-Prozess | Schaden-/Settlement-Snapshots und explizite Ziehungshistorie | eigener Prozesseingang |
| Grenzen | Persistenz, Run-Control, Runner, Carryover, Dateien und Legacy-Vergleich | fester Vertrag |

Die vorhandenen Materialisierungsberichte aus dem Browser sind keine
autoritative Quelle. Ein spaeterer Serverpfad muss die urspruenglichen
versionierten Dokumente erneut pruefen und materialisieren.

## Kanonische Sammlungen

Der Vertrag nennt exakt die elf Sammlungen von `LoadedScenario`:

- acht vorhandene VU-Regelsammlungen;
- `vn_insurance_rule_snapshots`;
- `vn_damage_settlement_snapshots`;
- `vn_settlement_snapshots`.

Die beiden VN-Prozesssammlungen bilden eine disjunkte Alternative je Ziel.
PR124 prueft diese Bedingung noch nicht und erzeugt keine dieser Listen.

## Herkunft und Altmodell

Die VU- und VN-Regeln bleiben den bereits dokumentierten Aktionen
`Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06` aus `IMS.E` zugeordnet.
PR124 fuegt keine Regel hinzu und veraendert weder Reihenfolge noch Wirkung
des vorhandenen Python-Kerns.

Der spaetere Anschlussanker
`ims.engine.explicit_period_runner.run_loaded_explicit_period` ist im Vertrag
nur als `planned_only` benannt. Daraus folgt noch kein Runneraufruf und keine
vollstaendige historische Simulation.

## Offene Anschlussarbeiten

- PR125: atomare Eingabevalidierung ohne Teilkandidat;
- PR126: bekanntes lokales Szenarioprofil aufloesen, serverseitig neu
  materialisieren und Digest berechnen;
- PR127: Kandidat nach eigener Freigabe unveraenderlich speichern;
- PR129: Kandidaten-ID und Digest an Run-Control anbinden;
- PR130: Einperioden-Wirkungsprobe auf einer isolierten Zustandskopie.

## API und Schutzgrenze

`GET /api/strategies/execution-candidate-contract` liefert nur die
Vertragsbeschreibung. `POST`, `PUT` und `DELETE` sind nicht zugelassen.

Kandidateneingabe, Validierung, Szenarioprofil-Aufloesung,
Neumaterialisierung, Digest, Kandidatenerzeugung, Speicherung, Run-Control,
Runner, Carryover, Ausgabedateien und Legacy-Vergleich bleiben deaktiviert.
Der Schritt startet keine Simulation und behauptet weder historische
RNG-Gleichheit noch historische Vollgleichheit.

## Naechster Schritt

PR125 darf die hier beschriebene gemeinsame Eingabe atomar pruefen. Auch ein
gueltiger Bericht ist dann noch kein Kandidat und keine Ausfuehrungsfreigabe.
