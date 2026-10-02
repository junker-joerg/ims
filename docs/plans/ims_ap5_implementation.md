# AP5: gemeinsamer Markt und Strategiefamilien

Begonnen am 02.10.2026 nach tatsächlich gemergtem AP4. Basis:
`9b0d45a22be4314eda8e9ab1db61c506a44160f7`,
[AP4 #293](https://github.com/junker-joerg/ims/pull/293).
Branch `codex/ims-market-strategy-groups`, ein zusammenhängender Draft-PR.
Der [archivierte Generatorauftrag](ims_ap5_work_order.md) wurde vor Änderungen
am Paketmanifest gegen diese origin/main-Basis im Modus authorized geprüft.
Der zunächst bestätigte Umsetzungsauftrag war kein angenommener neuer Fachvertrag.
Der konkrete Vorschlag in PR #294 wurde anschließend mit „Vertrag annehmen und
umsetzen“ angenommen; [Annahmebeleg](../reports/ims_ap5_contract_acceptance.md).

## Quellen und Umfang

Lieferbasis ist der angenommene AP4–AP9-Plan samt Manifest. Die angenommenen
Ergänzungen aus [Boardplanung #292](ims_board_strategy_2026_10.md) haben eigene
Herkunft: **E05-01** Maßnahmenkosten, Vorlauf, Wirkungsdauer;
**E05-02** zeitpunktbezogene Information sowie konsistente Kunden, Risiken
und Kapazitäten. Sie sind hier Teil der AP5-Lieferung und werden separat geprüft.
Der unbearbeitete Generatorauftrag aus dem älteren Marktmanifest führt sie
noch nicht auf; dieser konkrete Paketplan ergänzt ihren angenommenen Umfang.

Die Altquellen `IMS.E`, `ESS.C`, `IMSDATA.C` und vorhandene Python-Kerne wurden
vor der Vertragsarbeit gelesen. Die Tabelle im
[Marktvertrag](ims_ap5_market_contract.md) nennt Ursprung und Abweichung.
AP3 bleibt eigener unveränderter Eingangs-/Ergebnisvertrag. Neue Semantik wird
nicht in AP3-Schadeneingaben oder historische 25er-Validatoren hineingeschrieben.

## Meilensteine im selben PR

| Schritt | Inhalt / Nachweis | Aktueller Stand |
| --- | --- | --- |
| M1 Fachvertrag | Zwei/drei VUs, Risikoträger/Altreserve, Mengen/Gruppe/Familie, Maßnahmen und Information erklären; fachlich annehmen. | Handfallproben bestanden; vom Auftraggeber am 02.10.2026 angenommen. |
| M2 Gemeinsame Rechnung | Eigener Validator, Periodenphasen, Kohorten-/Risikoledger, alle VU-Bilanzen, gruppierte Summen, stabiler RNG, Prefixe. | Implementiert; Handfälle, Replay, Prefixe und 40/41×100-Produktläufe bestanden. |
| M3 Anschluss | API und erste Marktsicht mit Zeit-/Sparten-/Familien-/Vergleichsfilter, Erklärweg und Einzel-VU-Excel. | Angeschlossen; Browserprüfung läuft. |
| M4 Lieferung | Einsteigeranleitung, vollständige Regressionen, gemessene 40/41×100-Grenzen, neue Releasekennung, Installer und CI. | Anleitung und alpha.5-Metadaten vorhanden; Installer/Gesamtprüfungen folgen. AP5-Merge/Public-Release nicht beauftragt. |

Ein eigener moderner ID-Validator muss mindestens 41 Anbieter zulassen, ohne
das alte Vdefmd6-Limit aufzuheben. Das Ergebnisvolumen und Laufzeitbudget werden
am vollständigen Produktlauf gemessen. Der kleine Angebotskernversuch ist
hierfür Orientierung und ausdrücklich keine vollständige Markt-Abnahme.

## Abnahmematrix

| Herkunft | Abnahme / späterer Prüfweg |
| --- | --- |
| AP5 R05/R06 | Gemeinsam bilanzierter 40/41er-Modellmarkt; API und IMS-Summen gleich den VU-Zeilen. |
| AP5 R09/R11 | Vier getrennte Gruppenbegriffe; disjunkte Familien summieren sich je Sparte/Periode zum Markt; überlappende Peers bleiben Filter. |
| AP5 R10/R12 | Handfälle ohne Doppelbuchung; Risiko folgt neuem Träger, Altreserve bleibt; Carryover, A=L+E, unversicherte Mengen/Schäden sichtbar. |
| AP5 R13 | Versionierter Vertrag/Quelle, Anleitung und gemeinsamer höherer Installer-Release; bestehende AP3-Regressionen. |
| E05-01 | Kosten in Entscheidungsperiode, Wirkung erst nach Vorlauf und nur während erklärter Dauer; Ende stellt Grundprofil her; keine doppelten Kosten. |
| E05-02 | Entscheidungen kennen keine Zukunft; Aufnahme und gebuchte Menge/Risiko passen; größere Märkte verschieben keine bisherigen Akteur-Zufallswerte. |

Leben und Kranken verwenden nur die benannten bisherigen begrenzten Kanäle.
Neue Lebens-Nachfrage bleibt ein separates fachliches Tor des späteren Pakets.
Top-40-Namen/Daten/Ranggrenze sind AP6, Schock-Demos und ICT-Kopplung AP7,
erweiterte Prozessgrafiken AP8. Die erhaltene DORA-PDF wird als Quellenaufnahme
gesichert; keine Erhebungsquote fließt in den AP5-Risikopfad ein.

## Fortsetzen

Die echte Zustimmung zu `ims_ap5_market_contract.md` ist dokumentiert.
Im selben PR M2–M4 vollständig prüfen. Bei Änderungen zuerst
betroffene Handfälle nachführen. Technische Fertigstellung, Benutzerabnahme
und Merge bleiben getrennt; `completion_evidence` ist bisher leer.
