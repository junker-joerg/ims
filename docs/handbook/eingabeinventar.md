# Notwendige Eingaben im IMS-Marktexperiment

Stand: 06.10.2026 · AP8 alpha.11. Die Liste leitet sich aus dem bestehenden UI und den ausgeführten AP5-/AP6-/AP7-Verträgen ab. Die Bilder sind Gestaltungsvorlagen und liefern keine Modellparameter.

## Was ein Anwender zunächst eingeben muss

1. Einen benannten Analysefall und einen Horizont wählen, dann die Vorlage laden. Die Vorlage liefert den vollständigen Modellvertrag einschließlich Seed, Beständen, Strategien, Kunden, Risiken und gegebenenfalls ICT.
2. Für Änderungen dieselbe Quelle als eigenes Experiment übernehmen. Je nach Frage Anbieterparameter, Maßnahmenfenster und Kosten oder äußere Ereigniszeit, Dauer und Intensität verändern.
3. Die Vergleichsachse prüfen: gleicher Schock mit unterschiedlichen Antworten oder gleiche Entscheidungen mit/ohne Schock. Alle Annahmen bleiben im exportierbaren Quellenobjekt.
4. Frisch berechnen. Reine Anzeigeauswahl, Suche und Wiedergabe sind keine zusätzlichen Modelleingaben.

Es gibt keinen universellen Standardwert für Preis, Garantie, Kapazität oder Anfangsbilanz. Die gültige Vorlage des gewählten Falls liefert diese Werte. Neue GUI-Maßnahmen starten zunächst in P6, mit Vorlauf 0, Dauer bis zum Horizont und Kosten 0. Bereits vorhandene Maßnahmen behalten ihr Zeitfenster. Geldwerte sind Dezimaltext in **Modellwährung**, nicht die Quellen-Euro.

## Fachliche Feldliste

| Bereich | Erforderliche Items / JSON-Pfade | Zweck / Eingabeort | Einheiten und Grenzen | Pflicht / Bedingung |
| --- | --- | --- | --- | --- |
| Modellbasis | `schema_version, case_id, period_count, seed, provenance.kind/units/description` | Version, Versuch, Horizont und Reproduzierbarkeit; JSON / Fallwahl | GUI 10/25/50/100; Vertrag 2/5/10/25/50/100; Seed Ganzzahl 0..2^53−1; units=model_currency | Pflicht; Vorlage liefert Werte |
| Modellbasis | `insurers[].insurer_id/name/insurance_group_id/sectors` | Identität und vorhandene Sparten; JSON / Quellenprofil | 1..41 VUs; ID 1..1000000; Name 1..120 Zeichen; motor/property_liability/life/health | Pflicht; keine freien VUs aus Mockup erzeugen |
| Modellbasis | `insurers[].sectors.{motor,property_liability}.opening.assets/liabilities/equity` | Anfangsbestand je Nichtleben-Buch; JSON | Modellwährung; assets=liabilities+equity | Pflicht pro deklarierter Nichtleben-Sparte |
| Modellbasis | `insurers[].sectors.{motor,property_liability}.capacity` | Kapazität zur Aufnahme ganzer Kohorten; JSON / Maßnahme | Nichtnegative Menge; Aufnahmekapazität ist keine ICT-Stundenkapazität | Pflicht |
| Modellbasis | `insurers[].sectors.{motor,property_liability}.periods[].period/old_claims_paid/operating_expense/investment_income/capital_contribution/capital_distribution` | Vollständiger Zahlungs- und Kostenpfad; JSON | Genau jede Periode; Geld, Anlageertrag darf negativ sein; Altzahlung <= Anfangsverpflichtungen | Pflicht |
| Modellbasis | `insurers[].sectors.{life,health}.source` | Bestehender Spartenvertrag; JSON / eigene Fachwerkzeuge | Passende Version und voller Horizont; lokale VU-ID 1; Details im Leben-/Krankenvertrag | Pflicht bei deklarierter Leben-/Kranken-Sparte |
| Nachfrage | `customer_groups[].group_id/sector_id/quantity/initial_insurer_id` | Kohorte und anfänglicher Vertrag; JSON | Bis 200 Gruppen; motor oder property_liability; positive Menge; Anfangs-VU bekannt oder null | Pflicht |
| Nachfrage | `customer_groups[].insurance_threshold` | VN-Versicherungsschwelle; GUI Vorstand / JSON | Dezimalanteil 0..1; gemeinsame Verhaltensannahme, kein VU-Steuerhebel | Pflicht pro Gruppe |
| Nachfrage | `customer_groups[].risk_periods[].period/loss/paid_share` | Risikoschaden und sofort gezahlter Anteil; JSON | Voller Horizont; Modellwährung; paid_share 0..1 | Pflicht; deklarierte Risiken, keine C-Schadenzüge |
| Umwelt | `damage_indicators[]` | Öffentlicher Schadenindikator je Periode; JSON | Voller Horizont; Dezimalanteile 0..1 | Pflicht im Marktvertrag |
| Strategie | `families[].family_id/label/sector_id/rule/parameters` | Ausführbare Strategiefamilie; JSON / Vorlage | Bis 200; eindeutige ID; Regel muss zur Sparte passen | Pflicht; vollständiger Parametersatz |
| Strategie | `families[].parameters.price/advertising` | Festangebot offer.fixed; GUI Vorstand / JSON | Modellwährung 0..1000000 | Nur offer.fixed; Preis und Werbung |
| Strategie | `families[].parameters.premium_factor/advertising_factor` | VU-Regel vu.vrvu01; GUI Vorstand / JSON | Dezimalfaktor 0..1000000 | Nur vu.vrvu01; beide Faktoren |
| Strategie | `families[].parameters.rate_per_period` | life.opening_assets_rate; GUI Vorstand / JSON | Dezimalanteil −1..1 je Modellperiode | Nur Leben-Regel; keine Jahresrendite behauptet |
| Strategie | `families[].parameters.price_per_policy/new_business/exits` | health.declared_profile; GUI Vorstand / JSON | Preis 0..1000000; new_business/exits Ganzzahl 0..1000 | Nur Kranken-Regel |
| Strategie | `assignments.{baseline,variant}[].insurer_id/sector_id/family_id/start/end` | Familienzuordnung je Seite und Zeitfenster; JSON / Fachwerkzeug | Inklusive Fenster; 1..100; genau eine gültige Zuordnung je VU/Sparte/Periode | Pflicht, lückenfrei; P1–P5 identisch |
| Strategie | `measures.{baseline,variant}[].measure_id/insurer_id/sector_id` | Maßnahmenidentität und Träger; JSON / GUI generiert | Bis 200 Maßnahmen je Seite; eindeutige ID; bekannte VU/Sparte | Liste darf leer sein |
| Strategie | `measures.{baseline,variant}[].decision_period/lead_periods/duration/cost/overrides` | Wirksamkeit, einmalige Kosten und Parameter; GUI Vorstand / JSON | Entscheidung 1..100 (neue GUI-Variante ab P6); Vorlauf 0..100; Dauer 1..100; cost nichtnegatives Geld; Overrides regelabhängig | Bei Maßnahme Pflicht; gleicher Parameter nicht widersprüchlich überlappen |
| Strategie | `measures.{baseline,variant}[].overrides.capacity` | Nichtleben-Aufnahmekapazität verändern; JSON / vorhandenes Profil | Nichtnegative Menge; nur Nichtleben | Optional zusätzlich zu ausführbarem Override |
| Gruppen | `peer_groups[].group_id/label/insurer_ids` | Benannte Vergleichsgruppe; JSON / Fachwerkzeug | Bis 50 Gruppen; Mitglieder eindeutig und bekannt; Gruppen dürfen überlappen | Pflichtliste darf leer sein; keine Summierung über überlappende Gruppen |
| BaFin-Quelle | `source_catalog/catalog_digest/workshop/overrides/model_input` | Quellengebundene Referenz und Modellabbildung; Quellen und Handfälle / JSON | Exakter Quellenbeleg; angenommene Workshop-Abbildung; Details in market_data_ap6.md | Im BaFin-Bündel Pflicht; eigener AP7-Fall separat model_input |
| AP7-Bündel | `schema_version/case_id/title/assumption_note/reference_bundle/model_input/period_hours/comparison` | Schockvertrag und Vergleichsachse; GUI / JSON | period_hours exakt Text 24; shock_with_response oder no_shock_vs_shock; gleicher Seed/Horizont zur Referenz | Pflicht im AP7-Fall; Vorlage liefert Bezüge |
| Umwelt | `events[].event_id/kind/insurer_ids/asset_ids/channels/assumption_note` | Ereignisidentität, Ziele und ausgeführter Kanal; JSON / Vorlage | 1..20 Ereignisse; entry/life_demand/regulatory/provider_outage; bekannte Ziele, typabhängige Kanäle | Pflicht im AP7-Fall |
| Umwelt | `events[].start_hour/duration_hours/intensity/cost` | Äußeres Zeitfenster und Stärke; GUI Umwelt / JSON | Stundenstart 120..2400; Dauer 0.0001..2400; Intensität 0..1; Kosten nichtnegatives Geld; Eintritt Intensität=1 bis Horizont | Pflicht; Eintritt/Nachfrage am Periodenanfang |
| Antwort | `responses.{baseline,variant}[].response_id/kind/insurer_ids/asset_id/replacement_asset_id/assumption_note` | Ausführbare Vorstandsantwort; JSON / konkreter Ersatzpfad GUI | Bis 20; price/life_attractiveness/fallback/capacity; bekannte Träger; konkreter Pfad inkl. Abhängigkeiten | Listen dürfen leer sein; alle Schlüssel erforderlich |
| Antwort | `responses.{baseline,variant}[].decision_period/lead_periods/duration_periods/value/cost/cost_per_hour` | Antwortzeit, Wirkung und einmalige/laufende Kosten; GUI Vorstand / JSON | P6..100; Vorlauf 0..100; Dauer 1..100; value Geld/Faktor/Attraktivität je kind; nichtnegative Kosten | Bei Antwort Pflicht; typabhängige zusätzliche Pfadprüfung |
| Eintritt | `activation[].insurer_id/event_id/capital/reachable_group_ids` | Fiktiven Anbieter aktivieren und finanzieren; JSON / Vorlage | Max. 1 zusätzlicher Anbieter; Kfz; Null-Anfangsbestand; Kapital einmal; bekannte erreichbare Kohorten | Google-Fall Pflicht, sonst ggf. leer |
| Lebensnachfrage | `life.pool_per_period/start_period/offers` | Deterministischer Neugeschäftspool; JSON / Vorlage | Pool Ganzzahl 0..20; Start P6..100; bis 40 Angebote | Pflichtstruktur AP7, leerer Pool möglich |
| Lebensnachfrage | `life.offers[].insurer_id/premium/allocation/renewal_premium/renewal_allocation/term_periods/guarantee_rate/admission_per_period` | Neue Police, Garantie und Zulassung; JSON | Garantiezuführung <= jeweiliger Prämie; Laufzeit 1..20; Garantiesatz 0..1; Zulassung 1..4; Anbieter mit Antragsprozess | Bei Angebot Pflicht; Altgarantien bleiben erhalten |
| ICT | `ict.assets[].asset_id/label/control/depends_on/assumption_note` | Vorleistungen und Abhängigkeitsgraph; JSON / Vorlage | 1..40 Assets; Kontrolle US/EU/unknown; bekannte eindeutige Kanten; azyklisch | Pflicht AP7; reale Modellkanten, keine real erhobenen Providerbeziehungen |
| ICT | `ict.resources[].resource_id/asset_id/capacity_per_hour/cost_per_hour/owners` | Geteilte Arbeitsressource; JSON | 1..40 Ressourcen; Arbeitsmenge/Stunde und Geld/Stunde; bekannter Pfad | Pflicht AP7 |
| ICT | `ict.resources[].owners[].insurer_id/sector_id/weight` | Kostenverteilung; JSON | Bekannte VU/Sparte; Dezimalgewichte Summe exakt 1 | Pflicht pro Ressource |
| ICT | `ict.services[].service_id/insurer_id/sector_id/kind/resource_id/arrivals_per_period/assumption_note` | Anträge, Claims und Servicearbeit; JSON | Bis 246 Dienste; underwriting/claims/service; Zufluss Ganzzahl 0..20; underwriting exogener Zufluss exakt 0 | Pflichtstruktur; Anträge entstehen aus dem Markt |
| ICT | `ict.holding_cost_per_job_hour` | Kosten wartender Arbeit; JSON | Modellwährung je Vorgangsstunde, nichtnegative Dezimalzahl | Pflicht AP7 |
| Anzeige | `Periode, Sparte, Vergleichsgruppe, Seite, Fokus-VU, Erklärrolle, ICT-Asset` | Gemeinsame Auswahl der sechs Ansichten; GUI Auswertung | Nur vorhandene Ergebniszeilen; kein Neulauf | Anzeige, kein Rechenkern-Input |
| Anzeige | `Portfolio-Suche, Portfoliosparte, Anzeigevergleich, Modellebene, Wiedergabe/Pause/Schieber` | Modellwelt, Portfolio und Laufansicht; GUI alpha.11 | Anzeige vorhandener Quelle/Ergebnisse; kein fortsetzbarer Kernzustand | Anzeige, kein Rechenkern-Input |
| Import/Export | `JSON-Datei; Export-VU und erwarteter Modelldigest` | Quelle laden und frisch gebunden exportieren; GUI / HTTP | Import <=16 MiB; Export frisch, If-Match erwarteter Digest; Einzel-VU Excel | Datei ist Eingabe; Digest technische Bindung |

## Bestehende Fachwerkzeuge vollständig auffinden

Das [maschinenlesbare fachliche Inventar](eingabeinventar.json) enthält die obenstehenden Gruppen. Das [UI-Syntaxinventar](eingabeinventar_ui.json) erfasst alle input-, select- und textarea-Deklarationen in den vorhandenen TSX-Komponenten, mit Datei, Zeile, Attributen und zugehöriger Label-Syntax. Wiederholte Felder aus Schleifen stehen als Quellsyntax darin; eine Deklaration ist deshalb keine feste Anzahl sichtbarer Felder. Dynamische Parametertabellen sind in der fachlichen Liste regelabhängig aufgelöst.

Die bisherigen Einzelwerkzeuge unter Modellwerkzeuge/Fallablage behalten eigene Quellenverträge: historische Metadaten und Laufadapter, Regelkandidaten, Bilanz, Leben, Kranken, Gesamtbilanz, Kapitalwirkung, ICT sowie Managementseminar. Deren Eingaben werden nicht still in das gemeinsame Marktexperiment übernommen. Ihre versionsabhängigen Fachverträge und Grenzen stehen in der [technischen Quellenübersicht](technical_reference.md) und den verlinkten Migrationsnotizen. Das Syntaxinventar ermöglicht, jedes bisherige Feld auch außerhalb des neuen Marktbereichs wiederzufinden.

## Was kein notwendiges Eingabefeld ist

Solvenzquote, SCR, MCR, ein frei wählbarer Pausenmonat zum Fortsetzen des Kerns, beliebig ergänzbare Unternehmen/Prozessbausteine und eine echte Deutschlandkarte aus den Mockups sind keine vorhandenen Eingabekanäle des gemeinsamen Marktes. Ihre Aufnahme würde einen eigenen Modellvertrag verlangen. Eine im Portfolio gewählte Vergleichsmenge ist ein Anzeigefilter; sie erzeugt keine neue Peer-Gruppe und ändert keine Strategie.

Die [Rechenkern-Grafiken](rechenkern.html) zeigen, welche Eingaben welchen Pfad erreichen. Die Validatoren in `python_port/ims/market/contract.py`, `reference.py` und `shock_contract.py` sind bei typabhängigen Randbedingungen die verbindliche ausführbare Quelle.
