# AP3: Umsetzung des 100-Perioden-Managementlabors

Start: 01.10.2026, nach externer AP2-Abnahme, verifiziertem AP2-Merge
`2e70b8f814870807a7c8c34d8fc384f8f6a5bb3c` und erfolgreicher Evernote-Ablage.
Branch `codex/ims-management-integration`, ein Draft-PR für das gesamte Paket.
Der Planprüfer erzeugte den AP3-Auftrag aus diesem tatsächlichen main-Stand.

## Meilensteine und vollständige Anforderungszuordnung

| Meilenstein | Anforderungs-IDs | Status / Abnahme |
| --- | --- | --- |
| M1: ICT-/DORA-Wirkungskette | PR179–186 | implementierter Zwischenstand: gerichteter Quellenvertrag, Ereignisse, Stunden-/Periodenskala, Kapazität/Rückstand/Erholung, gemeinsame Anbieter, Gegenmaßnahmen, deklarierte Modellbilanz und Dossier; technische Nachweise unten, Gesamtabnahme AP3 offen |
| M2: Geführter Lauf | PR187, PR187a–c | implementierter Zwischenstand: 100 vollständige Kontexte, frischer Bau, atomare unveränderliche Speicherung und tatsächlicher PR151-Lauf/Export mit echten Prefixnachweisen; Laufindex ausdrücklich auf 0 begrenzt, technische Belege in Mapping/Handbuch |
| M3: Vier Sparten | PR187d–f | implementierter Zwischenstand: ausdrücklich gemeinsamer Quellenvertrag, frische Rechnung beider Seiten/Carryover/Prefixe und digestgleiche Anzeige/CSV/JSON/XLSX; technische Belege im Mapping |
| M4: Belegte Strategiewirkung | PR187g–k | fachlich blockiert vor Adapter: historische Preisentscheidung ist kein Gesamtprämienfluss; Population/Einheiten/Abrechnung fehlen. Konkreter moderner Vorschlag in ims_ap3_strategy_gate.md, Entscheidung angefragt. Vollständiger Umfang bleibt erhalten. |
| M5: Seminar | PR188–190 | Vorbereitung: drei deklarierte Eingabevarianten, ICT-Fall, Anleitungen und Moderationsentwurf vorhanden; vollständige Fälle mit Strategiepfad, portable Bündel und installierte Gesamtabnahme abhängig von M4 offen |

Keine Anforderung ist durch diesen Plan bereits abgenommen. AP3 bleibt
in_progress; completion_evidence wird erst für tatsächliche Abnahmen ergänzt.
Ein fachlich blockierter Teil wird ausdrücklich benannt und nicht als done geführt.

M1-Nachweise: 22 neue Kern-/API-Prüfungen, 70 bestehende Bilanz-/API-
Regressionen, sechs reale Browserfälle (drei Größen, zwei Farbmodi) und
TypeScript-/Vite-Build bestanden. Fachliche Zuordnung und Grenzen:
`docs/migration/ims_ap3_ict_workshop.md`; Bedienung:
`docs/handbook/ict_ap3.md`. Es handelt sich um einen deklarierten Bilanzoverlay,
noch nicht um automatische Markt-/Vier-Sparten-Kopplung.

M2-Nachweise: 15 neue Kern-/API-Prüfungen und 30 bestehende Bau-/Auflösungs-
Regressionen, vier reale Browserfälle und Build bestanden. Mapping/Bedienung:
`docs/migration/ims_ap3_guided_period_chain.md`, `docs/handbook/hundred_ap3.md`.
Der bestehende Globalperiodenexport wird erhalten; gemeinsame Prefixe sind hier
für Laufindex 0 freigegeben. Ein zusätzlicher Negativfall sperrt ungültige
Profil-IDs vor dem frischen Bau. Gesamtpaket bleibt in_progress.

M3-Nachweise: 49 neue und bestehende Kern-/API-Bilanzprüfungen bestanden
(70,98 s), darunter 13 neue Tests. Vier reale Browserfälle bestanden bei
1440/390 Pixeln in Hell/Dunkel: 100er-Resultat, drei tatsächliche Downloads,
Kapitalübergabe und erneute Quellenbindung. Vollständige Browser-/Gate-Evidenz
wird im Zwischenbericht festgehalten. Mapping/Bedienung:
`docs/migration/ims_ap3_management_case.md`, `docs/handbook/management_ap3.md`.
Die Eingabevarianten sind exogen und ersetzen M4 nicht. Nächster fachlicher
Schritt: Entscheidung über den konkreten Quellen-/Abrechnungsvertrag; danach
begrenzter Adapter und vollständiger M5-/Installerpfad im selben PR.

## Quellen und konservative Annahmen

- `ESS.C:main/sy_simltp` verarbeitet diskrete Perioden und logische Zeitpunkte;
  `IMSDATA.C:SIMLAENGE`, `gperiod/glogtime` und `classBAV.As/Ar` begrenzen die
  alte Perioden-/Schocklogik. Keine reale Stundenlänge ist dadurch belegt.
- Die ICT-Schicht ist eine neue ausdrückliche Workshop-Erweiterung, keine
  portierte historische ICT-/DORA-Funktion. Historische Quellen bleiben erhalten.
- `non_life_model_balance.py` ist bereits ein ausdrücklich szenariobasiertes
  Modell ohne historische Spartenbindung. `solvency_risk_aggregation.py` hat
  deklarierte operationelle Modellverluste; `solvency_capital_readiness.py`
  bewertet ausschließlich Workshop-Grenzen und sperrt regulatorische Kennzahlen.
- Stunden, Tage und Perioden werden nur mit einem expliziten Zeitvertrag
  übersetzt. Services/Assets/Anbieter, VU-Verantwortung, gerichtete Abhängigkeiten,
  Kapazität, Nachfrage, Kosten und Wirkungsannahmen müssen benannt sein.
- Der M4-Entscheidungspunkt bleibt offen bis zum Quellenmapping. Anonyme
  historische Schadenpositionen werden nicht als Kfz/Sach ausgeführt.

## Risiken und Prüfstrategie

Gegen doppelt gezählte gemeinsame Ausfälle, Kreisabhängigkeiten, verschobene
Ereignisgrenzen, verlorene Rückstände und doppelte Bilanzverluste werden
deterministische kleine Positiv-/Negativfälle gerechnet. Ungültige Eingaben
liefern keinen Digest und keine Teilresultate. Ressourcenlimits gelten vor
Rechnung und Speicherung; Inputs werden nicht verändert.

Jeder Meilenstein erhält passende Kern-/API-Prüfungen, Anschluss in der AP2-UI
und Benutzeranleitung. Reale Browser prüfen breite/schmale Ansichten, Fehler,
Zustand/Freigaben und echte Exporte. Zum Paketabschluss folgen vollständiger
Windows-Release-Gate, aktualisiertes Installationsartefakt und Seminarpfad.
Messzeiten werden getrennt von unbekannter aktiver Arbeitszeit dokumentiert.

Keine historische Vollgleichheit, gesetzliche Bilanz, regulatorische SCR/MCR-
oder Bedeckungsquote, DORA-Konformität oder endogene All-Sparten-Kopplung wird
aus technischem Bestehen abgeleitet. Merge und öffentliche Veröffentlichung
bleiben einer gesonderten Freigabe vorbehalten.
