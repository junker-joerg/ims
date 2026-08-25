# Gemeinsame Vdefmd6-Kernexportbewertung

Stand: 2026-08-25
Vertragsversion: `pr86-v1`

## Ziel

PR 86 fuehrt erstmals alle 15 berechneten Kernexportidentitaeten aus einem
gemeinsamen kontrollierten `Vdefmd6`-Zustand durch den vorhandenen
PR-59-Abweichungsbericht. Die historischen Referenzen werden erst nach der
vollstaendigen In-Memory-Erzeugung gelesen.

Der Vergleich umfasst fuer jede Identitaet die Perioden 1-100. Er umfasst
damit 1.500 Zielzeilen, nicht den gesamten Produktionskorpus mit 19 Referenzen
und 6.300 Zielzeilen.

## Gemeinsamer Befund

| Familie | Exporte | Felder | Treffer | Fachwerte | Fachwerttreffer | Volle Zeilen |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| VU14 | 1 | 1.400 | 488 | 1.200 | 288 | 1 |
| VU SK1/all und Klassen | 4 | 5.600 | 898 | 4.800 | 98 | 2 |
| VN-Regeln | 6 | 7.800 | 1.872 | 6.600 | 672 | 0 |
| VN SK1/all und Klassen | 4 | 5.200 | 1.234 | 4.400 | 434 | 0 |
| Gesamt | 15 | 20.000 | 4.492 | 17.000 | 1.492 | 3 |

Alle 3.000 Strukturfelder fuer Header und Periodenindex treffen. Von den
20.000 Feldern treffen damit 4.492/20.000; von den 17.000 eigentlichen
Fachwerten treffen 1.492/17.000. Nur VU14, VU-SK1/all und
VU-Klasse 1 stimmen jeweils in Periode 1 als ganze Zielzeile; gemeinsam ueber
alle 15 Exporte ist bereits Periode 1 nicht vollstaendig gleich.

## Abweichungsklassen

Der bestehende Abweichungsbericht klassifiziert die 20.000 Felder wie folgt:

- 3.839 exakte Feldtreffer;
- 653 tolerierte numerische Unterschiede innerhalb der bestehenden Toleranz;
- 14.752 blockierende numerische Unterschiede;
- 756 offene nichtnumerische Feldfragen.

Exakte und tolerierte Treffer ergeben zusammen die 4.492 Feldtreffer. Die
offenen Feldfragen werden nicht pauschal einer Ursache zugeschrieben. Besonders
die historische Bedeutung von `Ev1` und `Ev2` sowie fehlende moderne
Moduswerte bleiben separat zu klaeren.

## Zeitfenster und Referenzidentitaet

`VUSK1L5.DAT` belegt im gemeinsamen Bericht das Fenster 1-100 des
VU-SK1-/all-Aggregats auf Stufe IV. `VUSK1L1.DAT` bis `VUSK1L4.DAT` bleiben
die spaeteren Zeitfenster 401-500 bis 101-200 derselben Exportidentitaet. Sie
sind keine unterschiedlichen Aggregatebenen.

Viele Regel- und Klassenreferenzen reichen bis Periode 300 oder 500. Der
kontrollierte Runner erzeugt in diesem Vertrag nur 1-100. Deshalb bleibt
`full_legacy_corpus_window_complete = false`, obwohl alle 15 Identitaeten fuer
das gemeinsame Fenster vorhanden und verglichen sind.

## Menschliche Freigabebewertung

Die Empfehlung lautet `keep_blocked`. Die technische Workbench-Demo und ihre
Windows-Pruefkette bleiben nutzbar; eine historische Gleichwertigkeit oder
fachliche Produktionsfreigabe ist dagegen nicht belegt.

Blockierend bleiben insbesondere:

- historische Laufidentitaet und Koharenz aller Referenzfamilien;
- Same-Slot-Reihenfolge und RNG-Ziehfolge;
- Ableitung des historischen Versicherungsgrads;
- historische VU-Klassen-, VN-Regel- und VN-Klassenakkumulatoren;
- Initialisierungsdetails des VN-SK1-/all-Aggregats;
- Bedeutung der VN-`Ev`-Felder;
- Pflichtfenster oberhalb von Periode 100.

Die abgeschlossene PR-72- bis PR-86-Serie liefert damit eine belastbare
Abweichungskarte, aber keine historische Vollgleichheitsbehauptung.

## Maschinenlesbarer Bericht

Aus dem Verzeichnis `python_port`:

```powershell
python -m ims.api.vdefmd6_core_export_review_report --repo-root ..
```

Erwartet werden `status = "review_ready"`, 15 kontrollierte Exporte,
`review_recommendation = "keep_blocked"`,
`production_release_approved = false`, `writes_performed = false` und
`simulation_performed = false`.

## Folgephase

Es gibt nach PR 86 keinen weiteren vorab nummerierten Pflicht-PR. Der naechste
groessere Block sollte zuerst die historische Lauf- und Referenzprovenienz
klaeren. Erst auf dieser Basis ist zu entscheiden, ob anschliessend
Akkumulator-, Scheduler- oder RNG-Kompatibilitaet in kleinen fachlichen Slices
umgesetzt wird.
