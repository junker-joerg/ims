# Plan: Historische Referenzprovenienz und Vollfenster

Stand: 2026-08-31
Planungsschnitt: PR 87
Umsetzungsstand: PR 90

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
5. **PR 91: Referenzschicht-Vertrag entscheiden.**
   Fuer jedes der 19 Ziele `layer_id`, Quellarchiv oder Direktquelle,
   Hashbezug, Koharenzklasse und zulaessige Aussage einfrieren. Das bestehende
   Kernbundle wird nur nach separatem, belegtem Entscheid geaendert. Dieses
   PR setzt das Stop/Go-Tor fuer die Vollfensterphase.

### Phase B: Kontrollierte Vollfenster

6. **PR 92: Horizontvertrag 100/300/500 vorbereiten.**
   Periodengrenzen konfigurierbar machen, Prefix-Stabilitaet und identische
   1-100-Ergebnisse vertraglich pruefen. Noch kein 300-/500-Vollvergleich.
7. **PR 93: bestehende 100-Perioden-Tabellen streng anbinden.**
   `imsvu014.dat` und `imsvnsk1.dat` als die zwei bereits vollstaendigen
   100er-Ziele an den Produktionskorpusbericht uebergeben. Erwarteter
   Fortschritt: 2/15 Tabellen und 200/6.300 Zielzeilen vollstaendig geliefert.
8. **PR 94: Zustandsfortschreibung bis Periode 300 schliessen.**
   Den bestehenden kontrollierten Zustand deterministisch bis 300 fortsetzen.
   Die Perioden 1-100 muessen unveraendert bleiben; neue historische
   Scheduler-, RNG- oder Akkumulatorsemantik wird nicht still eingefuehrt.
9. **PR 95: 300er-Regelfenster anbinden.**
   `imsvnr01.dat` und `imsvnr02.dat` vollstaendig vergleichen. Erwarteter
   kumulierter Fortschritt: 4/15 Tabellen und 800/6.300 Zielzeilen.
10. **PR 96: Zustandsfortschreibung bis Periode 500 schliessen.**
    Den 300er-Zustand deterministisch bis 500 erweitern und Prefix-Stabilitaet
    fuer 1-100 und 1-300 pruefen.
11. **PR 97: VU-SK1-Zeitfenster anbinden.**
    Eine berechnete `imsvusk1.dat` mit 500 Perioden gegen `VUSK1L5` bis
    `VUSK1L1` ausrichten. Erwarteter Fortschritt: 5/15 Tabellen und
    1.300/6.300 Zielzeilen.
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

PR 87 ist der Planungs-PR; PR 88 bis PR 90 haben Archivmanifest,
Referenzkohaerenz und archivlokale Laufmetadaten abgeschlossen. Danach sind
**11 geplante PRs** bis zum ersten gemeinsamen
6.300-Zeilen-Vollfensterbericht offen: ein Provenienz-PR und zehn
Vollfenster-/Bewertungs-PRs.

Verbleibende grobe Bruttoabschaetzung fuer PR 91 bis PR 101:

| Anteil | Erwarteter Umfang |
| --- | ---: |
| Python-Produktionscode | 600-1.400 LoC |
| Tests | 800-1.700 LoC |
| Vertraege, Fixtures und Dokumentation | 900-2.200 LoC |
| Gesamt | 2.300-5.300 LoC |

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
