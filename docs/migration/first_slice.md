# Erster portierter Slice

## Ziel des Slices

Als erster sehr kleiner, überprüfbarer Slice wird **B) Initialisierung eines kleinen Runs mit deterministischem Seed** portiert.
Der Slice bereitet nur den technischen Start eines Runs vor und enthält noch keine IMS-Fachregeln.

## Altcode-Bezug und Mapping Alt -> Neu

Im Repository liegen derzeit keine historischen C-Dateien vor.
Der Slice stützt sich daher nur auf die bereits dokumentierte, vorläufige Zuordnung aus dem Migrationsinventar:

- vermutete Kontext-/Initialisierungslogik (`inventory_context.c`) → `python_port/ims/engine/context.py`
- vermutete RNG-/Seed-Logik (`inventory_rng.c`) → `python_port/ims/engine/context.py`

## Neue Python-Datei(en)

- `python_port/ims/engine/context.py`
- `tests/test_run_initialization.py`

## Bewusste Vereinfachungen

- Der Run startet immer bei `period = 0` und `logtime = 0`.
- Es wird nur ein Python-`random.Random` mit festem Seed erzeugt.
- Der RNG-Halter liegt zunächst technisch in `context.registries["rng"]`.
- Es werden keine fachlichen Entitäten, UI-Komponenten oder Regeln initialisiert.

## Teststrategie

- Referenztest mit festem Seed auf reproduzierbare Zufallswerte.
- Prüfung der initialen Kontextwerte (`period`, `logtime`, `max_periods`, `run_index`, `rng_seed`).

## Bekannte Grenzen

- Keine Aussage über vollständige Gleichwertigkeit zum Altcode möglich, da dieser noch nicht im Repository vorliegt.
- Keine Portierung von Run-Setup über Szenarien, Produkte, Bestände oder Scheduler-Verknüpfung.
- Keine Portierung fachlicher Initialisierungsreihenfolgen jenseits des Seeds und der Startwerte.
