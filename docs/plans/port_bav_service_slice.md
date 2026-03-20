# Plan: erster substanzieller BAV-Portierschnitt

Dieses Dokument skizziert einen kleinen, belastbaren Plan für die nächste echte Fachportierung des historischen BAV-Servicekerns.
Der Plan bleibt bewusst konservativ und setzt voraus, dass die historischen Quellen `IMS.E`, `IMSDATA.C` und `DISS.pdf` bereitgestellt werden.

## Ziel des nächsten Portierschnitts

Ein erster substanzieller BAV-Slice soll vorbereitet werden, ohne bereits eine Vollportierung oder historische Gleichwertigkeit zu behaupten.
Bevorzugte Reihenfolge:

1. BAV-Datencontainer
2. Initialisierung
3. kleiner `Frmdinf`-Teilschnitt
4. später `Agrsich`

## Empfohlene Reihenfolge

## 1. BAV-Datencontainer

### Inhalt
- historische `classBAV` aus `IMSDATA.C` vollständig sichten
- Felder in fachliche Gruppen zerlegen
- konservative Python-Datencontainer ohne Fachmethoden definieren

### Abhängigkeiten
- `IMSDATA.C`
- belastbare Zuordnung aus dem BAV-Servicekern

### Teststrategie
- reine Strukturtests
- Feldpräsenz und Gruppenmapping gegen dokumentierte Altfelder
- keine Verhaltensbehauptungen

### Risiken
- hohe Feldzahl oder schwer lesbare Altbezeichner
- unklare Bedeutung einzelner Status- oder Aggregatfelder

## 2. Initialisierung

### Inhalt
- `Myinitbv` und `Newinibv` quellenbasiert sichten
- kleinsten belastbaren Initialisierungsschnitt in Python übertragen
- nur direkt beobachtbare Initialwerte übernehmen

### Abhängigkeiten
- BAV-Datencontainer
- `IMS.E`
- ergänzende Erläuterungen aus `DISS.pdf`, falls vorhanden

### Teststrategie
- Golden-Master-nahe Initialisierungstests auf kleinen historischen Beispielen
- Vergleich einzelner Kernfelder vor/nach Initialisierung

### Risiken
- Verhältnis zwischen `Myinitbv` und `Newinibv` könnte historisch komplexer sein als die Namen nahelegen
- mögliche versteckte Abhängigkeiten zu globalen Tabellen oder Vorperiodenwerten

## 3. Kleiner `Frmdinf`-Teilschnitt

### Inhalt
- kleinsten direkt beobachtbaren Teil von `Frmdinf` auswählen
- bevorzugt einen Abschnitt mit klaren Eingängen/Ausgängen und begrenzter Abhängigkeitstiefe portieren
- Versicherer- und Versicherungsnehmer-Bezug getrennt halten

### Abhängigkeiten
- BAV-Datencontainer
- initialisierte BAV-Basiszustände
- historische Routinen/Kommentare zu Fremdinformation

### Teststrategie
- tabellengetriebene Tests für wenige kontrollierte Eingangskonstellationen
- getrennte Assertions für Update an Versicherer- bzw. Versicherungsnehmer-nahen Zielcontainern

### Risiken
- starke implizite Kopplung an andere Subjektklassen
- Altcode könnte Fremdinformation und Aggregatfortschreibung enger vermischen als gewünscht

## 4. Später `Agrsich`

### Inhalt
- erst nach stabiler Initialisierung und kleinem `Frmdinf`-Slice angehen
- Aggregat-Sicherung oder Aggregat-Fortschreibung nur quellenbasiert portieren

### Abhängigkeiten
- belastbarer Aggregatbereich im BAV-Datencontainer
- Verständnis, welche Vorstufen `Agrsich` historisch voraussetzt

### Teststrategie
- Regressionstests auf klar isolierten Aggregatfeldern
- keine breiten End-to-End-Behauptungen ohne historische Referenzläufe

### Risiken
- `Agrsich` könnte stark von nicht portierten Vorarbeiten abhängen
- Gefahr einer vorschnellen Aggregat-Neudeutung ohne Altcodebeleg

## Bewusst noch nicht portierte Teile

- keine historische Vollsimulation
- keine allgemeine Event-Semantik des Altmodells
- keine vollständige Portierung aller BAV-Unterprogramme in einem Schritt
- keine UI
- keine komplexe Marktlogik außerhalb des zuerst gewählten BAV-Slices

## Sofortige Voraussetzung vor Start der Fachportierung

Der nächste echte Fachslice sollte **erst** beginnen, wenn mindestens eine der folgenden Grundlagen vorliegt:

- `IMS.E`, `IMSDATA.C` und `DISS.pdf` im Repo verfügbar, oder
- dieselben Quellen in anderer nachvollziehbarer Form für die Analyse bereitgestellt

Ohne diese Primärquellen bleibt der aktuelle Stand eine Planungs- und Mapping-Vorstufe.
