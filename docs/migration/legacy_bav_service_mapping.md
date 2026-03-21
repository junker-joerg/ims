# Historischer BAV-Servicekern: Mapping-Stand

Dieses Dokument hält den derzeit belastbaren Mapping-Stand zum historischen BAV-Servicekern fest.
Der aktuelle Checkout enthält jedoch **nicht** die im Auftrag genannten Primärquellen `IMS.E`, `IMSDATA.C` und `DISS.pdf`, sondern nur `legacy_c/.gitkeep`.
Damit ist diese Datei bewusst eine **quellenkritische Vorarbeit** für die nächste Portierungsstufe und keine abgeschlossene Fachdeutung.

## Quellenlage im aktuellen Repo-Stand

### Direkt im Repo beobachtbar
- `legacy_c/.gitkeep` ist vorhanden.
- Die genannten historischen Primärdateien `IMS.E`, `IMSDATA.C` und `DISS.pdf` sind im aktuellen Checkout nicht vorhanden.
- Die Unterprogrammnamen `Myinitbv`, `Newinibv`, `Frmdinf` und `Agrsich` sind im aktuellen Checkout ebenfalls nicht textuell nachweisbar.

### Aus Auftrag / bestehender Migrationsabsicht fachlich nahegelegt
- Es gibt einen historischen BAV-Servicekern mit vier benannten Unterprogrammen.
- Diese vier Unterprogramme sind für die nächste echte Fachportierung relevant.
- Die BAV-Struktur und ihr Servicekern sollen vor einer Portierung zuerst fachlich zerlegt werden.

### Für die Portierung noch offen
- exakte Signaturen der Unterprogramme
- konkrete Reihenfolge im historischen Ablauf
- genaue Datenfeldnutzung innerhalb von `classBAV`
- direkte Kopplungen zu Versicherern, Versicherungsnehmern und Vorperiodendaten

## Unterprogramme des historischen BAV-Servicekerns

## `Myinitbv`

### Direkt beobachtbar
- Im aktuellen Repo-Stand nicht direkt im Altcode verifizierbar.

### Aus Namen / Auftrag fachlich vorsichtig ableitbar
- wahrscheinlich ein Initialisierungs- oder Reinitialisierungsschritt des BAV-Kerns
- vermutlich zeitlich früh im Lauf oder am Beginn eines technischen/fachlichen Abschnitts verortet

### Zentrale Ein-/Ausgaben
- **offen**: vermutlich BAV-Zustand als Zielstruktur
- **offen**: mögliche Vorperiodenwerte, Laufparameter oder Schock-/Statusinformationen

### Abhängigkeiten
- **offen**: Vorperiodenabhängigkeit nicht belastbar belegbar
- **offen**: Beziehungen zu anderen Subjektklassen noch nicht nachweisbar

## `Newinibv`

### Direkt beobachtbar
- Im aktuellen Repo-Stand nicht direkt im Altcode verifizierbar.

### Aus Namen / Auftrag fachlich vorsichtig ableitbar
- wahrscheinlich eine alternative oder neuere Initialisierungsroutine für BAV-nahe Zustände
- denkbar als Ergänzung oder Nachfolger von `Myinitbv`

### Zentrale Ein-/Ausgaben
- **offen**: BAV-Datencontainer als Hauptziel naheliegend, aber nicht aus Quellcode belegbar
- **offen**: mögliche Eingänge aus Laufsteuerung, Vorperioden oder globalen Tabellen

### Abhängigkeiten
- **offen**: Verhältnis zu `Myinitbv` ungeklärt
- **offen**: Interaktion mit anderen Subjektklassen ungeklärt

## `Frmdinf`

### Direkt beobachtbar
- Im aktuellen Repo-Stand nicht direkt im Altcode verifizierbar.

### Aus Namen / Auftrag fachlich vorsichtig ableitbar
- naheliegend ist ein Schritt zur Bereitstellung von Fremdinformationen
- laut Arbeitsauftrag ist dieser Schritt für einen frühen substantiellen Fachslice besonders geeignet
- vermutlich erzeugt oder verteilt die Routine BAV-seitige Information an andere Klassen

### Zeitliche Einordnung im Ablauf
- wahrscheinlich nach grundlegender Initialisierung des BAV-Zustands
- wahrscheinlich vor späteren Aggregat-/Sicherungs- oder Abschlussroutinen

### Zentrale Ein-/Ausgaben
- **offen**: Eingänge wahrscheinlich aus BAV-Zustand und Vorperioden-/Laufdaten
- **offen**: Ausgänge wahrscheinlich in Richtung Versicherer und/oder Versicherungsnehmer

### Abhängigkeiten
- mögliche Abhängigkeit von Vorperiodenwerten ist fachlich plausibel, aber nicht direkt belegt
- mögliche Abhängigkeit zu Versicherern und Versicherungsnehmern ist durch den Namen "Fremdinformation" nahegelegt, aber nicht direkt belegt

## `Agrsich`

### Direkt beobachtbar
- Im aktuellen Repo-Stand nicht direkt im Altcode verifizierbar.

### Aus Namen / Auftrag fachlich vorsichtig ableitbar
- wahrscheinlich eine Routine zur Aggregat-Sicherung, Aggregat-Fortschreibung oder Aggregat-Ablage
- eher später im Ablauf zu erwarten als Initialisierung und Fremdinformationsaufbau

### Zeitliche Einordnung im Ablauf
- plausibel im späteren Teil eines Perioden- oder Auswertungsschritts
- möglicherweise nach Berechnung/Verteilung fachlicher Größen

### Zentrale Ein-/Ausgaben
- **offen**: Aggregatnahe Felder in `classBAV` als Kernzielstruktur wahrscheinlich
- **offen**: mögliche Übergabe an Auswertungs-, Speicher- oder Folgeschritte nicht belegbar

### Abhängigkeiten
- denkbare Abhängigkeit von bereits berechneten Zuständen anderer Klassen
- Vorperiodenbezug und genaue Persistenzrolle bleiben offen

## Vorläufiges Portierungsfazit

Der aktuelle Repo-Stand reicht **nicht** aus, um die vier Unterprogramme belastbar aus Primärquellen zu beschreiben.
Für die nächste echte Fachportierung sollten deshalb zunächst die historischen Dateien `IMS.E`, `IMSDATA.C` und `DISS.pdf` in den Arbeitsstand aufgenommen oder anderweitig bereitgestellt werden.
Bis dahin ist nur ein vorsichtiger, quellenkritischer Planungsstand möglich.
