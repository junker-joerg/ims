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
