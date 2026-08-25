# Plan: kontrollierter Vdefmd6-Schockpfad fuer PR 81

## Ziel

PR 81 erweitert den kontrollierten modernen `Vdefmd6`-Zustand aus PR 80 um
die Perioden 50-100. Ab Periode 50 werden die belegten Schockparameter der
VU- und VN-Regeln verwendet und die 50 spaeten VN `151-200` aktiviert. Der
VU14-Export entsteht vollstaendig im Speicher, bevor die historische Reihe
gelesen wird.

## Quellen und konservative Einordnung

- `IMS.E:4566-4687`, `Vdefmd6`: `Bavauin(50,0,0.8,0.02,1)`, VU-/VN-Gruppen
  und Parameter vor/nach dem Aenderungsschock;
- `IMS.E:4102-4130`, `Bavauin`: `As[j] = 1` fuer `j >= 50` und
  `Ar[j] = 1` fuer alle Laeufe bei `l = 0`;
- `IMS.E`, `Vrvu01` bis `Vrvu09`: Schockparameter werden bei gesetztem
  Aenderungsschock verwendet;
- `IMS.E`, `Vrvn01` bis `Vrvn06`: VN-Regeln laufen bei
  `gperiod >= Ap * Al[rl]` und verwenden dann die Schockparameter;
- `Vnauini(..., ap=50, ...)` fuer VN `151-200`.

Der beschreibende Bildschirmtext nennt teilweise `t > 50` sowie andere
Teilbereiche als die Initialisierungsschleifen. PR 81 folgt dem ausfuehrbaren
Code: Schock und Aktivierung beginnen in Periode 50; die spaeten Gruppen sind
`151-190` mit Praeferenz und `191-200` mit Zufall II.

## Kontrollierter Vertrag

Die moderne Reihenfolge lautet ab Periode 50:

1. VN mit `activation_period <= period` aktivieren;
2. BAV-Vorperiodeninformationen erfassen;
3. VU-Regeln nach aufsteigender VU-ID mit `change_shock = true` anwenden;
4. VN-Regeln, Schaden und Settlement nach aufsteigender VN-ID mit
   `change_shock = true` anwenden;
5. VU14 im Speicher aggregieren.

Der bereits erzeugte Zustand der Perioden 1-49 wird mit demselben expliziten
`random.Random` und derselben modernen Reihenfolge fortgesetzt. Legacy-Zeilen
sind kein Erzeugungsinput.

## Risiken und Grenzen

- Die historische Same-Slot-Reihenfolge bleibt unbekannt.
- Der historische Seed und die genaue C-interne RNG-Reihenfolge bleiben offen.
- Der vorhandene moderne `market_damage_indicator` bleibt fuer diesen Schnitt
  unveraendert; seine gesonderte BAV-Ableitung waere ein eigener Fachschnitt.
- Keine Datei wird geschrieben, kein Scheduler und keine allgemeine
  Simulation werden gestartet.
- Der Vergleich klassifiziert Abweichungen und begruendet keine historische
  Vollgleichheit oder fachliche Freigabe.

## Restplanung

Nach PR 81 bleiben mindestens fuenf reviewbare Schritte bis PR 86:

1. PR 82: VU-Population auf SK1/all und VU-Klassen verbreitern;
2. PR 83 und PR 84: VN-Regelzustand in zwei kleinen Gruppen schliessen;
3. PR 85: VN-Klassen- und SK1/all-Exporte vergleichen;
4. PR 86: alle 15 Kernexporte gemeinsam vergleichen und die fachliche
   Freigabe menschlich neu bewerten.
