# Plan: Historische Referenzprovenienz und Vollfenster

Stand: 2026-08-31
Planungsschnitt: PR 87
Umsetzungsstand: PR 96

## Ziel

Dieser Block klaert zuerst, aus welchen historischen Archiv- und Laufschichten
die 19 versionierten Kernreferenzen stammen. Erst nach einer ausdruecklichen
Provenienzentscheidung wird der kontrollierte moderne Zustand von 100 auf 300
und 500 Perioden erweitert und fuer alle 15 Kernexportidentitaeten an den
bestehenden Abweichungsbericht gebunden.

Der Block soll am Ende 15 vollstaendige berechnete Tabellen fuer die 19 Ziele
und 6.300 Referenzperioden liefern. Das ist ein Vollfenstervergleich, aber noch
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
- `VUSK1L1.DAT` bis `VUSK1L5.DAT` sind die Fenster 401-500 bis 1-100
  desselben SK1-/all-Aggregats auf Stufe IV;
- `WVEMOD1.ZIP`, `WVEMOD2.ZIP` und `WVEMOD3.ZIP` enthalten jeweils alle
  15 Kernexportnamen, aber keinen zugeordneten `IMSREPOR.DAT`;
- nur `VDEFMD5A.ZIP` enthaelt im bekannten Bestand einen `IMSREPOR.DAT` mit
  Seed `5616`, deckt aber nur fuenf der 15 Kernexportnamen ab.

Ein gemeinsamer Archivcontainer ist nur ein Indiz fuer eine Archivfamilie.
Ohne Laufbericht oder gleichwertige Quellkette beweist er weder denselben
historischen Lauf noch Seed, Scheduler-Reihenfolge oder RNG-Ziehfolge.

## Verbindliche Zielmatrix

| Pflichtgrenze | Exportidentitaeten | Tabellen | Zielzeilen |
| --- | --- | ---: | ---: |
| 100 | `imsvu014.dat`, `imsvnsk1.dat` | 2 | 200 |
| 300 | `imsvnr01.dat`, `imsvnr02.dat` | 2 | 600 |
| 500 | `imsvusk1.dat`, `imsvnr03.dat` bis `imsvnr06.dat`, `imsvnvk1.dat` bis `imsvnvk3.dat`, `imsvuvk1.dat` bis `imsvuvk3.dat` | 11 | 5.500 |
| Gesamt | 15 Exportidentitaeten / 19 Referenzziele | 15 | 6.300 |

`imsvusk1.dat` bleibt eine einzige 500-zeilige berechnete Tabelle. Im
Legacy-Bundle wird sie gegen die fuenf historischen 100-Perioden-Zeitfenster
`VUSK1L5` bis `VUSK1L1` ausgerichtet. Die Fenster werden nicht als fuenf
Aggregate oder Aggregatebenen gezaehlt.

## Entscheidungstor Provenienz

Vor jeder Erweiterung ueber Periode 100 muss ein versionierter Bericht jede
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

6. **PR 92: Horizontvertrag 100/300/500 vorbereiten (umgesetzt).**
   Der Vertrag `pr92-v1` bindet 15 Exportidentitaeten, 19 Referenzziele und
   6.300 Zielperioden an die Pflichtgrenzen 100, 300 und 500. Ein generischer
   Pruefer vergleicht bereits berechnete `ExportTable`-Snapshots exakt auf
   stabile 100er- und 300er-Prefixe und verlangt die `layer_id` aus
   `pr91-v1`. `VUSK1L1-5` bleiben Zeitfenster desselben SK1/all-Aggregats auf
   Stufe IV, waehrend `VUSK1L4` seine isolierte Herkunftsschicht behaelt. Es
   wurde kein 300-/500-Vollvergleich ausgefuehrt. Der Befund steht in
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
9. **PR 95: 300er-Regelfenster anbinden (umgesetzt).**
   `imsvnr01.dat` und `imsvnr02.dat` wurden als getrennte
   `zins000_archive`-Referenzen vollstaendig verglichen. Beide kontrollierten
   Tabellen halten ihren exakten 100er-Prefix; der historische Vergleich
   deckt 600 Zeilen und 7.800 Felder ab. 600/600 Zeilen unterscheiden sich in
   mindestens einem Fachfeld. Kumuliert sind 4/15 Tabellen und 800/6.300
   Zielzeilen geliefert; die Freigabe bleibt blockiert. Der Befund steht in
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
11. **PR 97: VU-SK1-Zeitfenster anbinden.**
    Eine berechnete `imsvusk1.dat` mit 500 Perioden gegen `VUSK1L5` bis
    `VUSK1L1` als fuenf getrennte Referenztests ausrichten. `VUSK1L4.DAT`
    bleibt dabei die isolierte Direktreferenz; es wird keine koharente
    historische 500-Perioden-Archivquelle behauptet. Erwarteter Fortschritt:
    5/15 Tabellen und 1.300/6.300 Zielzeilen.
12. **PR 98: VN-Regeln 3-6 anbinden.**
    Vier 500er-Tabellen vollstaendig vergleichen. Erwarteter Fortschritt:
    9/15 Tabellen und 3.300/6.300 Zielzeilen.
13. **PR 99: VN-Klassen 1-3 anbinden.**
    Drei 500er-Tabellen vollstaendig vergleichen. Erwarteter Fortschritt:
    12/15 Tabellen und 4.800/6.300 Zielzeilen.
14. **PR 100: VU-Klassen 1-3 anbinden.**
    Die letzten drei 500er-Tabellen vollstaendig vergleichen. Erwarteter
    Fortschritt: 15/15 Tabellen und 6.300/6.300 Zielzeilen.
15. **PR 101: gemeinsamen Vollfensterbericht bewerten.**
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

PR 87 ist der Planungs-PR; PR 88 bis PR 96 haben Archivmanifest,
Referenzkohaerenz, archivlokale Laufmetadaten, den getrennten
Referenzschicht-Vertrag, den Horizontvertrag und die erste 100er-Korpuslieferung
abgeschlossen, den modernen Zustand bis 500 fortgeschrieben und die zwei
ZINS000-Regelfenster verglichen. Danach sind **5 geplante PRs** bis zum ersten
gemeinsamen 6.300-Zeilen-Vollfensterbericht offen: vier historische
Vollfenster-Liefer-PRs und ein Bewertungs-PR.

Verbleibende grobe Bruttoabschaetzung fuer PR 97 bis PR 101:

| Anteil | Erwarteter Umfang |
| --- | ---: |
| Python-Produktionscode | 75-350 LoC |
| Tests | 200-600 LoC |
| Vertraege, Fixtures und Dokumentation | 250-650 LoC |
| Gesamt | 525-1.600 LoC |

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
