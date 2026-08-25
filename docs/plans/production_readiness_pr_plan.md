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
  Altdatenumfang, Tests, Abweichungen, Grenzen und Bedienpfad (erledigt:
  read-only Vertrag `pr69-v1`, 19/6.300 Coverage und 15 explizite
  Exportblocker ohne Produktionsfreigabe).
- PR 70: CI-/Windows-Gate fuer Python-Tests, Frontend-Build, Korpusbericht,
  ZIP/Staging und Release-Smoke (erledigt; lokales PowerShell-Gate und GitHub
  Actions auf `windows-latest`, ohne Server- oder Simulationsstart).
- PR 71: Herkunfts- und Erzeugungswegkarte fuer die 15 fehlenden berechneten
  Kernexporte erstellen (erledigt: 15/19/6.300-Vertrag, Writer-Anschluss fuer
  alle Identitaeten, zwei gemeinsame Zustandsfamilien und null unabhaengig
  erzeugte Vollfenster).
- PR 72: vollstaendigen 100-Perioden-Erzeugungsvertrag fuer `imsvu014.dat`
  mit belegten Eingaben und Negativgrenzen vorbereiten (erledigt: Vertrag
  `pr72-v1`, sechs Herkunftsgruppen, Referenz-Echo-Sperre und weiter
  `generation_ready = false`).
- PR 73: VU14 an `Vdefmd6` binden, die echte Referenz korrigieren und Periode 1
  unabhaengig pruefen (erledigt).
- PR 74: `Vdefmd6`-Population fuer 25 VU und 200 VN typisiert aufbauen
  (erledigt: `pr74-v1`, 225 Entitaeten und 13 gepruefte Quellanker).
- PR 75: Aktionsslots und moderne reproduzierbare Seed-Policy anbinden
  (erledigt: `pr75-v1`, 200 Slots, 20.250 wirksame Aufrufe und 13 Quellanker;
  keine historische Same-Slot- oder RNG-Gleichheitsbehauptung).
- PR 76: VU14-Regelprojektion fuer Perioden 2-49 erzeugen und Abweichungen
  klassifizieren (erledigt: `pr76-v1`, Regelausgaben treffen 1-16, erste
  entscheidungsrelevante Luecke in 17, Vollzustand bleibt blockiert).
- PR 77: VN-/Schaden-/Settlement-Eingaben und Draw-Reihenfolge fuer die
  Vorschockperiode kartieren (erledigt: `pr77-v1`, sechs Regeln und 150 aktive
  VN gebunden; C-interne Normalreihenfolge und Same-Slot-Reihenfolge bleiben
  explizit offen).
- PR 78: explizite VN-Vorschock-Snapshots und moderne Drawfolge fuer eine
  einzelne Periode materialisieren (erledigt: `pr78-v1`, 150 Regel- und 150
  Schaden-Snapshots; kein Runner oder Simulationsstart).
- PR 79: Snapshotableitung aller 25 VU-Regeln, BAV-Vorperiodeninputs und
  Informationskostengrenze schliessen (erledigt: `pr79-v1`, 25 VU-Snapshots,
  25/150 Vorperiodeninputs und belegte, noch nicht angewendete Suchkosten).
- PR 80: kontrollierten VU-/VN-/Schaden-/Settlement-Pfad fuer Perioden 2-49
  ausfuehren und VU14-Abweichungen klassifizieren (erledigt: `pr80-v1`,
  1.200/7.200/7.200 Anwendungen, 76.032 Suchkosten und 236/686 Feldtreffer;
  keine historische Gleichheitsaussage).
- PR 81: Schockgrenze und VU14-Perioden 50-100 schliessen (erledigt:
  `pr81-v1`, 50 spaete VN in Periode 50 aktiviert, 17.400 VN-Anwendungen und
  488/1.400 VU14-Feldtreffer; keine historische Gleichheitsaussage).
- PR 82: Versicherer-Population auf `imsvusk1.dat` und `imsvuvk1-3.dat`
  verbreitern (erledigt: `pr82-v1`, 898/5.600 Feldtreffer; die historische
  klassenuebergreifende Akkumulatorsemantik bleibt offen).
- PR 83: VN-Regelzustand fuer `imsvnr01.dat` bis `imsvnr03.dat` schliessen
  (erledigt: `pr83-v1`, 946/3.900 Feldtreffer; historischer VN-
  Regelakkumulator und `Ev`-Feldbedeutung bleiben offen).
- PR 84: VN-Regelzustand fuer `imsvnr04.dat` bis `imsvnr06.dat` schliessen
  (erledigt: `pr84-v1`, 926/3.900 Feldtreffer und 326/3.300 Fachwerttreffer;
  historische Laufidentitaet fuer `WVEMOD1` bleibt offen).
- PR 85: VN-Klassen- und SK1/all-Exporte aus demselben Zustand vergleichen
  (erledigt: `pr85-v1`, 1.234/5.200 Feldtreffer und 434/4.400
  Fachwerttreffer; historische Klassenakkumulator- und Laufidentitaet bleiben
  offen).
- PR 86: alle 15 Exporte gemeinsam vergleichen und die Freigabe menschlich
  neu bewerten.

## Grobe Anzahl

Nach PR 85 sind `0` technische Pflicht-PRs fuer die eingefrorene Windows-
Pruefkette offen. Fuer eine interne, reviewbare Erzeugung sind mindestens
`1` weiterer PR bis zur erneuten fachlichen Freigabepruefung geplant. Funde zu
Population, Scheduler, RNG oder Zustandsfortschreibung koennen diese Zahl
erhoehen. Eine unabhaengige externe Vollieferung mit belegter Herkunft kann die
interne Erzeugungsserie verkuerzen.

## Naechster Schritt

PR 86 fuehrt als naechstes alle 15 Kernexporte in einer gemeinsamen
Klassifikation zusammen und bereitet die menschliche Freigabebewertung vor.
Historische Laufidentitaet, Reihenfolge, RNG-Grenze, BAV-Versicherungsgrad-
Ableitung, VU-/VN-Akkumulatoren und die `Ev`-Feldbedeutung bleiben Blocker;
Legacy-Ausgaben werden nicht zurueckgefuehrt.
