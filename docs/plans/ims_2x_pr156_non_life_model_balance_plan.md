# PR156: Deterministische Nichtleben-Modellbilanz

Stand: 2026-09-16

## Ziel und historischer Bezug

Die in PR155 vereinbarten Bewegungen fuer Kfz und Sach-Haftpflicht werden
je Versicherer und Periode deterministisch gerechnet. `IMSDATA.C` fuehrt
fuer die historischen Sparten 1/2 die Vektoren `Pr`, `Wa`, `Rs`, `Vn`,
`Sa` und `Sh`. `IMS.E` und die portierte VN-Abrechnung schreiben `Rs`
mit Zins, Praemien und bezahlten Schaeden fort. Das ist **keine** fertige
Bilanz; die Altpositionen sind nicht auf moderne Sparten gemappt.

## Umsetzung

1. Ein versionierter Eingang benoetigt fuer einen VU (Vdefmd6-ID 1-25)
   und genau eine benannte Nichtleben-Sparte Anfangsbestaende sowie
   aufeinanderfolgende Fluesse ab Periode 1 bis hoechstens 100.
2. Quellbindung: ausschliesslich explizite Szenariowerte. Keine automatische
   Uebernahme von `Rs`, `Pr`, `Wa`, `Sh` oder Alt-Zweierpositionen. Ein
   spaeterer Adapter muesste diese Herkunft separat pruefen.
3. Betragformat: JSON-Dezimalstrings mit hoechstens 12 Vorkomma- und vier
   Nachkommastellen, keine Exponenten, keine Float-Umrechnung und keine
   implizite Rundung. Ausgabe kanonisch mit vier Nachkommastellen.
4. Anfangsbilanz, Vorzeichen, Periodenfolge und beide Schlussbestands-
   Invarianten werden geprueft. Schlussbestaende werden als naechste
   Anfangsbestaende uebertragen. Jeder Fehler verwirft das ganze Ergebnis.
5. Die PR155-Vertragsversion v1 bleibt separat abrufbar. Der aktuelle
   read-only Vertrag v2 benennt die nun festgelegte Betragdarstellung und
   die reine Python-Bibliotheksfunktion, ohne Berechnungs-API.
6. Reiner, speicherfreier Rechenkern in `ims.accounting`; Tests fuer
   beide Sparten, Mehrperioden-Carryover, Wiederholung, Fehlerpfade und
   strikte Quellgrenze. PR157 bindet Darstellung und XLSX an.

## Grenzen und Risiken

Nur eine Cash-Aktivposition und eine Schadenverbindlichkeit; Kapital wird
je Sparte explizit zugeteilt. Kein Bilanzanschluss an historische Runner,
keine Solvency-II-Rechnung, keine gesetzliche Bilanz und keine historische
Vollgleichheit. Die Modellannahme ueber verdiente/eingenommene Praemien
bleibt aus PR155 erhalten. Das Aufwandsfeld uebernimmt Werbung nicht
automatisch. Numerische Begrenzung soll zu grosse oder ungeeignete
Payloads ablehnen, nicht wirtschaftliche Werte still korrigieren.
