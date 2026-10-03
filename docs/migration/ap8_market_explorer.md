# AP8: vorhandene Marktlogik erklären, keine neue Finanzlogik

03.10.2026. [Paketplan](../plans/ims_ap8_implementation.md) und
[Darstellungsvertrag](../plans/ims_ap8_view_contract.md). M1 vorbereitet;
die nachstehenden Zielkomponenten sind noch nicht als implementiert behauptet.

| Ursprung | Vorhandener Python-Vertrag | AP8-Aufgabe / Grenze |
| --- | --- | --- |
| `IMSDATA.C` 312–335, `classBAV.Vuag*`/`Vnag*` und Informationsvektoren | AP5 VU-/Markt-/Familien-/Gruppenbuchungen und verfügbare Vorperiodeninformation | Tatsächliche aktive Mitglieder/Zeilen auswerten; keine statischen Gruppennamen als zeitabhängige Mitgliedschaft |
| `IMS.E` 3533–3591, `Vrvn06`, aktive Minimum-Prämienwahl | AP5 `customer_decisions`, Risiko beim aktuellen Träger; AP7 bearbeitete Wechsel | Tatsächlich wirksame Eigentümeränderungen zeigen, P1/Anträge nicht als Wechsel doppelt zählen |
| AP5 `ims.market.runner.aggregate` / `side_result` | Vier-Sparten-Finanzfelder, exakte VU-/Marktsummen, Mengen nur je Sparte | Reine Projektion und exakte Buchungsbrücke, benannte Nenner/Gewichte; keine neuen Buchungen |
| AP6 `ims.market.reference` | Kuratierte BaFin-Namen/Quellen und sichtbar angenommene Modellbilanzen | Unternehmensnamen nicht als reale Modellbeiträge/Strategien/Provider ausgeben |
| AP7 `shock_plan` / `shock_process` | Aktive Ereignisse, konkrete Graphen, gemeinsame Budgets, FIFO, wirksame Policen/Wechsel und Kosten | Uhrzeit/Verfügbarkeit/Effekt unterscheiden; gemeinsame Ressourcen nicht pro VU vervielfachen |
| Boardplan E08-01, angenommen über PR #292 | Separat angenommener Vergleich Fokus/Rivalen/Modellmarkt | Absolute Buchungswerte und relative Position mit eigenem AP8-Abnahmebeleg |

Ziel: reines Modul `python_port/ims/market/explorer.py`, frischer API-Anschluss
`/api/market/explore`, vorhandene Rechensperre und unveränderte Modell-Ergebnis-
Digests. React-Komponente und reine Filter-/Darstellungsfunktionen verwenden
dieselben Zeilen; SVG-Positionen dürfen gerundet sein, Werte/Tabellen bleiben
exakte Modellzahlen. JSON/Excel verwendet das vollständige Originalbündel.

Keine historische Terminal-UI portieren. Konzentration, Familienquoten und
neue Darstellungen sind ausdrücklich moderne Auswertungen; keine historische
Vollgleichheit, empirische Firmenkalibrierung oder neue Ursache behauptet.
