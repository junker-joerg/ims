# VU14-Erzeugungsvertrag fuer Perioden 1-100

Stand: 2026-08-25
Vertragsversion: `pr72-v1`

## Ziel

PR 72 bereitet den maschinenlesbaren Abnahmevertrag fuer eine spaetere,
unabhaengige Erzeugung von `imsvu014.dat` vor. Der Vertrag umfasst genau
Versicherer 14, Aggregatstufe I und die lueckenlosen globalen Perioden
`1-100`.

Der Schritt erzeugt keine Exporttabelle und startet weder Runner noch
Simulation. `contract_ready = true` bedeutet nur, dass die Anforderungen an
PR 73 vollstaendig und widerspruchsfrei beschrieben sind.

## C-zu-Python-Zuordnung

| Historischer Ursprung | Python-Anschluss | Bedeutung |
| --- | --- | --- |
| `IMSDATA.C:94-103` | `agrsich_export.py` | Dateiname `imsvu014.dat`, Stufe I, Entity 14 |
| `IMS.E:1045-1063`, `PlanVU` | `vu_rule_runner.py` | Regelaufruf nach expliziter Zuordnung und Aktionszeit |
| `IMS.E:402-446`, `Agrsich` | `agrsich_service.py` und `agrsich_export.py` | Projektion des aktuellen VU-Zustands in 13-spaltige Periodenzeilen |
| vorhandener Vier-Perioden-Plan | `replay_plan.py` | Writer-/Vergleichsnachweis, keine unabhaengige Zustandsentstehung |

Der versionierte Altcode belegt Dateiname, Ausgabeform und Dispatchgrenze. Er
belegt fuer den konkreten Referenzlauf weder die vollstaendige Population noch
Regelparameter, Aktionsfolge oder historischen Zufallsstrom.

## Maschinenlesbarer Vertrag

Die Datei `tests/fixtures/vu14_100_period_generation_contract.json` verlangt:

- Zielidentitaet `insurer / I / entity = 14 / imsvu014.dat`;
- Periodenstart `1`, Periodenende `100`, Anzahl `100`;
- sechs belegte Eingangsgruppen fuer Population, Startzustand,
  Regel-/Aktionsplan, RNG, Zustandsfortschreibung und VN-/Schadensergebnisse;
- sechs Zwei-Sparten-Zustandsfelder fuer Praemie, Werbung, Reserven,
  Versicherte, Schadenanzahl und Schadensumme;
- Vergleich mit `VU14L1.DAT` erst nach unabhaengiger Berechnung.

Read-only pruefbar ist der Vertrag mit:

```powershell
python -m ims.api.vu14_generation_contract --repo-root .
```

Der erwartete Befund lautet:

- `status = "prepared"` und `contract_ready = true`;
- `required_period_count = 100`;
- `input_requirement_count = 6`;
- `currently_evidenced_input_requirement_count = 4` nach der PR-73-Quellenbindung;
- `generation_ready = false`;
- `independent_full_window_ready = false`;
- keine Schreib-, Runner-, Ausfuehrungs- oder Simulationsflags.

## Bestehender Vier-Perioden-Slice

`replay_vu14_period_plan.json` belegt die Perioden `1-4`, den Writer und den
Vergleich. Seine Periodenupdates setzen jedoch direkt:

- Praemie und Werbung;
- Reserven und Versicherte;
- Schadenanzahl und Schadensumme.

Der Slice bleibt deshalb `acceptable_as_generation_input = false`. Eine
Ausdehnung derselben direkten Vorgaben auf Perioden `5-100` waere lediglich
ein Referenz-Echo und kein unabhaengiger Zustandsweg.

## Offene Erzeugungsblocker

1. belegte RNG-Ziehungs- und Verbrauchsreihenfolge;
2. VN-/Schadenpfad fuer die Ergebnisfelder;
3. unabhaengige, durchgaengige Zustandsfortschreibung fuer Perioden 2-100;
4. daraus berechnete Exporttabelle fuer alle 100 Perioden.

Historische RNG-Vollgleichheit ist keine Annahme des Vertrags. Eine spaetere
Abweichung muss als RNG-, Scheduler-, Populations-, Daten- oder
Implementierungsbefund klassifiziert werden.

## PR-72-Pruefnachweis

Am 2026-08-25 wurden ausgefuehrt:

- read-only Vertragsbericht: `status = "prepared"`, 100 geforderte Perioden,
  sechs Herkunftsgruppen, acht Quellanker und keine Vertragsissues;
- 99 gezielte Vertrags-, Replay-, Plan- und Dokumentationstests;
- vollstaendiges Windows-Gate mit 1.177 Python-Tests;
- Frontend-Produktionsbuild mit 1.578 transformierten Modulen;
- Bundle-, Staging-, Readiness- und Release-Smoke;
- keine Ausfuehrung, keine Simulation und keine fachliche Freigabe.

## Fortschreibung durch PR 73

PR 73 hat Population, Startzustand, VU14-Regel/Aktionszeit und
Zustandsursprung an `Vdefmd6` gebunden. Die echte VU14-Referenz ersetzt die
zuvor linear konstruierte Testreihe. Eine unabhaengig erzeugte Periode 1 stimmt
in 14/14 Feldern; RNG und VN-/Schadenpfad fuer Perioden 2-100 bleiben offen.

## Fortschreibung durch PR 74

PR 74 hat die `Vdefmd6`-Population mit 25 VU und 200 VN typisiert aufgebaut
und den VU14-Perioden-1-Pfad daran angeschlossen. Nach PR 74 verbleiben
mindestens acht reviewbare Schritte bis zur gemeinsamen fachlichen Bewertung.
Die aktuelle Detailplanung steht in `vu14_vdefmd6_source_binding.md`.

## Fortschreibung durch PR 75

PR 75 hat 200 wirksame Aktionsslots fuer Perioden 1-100 und die moderne Policy
`ims-modern-explicit-run-v1` gebunden. Der Basis-Seed ist zwingend explizit;
Run `n` verwendet reproduzierbar `base_seed + n - 1`. Diese Policy belegt
weder den historischen Seed noch Algorithmus, Draw-Reihenfolge oder
Draw-Anzahl. Deshalb bleiben vier Erzeugungsblocker und sieben geplante PRs
bis PR 82 offen.

## Fortschreibung durch PR 76

PR 76 hat VU14 aus `Vdefmd6` und `Vrvu06` fuer Perioden 1-49 ohne Legacy-
Erzeugungsinput projiziert. Die direkten Regelfelder treffen die Referenz fuer
Perioden 1-16; nur Periode 1 trifft als vollstaendige Zeile. In Periode 17
wird der fehlende Vorperiodenschaden erstmals fuer die Regelverzweigung
entscheidungsrelevant. Reserven, Versicherte und Schadenfelder bleiben ab
Periode 2 durch den VN-/Schaden-/Settlement-Pfad offen.

Der Bericht ist `rule_projection_ready = true`, aber weiterhin
`independent_periods_2_49_ready = false` und `generation_ready = false`.
Der Befund teilte die damalige Restplanung; die Fortschreibung durch PR 78
unten ersetzt inzwischen deren Nummerierung und Umfang.

## Fortschreibung durch PR 77

PR 77 hat fuer alle sechs `Vdefmd6`-VN-Regeln die Vorschock-Eingaben, den
gemeinsamen Schadenpfad und die Settlement-Schreibflaechen kartiert. Die 150
aktiven VN verursachen historisch mindestens 7.200 uniforme Basisziehungen je
Periode allein im Schadenteil. Die Reihenfolge der zwei `normal()`-Aufrufe
innerhalb einer C-Schadenformel sowie die historische VN-Same-Slot-Reihenfolge
bleiben unbestimmt. Deshalb bleiben Erzeugung und historische RNG-Gleichheit
gesperrt. PR 78 hat darauf die VN-Snapshots einer einzelnen Vorschockperiode
materialisiert. PR 79 hat alle VU-Snapshots und BAV-Vorperiodeninputs
geschlossen. Ab PR 80 verbleiben mindestens sieben Schritte bis PR 86.

Eine fachliche Freigabe oder historische Vollgleichheit folgt weder aus PR 72
noch aus Quellenbindung, Populationsbuilder, Aktions-/Seed-Vertrag oder
Vorschock-Regelprojektion in PR 73 bis PR 76.
