# Historische BAV-Feldkartierung: vorbereitender Stand

Dieses Dokument zerlegt die historische `classBAV` für die nächste Portierungsstufe **vorläufig** in fachliche Gruppen.
Da `IMSDATA.C` im aktuellen Checkout nicht vorliegt, ist dies ausdrücklich **kein Feldinventar aus Primärquellen**, sondern eine konservative Mapping-Struktur für die spätere echte Analyse.

## Quellenlage und Grenze

### Direkt im Repo beobachtbar
- `classBAV` ist im aktuellen Checkout nicht aus historischem Code auslesbar.
- Ein echtes Feldinventar aus `IMSDATA.C` ist daher aktuell nicht möglich.

### Für die nächste Portierung vorbereitet
- Die spätere Analyse soll `classBAV` mindestens in vier Gruppen zerlegen:
  - Schock-/Laufsteuerung
  - Aggregatverwaltung
  - Fremdinformation für Versicherer
  - Fremdinformation für Versicherungsnehmer

## Fachliche Gruppen für die spätere Zerlegung von `classBAV`

## 1. Schock-/Laufsteuerung

### Zweck der Gruppe
Felder dieser Gruppe würden den technischen oder fachlichen Laufzustand des BAV-Kerns tragen,
etwa Initialisierungsstatus, Periodenbezug, Schockzustände oder laufbezogene Marker.

### Historische Altfelder
- **noch offen, da `IMSDATA.C` fehlt**

### Vorsichtige Python-Zielabbildung auf Datencontainer-Ebene
- separates Container-Segment innerhalb eines späteren `BAVState` oder `BAVCoreState`
- mögliche Unterstruktur wie `BAVRunControlData`
- zunächst nur einfache Datenfelder, keine Fachmethoden

## 2. Aggregatverwaltung

### Zweck der Gruppe
Felder dieser Gruppe würden aggregierte Größen des BAV-Servicekerns tragen,
die später für Speicherung, Sicherung, Auswertung oder Folgeentscheidungen benötigt werden.

### Historische Altfelder
- **noch offen, da `IMSDATA.C` fehlt**

### Vorsichtige Python-Zielabbildung auf Datencontainer-Ebene
- separates Aggregat-Segment, z. B. `BAVAggregateData`
- klare Trennung von laufender Berechnung und gespeicherten Aggregatständen
- keine Ableitung komplexer Historienlogik vor Sichtung der Primärquellen

## 3. Fremdinformation für Versicherer

### Zweck der Gruppe
Felder dieser Gruppe würden jene BAV-seitigen Informationen bündeln,
die in historischen Routinen mutmaßlich an Versicherer weitergegeben oder für diese bereitgestellt werden.

### Historische Altfelder
- **noch offen, da `IMSDATA.C` fehlt**

### Vorsichtige Python-Zielabbildung auf Datencontainer-Ebene
- eigener Teilcontainer wie `BAVForeignInfoInsurerData`
- spätere Portierung sollte Eingangs-/Ausgangsfelder getrennt dokumentieren
- noch keine Aussage über Vektor-/Array-Strukturen ohne Altcodebeleg

## 4. Fremdinformation für Versicherungsnehmer

### Zweck der Gruppe
Felder dieser Gruppe würden BAV-seitige Informationen bündeln,
die historisch wahrscheinlich für Versicherungsnehmer oder VN-nahe Verarbeitung vorgesehen waren.

### Historische Altfelder
- **noch offen, da `IMSDATA.C` fehlt**

### Vorsichtige Python-Zielabbildung auf Datencontainer-Ebene
- eigener Teilcontainer wie `BAVForeignInfoPolicyholderData`
- klare Trennung von Versicherer- und Versicherungsnehmer-bezogenen Fremdinformationen
- spätere Portierung sollte erst nach Quellensichtung entscheiden, ob gemeinsame Basisfelder sinnvoll sind

## Vorläufige Python-Zielstruktur auf Container-Ebene

Ohne Implementierung und ohne neue Fachlogik bietet sich für die spätere Portierung eine konservative Container-Zerlegung an:

- `BAVCoreState`
  - `run_control`: Schock-/Laufsteuerung
  - `aggregates`: Aggregatverwaltung
  - `foreign_info_insurer`: Fremdinformation für Versicherer
  - `foreign_info_policyholder`: Fremdinformation für Versicherungsnehmer

Diese Zielabbildung ist bewusst nur strukturell.
Welche historischen Felder tatsächlich wohin gehören, muss erst aus `IMSDATA.C` belastbar extrahiert werden.
