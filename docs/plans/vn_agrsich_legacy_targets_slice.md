# Plan: VN-Agrsich-Legacy-Ziele

## Ziel

Erweitere den VN-Agrsich-Replay-Runner um optionale Legacy-Ziele. Dadurch kann
ein expliziter VN-Replay-Lauf seine geschriebenen Exporttabellen direkt gegen
angegebene historische oder testweise bereitgestellte Agrsich-Dateien
vergleichen.

## Ursprung im Altcode

- historische VN-Agrsich-Dateien wie `IMSVNR*.DAT` und `IMSVNSK1.DAT`
- `IMS.E`, `act Vrvn01` bis `Vrvn03` als Ursprung der VN-Zustandsfortschreibung

## Umsetzung

1. Legacy-Zieltyp fuer VN-Agrsich-Replay einfuehren.
2. Exporttabellen ueber mehrere Perioden nach Dateiname zusammenfassen.
3. Zieltabellen gegen bestehende Legacy-Vergleichsfunktionen pruefen.
4. Fixture-Feld `legacy_targets` laden und relative Pfade zum Fixture
   aufloesen.
5. Tests fuer erfolgreichen VN-Legacy-Vergleich, Fixture-Laden und fehlende
   Exportziele ergaenzen.

## Grenzen

- keine Aussage historischer Vollgleichheit ohne passend belegtes Fixture
- keine automatische Auswahl von Legacy-Dateien
- keine neue VN-Regellogik
