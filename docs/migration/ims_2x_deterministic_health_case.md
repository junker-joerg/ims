# PR169: Deterministischer Kranken-Bilanzfall

Stand: 2026-09-17
Eingang: `ims.health-model-balance-input.v1`
Ergebnis: `ims.health-model-balance-result.v1`
Vertrag: `ims.health-sector-contract.v2`

## Ursprung und Abgrenzung

| Altcode | Python | Bedeutung |
| --- | --- | --- |
| `IMSDATA.C`: `MAXSPARTEN 2`, `classVU.Sp[1/2]`, `classVN.Rk[1/2]` | `ims.model.health_sector_contract` und `ims.accounting.health_model_balance` | Neue, getrennte IMS-2.x-Zielrechnung fuer `health`; keine historische Zuordnung von `KV`, `Sp[2]` oder `Rk[2]`. |
| `IMS.E`: Praemien-, Schaden- und Reserveaggregate der zwei alten Positionen | explizite Szenariowerte statt Alt-Runner | Weder Schadensummen noch historische Reservewerte werden still in Leistungen oder Alterungsrueckstellung umgedeutet. |
| PR156: `ims.accounting.non_life_model_balance` | gleiches Validierungsprinzip, separate Krankenfelder | Exakte Dezimalstrings, lokale Praezision und atomarer Fehlerpfad sind technische Muster, keine Gleichsetzung der Sparten. |

PR169 berechnet eine **einfache Modellbilanz**, kein privates
Krankenversicherungs-Vollmodell und keine historische Vollgleichheit.
`GET /api/model/health-sector-contract` beschreibt jetzt den v2-Stand;
der PR168-v1-Vertrag bleibt unter `/api/model/health-sector-contract/v1`
inhaltlich unveraendert. Es gibt keine POST-API fuer Krankenwerte.

## Eingabe und Periodenfolge

Der Python-Bibliotheksaufruf
`ims.accounting.health_model_balance.build_health_model_balance` erwartet
genau `health`, eine VU-ID 1-25, `source_kind = explicit_scenario`, die
Vertragsversionen und einen expliziten Anfangsbestand. `periods` umfasst
**genau eine oder zwei** lueckenlose, bei 1 beginnende Perioden. Alle
Betragsspalten sind Dezimalstrings mit hoechstens 12 Vorkomma- und vier
Nachkommastellen. Es findet keine implizite Rundung statt. Die Zahl aktiver
Vertraege ist eine nichtnegative ganze Zahl und bleibt in diesem
geschlossenen Fall konstant.

Anfangs gilt `Kasse = offene Leistungsverpflichtung + Eigenkapital`.
Eingezogene Beitraege sind zugleich verdient. Angefallene Leistungen
mindern das Periodenergebnis und erhoehen die offene Verpflichtung.
Bezahlte Leistungen mindern Verpflichtung und Kasse; sie sind **kein
zweiter Aufwand**. Zahlungen duerfen die vorhandene plus neu angefallene
Verpflichtung nicht uebersteigen. Ein alter offener Betrag kann auch bei
null aktiven Vertraegen bezahlt werden; neue Beitraege und neue Leistungen
sind dann null. Anlageergebnis und Aufwand werden periodengleich erfasst.
Kapitalzufuehrung/-ausschuettung beruehren das Ergebnis nicht.

Der Schlussbestand (aktive Vertraege, Kasse, Verpflichtung, Eigenkapital)
ist exakt der Anfangsbestand der Folgeperiode. Die Schlussbilanz muss
aufgehen; Kasse und Verpflichtung bleiben nichtnegativ. Jeder fehlerhafte
Eingang, auch ein Fehler **erst in Periode 2**, liefert eine Fehlerliste
und **null Ergebniszeilen**. Rechenfehler hinterlassen keine Datei und
keinen gespeicherten Teilstand. Die festen Beispiele stehen in
`tests/fixtures/health_model_balance_v1.json`.

## Verbleibende Produktarbeit

`PR169a` hat Neugeschaeft, Abgang, Beitrags-/Leistungsquellen
getrennt und atomar validiert; siehe `ims_2x_health_period_sources.md`.
`PR169b` fuehrt diese Werte nun als fluechtige Kette kontrolliert bis
100 IMS-Perioden; siehe `ims_2x_health_period_chain.md`. `PR169c` liefert geschuetzte Ablage
und CSV/JSON/XLSX, `PR169d` erst den bedienbaren Workbench-Pfad mit
Baseline/Variante. **PR169 selbst startet weder Runner noch Simulation**.
Danach konsolidiert PR170 die vier getrennten Segmente.

Alterungsrueckstellung, Tarife, Morbiditaet, Behandlungen,
aufsichtsrechtliche Bewertung und historische Gleichheit sind weiterhin
ausgeschlossen. Diese offenen Punkte duerfen bei einer spaeteren
Kranken-Simulation nicht als bereits implementierte Fachlogik erscheinen.
