# Plan: PRs bis zur Produktionsreife

## Zielbild

Produktionsreife bedeutet in diesem Migrationsstand nicht nur, dass die lokale
Workbench startet. Produktionsreife ist erst erreicht, wenn ein abgegrenzter
historischer Altdaten-Korpus reproduzierbar validiert ist, fachliche
Abweichungen dokumentiert sind, kontrollierte Ausfuehrung und Ergebnisanzeige in
der UI stabil laufen und die lokale Auslieferung pruefbar ist.

Diese Planung ist keine aktuelle Behauptung historischer Vollgleichheit. Sie ist
eine Roadmap zu einem spaeteren, belegten Produktionsfreigabestand.

## Produktionsreife-Kriterien

- Altdaten-Korpus: referenzierte historische DAT-Dateien sind versioniert oder
  bewusst ausgeschlossen; Herkunft, Header, Periodenfenster und Parsergrenzen
  sind dokumentiert.
- Fachvalidierung: VU-/VN-Regel-, Carryover-, Schaden-/Settlement- und
  Aggregatpfade haben schmale Regressionstests und mindestens einen
  kontrollierten Mehrperiodenvergleich gegen belegte Legacy-Referenzen.
- Abweichungsmanagement: bekannte Abweichungen sind klassifiziert als
  implementierungsbedingt, datenbedingt, RNG-/Scheduler-bedingt oder offen.
- UI: die Workbench startet lokal, kann kontrollierte Runs vorbereiten, nach
  expliziter Freigabe ausfuehren oder deren vorab erzeugte Ergebnisse lesen,
  Ergebnisstatus anzeigen und Fehler erklaeren.
- Betrieb: Start-/Check-Skripte, Packaging, Backup-/Restore- und
  Update-/Rollback-Grenzen sind getestet.
- Grenzen: keine automatische historische Regelwahl, keine stille
  Fachlogikmutation und keine Vollgleichheitsbehauptung ohne Abschlussbericht.

## Roadmap ab PR 50

### Phase A: Fachliche Slice-Abdeckung erweitern

- PR 50: sechsten fachlichen Slice waehlen. Dieser Schnitt: Vrvn04 /
  `search_history` als expliziter VN-Regel-Snapshot-Regressionstest planen.
- PR 51: sechsten fachlichen Regressionstest fuer Vrvn04 / `search_history`
  umsetzen, inklusive Runner-Grenze zu Schaden/Settlement (erledigt).
- PR 52: siebten fachlichen Regressionstest fuer Vrvn03 / `preference`
  umsetzen, inklusive Runner-Grenze zu Schaden/Settlement (erledigt).
- PR 53: Vrvn02 / `random` mit expliziten Draws und Seed-/Draw-Grenze als
  schmalen Regressionstest absichern (erledigt).
- PR 54: VN-Schaden-/Settlement-Pfad aus `Vrvn01` bis `Vrvn03` breiter gegen
  vorhandene explizite Fixtures pruefen (erledigt).
- PR 55: VU-Regelbreite ergaenzen, vorzugsweise ein expliziter VU-Random- oder
  VU-Markup-Slice mit Draw-/Carryover-Grenze. Dieser Schnitt prueft
  `Vrvu01` / Zufall I ueber zwei explizite Draw-Vektoren und eine kontrollierte
  Carryover-Opt-in-Grenze (erledigt).

### Phase B: Altdaten-Validierung verdichten

- PR 56: Produktions-Altdatenkorpus als Plan fixieren: welche historischen
  Referenzen zaehlen fuer die erste Freigabe, welche bleiben ausgeschlossen.
  Der Kernkorpus umfasst 19 versionierte Referenzen und 6.300 eingetragene
  Vergleichszeilen; PR 57 prueft nur das getrennte ZINS000-Paar
  `IMSVU014.DAT` und `IMSVUSK1.DAT` (erledigt).
- PR 57: gezielte weitere Altdaten nur nach Header-/Feldpruefung uebernehmen;
  genau `IMSVU014.DAT` und `IMSVUSK1.DAT` sind als getrennte ZINS000-Schicht
  versioniert; `incomming/` bleibt weiterhin kein Sammelimport (erledigt).
- PR 58: Mehrperioden-Legacy-Vergleich fuer den Freigabekorpus vorbereiten,
  als strikten Vertrag fuer extern gelieferte berechnete Exporttabellen mit
  15 Exporten, 19 Zielen und 6.300 Perioden, weiterhin ohne Vollsimulation
  (erledigt).
- PR 59: Abweichungsbericht erzeugen: Treffer, tolerierte Differenzen,
  blockierende Differenzen und offene Feldfragen; bei unvollstaendigem Input
  blockierend abbrechen. Der Kernkorpus meldet derzeit 15 fehlende berechnete
  Exporte (erledigt).
- PR 60: ersten tatsaechlich berechneten schmalen Output aus einem vorhandenen
  expliziten Mehrperiodenpfad anbinden. Vier VU14-Perioden sind als
  Aggregat-/Export-Slice angeschlossen; die expliziten Zustandswerte bleiben
  referenzausgerichtete Inputs (erledigt).
- PR 61: technische Level-IV-Selektorgrenze `all` gegen `SK1` explizit
  kanonisieren und testen; keine Aenderung der Aggregatstufe oder Fachlogik
  (erledigt). Modellkorrekturen nur fuer danach belegte Abweichungen umsetzen.

### Phase C: Kontrollierte Ausfuehrung und UI

- PR 62: Run-Control-Ausfuehrungsfreigabe fuer den lokalen Adapter als
  kontrollierten Startpfad vorbereiten, mit Auditfeldern und weiter ohne freien
  Browser-Upload (read-only Freigabecheck erledigt).
- PR 63: atomare Backend-Start-, Status- und Ergebnisgrenze gegen Doppelstarts
  schaffen, noch ohne UI-Startbutton (erledigt: Idempotenz-Claim,
  `starting`/`failed`/`result_persisted` und atomare Resultatablage).
- PR 64: UI-Startpfad hinter expliziter Freigabe aktivieren; Queue-Worker und
  Adapterstart bleiben eng gegated (erledigt: zweistufiger Freigabecheck,
  stabiler Idempotenzpayload und manuell ausgeloester Start).
- PR 65: UI-Ergebnisverlauf, Fehlerzustaende und erneute Ergebnisanzeige fuer
  persistierte Runs stabilisieren (erledigt: read-only Attempt-Verlauf,
  Fehlermeldung und manueller GET-Neuladepfad ohne Retry).
- PR 66: Browser-/Screenshot-E2E-Smoke fuer den freigegebenen lokalen Demo-Run
  ergaenzen (erledigt: isolierter Loopback-Server, injizierter Fake-Adapter,
  sichtbare Freigabe, genau ein Start, persistiertes Ergebnis und Verlauf ohne
  Engine-Runner oder Simulation).

### Phase D: Freigabehaertung

- PR 67: Packaging-/Staging-/Startskript-Smoke fuer den freigegebenen Stand
  wiederholen und Release-Checkliste einfrieren (erledigt: Checklistenvertrag
  `pr67-v1`, read-only Sammelcheck, Produktionsskript-/Artefaktabgleich und
  normaler Loopback-Start ohne PR-66-Fake-Adapter oder Simulation).
- PR 68: Backup-/Restore- und Update-/Rollback-Probe fuer lokale Metadaten mit
  einem validierten Ergebnisstand pruefen (erledigt: SQLite-Backup/Restore,
  Digest ueber fuenf Tabellen und getrennte Repo-/Portable-Anwendungspfade).
- PR 69: Abschlussbericht fuer den ersten Produktionsfreigabekorpus erstellen:
  Altdatenumfang, Tests, Abweichungen, Grenzen und Bedienpfad.
- PR 70+: Review-Fixes, CI-/Windows-Haertung und blockierende
  Abweichungskorrekturen.

## Grobe Anzahl

Nach PR 68 bleiben grob `2-8` reviewbare PRs bis zu einer konservativen
Produktionsreife mit validiertem Altdaten-Korpus und laufender UI. Die Zahl kann
steigen, wenn historische Feldfragen, RNG-/Scheduler-Abweichungen oder
Review-Funde blockieren.

## Naechster Schritt

PR 69 erstellt den Abschlussbericht fuer den ersten Produktionsfreigabekorpus.
Er fasst Altdatenumfang, belegte Tests, bekannte Abweichungen, Betriebsgrenzen
und den Bedienpfad zusammen. Er darf weder fehlende berechnete Exporte als
validiert darstellen noch eine historische Vollgleichheit behaupten.
