# PR169 und Folgepfad: Krankensparte bis zur bedienbaren Simulation

Stand: 2026-09-17

## Entscheidung

Kranken muss, wie die anderen Zielsparten, ueber die volle gewaehlte
Simulationsdauer bis 100 IMS-Modellperioden bedienbar sein. Ein isolierter
Bilanzfall erfuellt dieses Ziel **nicht**. Die vier zusaetzlichen, kleinen
PRs `PR169a` bis `PR169d` liegen fachlich zwischen PR169 und dem bereits
nummerierten PR170. Die Buchstaben vermeiden eine Umnummerierung der
anderen geplanten PRs; sie zaehlen bei Meilensteinen jeweils als ein PR.

| Schritt | Lieferung | Abnahme |
| --- | --- | --- |
| PR169 | Geschlossener Krankenbestand, explizite Beitraege und Leistungen, ein bis zwei deterministische Perioden als reine Python-Bilanzrechnung | Vertrag v1 unveraendert abrufbar; v2 kennzeichnet die getrennte Rechnung; Bilanz, Bestand und Carryover stimmen; ungueltige zweite Periode liefert atomar keine Zeile |
| PR169a | Versionierter Vertrag und Validierung fuer Neugeschaeft/Abgang, Beitragsanpassung und exogene Leistungsannahmen je Periode | Quellen, Zeitfenster, Akteur und Szenariovariante sind eindeutig; Leistungsanfall ist kein frei abschaltbarer VU-Hebel |
| PR169b | Kontrollierte fluechtige Kranken-Periodenkette fuer 1, 2, 5, 10, 25, 50 und 100 Perioden | deterministische Wiederholung, exakte Prefixe, Bestands-/Bilanzinvarianten, Laufzeit-/Speicherbudget und Abbruch ohne Teilresultat |
| PR169c | Ergebnis-API, explizite Freigabe, Idempotenz, unveraenderliche Ablage und CSV/JSON/XLSX | Ergebnis/Digest/Herkunft stimmen nach erneutem Abruf und in allen Exporten; fehlgeschlagene Laeufe bleiben ohne Teilablage |
| PR169d | Gefuehrte Kranken-Workbench mit einfacher Szenarioeingabe, Baseline/Variante und Zeitreihen bis 100 Perioden | echter Browserstart, Verlauf und Download; breite/schmale Ansicht, Fehlerpfade und Handbuchbilder sind abgenommen |
| PR170 | Vier-Sparten-Konsolidierung | Kranken, Leben, Kfz und Sach-Haftpflicht sind explizit allokiert und je Versicherer zur Gesamtbilanz abgestimmt |

Damit ist eine **bedienbare 100-Perioden-Kranken-Simulation nach PR169d**
geplant, nicht bereits nach PR169 oder erst irgendwann nach PR190. Der
gewaehlte Horizont darf kuerzer sein; der exakt gleiche Anfang eines
laengeren Laufs muss stabil bleiben. Ein frei skalierbares Vollmodell der
privaten Krankenversicherung, gesetzliche Alterungsrueckstellungen,
Solvency-II- oder historische Gleichheitsaussagen sind kein Teil dieses
Meilensteins.

## PR169: fachlicher Schnitt

`IMSDATA.C` hat nur zwei historische Schadenpositionen; das Kuerzel
`KV` beweist keine moderne Krankenversicherung. `IMS.E` aggregiert dort
Praemie, Schadenreserve und Schadensumme. PR169 rechnet daher
**ausschliesslich** den neuen IMS-2.x-`health`-Vertrag aus expliziten
Szenariowerten. `ims.accounting.non_life_model_balance` ist ein
strukturelles Vorbild fuer exakte Dezimalwerte und atomare Bilanzpruefung,
aber keine Quelle fuer Krankenwerte oder -regeln.

Ein Vertragspool je VU bleibt geschlossen. `benefits_incurred` belastet
den Periodengewinn und erhoeht die offene Leistungsverpflichtung;
`benefits_paid` mindert diese und die Kasse. Beitraege sind periodengleich
vereinnahmt und verdient; Anlageergebnis und Aufwand sind explizit,
Kapitalbewegungen separat. Anfangs- und Schlussbilanz sowie
Nichtnegativgrenzen sind Pflicht. Der Schlusszustand von Periode 1 ist
der Anfang von Periode 2. Eingang und Ergebnis sind versioniert; v1 des
PR168-Vertrags bleibt bytegleich unter eigenem Lesepfad erhalten.

PR169 hat weder Web-Eingabe, Persistenz, Runner noch eine historische
Vollgleichheitsbehauptung. Seine feste Zwei-Perioden-Basis dient den
nachfolgenden Prefix- und Bedienabnahmen.

## Risiken und offene Entscheidungen

- PR169a muss Neugeschaeft und Austritte **vor** der 100er-Kette
  entscheiden; ohne Bestandsbewegung waere die Seminarwirkung zu schmal.
- Preisentscheidungen, Leistungsannahmen und VN-Wechsel sind verschiedene
  Quellen. Eine strategische Wirkung auf Leistungen braucht spaeter eine
  begruendete, getrennte Kausalregel statt einer stillen Kuerzung.
- Keine historische `Sp[2]`-/`Rk[2]`-Zuordnung zu `health`. Die vier
  Modellsegmente werden vor PR170 nur als getrennte Rechnungen gefuehrt.
- Ressourcenbudgets, Speicherung und UI-Freigabe sind **nicht** aus der
  Existenz eines Python-Rechenkerns abzuleiten; jede Grenze bekommt ihre
  eigene Abnahme.
