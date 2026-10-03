# AP7: Herkunft und begrenzte Erweiterungen

03.10.2026. Der konkrete Vertrag wurde ausdrücklich angenommen;
[Annahme](../reports/ims_ap7_contract_acceptance.md).
Die folgenden Ursprünge wurden in M1 geprüft; die moderne Erweiterung ist
in M2/M3 implementiert. [Vertrag](../plans/ims_ap7_shock_contract.md),
[historische M1-Kern-/Handproben](../reports/ims_ap7_contract_probes.json).

| Ursprung | Bestehende Entsprechung | AP7-Erweiterung / Grenze |
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

M1 enthält `scripts/planning/probe_ap7_contract.py` und dessen Tests als
wissenschaftliche Vorbereitung. Seine Quellen-Hashes und damaligen
Produktbeobachtungen bleiben unverändert im Probebericht.

## Tatsächliche Komponenten der angenommenen Umsetzung

| Datei unter `python_port/ims/market/` | Fachliche Entsprechung |
| --- | --- |
| `shock_contract.py` | Eigene versionierte Ereignis-/Antwort-/Lebens-/Graphhülle mit Quellenbindung und atomaren Grenzen. Unveränderte AP5- und AP6-Verträge bleiben erhalten. |
| `shock_presets.py` | Vier vollständige 100er-Standards aus dem kuratierten BaFin-Katalog, explizite synthetische Produkte, Finanzierung, Ressourcen und Kontrollannahmen. |
| `shock_process.py` | Transitive Ausfallgraphen, konkrete Ersatzpfade, halboffene Stundenfenster, gemeinsames FIFO-Arbeitsbudget, Teilfortschritt, eindeutiger Kostenverteiler. Kein alter skalarer Fallback als Unabhängigkeitsbeweis. |
| `shock_plan.py` | Aktivierung 41, alte Eigentümer während wartender Wechsel, tatsächliche Ausgabe ab Folgeperiode, gemeinsamer deterministischer Lebenspool und einmalige Vorsorge-/Ereigniskosten. |
| `shock_life.py` | Ausschließlich ausgegebene neue Policen an den vorhandenen Garantie-/Policenperiodenkern anhängen; Altpolicen, alte Todes-/Ablaufflüsse erhalten. |
| `shock_runner.py` | Frische gekoppelte Rechnung beider Seiten, gemeinsame Anfangsperioden und vollständiger Quellen-/Ergebnisdigest. Markt ist einzige finanzielle Rechnung. |
| `runner.py`, `export.py` | Optionale Brücke zur vorhandenen VU-/Sparten-/Markt-/Gruppenbuchung; bestehende Pfade ohne Brücke unverändert. Excel enthält echte Einzel-VU-Zeilen und gemeinsame Erklärbelege. |

API: `python_port/ims/api/market.py`, frische Fall-/Quellen-/Rechnungs-/Export-
Routen mit bestehender Rechensperre. Oberfläche:
`frontend/src/MarketShockWorkbench.tsx` und `.css`, Ereignis → Vorleistungen →
Queue → Vertrag → Buchung, exakt aus geprüften Zeilen. Präsentation erzeugt
keine Versicherungsflüsse. Anleitung: `docs/handbook/market_ap7.md` / `.html`.
Tests: `tests/test_market_shocks.py`, `frontend/tests-browser/market-shocks.spec.ts`.

Zusätzliche Nachfrage ist deterministisch; keine neue Zufallskalibrierung.
Vorhandene akteurgebundene `quote_offer`-Draws werden unverändert wiederverwendet.
Claims/Service erfassen nur administrative Arbeit/Kosten, keine Verschiebung
von Versicherungszahlungen. Personal-Kapazität wirkt auf den verfügbaren
Primär-/Ersatzpfad unabhängig von Listenreihenfolge. Unbekannte Kontrolle
belegt keine Unabhängigkeit. Die moderne Kopplung behauptet keine historische
C-Vollgleichheit und erweitert keine alten Abnahmen rückwirkend.

Die vorhandene Lebens-Kernprobe bewahrt Todes- und alte Ablaufleistungen; ihre
kleine deklarierte Neupolice kann Eigenkapital am Horizont sogar senken. Die
ICT-Kernprobe zeigt einen alten Kapazitätsfallback trotz ausgefallenem
Plattformpfad. Die Eintrittsprobe zeigt korrekte Finanzierung/Buchung, aber eine
zu frühe AP5-Aktivzählung. Unabhängige Handrechnung zeigt Warteschlangen-
konservation, Horizont-Aufholung und gemeinsame Kosten. Diese Beobachtungen
begründen Prüfanforderungen, keine bereits gelieferten neuen Modellwirkungen.
