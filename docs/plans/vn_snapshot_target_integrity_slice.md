# Plan: VN-Snapshot-Zielintegritaet

## Ziel

Haerte den expliziten VN-Periodenpfad gegen doppelte Zieladressierung eines
Versicherungsnehmers innerhalb derselben Periode. Ein VN darf entweder ueber
`vn_damage_settlement_snapshots` oder ueber `vn_settlement_snapshots`
verarbeitet werden, aber nicht ueber beide Pfade zugleich.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`
- periodische VN-Aktionen im historischen PlanVN-Umfeld

Die historischen Aktionen schreiben den VN-Zustand je Periode einmal fort. Der
Python-Slice sichert diese Integritaetsgrenze fuer explizite Snapshot-Eingaben
ab.

## Umsetzung

1. Cross-Set-Validierung im Szenario-Loader ergaenzen.
2. Loader-Test fuer ueberlappende VN-Ziele zwischen Schaden-Abrechnungs- und
   direkten Settlement-Snapshots ergaenzen.
3. Bestehende Runner-Validierung als zweite Schutzlinie beibehalten.
4. Migrationsdokumentation fuer die Snapshot-Zielintegritaet aktualisieren.

## Grenzen

- keine neue historische Wahl- oder Praeferenzlogik
- keine automatische Zustandsfortschreibung zwischen Perioden
- keine Vollsimulation und keine Behauptung historischer Vollgleichheit
