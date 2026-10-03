# AP7: technisch fertig; Anwenderabnahme offen

03.10.2026. M1–M4 im selben Draft-PR #296 abgeschlossen. **alpha.7 technisch
fertig**, vier Produktchecks am festgehaltenen Produktkommitt 37fe791 erfolgreich;
2.755 Python-Tests/14 Subtests, 70 Browserfälle und echter Installer mit
14 Lifecycle-/70 installierten Browserprüfungen. Vier vollständige 100er-Fälle
mit exakten 25er-Prefixen; installierte und Checkout-Ergebnisdigests identisch.
Git-Tree, Binär-/Archivhash und Offline-Ressourcen geprüft.
[Abschluss](ims_ap7_abschlussbericht.md), [Produktprüfung](ims_ap7_produktpruefung.md),
[Verifikation](ims_ap7_verification.json).

Der ausdrücklich angenommene Vertrag bleibt verbindlich. ICT zeigt Ereignis,
Abhängigkeiten, echtes gemeinsames Arbeitsbudget/Rückstand, Vertrag und Buchung.
Anwenderabnahme/Merge bleiben offen, kein öffentliches Release und kein
AP8–AP14-Auftrag. Die nachstehenden Zwischenstände sind historisch und werden
durch diesen Abschluss ersetzt.

## Historischer AP7-Arbeitsstand

**Fortsetzung nach Annahme am 03.10.2026:** Der Auftraggeber hat den konkreten
Vertrag ausdrücklich angenommen; [Beleg](ims_ap7_contract_acceptance.md).
Beide fachlichen Tore angenommen, M2 läuft im selben PR #296. Zusätzlich
besonders sichtbarer ICT-Erklärpfad von Ereignis über Abhängigkeiten/Queues
bis Vertragswirkung und Buchung für beide Seiten. Nachstehender M1-Stand ist
historischer Vorbereitung-/Prüfnachweis; keine weiterhin offene Vertragsannahme.

03.10.2026. Branch `codex/ims-market-shock-demos`, von frisch gefetchtem main
`88841290113a37faa6bf117d4cd67dcd9ff0867c`. Der ausdrücklich beauftragte AP6-
Merge ist tatsächlich erledigt; [Beleg](ims_ap6_merge.md). Der anschließende
AP7-[Arbeitsauftrag](../plans/ims_ap7_work_order.md) wurde vor Änderung seines
Manifeststatus im authorized-Modus erfolgreich erzeugt. AP7 **in_progress**,
technisch nicht fertig, Anwenderabnahme/Merge nicht freigegeben.

Das gesamte Paket wird in [Draft-PR #296](https://github.com/junker-joerg/ims/pull/296)
fortgesetzt. M1-Vorschlagskommitt `c9e8c63be7ed7a4eb2495dfdef22e4db83eb3780` enthält
den konkreten Vertrag und die hier beschriebenen Prüfungen. PR wurde angelegt
und diesem Chat als Artefakt zugeordnet. Die gemeinsame fachliche Annahme des
Lebens-/ICT-Vertrags ist beim Auftraggeber angefragt; keine Antwort als erteilt
behauptet. Die späteren CI-Produktchecks sind vom lokalen M1-Stand getrennt.

## M3 lokal vollständig geprüft; M4 folgt

Vier tatsächliche 100er-Browserfälle bestanden (667,07 s einschließlich
25er-Prefixrechnungen). Frische Rechnung/Anzeige pro Fall: US 136,484 s /
55.758.615 Bytes; Google 134,406 s / 55.999.982 Bytes; Leben 138,856 s /
55.324.176 Bytes; DORA 137,550 s / 55.787.965 Bytes. Alle liegen unter dem
64-MiB-Ergebnisbudget. P1–P5 gleich, Prefix25 exakt, A=L+E/Carryover,
Markt=VU-Summe, disjunkte Familien-/Gruppensummen, Risiko-/Mengen-/Kosten-
konservation geprüft. Unabhängiger Q liefert in P21 96 statt 0 Einheiten.
Sieben Bedienungs-/Wiederaufnahme-/Export-/Kontrastfälle bestanden zuvor:
Minimum 6,13:1 hell / 6,85:1 dunkel, keine Axe-Verstöße oder Seitenüberbreite
in 1440×900, 1024×768 und 390×844. Neue Rollen-Fokusnavigation, kompaktere aufklappbare Tabellen und JSON-
Fehlerbehandlung anschließend nachgeprüft: acht echte Browserfälle bestanden
(5,8 min), zwölf aktuelle Screenshots und alle acht über die lokale Anleitung
geladenen PNGs geprüft. Die großen Geld-/Mengenserien nutzen unveränderte
exakte Assertions im Node-Harness statt je Wert einen Browser-Trace-Schritt. 15 neue AP7-Tests und 10 AP6-Referenztests bestanden gemeinsam
(105,91 s); AP5s 16 Regressionen erneut bestanden (43,31 s).

Installer/Produkt-CI und deren Head-/Hash-/Ressourcenbindung stehen aus. AP7
bleibt in_progress und nicht merged. Die vorläufigen frühen Kernläufe bzw.
Browser-Harnessprobleme (exakte Beschriftungen, Inspector-Bodycache,
Einzelassertionen im Trace) werden nicht als finale Produktprüfung verwendet.
Korrigierter Harness leitet echte Antworten weiter und prüft große
Erhaltungsserien ohne Hunderttausende Trace-Schritte.

## M2/M3: angenommene Kanäle implementiert

03.10.2026. Eigenständige versionierte Hülle, vier portable Quellenfälle,
24-Stunden-Graph/FIFO, bearbeitete Lebensanträge/Wechsel, Aktivierung 41 und
einmalige Markt-Kostenbuchung sind angeschlossen. Oberfläche erklärt beide
Seiten über Ereignis, konkrete Vorleistungen, gemeinsames Arbeitsbudget,
Queue, Vertrag und Bilanz. Original/eigene Sitzung, JSON/Einzel-VU-Excel und
Offline-Anleitung alpha.7 sind angeschlossen. Vierzehn neue kleine AP7-Tests
bestanden lokal (27,28 s); die vorherige gemeinsame Regression umfasste
77 Tests und 14 Subtests (176,87 s). Frontend baut. Erste vier vorläufige 100er-Kernläufe
bestanden; sie werden nicht als Nachweis des endgültigen Produktkommitts
ausgegeben. Abschließende Browser-/Prefix-/Ressourcen-/Installerprüfungen
laufen noch. Produktstatus bleibt in_progress; keine Anwenderabnahme oder
Mergefreigabe erteilt.

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
| Plan-CI am M1-Kommitt c9e8c63 | [erfolgreich](https://github.com/junker-joerg/ims/actions/runs/37104003909/job/111148906606); Browser-/Release-Gate-/Installerchecks zum Beobachtungszeitpunkt noch laufend |

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
