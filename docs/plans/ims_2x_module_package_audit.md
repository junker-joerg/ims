# PR103: Python-Modul- und Paket-Audit fuer IMS 2.x

Stand: 2026-09-02
Status: umgesetzt
Ausgangspunkt: `ims-legacy-baseline-2026-09-01` auf Commit `2e92637`

## Ziel

PR103 prueft die gewachsene Python-Struktur, bevor Strategie-, Bilanz- und
Regulierungsfunktionen neue Modulgrenzen schaffen. Der Schritt verschiebt oder
vereinigt noch keine Module und fuehrt keine Fachlogik ein.

Der Freeze bleibt unveraendert als technisch release-bereite
IMS-1995-2026-Migrationsbaseline erhalten. IMS 2.x beginnt als Alpha-Fassung;
das ist keine fachliche Produktionsfreigabe.

## Messbarer Bestand

Das maschinenlesbare Inventar liegt in
`docs/plans/ims_2x_module_inventory.csv`. Es wird aus dem aktuellen
`python_port` mit `scripts/architecture/build-module-inventory.py` erzeugt.

| Bereich | Dateien | Zeilen | Einordnung |
| --- | ---: | ---: | --- |
| `python_port/ims/api` | 75 | 25.619 | Legacy-Berichte, Workbench, Run-Control und Packaging liegen noch gemeinsam |
| `python_port/ims/model` | 27 | 12.968 | historische Regeln, Zustandsobjekte und Legacy-Vergleich |
| `python_port/ims/engine` | 22 | 6.529 | Scheduler, Runner, Replay und Diagnose |
| `python_port/ims/io` | 2 | 513 | Szenarioeinlesung |
| `python_port/ims/analysis` | 2 | 60 | kleine Aggregatschicht |
| Paketwurzel `python_port/ims` | 1 | 6 | Paketmarker |
| alte Scaffolds ausserhalb `ims` | 7 | 80 | nicht installiert und ohne nachgewiesene Imports |
| **Gesamt** | **136** | **45.775** | ohne Tests |

Hinzu kommen 171 Testdateien mit rund 39.815 Zeilen. Die Dateimenge ist damit
nicht mit 136 gleichgewichtigen Fachkomponenten gleichzusetzen. Allein 30
API-Dateien mit rund 13.900 Zeilen gehoeren zur abgeschlossenen historischen
Validierungs- und Lieferschicht.

## Bewertung der Dateifrage

Eine Rueckkehr zu sechs oder sieben Python-Dateien ist nicht sinnvoll. Bereits
heute haben `legacy_validation_run.py` rund 3.200, `vu_rules.py` rund 1.770,
`vn_insurance_rules.py` rund 1.590 und `simulation.py` rund 1.050 Zeilen. Eine
weitere Zusammenlegung wuerde fachliche Regeln, Ausfuehrung, historische
Diagnose und Web-Anwendung erneut vermischen.

Sinnvoll sind wenige verstaendliche Pakete mit kleinen, fachlich
zusammenhaengenden Modulen. Die Anzahl der Dateien ist dabei eine
Beobachtungsgroesse, aber keine Erfolgskennzahl.

## Zielpakete

| Zielpaket | Verantwortung | Grenze |
| --- | --- | --- |
| `ims.domain` | VU, VN, BAV und Marktobjekte | keine Web-, Persistenz- oder historische Vergleichslogik |
| `ims.strategies` | Katalog, Parameter, Zuordnung und Compiler | historische Regel-ID bleibt getrennte Identitaet |
| `ims.simulation` | Kontext, Scheduler, RNG, Periodenuebergang und Runner | keine UI- oder Speicherabhaengigkeit |
| `ims.accounting` | Bewegungsrechnung, Kosten, Modellbilanz und spaeter Kapital | zunaechst berichtend, keine stille Strategiewirkung |
| `ims.regulation` | Intervention, Geltungsbereich, DORA und Resilienz | eigene operative Zeitskala und expliziter Marktadapter |
| `ims.legacy` | Referenzen, Korpus, Vergleiche und Migrationsdiagnostik | eingefrorene Benchmark-Schicht, keine neue Produktlogik |
| `ims.workbench` | Web-API, Metadaten, Run-Control und lokale Auslieferung | greift nur ueber Anwendungsvertraege auf den Kern zu |
| `ims.io` / `ims.reporting` | Szenarien, Manifeste, ResultBundle und Exporte | ein gemeinsamer Datenstand fuer UI, CSV, JSON und XLSX |

Die Namen sind Zielrichtungen, noch keine freigegebenen Dateiverschiebungen.
Oeffentliche Imports bleiben bis zu getrennten Konsolidierungs-PRs stabil.

## Konkrete Auditentscheidungen

1. Historische `legacy_*`, `historical_*`, `vdefmd6_*` und `vu14_*`-Module
   werden fachlich eingefroren und spaeter unter `ims.legacy` gebuendelt.
2. Die grossen 100-/300-/500-Liefermodule sind Kandidaten fuer einen
   konfigurationsgetriebenen gemeinsamen Kern. Wegen ihrer Referenzvertraege
   ist das Risiko hoch; die Zusammenlegung erfolgt nur mit unveraenderten
   Korpus- und CLI-Tests.
3. `legacy_validation_run.py`, die VU-/VN-Regelmodule und `simulation.py`
   duerfen nicht weiter anwachsen. Eine Teilung ist nur nach Verantwortung und
   mit Charakterisierungstests sinnvoll.
4. Duenne Workbench-Vertraege werden nur vereinigt, wenn sie denselben
   Aenderungsgrund, dieselben Abhaengigkeiten und denselben Lebenszyklus haben.
5. `app.py` bleibt vorerst kompatibel, soll aber spaeter Routenregistrierung
   von Payload-Aufbau und Anwendungsdiensten trennen.
6. `python_port/context`, `python_port/entities` und
   `python_port/scheduler` sind alte, nicht installierte Scaffolds ohne
   nachgewiesene Imports. Sie koennen nach einem letzten Paket- und Importcheck
   entfernt werden.
7. Es gibt keine pauschale Zielquote. Der fruehere Pruefbereich von etwa 90 bis
   115 Produktionsdateien bleibt nur eine Schaetzung; notwendige Teilungen
   koennen die Zahl wieder erhoehen.

## Bereits vorhandene Grundlage fuer Regulierung

| Bedarf | Heutiger Stand | Folgerung |
| --- | --- | --- |
| deterministische Zeit und Seeds | `SimulationContext`, Scheduler und expliziter RNG vorhanden | weiterverwenden |
| VU-/VN-Zustaende | Praemien, Werbung, Reserven, Versicherte und Schadensummen vorhanden | Legacy-Felder nicht umdeuten |
| historische Herkunft | 15 Tabellen und 6.300 Zeilen diagnostisch angeschlossen | read-only unter `ims.legacy` erhalten |
| Szenario- und Run-Nachweis | Metadaten, Freigaben und Run-Control vorhanden | zu `ScenarioVersion` und `RunManifest` erweitern |
| Fachaggregate | bislang nur Aktivitaet und Zuordnung in der kleinen Analyseschicht | neue Kennzahlen aus einem ResultBundle ableiten |

## Fehlende gemeinsame Zustaende

Fuer eine realistischere Regulierungssimulation fehlen weiterhin:

- Aktivitaetskosten und regulatorische Befolgungskosten je VU und Sparte;
- abstimmbare Bewegungsrechnung, Modellbilanz und vereinfachter Kapitalpuffer;
- Rueckversicherung und Gegenparteirisiko;
- wichtiger Geschaeftsservice, operative Abhaengigkeit und Drittanbieter;
- Schadenprozess mit Kapazitaet, Rueckstand, Durchlaufzeit und Kontrollwirkung;
- versionierte regulatorische Intervention und expliziter Geltungsbereich;
- benannte Sparten statt dauerhafter anonymer Zweiervektoren;
- formatunabhaengiges ResultBundle fuer UI, CSV, JSON und XLSX.

Diese Zustaende werden nicht in die historischen `Insurer`- und
`Policyholder`-Felder hineingedeutet. Neue Dataclasses und Adapter schuetzen
die eingefrorene Legacy-Semantik.

## Kandidatenfilter

Das Evernote-Register `IMS Features Kandidaten-Register` ist die fachliche
Eingangsgrenze. Eine Erweiterung wird nur umgesetzt, wenn regulatorischer
Eingriff, Wirkungskanal, messbarer Zielwert, versionierte Parametrisierung und
deterministische Testbarkeit benannt sind. Reine Produktideen oder
Techniktrends erzeugen keine IMS-Funktion.

## Validierung

- vollstaendiges Windows-Release-Gate vor dem Freeze: 1.480 Tests bestanden;
- Frontend-Build: 1.578 Module transformiert;
- portables Anwenderpaket geprueft, keine Simulation gestartet;
- Inventar mit `build-module-inventory.py --check` reproduziert;
- Versionsvertrag prueft Python-Paket, API und Frontend gemeinsam.

Die Klassifikation im CSV ist eine Planungsentscheidung und kein
automatischer Refactoring-Auftrag.

## Naechster PR

PR104 erstellt den versionierten Strategiekatalog und seine Taxonomie. Das ist
fuer die Regulierungssimulation relevant, weil Baseline und Intervention nur
realistisch vergleichbar sind, wenn VU-/VN-Strategie, Akteurstyp,
Parameterfaehigkeit, historische Herkunft und Teststatus eindeutig benannt
sind. PR104 bleibt ohne UI-Bearbeitung, ohne Strategiewechsel und ohne neue
Fachregel.
