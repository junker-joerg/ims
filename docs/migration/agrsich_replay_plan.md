# Deterministischer Agrsich-Periodenplan

## Ziel

Dieser Schritt reduziert die Abhaengigkeit von vollstaendig ausgeschriebenen Replay-Snapshots.
Kleine Periodenplaene beschreiben jeweils einen Startzustand und explizite periodische Updates.
Daraus werden deterministisch Replay-Snapshots erzeugt, die anschliessend unveraendert durch
den bestehenden Replay-Runner laufen.

## Einordnung

Der Periodenplan ist ein Zwischenschritt zwischen statischem Snapshot-Replay und spaeterer
Regellogik. Er nutzt weiterhin:

- den vorhandenen Scenario-Loader
- den vorhandenen Agrsich-Record-Pfad
- den vorhandenen Export-Writer
- den vorhandenen Legacy-Fenstervergleich

Es wird keine neue Versicherungslogik eingefuehrt. Die Updates sind explizit und dienen nur
dazu, die Snapshot-Erzeugung reproduzierbar aus einem Startzustand zu machen.

Aktuell ist dieser Pfad fuer zwei kleine Legacy-Fenster abgesichert:

- `VU14L1.DAT`, Perioden 0001 bis 0004, Stufe-I-VU-Datei
- `VUSK1L4.DAT`, Perioden 0101 bis 0104, Stufe-IV-VU-Datei

## Grenzen

Dieser Schritt ist noch kein historischer Simulationslauf. Die Updates werden nicht aus
wirtschaftlichem Verhalten, Scheduling oder portierten VU-Regeln berechnet. Er behauptet daher
keine historische Vollgleichheit.

## Anschluss

Der naechste grosse Schritt sollte einzelne periodische Updates aus portierter Regel- und
Scheduling-Logik ableiten und die entstehenden Zustandsfenster weiter gegen echte Legacy-Dateien
validieren.
