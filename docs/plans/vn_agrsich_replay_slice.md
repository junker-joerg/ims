# Plan: VN-Agrsich-Replay

## Ziel

Verbinde den expliziten VN-Periodenrunner mit dem bestehenden Agrsich-Export.
Damit koennen kontrollierte VN-Schaden-/Abrechnungsperioden ausgefuehrt und
anschliessend als Agrsich-Tabellen geschrieben werden.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`
- historische VN-Agrsich-Dateien wie `IMSVNR*.DAT` und `IMSVNSK1.DAT`

Der Slice bildet keinen historischen Scheduler ab. Er nutzt nur explizite
Periodenszenarien, fuehrt die bereits portierten VN-Kerne aus und exportiert
den daraus entstandenen Python-Zustand.

## Umsetzung

1. Eigenen Engine-Baustein fuer VN-Agrsich-Replay anlegen.
2. In-Memory- und Fixture-Einstiege fuer mehrere Periodenszenarien ergaenzen.
3. Periodenfolge anhand globaler Perioden validieren.
4. Nach VN-Regelanwendung Agrsich-Records sammeln und Exporttabellen schreiben.
5. Tests fuer mutierte Exportwerte, Fixture-Laden und Periodenvalidierung
   ergaenzen.

## Grenzen

- keine Legacy-Gleichheitsbehauptung
- keine automatische Zustandsfortschreibung zwischen Perioden
- keine historische Versichererwahl oder Praeferenzlogik
- keine versteckte RNG-Nutzung
