# Vertrag fuer berechnete Legacy-Mehrperiodenvergleiche

## Ziel

PR 58 trennt den kuenftigen berechneten Neu-/Alt-Vergleich technisch vom
bisherigen fixturegetriebenen Legacy-Selbstvergleich. Das neue Modul
`python_port/ims/model/legacy_calculated_comparison.py` nimmt bereits
berechnete `ExportTable`-Ergebnisse entgegen und vergleicht sie erst nach einer
strikten Vollstaendigkeitspruefung mit den historischen Referenzen.

Dieser PR startet keine Simulation und fuehrt noch keinen berechneten Lauf fuer
den gesamten Kernkorpus aus. Er schafft den Eingangs- und Vergleichsvertrag.
Damit ist weiterhin weder historische Vollgleichheit noch eine fachliche
Abweichungsfreiheit belegt.

## Ursprung und Python-Zuordnung

Dieser Schnitt portiert keine neue C-Fachlogik. Er verbindet vorhandene
Migrationsbausteine:

| Ursprung / bestehende Grenze | Python-Komponente | Rolle in PR 58 |
| --- | --- | --- |
| historische Agrsich-Ausgaben | `legacy_agrsich_reference.py`, `legacy_vn_reference.py` | Referenzparser fuer VU- und VN-Tabellen |
| vorhandener Mehrperiodenvergleich | `legacy_agrsich_multi_period.py` | Feld- und Zeilenvergleich mit Toleranz |
| Kernbundle | `tests/fixtures/legacy_validation_bundle.json` | 19 Ziele und 6.300 belegte Referenzperioden |
| berechnete Agrsich-Tabellen des Python-Ports | `ExportTable` | von aussen zu liefernde Neu-Ergebnisse |
| neuer Vertrag | `legacy_calculated_comparison.py` | Sollplan, Eingangspruefung und Vergleich |

Der historische C-Generator, Scheduler und RNG werden durch diesen Vertrag
nicht rekonstruiert. Die `calculation_origin` ist eine verpflichtende
Herkunftsangabe des Aufrufers, aber noch kein automatisch verifizierter
Provenienznachweis.

## Sollplan fuer den Kernkorpus

`build_calculated_legacy_comparison_plan(...)` liest nur Zielmetadaten und
liefert fuer das aktuelle Kernbundle:

- 19 historische Ziele;
- 6.300 Zielperioden;
- 15 eindeutig benoetigte berechnete Exporttabellen;
- fuer `imsvusk1.dat` genau die Perioden `1-500`, zusammengesetzt aus den
  fuenf Zeitfenstern desselben `SK1`-/`all`-Aggregats auf Stufe IV;
- fuer `imsvnsk1.dat` weiterhin nur das belegte Fenster `1-100`.

ZINS000 ist nicht Teil dieses Sollplans. Die getrennte Schicht unter
`tests/references/legacy_agrsich/zins000/` kann nur ueber ein eigenes Fixture
ausgewaehlt werden.

## Strikte Vergleichsgrenzen

`compare_calculated_export_tables_to_legacy_fixture(...)` verlangt:

1. eine nichtleere deklarierte `calculation_origin`;
2. genau die im Fixture benoetigten Exportidentitaeten aus Dateiname,
   Subjekttyp, Stufe, Selektorart und Selektorwert;
3. keine fehlende, doppelte oder zusaetzliche Exporttabelle;
4. je Export exakt die sortierte Periodenmenge des Sollplans;
5. keine fehlende, doppelte, vertauschte oder stillschweigend ignorierte
   Periodenzeile;
6. Vergleich nur gegen das jeweils explizit eingetragene Referenzfenster.

Der Vergleich baut keine Exportzeile aus einer Legacyreferenz. Er schreibt
keine Datei, startet keinen Runner und meldet
`legacy_fixture_rows_used_as_export = false`, `execution_performed = false`
sowie `simulation_performed = false`.

`calculation_origin_verified = false` bleibt bewusst sichtbar: Der Vertrag
belegt, dass die Tabellen von aussen uebergeben wurden, kann aber allein nicht
beweisen, welcher Runner sie erzeugt hat.

## Validierung in PR 58

Die Tests pruefen:

- den 15-/19-/6.300-Sollplan des Kernkorpus;
- die korrekte VUSK1-Zeitfenstervereinigung ohne Aggregatebenenwechsel;
- den Ausschluss der ZINS000-Schicht;
- einen positiven In-Memory-Vergleich zweier berechneter Testperioden;
- die Meldung einer numerischen Feldabweichung;
- die Ablehnung falscher Periodengrenzen, falscher Exportmetadaten und einer
  fehlenden Herkunftsangabe.

Der positive Vertragstest ist kein historischer Kernkorpus-Nachweis. Er
verifiziert nur die Vergleichsmechanik mit kontrollierten Testwerten.

## Naechster Schritt

PR 59 hat den read-only Abweichungsbericht angebunden und weist fehlende der 15
Kernexporttabellen als blockierende Inputluecken aus. PR 60 soll einen ersten
schmalen Aggregat-/Export-Output liefern und hat vier VU14-Perioden angebunden.
PR 61 hat die technische Level-IV-Selektorgrenze `all` gegen `SK1` eng
kanonisiert und getestet. Fixturegenerierte Echo-Tabellen duerfen nicht als
Neu-Ergebnisse verwendet werden. Erst tatsaechlich gelieferte berechnete
Tabellen duerfen Treffer oder Abweichungen erzeugen. PR 62 hat den read-only
Run-Control-Freigabecheck umgesetzt; PR 63 bereitet als naechstes die atomare
Backend-Start-/Statusgrenze vor.
