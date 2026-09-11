# PR123: Kontrollierten gemeinsamen Strategie-Ausfuehrungsanschluss planen

Stand: 2026-09-08
Status: Planungsentscheidung, noch keine Ausfuehrungsfreigabe

## Ziel

PR123 legt fest, wie die in PR116 und PR121 materialisierten VN- und
VU-Regel-Snapshots spaeter kontrolliert an den vorhandenen expliziten
Einperiodenpfad angeschlossen werden koennen.

Dieser PR fuehrt keinen neuen Vertrag, keinen POST-Endpunkt, keine
Kandidatenablage und keinen Runneraufruf ein. Er startet keine Simulation und
aendert keine Fachlogik.

## Ausgangsstand

Die Strategie-Workbench kann heute fuer denselben Strategieentwurf und
Einperiodenkontext zwei atomare, fluechtige Ergebnisse erzeugen:

- PR116: `VNInsuranceRuleSnapshot`-Objekte in
  `vn_insurance_rule_snapshots`;
- PR121: zehn VU-Strategien in acht vorhandenen VU-Snapshot-Sammlungen;
- PR117 und PR122: rein lesende Vorschau beider Materialisierungen;
- PR62 bis PR66: kontrolliertes Run-Control mit Freigabe, Idempotenz,
  Ergebnisablage und UI-Flow fuer serverseitig bekannte Fixture-Profile.

Der vorhandene Kernanker `run_loaded_explicit_period` verarbeitet ein
vollstaendiges `LoadedScenario` in der Reihenfolge VU-Regeln, VN-Regeln,
Schaden/Settlement und Aggregatbildung. Er ist kein historischer Scheduler und
keine vollstaendige Markt-Simulation.

## Noch fehlende Bruecke

Die beiden Materialisierungsberichte sind allein nicht ausfuehrbar. Ein
`LoadedScenario` benoetigt zusaetzlich:

- den vollstaendigen `SimulationContext`, insbesondere `max_periods`,
  `logtime`, `run_index` und `rng_seed`;
- einen BAV-Zustand;
- die vollstaendigen VU- und VN-Populationen;
- `vn_damage_settlement_snapshots` oder `vn_settlement_snapshots`, wenn
  VN-Entscheidungen fachlich in Schaden und Abrechnung fortwirken sollen;
- eine eindeutige Herkunft fuer alle expliziten Ziehungen;
- eine isolierte Zustandskopie, weil die vorhandenen Regelpfade VU- und
  VN-Zustaende veraendern;
- einen Ergebnis- und Provenienzvertrag fuer genau diesen Strategielauf.

Der PR112-Kontext ist absichtlich nur ein Kontext fuer offene Snapshotfelder.
Er darf nicht still in einen vollstaendigen Markt- oder Runnerzustand
umgedeutet werden. Der PR120-Zustandsbeleg bestaetigt Herkunft, ist aber keine
zweite Snapshot- oder Populationsquelle.

## Architekturentscheidung

Der Anschluss erfolgt spaeter ueber einen **unveraenderlichen
Einperioden-Ausfuehrungskandidaten**, nicht ueber einen direkten
Browser-zu-Runner-Pfad.

Der Kandidat soll serverseitig aus den urspruenglichen, versionierten
Quelldokumenten aufgebaut werden:

1. gemeinsamer Strategieentwurf und PR112-Kontext;
2. PR119-/PR120-Quellen- und Zustandsbeleg fuer die VU-Seite;
3. ein ueber stabile ID ausgewaehltes lokales Szenarioprofil fuer Kontext,
   BAV und Population;
4. explizite VN-Schaden-/Settlement-Eingaben fuer den ersten fachlich
   vollstaendigen Einperiodenschnitt;
5. erneute atomare PR116-/PR121-Materialisierung auf dem Server;
6. kanonische Einordnung der Snapshots in die vorhandenen Sammlungen des
   `LoadedScenario`;
7. Inhaltsdigest ueber Versionen, Quellen, Periode, Population und alle
   Eingabesnapshots.

Ein vom Browser zurueckgesendeter Materialisierungsbericht wird nicht als
autoritative Ausfuehrungsquelle akzeptiert. Ebenso bleiben freie Fixture- und
Outputpfade im Browser verboten.

## Vorgesehener Kandidateninhalt

Der genaue JSON-Vertrag wird erst in PR124 versioniert. Er muss mindestens
folgende Gruppen unterscheiden:

| Gruppe | Inhalt | Herkunft |
| --- | --- | --- |
| Identitaet | Kandidaten-ID, Entwurfs-ID, Periode, Inhaltsdigest | serverseitige Kanonisierung |
| Vertragsversionen | Entwurf, Kontext, VN-/VU-Materialisierung | vorhandene PR108- bis PR121-Vertraege |
| Marktgrundzustand | Kontext, BAV, VU, VN | bekanntes lokales Szenarioprofil |
| VU-Regeln | acht VU-Snapshot-Sammlungen | erneute PR121-Materialisierung |
| VN-Regeln | `vn_insurance_rule_snapshots` | erneute PR116-Materialisierung |
| VN-Prozess | Schaden-/Settlement-Snapshots mit expliziten Draws | eigener belegter Periodeneingang |
| Grenzen | Schreiben, Ausfuehrung, Carryover, Legacy-Vergleich | feste boolesche Vertragsfelder |

Die VU-Sammlungen sind:

- `vu_foreign_info_rule_snapshots`;
- `vu_random_uniform_rule_snapshots`;
- `vu_random_normal_rule_snapshots`;
- `vu_reserve_markup_rule_snapshots`;
- `vu_net_switcher_markup_rule_snapshots`;
- `vu_expected_claim_rule_snapshots`;
- `vu_market_share_markup_rule_snapshots`;
- `vu_free_linear_rule_snapshots`.

## Atomare Prueffolge

Ein spaeterer Kandidaten-Builder muss vor jeder Freigabe gemeinsam pruefen:

1. identische `draft_id` und Periode in allen Quelldokumenten;
2. vollstaendige, fehlerfreie VN- und VU-Materialisierung;
3. eindeutige Ziel-IDs und genau eine Strategie je Akteur und Periode;
4. Existenz jedes Snapshotziels in der ausgewaehlten Population;
5. Uebereinstimmung von Perioden-, Markt- und Herkunftswerten;
6. vollstaendige explizite Draws ohne RNG- oder Loader-Fallback;
7. disjunkte VN-Schaden-/Settlement-Ziele;
8. erfolgreiches Laden des kanonischen Mappings als `LoadedScenario`;
9. stabilen Inhaltsdigest und unveraenderte Vertragsversionen.

Bei einem Fehler wird kein Kandidat veroeffentlicht. Es gibt keine
Teilkandidaten und keine teilweise ausfuehrbare Snapshotliste.

## Erster spaeterer Ausfuehrungsschnitt

Der erste freigabefaehige Schnitt bleibt absichtlich klein:

- genau eine Periode;
- genau ein serverseitig bekanntes Szenarioprofil;
- explizite VU-, VN- und Schaden-Draws;
- keine RNG-Fallbacks;
- kein Carryover und kein Strategiewechsel innerhalb eines Laufs;
- `run_loaded_explicit_period` nur auf einer tiefen Kopie des Kandidaten;
- kein `output_dir` und damit keine Exportdateien;
- kein automatischer Legacy-Vergleich;
- Ergebnis als neuer, klar als Einperioden-Wirkungsprobe benannter Vertrag.

Diese Wirkungsprobe ist noch keine vollstaendige Markt-Simulation. Sie darf
erst als solche bezeichnet werden, wenn Mehrperiodenfolge, Carryover,
Schadenprozess, Ergebnisbundle und moderne Validierungsgates separat belegt
sind.

## Freigabe und Beobachtbarkeit

Die vorhandene Run-Control-Kette wird wiederverwendet, aber nicht umgangen:

`Kandidat validiert -> Kandidat unveraenderlich gespeichert -> Queue
vorgemerkt -> Preflight -> explizite Freigabe -> einmaliger Start -> Ergebnis
und Attempt-Verlauf`

Queue und Freigabe sollen nur Kandidaten-ID und Inhaltsdigest referenzieren.
Der Startpfad muss den Digest unmittelbar vor der Ausfuehrung erneut pruefen.
Idempotenz, Fehlerstatus und Ergebnisablage bleiben an die vorhandenen
Run-Control-Vertraege gebunden. Ein Queue-Worker und automatische
Wiederholungen bleiben ausserhalb des ersten Schnitts.

## Folge-PRs

- **PR124 (umgesetzt):** read-only Kandidatenvertrag mit Pflichtteilen,
  offenen Teilen, elf Sammlungen und Sperrfeldern versionieren; noch keine
  Validierung.
- **PR125 (umgesetzt):** gemeinsamen Kandidateneingang zustandslos und atomar
  validieren; noch keine Snapshot-Loader, Ablage oder Ausfuehrung.
- **PR126 (umgesetzt):** VN und VU serverseitig erneut materialisieren, das
  registrierte Marktprofil aufloesen und ein kanonisches `LoadedScenario`
  samt Digest bauen; kein Runneraufruf.
- **PR127 (umgesetzt):** unveraenderliche Kandidatenablage mit expliziter
  Speicherfreigabe, serverseitigem Neubau und Digest-Pruefung vor und nach
  dem Schreiben; kein Start.
- **PR128 (umgesetzt):** Kandidatenreife, Herkunft, Digest und Speicherstatus
  rein lesend in der Workbench zeigen.
- **PR129 (umgesetzt):** Run-Control-Resolver und Freigabecheck fuer
  Kandidaten-ID plus erneut geprueften Digest anbinden; Start weiterhin
  gesperrt.
- **PR130 (umgesetzt):** kontrollierte Einperioden-Wirkungsprobe auf
  isolierter Kopie im Backend ausfuehren; keine Dateien, kein Legacy-Vergleich
  und kein Carryover.
- **PR131 (umgesetzt):** manuellen Workbench-Start und read-only
  Ergebnisansicht an die vorhandene Freigabe-, Idempotenz- und Verlaufskette
  anbinden.
- **PR132 (umgesetzt):** Browser-Smoke, Fehlerpfade und
  Handbuch-Screenshots fuer diesen eng benannten Einperiodenpfad abschliessen.
- **PR133 (umgesetzt):** Periodenketten- und Carryover-Vertrag fuer den
  spaeteren 100-Periodenpfad festlegen.
- **PR134 (umgesetzt):** versionierten Ketteneingang zustandslos und atomar
  validieren.
- **PR135 (umgesetzt):** Kandidatenreferenzen und -kontexte serverseitig
  aufloesen und atomar abgleichen.
- **PR136 (umgesetzt):** kanonische fluechtige Kette und Gesamtdigest bilden.
- **PR137 (umgesetzt):** Kette ausdruecklich freigegeben, unveraenderlich
  und idempotent speichern; noch kein Carryover und kein Runner.
- **PR138 (umgesetzt):** gespeicherte Ketten-ID und Volldigest read-only
  erneut pruefen; Start weiterhin gesperrt.
- **PR139 (umgesetzt):** isolierte fluechtige Zwei-Perioden-Wirkungsprobe
  mit atomarem Fehlerstopp.
- **PR140 (naechster Schritt):** kontrollierter Workbench-Start mit
  dauerhafter Idempotenz und Ergebnisablage.

Nach PR132 ist die Einperioden-Wirkungsprobe kontrolliert bedienbar und
dokumentiert. Das ist weder die Zusage einer
vollstaendigen Mehrperiodensimulation noch eine Schaetzung bis zur fachlichen
Produktionsreife des Regulationslabors.

Mehrperiodenlauf, Carryover, Bilanz, ResultBundle/XLSX und
Regulierungsszenarien werden erst nach der Einperiodenabnahme in eigenen
Planungsbloecken aktiviert.

## Schutzgrenzen fuer PR123

- keine Codeaenderung am Simulations- oder Regelkern;
- keine Snapshot-, Szenario- oder Kandidatenpersistenz;
- kein neuer API- oder UI-Startpfad;
- kein Aufruf von `run_loaded_explicit_period` oder eines anderen Runners;
- keine Simulation und kein Schedulerstart;
- keine automatische historische Regelwahl;
- keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.

## Validierung dieses Plans

Ein Dokumentationstest prueft Ausgangsanker, fehlende Runnerteile,
Architekturentscheidung, atomare Prueffolge, Folge-PRs und Schutzgrenzen. Der
neue PR123-Test ruft keinen Runner und keine Simulation auf. Die bestehende
Gesamtsuite darf ihre bereits vorhandenen kontrollierten Runner-Tests weiter
ausfuehren; PR123 fuegt ihnen keinen neuen Ausfuehrungspfad hinzu.

## Naechster Schritt

PR134 validiert den versionierten Ketteneingang. PR135 loest die
Kandidatenreferenzen serverseitig auf. PR136 bildet daraus inzwischen die
kanonische fluechtige Kette samt Gesamtdigest. PR137 legt sie inzwischen
unveraenderlich ab, ohne bereits einen Mehrperiodenstart freizuschalten.
PR138 prueft inzwischen die gespeicherte Freigabeidentitaet read-only. PR139
fuehrt nun genau zwei Perioden auf isolierten Kopien fluechtig aus. PR140
soll den kontrollierten dauerhaften Workbench-Start ergaenzen.
