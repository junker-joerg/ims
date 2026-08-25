# Plan: Herkunfts- und Erzeugungswegkarte fuer PR 71

## Ziel

PR 71 ordnet die 15 vom PR-69-Bericht verlangten berechneten Kernexporte
ihren historischen Ausgabestellen, vorhandenen Python-Pfaden und verbleibenden
Erzeugungsluecken zu. Die Karte ist read-only. Sie erzeugt keine Exporttabelle,
startet keinen Runner und fuegt keine Fachlogik hinzu.

## Quellen

- `IMSDATA.C` benennt die historischen Dateien in `agvu*nm` und `agvn*nm`.
- `IMS.E`, `act Agrsich`, bildet und schreibt die Stufen I bis IV.
- `tests/fixtures/legacy_validation_bundle.json` definiert die 19
  Referenzziele und 15 eindeutigen Exportidentitaeten des Kernkorpus.
- `legacy_calculated_comparison.py` gruppiert diese Ziele zum bestehenden
  strikten Vergleichsvertrag.
- `explicit_period_runner.py` verbindet explizite VU-/VN-Snapshots mit
  Aggregatbildung und Exportrepraesentation.
- `agrsich_service.py` und `agrsich_export.py` bilden die vorhandene
  Aggregat-/Writer-Grenze.

## Einordnung

Die 15 Dateien sind keine 15 unabhaengigen Generatoren. Sie stammen aus zwei
gemeinsamen Zustandsfamilien:

1. Versichererzustand: `imsvu014.dat`, `imsvusk1.dat` und
   `imsvuvk1.dat` bis `imsvuvk3.dat`;
2. VN-Zustand: `imsvnr01.dat` bis `imsvnr06.dat`, `imsvnsk1.dat` und
   `imsvnvk1.dat` bis `imsvnvk3.dat`.

Der Python-Port kann fuer explizit gelieferte Periodenzustaende alle 15
Dateinamen und Aggregatstufen bilden. Daraus folgt noch keine vollstaendige,
unabhaengige Erzeugung der geforderten 100 bis 500 Perioden.

## Bericht

`python_port/ims/api/calculated_export_provenance_report.py` soll:

- die 15 Identitaeten aus dem bestehenden Bundle ableiten;
- je Identitaet Referenzdateien, Periodenfenster und C-/Python-Anker melden;
- Writer- und expliziten Runner-Anschluss getrennt von der vollstaendigen
  Zustandsentstehung ausweisen;
- den kleinen VU14-Nachweis und vorhandene Replay-Fixtures nur in ihrem
  belegten Umfang benennen;
- gemeinsame Luecken fuer Produktionspopulation, historische automatische
  Regelwahl/Scheduling, RNG-Ausrichtung und volle Periodenfortschreibung
  sichtbar halten;
- `independent_full_window_ready = false` fuer alle 15 Identitaeten melden.

## Validierung

- exakt 15 eindeutige Identitaeten und 19 Referenzziele;
- exakt 5 Versicherer- und 10 VN-Exporte;
- Writer- und expliziter Runner-Anschluss fuer alle 15 Identitaeten;
- kein vollstaendig unabhaengig erzeugtes Exportfenster;
- VUSK1L1-5 bleiben fuenf Zeitfenster derselben Identitaet
  `imsvusk1.dat` auf Stufe IV mit `all = SK1`;
- read-only CLI mit stabilen Negativflags;
- Drift oder fehlende Quellanker fuehren zu `status = "error"`.

## Grenzen

- kein Zugriff auf `incomming/`;
- keine Exporterzeugung und kein Dateischreiben;
- kein Adapter-, Runner-, Scheduler-, Queue- oder Serverstart;
- keine Simulation als Produktlauf;
- keine neue Fachlogik oder automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung;
- keine fachliche Produktionsfreigabe.

## Danach

PR 72 soll den kleinsten gemeinsamen Erzeugungsblock festlegen. Nach heutigem
Stand ist das kein weiterer Writer-PR, sondern ein kontrollierter
Versicherer-Zustandspfad fuer den 100-Perioden-Kern von `imsvu014.dat`, bevor
breitere Klassen- oder VN-Familien angegangen werden.
