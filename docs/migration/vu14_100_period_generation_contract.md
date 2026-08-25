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
- `currently_evidenced_input_requirement_count = 0`;
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

1. vollstaendig belegte VU-/VN-/BAV-Population;
2. belegte VU14-Regelparameter und logische Aktionsfolge;
3. belegte RNG-Quelle mit Seed-, Ziehungs- und Verbrauchsreihenfolge;
4. unabhaengige, durchgaengige Zustandsfortschreibung;
5. daraus berechnete Exporttabelle fuer alle 100 Perioden.

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

## Restplanung

Nach PR 72 verbleiben mindestens sechs reviewbare Schritte:

1. PR 73: unabhaengigen VU14-Zustandsweg fuer `1-100` auf Basis belegter
   Population, Regel-/Aktionsdaten und RNG-Grenze umsetzen und vergleichen;
2. PR 74: dieselbe Versicherer-Population auf SK1/all und VU-Klassen
   verbreitern;
3. PR 75 und PR 76: VN-Regelzustand in zwei kleinen Gruppen schliessen;
4. PR 77: VN-Klassen und SK1/all aus demselben Zustand vergleichen;
5. PR 78: alle 15 Exporte gemeinsam bewerten.

Funde in Population, Scheduler, RNG oder Zustandsfortschreibung koennen PR 73
in weitere kleine Slices teilen. Eine fachliche Freigabe oder historische
Vollgleichheit folgt aus PR 72 nicht.
