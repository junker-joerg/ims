# Zielbild der Python-Struktur

Dieses Dokument beschreibt ein erstes Zielbild für die spätere Python-Portierung von IMS.
Es dient ausschließlich der Orientierung für künftige, kleine Migrations-PRs.

## Geplante Zielstruktur

```text
python_port/
  ims/
    model/
    engine/
    io/
    analysis/
tests/
```

## Bedeutung der Zielbereiche

- `python_port/ims/model/`: Fachliche Modelle, Entitäten und wertartige Strukturen.
- `python_port/ims/engine/`: Ablaufsteuerung, Scheduler-nahe Koordination und orchestrierende Komponenten.
- `python_port/ims/io/`: Ein- und Ausgabe, Dateizugriffe und Adapter zu externen Schnittstellen.
- `python_port/ims/analysis/`: Auswertungen, Aggregationen und analytische Hilfsbausteine.
- `tests/`: Begleitende Tests für schrittweise, semantisch konservative Migrationen.

## Leitplanken

- Dieses Zielbild ist **vorläufig**.
- Aus der Struktur folgt **noch keine Portierung fachlicher Logik**.
- Abweichungen vom Zielbild sollen in späteren PRs begründet dokumentiert werden.
