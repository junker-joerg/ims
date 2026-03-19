# Zielarchitektur des Python-Ports

## Ziel

Die Python-Zielarchitektur soll:
- fachlich eng am Altmodell bleiben,
- technische Altlasten nicht übernehmen,
- kleine, testbare Module fördern,
- Reproduzierbarkeit und spätere Auswertung erleichtern.

## Vorläufige Struktur

```text
python_port/
  ims/
    __init__.py
    model/
      __init__.py
      entities.py
      rules.py
    engine/
      __init__.py
      context.py
      scheduler.py
      rng.py
      simulation.py
    io/
      __init__.py
      scenario_loader.py
      results_writer.py
    analysis/
      __init__.py
      aggregates.py
      reports.py
tests/
```
# Vorläufige Python-Zielstruktur

Die Python-Portierung soll schrittweise und mit kleinen PRs aufgebaut werden.
Dieses Zielbild ist bewusst knapp und noch keine endgültige Architekturentscheidung.

```text
docs/
  migration/
  plans/
python_port/
tests/
```

## Geplante Einordnung

- `python_port/`: Zielbereich für den späteren Python-Port
- `tests/`: Referenz- und Regressionstests für portierte Ausschnitte
- `docs/migration/`: Migrationsdokumentation und Bestandsinventar
- `docs/plans/`: Arbeitspläne für die Zerlegung in kleine PRs
