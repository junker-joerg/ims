# Plan: Read-only Adapter-Resultat fuer Run-Control

## Zweck

Dieser PR 36 entscheidet den naechsten groesseren Schritt nach dem lokalen
kontrollierten Ausfuehrungsadapter aus PR 35.

Gewaehlt wird nicht sofort eine Run-Control-Ausfuehrung und auch kein weiterer
fachlicher Regel-Slice, sondern zunaechst ein read-only Adapter-Resultat fuer
Run-Control. Die Workbench soll spaeter nur ein bereits lokal erzeugtes
Adapterergebnis einordnen koennen. Sie soll keinen Adapter starten.

## Entscheidung

Run-Control darf als naechstes nur lernen, ein vorhandenes Ergebnis des lokalen
Adapters zu lesen oder als erwartete Ergebnisform zu beschreiben.

Begruendung:

- Der lokale Adapter existiert inzwischen, aber sein Aufruf ist bewusst nur
  lokal und explizit freigegeben.
- Die Run-Control-Pfade kennen weiterhin nur Dry-Run, Queue-Vormerkung,
  Preflight, Aktionsplan und Kernblick-Bruecke.
- Ein sofortiger Startpfad aus Run-Control wuerde die bisherige Grenze
  `execution_enabled = false` zu frueh aufweichen.
- Ein weiterer fachlicher Slice bleibt sinnvoll, sollte aber nicht die offene
  Adapter-Ergebnisgrenze verdecken.

## Geplanter Folgeschnitt

PR 37 soll nur ein read-only Resultat-DTO oder einen Vertrag vorbereiten:

- Quelle: bereits lokal erzeugtes `controlled_execution_adapter`-JSON;
- erwartete Summary: `explicit_multi_period_execution_summary`;
- erlaubte Felder: Adaptermodus, Fixture-Art, Fixture-Pfad, Summary, Grenzen;
- verbotene Felder: Browser-Upload, freier Output-Pfad, Queue-Ausfuehrungsflag,
  Startbutton, Fachlogikdaten ausserhalb der Summary;
- Ergebnisstatus: sichtbar, aber nicht ausfuehrbar;
- kein HTTP-Schreibpfad und kein UI-Startbutton;
- kein Start von `ims.api.controlled_execution_adapter` aus Run-Control.

PR 37 ist umgesetzt:

- `python_port/ims/api/run_control_adapter_result_contract.py` beschreibt den
  read-only Vertrag und validiert bereits erzeugte Adapterresultate lokal;
- `tests/test_api_run_control_adapter_result_contract.py` prueft Vertrag,
  Validator, CLI und Schreibfreiheit;
- `docs/migration/run_control_adapter_result_contract.md` dokumentiert Ursprung,
  Mapping, Grenzen und offene Folgeschritte.

PR 38 kann danach optional eine rein lesende API-/UI-Anzeige fuer ein solches
vorab erzeugtes Ergebnis planen. Erst danach darf separat entschieden werden,
ob weitere fachliche Slices oder eine noch engere Ausfuehrungsfreigabe folgen.

## Grenzen

- keine Simulation;
- kein Scheduler-Start;
- kein Runner-Start aus Run-Control;
- kein Queue-Worker;
- kein API-/UI-Startpfad;
- kein Browser-Upload;
- kein freier Output-Pfad;
- keine neue Fachregel;
- keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung.

## Validierung dieses Plan-PRs

Dieser Plan- und Vertragsschnitt wird ueber Dokumentations- und Vertragstests
validiert. Er startet keinen Adapter und keine Simulation. Er fixiert die
Entscheidung, dass Run-Control hoechstens ein read-only Adapter-Resultat
einordnet.
