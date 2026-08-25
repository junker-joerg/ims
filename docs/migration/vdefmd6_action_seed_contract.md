# Vdefmd6-Aktions- und Seed-Vertrag

## Ziel

PR 75 beschreibt die wirksamen Aktionsslots der typisierten `Vdefmd6`-
Population fuer Perioden 1-100 und definiert eine explizite moderne
Seed-Policy. Der Vertrag ist eine pruefbare Vorbereitung fuer die spaetere
Zustandsfortschreibung; er fuehrt selbst nichts aus.

## Mapping

| Historischer Ursprung | Python-Ziel | Entsprechung |
| --- | --- | --- |
| `IMS.E:21-28`, `Frmdinf` | `Vdefmd6ActionSlot`, Zeit 1 | zentrale Fremdinformation |
| `imsvu.e`, `PlanVU` und `IMS.E:1045-1063` | `insurer_rule` | Koordinator 1-10, wirksame VU-Regel bei Zeit 1 |
| `imsvn.e`, `PlanVN` und `IMS.E:2143-2161` | `policyholder_rule` | Koordinator 1-10, wirksame aktive VN-Regel bei Zeit 1 |
| `IMS.E:21-28`, `Agrsich` | `Vdefmd6ActionSlot`, Zeit 10 | zentraler Aggregat-/Exportzeitpunkt |
| `IMS.E:6022-6044` | `ModernSeedPolicy` | dokumentierte Abgrenzung vom historischen Zeit-Seed |

Der Plan enthaelt 200 Slots und 20.250 wirksame Aufrufe. In Perioden 1-49
enthaelt Zeit 1 jeweils BAV, 25 VU und 150 aktive VN. Ab Periode 50 kommen die
50 spaet aktivierten VN hinzu. Zeit 10 enthaelt je Periode genau den zentralen
Aggregat-/Exportaufruf.

Die Koordinatoren werden auch zu Zeiten 2-10 aufgerufen. Da `Vdefmd6` nur den
ersten Aktionsvektoreintrag mit Zeit 1 belegt, entstehen daraus keine weiteren
wirksamen Regelaufrufe und damit keine zusaetzlichen Planslots.

## Seed-Policy

`ims-modern-explicit-run-v1` verlangt einen nichtnegativen expliziten
`base_seed`. Run `n` erhaelt reproduzierbar `base_seed + n - 1`, maximal fuer
100 Runs. Es gibt keinen versteckten Defaultseed.

Der historische Code leitete seinen Seed aus Sekunde, Minute und Kalendertag
ab. Der konkrete Seed des Referenzlaufs ist nicht belegt. Die moderne Policy
ersetzt diese fehlende Information nicht und belegt weder historischen
Generatoralgorithmus noch Draw-Reihenfolge oder Draw-Anzahl.

## Gleichzeitige Aktionen

Alle wirksamen VU- und VN-Regeln sowie `Frmdinf` liegen bei logischer Zeit 1.
Die Python-Struktur serialisiert einen solchen Slot stabil als BAV, VU nach ID
und VN nach ID. Diese Reihenfolge dient nur Vergleich, JSON-Ausgabe und Tests.
Sie ist keine Ausfuehrungsreihenfolge und keine historische Behauptung.

## Pruefbericht

`python -m ims.api.vdefmd6_action_seed_report --repo-root .` prueft:

- Slot-, Aktivierungs- und Aufrufzahlen;
- Seed-Ableitung und Beispielwerte;
- 13 historische Quellanker;
- die Sperre gegen Schedulerstart, RNG-Ziehungen und Simulation;
- die Sperre gegen historische RNG- oder Vollgleichheitsbehauptungen.

Der VU14-Erzeugungsvertrag nimmt diesen Bericht als weitere Quelle auf. Seine
vier offenen Blocker bleiben dennoch bestehen, insbesondere
`rng_stream_origin_missing`, weil der moderne Basis-Seed allein Algorithmus,
Draw-Reihenfolge und Draw-Anzahl nicht belegt.

## Grenzen und Folge

- kein Schedulerstart;
- keine RNG-Ziehung;
- keine Regel- oder Fachlogikausfuehrung;
- keine Verwendung historischer Ausgaben als Eingaben;
- keine historische Vollgleichheitsbehauptung.

PR 76 hat die VU14-Regelprojektion fuer Perioden 1-49 klassifiziert und dabei
den offenen VN-/Schaden-/Settlement-Pfad ab Periode 2 belegt. PR 77 hat diesen
Pfad fuer sechs Regeln und 150 aktive Vorschock-VN kartiert. PR 78 hat die
VN-Snapshots einer einzelnen Vorschockperiode materialisiert. Ab PR 79 bleiben
mindestens acht Schritte bis PR 86.
