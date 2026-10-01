# AP3: Umsetzung des 100-Perioden-Managementlabors

Start: 01.10.2026, nach externer AP2-Abnahme, verifiziertem AP2-Merge
`2e70b8f814870807a7c8c34d8fc384f8f6a5bb3c` und erfolgreicher Evernote-Ablage.
Branch `codex/ims-management-integration`, ein Draft-PR für das gesamte Paket.
Der Planprüfer erzeugte den AP3-Auftrag aus diesem tatsächlichen main-Stand.

## Meilensteine und vollständige Anforderungszuordnung

| Meilenstein | Anforderungs-IDs | Status / Abnahme |
| --- | --- | --- |
| M1: ICT-/DORA-Wirkungskette | PR179–186 | technisch abgenommen: gerichteter Quellenvertrag, Zeitadapter, Ereignisse, Rückstand/Nacharbeit, gemeinsame Anbieter, Gegenmaßnahmen, Modellbilanz und vollständige Exporte |
| M2: Geführter Lauf | PR187, PR187a–c | technisch abgenommen: 100 vollständige Kontexte, 107 frische Kandidaten, atomare idempotente Speicherung, tatsächliche Prefix-/100er-Läufe und ZIP; Laufindex 0 |
| M3: Vier Sparten | PR187d–f | technisch abgenommen: erklärter Quellenvertrag, frische 100er-Rechnung beider Seiten, Carryover/Bilanzinvarianten und digestgleiche UI/Exports |
| M4: Belegte Strategiewirkung | PR187g–k | bestätigter moderner Vertrag umgesetzt und abgenommen: kartierte Regelkerne, benannte Gruppen/Einheiten/Fenster, Preis × Exposition, begrenzte Leben/Kranken-Kanäle, handprüfbare Wirkung 302 × 95 |
| M5: Seminar | PR188–190 | technisch abgenommen: drei volle 100er-Fälle, Kapitaldruck, portable Bündel/frische Demo, Offline-Anleitung/Bilder und vollständiger installierter Seminarpfad |

Alle 23 Anforderungen sind im bestätigten begrenzten Umfang abgenommen und
mit konkreten completion_evidence-Einträgen im Manifest done dokumentiert.
Geprüfter Produkthead 589689d: vier grüne CI-Checks, 2.672 Tests + 8 Subtests,
30 Browserfälle, 14 Installer-Lifecycleprüfungen einschließlich 30 Browserfällen
gegen die installierte EXE. Lokal sauberer 9d53a04-Installer ebenfalls 14/14
und 30/30. Der zunächst fehlende Ressourcenweg im portablen Prüfpaket ist durch
589689d und einen echten Staging-/Backend-Regressionsfall behoben.

Vollständige Anforderungszuordnung, Messzeiten, Artefakte, SHAs und Grenzen:
`docs/reports/ims_ap3_abschlussbericht.md`, `ims_ap3_ci_evidence.json` und
`ims_ap3_p52_evidence.json`. Moderne Quellenkartierung:
`docs/migration/ims_ap3_modern_strategy_bridge.md`; aktuelle Seminarhilfe:
`docs/handbook/seminar_ap3.md` und `.html`. M1–M3-Mappings und Teilanleitungen
bleiben erhalten. Frühere Zwischenstandsbelege beschreiben ihre jeweiligen
Produkt-SHAs, nicht nachträglich den ganzen Seminarpfad.

Ready erst nach grünen Checks des aktuellen Dokumentations-Heads. AP3-Merge
und öffentliche Veröffentlichung bleiben offen. Eine neue unabhängige
frische Windows-AP3-Abnahme wurde nicht durchgeführt. Für abhängige Pakete
zählt erst der nach main übernommene Status; kein neues Paket begonnen.

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
- Der M4-Entscheidungspunkt ist durch ausdrückliche Bestätigung geschlossen.
  Mapping: `docs/migration/ims_ap3_modern_strategy_bridge.md`. Anonyme
  historische Schadenpositionen werden nicht als historisches Kfz/Sach ausgeführt.

## Risiken und Prüfstrategie

Gegen doppelt gezählte gemeinsame Ausfälle, Kreisabhängigkeiten, verschobene
Ereignisgrenzen, verlorene Rückstände und doppelte Bilanzverluste werden
deterministische kleine Positiv-/Negativfälle gerechnet. Ungültige Eingaben
liefern keinen Digest und keine Teilresultate. Ressourcenlimits gelten vor
Rechnung und Speicherung; Inputs werden nicht verändert.

Jeder Meilenstein erhält passende Kern-/API-Prüfungen, Anschluss in der AP2-UI
und Benutzeranleitung. Reale Browser prüfen breite/schmale Ansichten, Fehler,
Zustand/Freigaben und echte Exporte. Zum Paketabschluss bestanden vollständiger
Windows-Release-Gate, aktualisiertes Installationsartefakt und Seminarpfad.
Messzeiten werden getrennt von unbekannter aktiver Arbeitszeit dokumentiert.

Keine historische Vollgleichheit, gesetzliche Bilanz, regulatorische SCR/MCR-
oder Bedeckungsquote, DORA-Konformität oder endogene All-Sparten-Kopplung wird
aus technischem Bestehen abgeleitet. Merge und öffentliche Veröffentlichung
bleiben einer gesonderten Freigabe vorbehalten.
