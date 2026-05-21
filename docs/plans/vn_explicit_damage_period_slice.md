# Plan: Expliziter VN-Schadenperiodenschritt

## Ziel

Erweitere den VN-Periodenpfad so, dass explizit vorliegende
Schadenerzeugungsparameter, Normalziehungen und Versicherungsentscheidungen in
einem Schritt verarbeitet werden koennen. Der Schritt verbindet die portierten
Kerne aus Schadenerzeugung und Abrechnung, ohne historische VN-Wahl- oder
RNG-Automatik zu portieren.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`

In den historischen Regeln liegen Schadenziehung und Abrechnung innerhalb
derselben VN-Aktion. Der Python-Slice bildet diesen Zusammenhang als
expliziten Snapshot-Pfad nach.

## Umsetzung

1. Snapshot fuer Schadenparameter, Schwellen, Draws,
   Versicherungsentscheidungen und Vorvermoegen ergaenzen.
2. Anwendung des Snapshots ueber den bestehenden VN-Schadenerzeugungskern und
   anschliessend den bestehenden Settlement-Kern.
3. VN-Periodenrunner fuer explizite Schaden-Abrechnungs-Snapshots erweitern.
4. Szenario-Loader-Feld und Referenzvalidierung ergaenzen.
5. `previous_wealth_sector` im Adapterpfad auf zwei Sparten normalisieren.

## Grenzen

- keine versteckte RNG-Nutzung
- keine Portierung der historischen Versichererwahl
- keine Praeferenz- oder Pflichtversicherungslogik
- keine Vollsimulation oder Behauptung historischer Vollgleichheit
