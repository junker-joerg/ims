# PR155: Bewegungsrechnung und einfache Versicherer-Modellbilanz

Stand: 2026-09-16

## Ziel

Ein kleiner, versionierter und rein lesender Vertrag legt fest, welche
Bestands-, Erfolgs-, Zahlungs- und Kapitalbewegungen eine spaetere
Modellbilanz je VU, benannter Nichtleben-Sparte und Periode benoetigt.
PR155 berechnet noch keine Bilanz.

## Historische Grundlage

- `IMSDATA.C`: VU `Sp[1/2]` mit Praemie `Pr`, Werbung `Wa`, Reserve `Rs`,
  Versichertenzahl `Vn`, Schadenanzahl `Sa` und Schadensumme `Sh`.
- `IMS.E`, VU-Regeln: `Rs` wird mit Zinssatz fortgeschrieben.
- `IMS.E`, VN-Abrechnung: `Rs` steigt um gezahlte Praemien und sinkt um
  bezahlte Schaeden. Werbung wird dort nicht als Aufwand abgezogen.
- Python: `Insurer.reserves_current`, `claims_sum_current` und
  `Policyholder.paid_premium_current` sind Diagnose-/Quellkandidaten,
  aber noch keine vollstaendige Rechnungslegung.

Die Altpositionen sind nicht als Kfz/Sach-Haftpflicht belegt (PR152/153).
`Rs` ist weder stillschweigend Cash noch Schadenverbindlichkeit oder
Eigenkapital.

## Vertrag

1. Neue Modellfelder fuer Anfangs-Cash, Anfangs-Schadenverbindlichkeit,
   Anfangs-Eigenkapital; Praemie, Zins, angefallene/bezahlte Schaeden,
   Aufwand, Kapitalzufuehrung/-ausschuettung; Ergebnis und Schlussbestaende.
2. Gleichzeitige Praemienvereinnahmung/-verdienung, Aufwandserfassung/-zahlung
   und Zinseinnahme/-zahlung als explizite Vereinfachung. Forderungen,
   Beitragsabgrenzung und Anlagenbestand bleiben draussen.
3. Gleichungen fuer Cash, Schadenverbindlichkeit, Ergebnis und Eigenkapital;
   Anfangs-/Schlussbilanz und Perioden-Carryover als pruefbare Invarianten.
4. Nur `motor` und `property_liability` als geplante Sektoren; keine
   automatische Ableitung aus historischen Zweiervektoren.
5. Read-only API, Integritaetstests und Migrationsdokumentation. Kein
   Bilanz-Input, kein Validator, kein Runner und keine Speicherung.

## Offene Umsetzung

PR156 implementiert erst nach expliziter Wahl der Betragsdarstellung und
Quellbindung eine deterministische Modellbilanz. Die fehlenden Aufwands-,
Verbindlichkeits- und Kapitaldaten muessen eigene Szenarioeingaben sein;
historische Felder duerfen nicht heimlich als Ersatz dienen.
