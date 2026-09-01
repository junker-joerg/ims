# Plan: Historische Referenzprovenienz und Vollfenster

Stand: 2026-09-01
Planungsschnitt: PR 87
Umsetzungsstand: PR 99

## Ziel

Dieser Block klaert zuerst, aus welchen historischen Archiv- und Laufschichten
die 19 versionierten Kernreferenzen stammen. Erst nach einer ausdruecklichen
Provenienzentscheidung werden alle 15 Kernexportidentitaeten an den
bestehenden Abweichungsbericht gebunden. Die historischen Dateien zaehlen
Ergebniszeilen ueber getrennte Laeufe von hoechstens 100 Perioden; sie sind
keine fortlaufenden 300- oder 500-Perioden-Trajektorien.

Der Block soll am Ende 15 vollstaendige berechnete Tabellen fuer die 19 Ziele
und 6.300 Referenzergebniszeilen liefern. Das ist ein Vollkorpusvergleich, aber noch
kein Nachweis historischer Modellgleichheit und keine automatische
Produktionsfreigabe.

## Ausgangsbefund

Der heutige Kernkorpus ist eine kontrollierte, aber nicht als ein historischer
Lauf belegte Referenzsammlung:

- `IMSVNR01.DAT` und `IMSVNR02.DAT` stammen aus der lokalen Schicht
  `ZINS000`;
- `IMSVNR03.DAT` bis `IMSVNR06.DAT`, `IMSVNVK1.DAT` bis `IMSVNVK3.DAT`
  und `IMSVUVK1.DAT` bis `IMSVUVK3.DAT` sind der Archivfamilie
  `WVEMOD1.ZIP` zugeordnet;
- `IMSVNSK1.DAT` stimmt bytegenau mit dem Eintrag in `WVEMOD1.ZIP`
  ueberein;
- `VU14L1.DAT` ist fuer 1-100 dreifach belegt, darunter durch
  `WVEMOD1.ZIP/IMSVU014.DAT`;
- `VUSK1L1.DAT` bis `VUSK1L5.DAT` sind die Ergebniszeilen 401-500 bis
  1-100 aus fuenf 100-Perioden-Laeufen desselben SK1-/all-Aggregats auf
  Stufe IV, keine unterschiedlichen Aggregatebenen;
- `WVEMOD1.ZIP`, `WVEMOD2.ZIP` und `WVEMOD3.ZIP` enthalten jeweils alle
  15 Kernexportnamen, aber keinen zugeordneten `IMSREPOR.DAT`;
- nur `VDEFMD5A.ZIP` enthaelt im bekannten Bestand einen `IMSREPOR.DAT` mit
  Seed `5616`, deckt aber nur fuenf der 15 Kernexportnamen ab.

Ein gemeinsamer Archivcontainer ist nur ein Indiz fuer eine Archivfamilie.
Ohne Laufbericht oder gleichwertige Quellkette beweist er weder denselben
historischen Lauf noch Seed, Scheduler-Reihenfolge oder RNG-Ziehfolge.

## Verbindliche Zielmatrix

| Ergebniszeilengrenze | Exportidentitaeten | Tabellen | Zielzeilen / Laeufe |
| --- | --- | ---: | ---: |
| 100 | `imsvu014.dat`, `imsvnsk1.dat` | 2 | 200 / je 1 |
| 300 | `imsvnr01.dat`, `imsvnr02.dat` | 2 | 600 / je 3 |
| 500 | `imsvusk1.dat`, `imsvnr03.dat` bis `imsvnr06.dat`, `imsvnvk1.dat` bis `imsvnvk3.dat`, `imsvuvk1.dat` bis `imsvuvk3.dat` | 11 | 5.500 / je 5 |
| Gesamt | 15 Exportidentitaeten / 19 Referenzziele | 15 | 6.300 |

`imsvusk1.dat` bleibt eine einzige 500-zeilige berechnete Tabelle. Ihre Zeilen
werden aus fuenf getrennten modernen 100-Perioden-Laeufen zusammengesetzt und
gegen die fuenf historischen Laufabschnitte `VUSK1L5` bis `VUSK1L1`
ausgerichtet. Die Abschnitte werden nicht als fuenf Aggregate oder
Aggregatebenen gezaehlt.

Die Formel des Altprogramms nummeriert eine Ausgabezeile als
`(Lauf - 1) * Simulationslaenge + lokale Periode`. `SIMLAENGE` ist im
historischen Quellstand auf maximal 100 begrenzt. Die modernen 300- und
500-Perioden-Zustandsfortschreibungen aus PR 94 und PR 96 bleiben wertvolle
deterministische Stabilitaetstests, sind aber keine historischen
Vergleichslaeufe.

## Entscheidungstor Provenienz

Vor jeder Lieferung von mehr als 100 Ergebniszeilen muss ein versionierter Bericht jede
Referenzschicht einer der folgenden Klassen zuordnen:

- `same_run_proven`: gemeinsamer Lauf durch direkte Laufmetadaten und
  konsistente Ausgabefamilie belegt;
- `archive_family_only`: gemeinsamer Archivkontext belegt, konkrete
  Laufidentitaet oder Seed nicht belegt;
- `mixed_reference_layers`: bewusst aus mehreren historischen Schichten
  zusammengesetzter Validierungskorpus;
- `contradictory_or_unresolved`: Herkunft oder Zusammengehoerigkeit ist
  widerspruechlich beziehungsweise nicht entscheidbar.

Nur `same_run_proven` darf eine Aussage ueber einen gemeinsamen historischen
Lauf tragen. Bei `archive_family_only` oder `mixed_reference_layers` duerfen
die Vollfenster als getrennte Referenztests weiter aufgebaut werden; die
gemeinsame historische Laufgleichheit und Produktionsfreigabe bleiben jedoch
gesperrt. `contradictory_or_unresolved` stoppt die Vollfensterphase, bis die
betroffenen Ziele getrennt oder neu belegt sind.

## PR-Folge

### Phase A: Provenienz und Referenzschichten

1. **PR 87: Block planen und Grenzen einfrieren.**
   Diese Notiz, Zielmatrix, Entscheidungsklassen, Stop/Go-Regeln und
   Restzaehlung dokumentieren. Keine Datei aus `incomming/` uebernehmen.
2. **PR 88: read-only Archivmanifest erstellen (umgesetzt).**
   Fuer die sieben bekannten ZIP-Archive Archivhash, Eintragspfad,
   Eintragshash, Groesse, Zeitstempel, Header, Zeilenzahl und Periodenfenster
   der 15 Kernexportnamen erfassen. Der Vertrag `pr88-v1` inventarisiert
   165 Eintraege und 64 Kerntreffer; drei Archive enthalten alle 15
   Kernexportnamen. Tests verwenden kleine synthetische Archive; lokale
   Rohdaten bleiben unversioniert. Der Befund steht in
   `docs/migration/historical_archive_manifest.md`.
3. **PR 89: Referenz-zu-Archiv-Koharenzmatrix bauen (umgesetzt).**
   Die 19 versionierten Referenzen byteweise und tokennormalisiert gegen
   gleichnamige Archiveintraege vergleichen. Fuer `VUSK1L1-5` zusaetzlich
   die fuenf Fenster gegen passende Abschnitte einer 500-zeiligen
   `IMSVUSK1.DAT` pruefen. Ergebnisse nur als `exact_archive_member`,
   `exact_window_slice`, `same_name_divergent` oder `unresolved` einordnen.
   Der Vertrag `pr89-v1` klassifiziert 13 Ziele als bytegenaue Eintraege,
   fuenf als tokennormalisierte Fenster und `VUSK1L4.DAT` als
   `same_name_divergent`. Der Befund steht in
   `docs/migration/historical_reference_archive_coherence.md`.
4. **PR 90: Laufmetadaten und Begleitdateien auswerten (umgesetzt).**
   `IMSREPOR.DAT` sowie vorhandene Modell-, Definitions- und Parameterdateien
   archivlokal zuordnen. Seed oder Laufparameter duerfen nicht zwischen
   Archiven uebertragen werden. Fehlende Metadaten bleiben ein eigener
   Befund, kein impliziter Standardwert. Der Vertrag `pr90-v1` findet genau
   einen direkten Laufbericht in `VDEFMD5A.ZIP`, keine separaten Modell-,
   Definitions- oder Parameterdateien und sechs Archive ohne direkte
   Laufmetadaten. Der Report belegt Seed `5616` sowie drei beobachtete
   Sequenzen `1-100` nur fuer sein eigenes Archiv. Der Befund steht in
   `docs/migration/historical_archive_run_metadata.md`.
5. **PR 91: Referenzschicht-Vertrag entscheiden (umgesetzt).**
   Der Vertrag `pr91-v1` friert fuer jedes der 19 Ziele `layer_id`,
   Quellarchiv oder Direktquelle, Hashbezug, Koharenzklasse und zulaessige
   Aussage ein. 18 Ziele sind `archive_family_only`; `VUSK1L4.DAT` bleibt
   als eigene Schicht `contradictory_or_unresolved` und darf nur fuer
   versionierte Fixture-Regressionen verwendet werden. Das Tor lautet
   `go_separate_reference_tests`: getrennte Vollfenstertests duerfen
   vorbereitet werden, ein gemeinsamer historischer Lauf bleibt unbelegt.
   Das Kernbundle wurde nicht geaendert. Der Befund steht in
   `docs/migration/historical_reference_layer_contract.md`.

### Phase B: Kontrollierte Vollfenster

6. **PR 92: Ergebniszeilenvertrag 100/300/500 vorbereiten (korrigiert in PR 98).**
   Der Vertrag bindet 15 Exportidentitaeten, 19 Referenzziele und 6.300
   Zielzeilen an ein, drei oder fuenf getrennte Laeufe mit jeweils hoechstens
   100 Perioden. `VUSK1L1-5` bleiben Laufabschnitte desselben
   SK1/all-Aggregats auf Stufe IV, waehrend `VUSK1L4` seine isolierte
   Herkunftsschicht behaelt. Der weiterhin vorhandene Prefix-Pruefer bewertet
   ausschliesslich moderne 300-/500-Perioden-Stabilitaet. Der Befund steht in
   `docs/migration/historical_horizon_contract.md`.
7. **PR 93: bestehende 100-Perioden-Tabellen streng anbinden (umgesetzt).**
   Der Vertrag `pr93-v1` uebergibt `imsvu014.dat` und `imsvnsk1.dat` aus dem
   kontrollierten `pr86-v1`-Zustandspfad an den Produktionskorpusbericht. Er
   prueft Identitaet, Header, Perioden 1-100 und die `wvemod1_archive`-Bindung
   aus `pr91-v1`/`pr92-v1`. Fortschritt: 2/15 Tabellen und 200/6.300
   Zielperioden vollstaendig geliefert; 13 Tabellen und 6.100 Perioden bleiben
   offen. Die Freigabe bleibt `blocked`, ein gemeinsamer Vollvergleich wurde
   nicht ausgefuehrt. Der Befund steht in
   `docs/migration/historical_100_period_corpus_delivery.md`.
8. **PR 94: Zustandsfortschreibung bis Periode 300 schliessen (umgesetzt).**
   Der Vertrag `pr94-v1` setzt denselben kontrollierten modernen Zustand mit
   festem Seed bis Periode 300 fort. Alle 299 Zustandsuebergaenge und 15
   Tabellen mit 4.500 Zeilen werden im Speicher erzeugt. Der 100er-Prefix ist
   fuer 99 Zustandsresultate und 1.500 Exportzeilen exakt stabil. Historische
   Scheduler-, RNG- oder Akkumulatorsemantik wird nicht ergaenzt; ein
   historischer 300er-Vergleich wurde nicht ausgefuehrt. Der Befund steht in
   `docs/migration/vdefmd6_300_period_state_contract.md`.
9. **PR 95: 300er-Regelzeilen anbinden (korrigiert in PR 98).**
   `imsvnr01.dat` und `imsvnr02.dat` werden als getrennte
   `zins000_archive`-Referenzen gegen je drei unabhaengige moderne
   100-Perioden-Laeufe verglichen. Dieser diagnostische Vergleich deckt 600
   Ergebniszeilen ab, reproduziert aber weder historischen Seed noch
   Zufallsfolge. Kumuliert sind 4/15 Tabellen und 800/6.300 Zielzeilen
   geliefert; die Freigabe bleibt blockiert. Der Befund steht in
   `docs/migration/historical_300_period_rule_delivery.md`.
10. **PR 96: Zustandsfortschreibung bis Periode 500 schliessen (umgesetzt).**
    Der Vertrag `pr96-v1` setzt denselben kontrollierten modernen Zustand mit
    festem Seed bis Periode 500 fort. Alle 499 Zustandsuebergaenge und 15
    Tabellen mit 7.500 Zeilen werden im Speicher erzeugt. Die Prefixe 1-100
    und 1-300 sind fuer 99 beziehungsweise 299 Zustandsresultate sowie 1.500
    beziehungsweise 4.500 Exportzeilen exakt stabil. Historische Scheduler-,
    RNG- oder Akkumulatorsemantik wird nicht ergaenzt; ein historischer
    500er-Vergleich wurde nicht ausgefuehrt. Der Befund steht in
    `docs/migration/vdefmd6_500_period_state_contract.md`.
11. **PR 97: VU-SK1-Ergebniszeilen anbinden (korrigiert in PR 98).**
    Eine berechnete `imsvusk1.dat` aus fuenf unabhaengigen 100-Perioden-Laeufen
    wurde gegen `VUSK1L5` bis `VUSK1L1` als fuenf getrennte Referenztests
    ausgerichtet. `VUSK1L4.DAT`
    bleibt die isolierte Direktreferenz `vusk1l4_direct_04410ef`; die vier
    anderen Abschnitte bleiben `wvemod2_archive`. Vier Anfangszustaende treffen
    vollstaendig; 1.052/7.000 Felder treffen exakt und 5.884 Abweichungen
    blockieren.
    Kumuliert sind 5/15 Tabellen und 1.300/6.300 Zielzeilen geliefert; eine
    koharente historische 500-Perioden-Lauf wird nicht behauptet. Der
    Befund steht in
    `docs/migration/historical_500_period_vusk1_delivery.md`.
12. **PR 98: Wiederholungsvertrag und Langlaufdeutung korrigieren (umgesetzt).**
    Historische Quellanker, Dissertation und Ausgabeformel belegen maximal
    100 Perioden je Lauf. Der Vertrag `pr98-v1` bildet deshalb 300/500
    Ergebniszeilen als drei/fuenf unabhaengige 100er-Laeufe ab; PR 94 und
    PR 96 bleiben getrennte moderne Stabilitaetstests. Keine historische
    Zufallsfolge oder Vollgleichheit wird verlangt.
13. **PR 99: VN-Regeln 3-6 anbinden (umgesetzt).**
    Vier Tabellen aus je fuenf 100er-Laeufen wurden vollstaendig verglichen.
    Keine der 2.000 Gesamtzeilen trifft vollstaendig; 5.678/26.000 Felder
    treffen exakt und 809 weitere innerhalb der Toleranz. Kumuliert sind
    9/15 Tabellen und 3.300/6.300 Zielzeilen geliefert. Gleiche historische
    Parameter oder Zufallsfolgen werden nicht behauptet.
14. **PR 100: VN-Klassen 1-3 anbinden.**
    Drei Tabellen aus je fuenf 100er-Laeufen vollstaendig vergleichen.
    Erwarteter Fortschritt:
    12/15 Tabellen und 4.800/6.300 Zielzeilen.
15. **PR 101: VU-Klassen 1-3 anbinden.**
    Die letzten drei Tabellen aus je fuenf 100er-Laeufen vollstaendig
    vergleichen. Erwarteter
    Fortschritt: 15/15 Tabellen und 6.300/6.300 Zielzeilen.
16. **PR 102: gemeinsamen Vollkorpusbericht bewerten.**
    Alle 19 Ziele in einem read-only Bericht klassifizieren, Abweichungen nach
    Referenzschicht trennen und die menschliche Freigabe neu entscheiden.
    Vollstaendige Eingabe ist dabei nicht automatisch Feldgleichheit oder
    Produktionsfreigabe.

## Abnahme je PR

Jeder Provenienz-PR braucht positive und negative Tests fuer Pfad-, Hash-,
Fenster- und Schichtgrenzen. Jeder Vollfenster-PR braucht deterministische
Wiederholung, Prefix-Stabilitaet, exakte Zielmenge, fehlende-/zusaetzliche-
Tabellen-Negativtests und den bestehenden Feldabweichungsbericht.

Das Windows-Release-Gate bleibt nach jedem PR gruen. Sein technisches
`release_ready = true` darf weiterhin nicht in eine fachliche
Produktionsfreigabe umgedeutet werden.

## Aufwand und Restzahl

PR 87 ist der Planungs-PR; PR 88 bis PR 99 haben Archivmanifest,
Referenzkohaerenz, archivlokale Laufmetadaten, den getrennten
Referenzschicht-Vertrag, den Horizontvertrag und die erste 100er-Korpuslieferung
abgeschlossen, den modernen Zustand bis 500 fortgeschrieben und die
historischen 300/500-Zeilen-Dateien als Wiederholungen von 100-Perioden-Laeufen
korrigiert und die vier VN-Regeltabellen 3-6 angebunden. Danach sind **3
geplante PRs** bis zum ersten gemeinsamen 6.300-Zeilen-Vollkorpusbericht
offen: zwei historische Tabellenfamilien-PRs und ein Bewertungs-PR.

Verbleibende grobe Bruttoabschaetzung fuer PR 100 bis PR 102:

| Anteil | Erwarteter Umfang |
| --- | ---: |
| Python-Produktionscode | 40-210 LoC |
| Tests | 110-330 LoC |
| Vertraege, Fixtures und Dokumentation | 140-360 LoC |
| Gesamt | 290-900 LoC |

Die Schaetzung umfasst keine noch unbekannten fachlichen Korrektur-PRs fuer
Akkumulatoren, Scheduler, RNG, Versicherungsgrad oder `Ev`-Felder. Solche PRs
werden erst aus belegten Abweichungen abgeleitet und koennen die Zahl bis zu
einer fachlichen Produktionsfreigabe erhoehen.

## Grenzen dieses Planungs-PRs

- nur read-only Sichtung lokaler Dateinamen und Archivverzeichnisse;
- kein Import, kein Staging und keine Versionierung aus `incomming/`;
- keine Aenderung des Legacy-Bundles oder historischer Referenzdateien;
- keine Runner-, Scheduler-, Adapter-, Server- oder Simulationsausfuehrung;
- keine neue Fachlogik und keine automatische historische Regelwahl;
- keine Seed-Uebertragung zwischen Archivfamilien;
- keine historische Vollgleichheits- oder Produktionsfreigabebehauptung.
