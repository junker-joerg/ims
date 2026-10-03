# AP7: Stand und nächste Entscheidung

03.10.2026. Branch `codex/ims-market-shock-demos`, von frisch gefetchtem main
`88841290113a37faa6bf117d4cd67dcd9ff0867c`. Der ausdrücklich beauftragte AP6-
Merge ist tatsächlich erledigt; [Beleg](ims_ap6_merge.md). Der anschließende
AP7-[Arbeitsauftrag](../plans/ims_ap7_work_order.md) wurde vor Änderung seines
Manifeststatus im authorized-Modus erfolgreich erzeugt. AP7 **in_progress**,
technisch nicht fertig, Anwenderabnahme/Merge nicht freigegeben.

## M1: konkret zur fachlichen Prüfung vorbereitet

[Paketplan](../plans/ims_ap7_implementation.md),
[Vertragsvorschlag](../plans/ims_ap7_shock_contract.md) und
[C-/Python-Mapping](../migration/ap7_shock_contract.md) liegen vor. E07-01 ist
mit eigener Herkunft aus dem angenommenen Boardplan einbezogen. Vorgeschlagen:
fiktiver Eintritt mit expliziter Finanzierung, deterministischer Lebens-
Interessentenpool, erhaltene Altgarantien, physische Stundenkanten, Antrags-/
Wechselbearbeitung und einmalige Kostenbuchung sowie wirkliche Ersatzpfade.
Claims-/Service-Queues verschieben zunächst keine Versicherungsleistungen;
diese sichtbare Begrenzung ist Teil der zu entscheidenden neuen Abnahme.

Die [ausgeführten Proben](ims_ap7_contract_probes.json) unterscheiden bestehende
Kerne und unabhängige Handrechnung ausdrücklich von zukünftigen Produktkanälen:

- Vorhandener Lebens-Kern: alte Todes-/Ablaufleistungen erhalten; ohne die
  deklarierte Neupolice P1 `94=46+48`, P2 `35=0+35`. Mit ihr P1 `104=54+50`,
  P2 `33=0+33`. Nachfrage allein ist keine Ergebnisgarantie.
- Vorhandener ICT-Kern: 0 gegen 240 bearbeitete Vorgänge beim skalaren
  Kapazitätsfallback trotz beibehaltener ausgefallener Plattformabhängigkeit.
  Das belegt keine unabhängige Ersatzinfrastruktur.
- Vorhandener 25-Perioden-/Drei-VU-Kernfall: Eintritt P21, Kapital 1.000,
  Prämie 10, bezahlter Schaden 8, Schlussaktiva/Eigenkapital 1.002. AP5 zählt
  bereits P20 drei registrierte Anbieter; AP7-Aktivierungsmerkmal fehlt noch.
- Unabhängiger sechs-Stunden-Handfall: `12=10+2` ohne Schock und `12=7+3+2`
  mit Schock; ausgegeben, bearbeitet für die nächste Periode und noch wartend
  getrennt. Differenz 9 Prämie am Horizont ist kein zusätzlicher ICT-Abzug.
  36 Stunden ab Stunde 480 treffen P21 mit 24 und P22 mit zwölf Stunden;
  unabhängiger Q-Pfad verfügbar, vom US-IAM abhängiger nicht. Kosten 6 werden
  in 1,9998/1,9998/2,0004 verteilt, Summe 6.

## Tatsächliche lokale Prüfungen

| Prüfung | Ergebnis |
| --- | --- |
| `probe_ap7_contract.py --out docs/reports/ims_ap7_contract_probes.json` | passed, 0,1608613 s; sieben Quellen-Hashes und unveränderte Eingänge |
| `pytest tests/test_ap7_contract_probes.py -q` | 5 bestanden, 1,40 s; Kernwerte, Finanzierung, Aktivzählgrenze, Queue-/Kosten-/Zeitkonservation und Überschreibschutz |
| `unittest discover -s tests -p test_ai_sprint_plan*.py -v` | 35 bestanden, 5,541 s |
| AP7-Umsetzungsauftrag gegen actual main | erfolgreich, AP6-Abhängigkeit erfüllt |

Diese M1-Prüfungen sind keine vier fertigen 100er-Demos, keine AP7-Produkt-CI
und kein alpha.7-Installer. Produktkern, API/UI und ausgelieferte alpha.6-Version
wurden durch M1 nicht geändert. AP6s vier erfolgreiche Produktchecks stehen
mit tatsächlichem Merge-/Hashbezug im eigenen Prüfprotokoll.

## Offenes Tor und nächster Schritt

Der angenommene [Manifestvertrag](../plans/ims_explainable_market_plan.json)
verlangt vor M2: „Lebens-Nachfragevertrag mit erhaltenen Garantien erklärt und
angenommen“ sowie „ICT-Zeitabbildung, Kostenzuordnung und Vermeidung doppelter
Verluste erklärt und angenommen“. Die konkrete fachliche Annahme des nun
reviewbaren Vorschlags fehlt. Kein Annahmebeleg erfunden; beide Tore offen.

Nach Annahme denselben Draft-PR fortsetzen: M2 neue versionierte Kernkanäle
mit Handtests, M3 vier vollständige portable Fälle und API/UI/Excel, M4
Anleitung/Bilder, eigene höhere Releasekennung und echter installierter
Windows-Produktlauf. Ursprüngliche deutsche Top-40-Tore bleiben sichtbar offen;
keine reale Unternehmens-/Providerbelegung, SCR- oder DORA-Compliancebehauptung.
AP7-Merge und Veröffentlichung brauchen eigene spätere Freigabe.
