# AP7: Herkunft und vorgeschlagene Erweiterungen

03.10.2026, M1. Noch nicht angenommener fachlicher Vertrag und keine fertige
Schockimplementierung. [Vorschlag](../plans/ims_ap7_shock_contract.md),
[Kern-/Handproben](../reports/ims_ap7_contract_probes.json).

| Ursprung | Bestehende Entsprechung | Vorgeschlagene AP7-Erweiterung / Grenze |
| --- | --- | --- |
| `IMS.E` 231–246, `aktiVU`: aktive VU-Verwaltung | `ims.market.runner` zählt registrierte Sektorzeilen; Kapazitätsfenster begrenzen Annahme | Eigenes zeitabhängiges Aktivierungsmerkmal für den fiktiven Anbieter 41; C-Vektorbestand nicht kopieren |
| `IMS.E` 3533–3591, `Vrvn06`: gesetzter Anfangsbestand, danach Minimum aktiver Angebote | AP5 `customer.price`, zulässige Anbieter, stabile Gleichstandsregel, Ganzkohortenaufnahme | Deklarierte Reichweite und bearbeiteter Wechsel; Werbeaufwand erhält keine implizite Elastizität |
| `IMSDATA.C` 309–350, `classBAV`, `Vuag`/`Vnag`, Vorperiodeninformation | AP5 VU-/Markt-/Gruppenaggregate und akteurgebundene Draws | Aktivzählung und neue Vorgangsaggregate; keine doppelte Buchung über Gruppen |
| `ESS.C` 88–149, `sy_simltp`, `sy_xaktion` | Explizite Periodenkette und bestehende ICT-Stunden-/Ereignisfenster | Halboffene Stundenfenster und deklarierte 24-Stunden-Abbildung; kein historischer Kalendermaßstab behauptet |
| AP3 `ims.accounting.life_period_chain` / `life_policy_core` | Ausdrücklich deklarierte Neupolicen, Garantien, Tod und Ablauf möglich | Deterministischer Markt-Interessentenpool und tatsächliche Ausgabe nach Bearbeitung; keine C-LV-Nachfragegleichheit behauptet |
| AP5 `ims.market.contract` / `runner.actuarial()` | Lebens-Altbestand geschlossen; Neugeschäft bisher ausdrücklich abgewiesen | Neue versionierte Hülle, alte AP5-Eingänge bleiben unverändert; Altgarantien werden wiederverwendet |
| AP3 `ims.ict.simulation` / `contract` | Transitive Ausfälle, Kapazität, Queue und separater ICT-Workshop-Aufwand | Konkreter Ersatzgraph; Vorgangsabschluss steuert neuen Vertrag/Wechsel, Kosten in Marktbilanz einmal |
| AP6 `ims.market.reference` | Originalquelle, Annahmen, stabile Referenz-IDs und frisches Bündel | Vier abgeleitete Schockfälle; synthetischer Anbieter/Provider nie als BaFin-Fakt |
| Boardplan E07-01, PR #292 | Separat angenommene AP7-Ergänzung | Gemeinsame Ereignishülle für Einzelereignis/Sequenz; eigene neue Abnahmen |

Die modernen vier Sparten sind keine belegte Eins-zu-eins-Interpretation eines
historischen C-Union-Felds. Neue Lebens-Neunachfrage, Providerkontrolle und
physische Markt-/ICT-Kopplung sind explizite Erweiterungen; dafür wird keine
historische Vollgleichheit behauptet. Historische Terminal-UI bleibt unverändert.

M1 enthält nur `scripts/planning/probe_ap7_contract.py` und dessen Tests als
wissenschaftliche Vorbereitung. Produktmodule/-Dateinamen für M2 werden erst
mit Annahme und Umsetzung konkret ergänzt; kein zukünftiger Modulname wird
als bereits portiert ausgegeben. Quellen-Hashes stehen im Probebericht.

Die vorhandene Lebens-Kernprobe bewahrt Todes- und alte Ablaufleistungen; ihre
kleine deklarierte Neupolice kann Eigenkapital am Horizont sogar senken. Die
ICT-Kernprobe zeigt einen alten Kapazitätsfallback trotz ausgefallenem
Plattformpfad. Die Eintrittsprobe zeigt korrekte Finanzierung/Buchung, aber eine
zu frühe AP5-Aktivzählung. Unabhängige Handrechnung zeigt Warteschlangen-
konservation, Horizont-Aufholung und gemeinsame Kosten. Diese Beobachtungen
begründen Prüfanforderungen, keine bereits gelieferten neuen Modellwirkungen.
