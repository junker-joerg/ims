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
