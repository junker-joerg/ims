# IMS-Vorstandsstrategie: begründeter Ausbauvorschlag

Version 1, 02.10.2026. **Vom Auftraggeber zum Merge freigegeben; angenommen mit
Übernahme von PR #292 nach main.** Umsetzung anschließend ausschließlich AP4
beauftragt; keine Umsetzung von AP5–AP14 und keine Release-Veröffentlichung.
Maschinenvertrag:
[ims_board_strategy_plan.json](ims_board_strategy_plan.json).

## Entscheidung und Ausgangsbasis

Empfehlung: den handprüfbaren gekoppelten DORA-Fall früh in AP10 liefern, sobald
AP7 seine Grundlage in main nachweist. Vollständige Kapitalanlagen, Rückversicherung
und KI sind dafür keine Voraussetzung. AP11 erweitert danach die Schaden-/RV-
Seite. AP13 kann nach AP11 ohne AP12 abgeschlossen werden. AP12 benötigt seinen
geprüften Lebens-/Liquiditätsvertrag. AP14 verbindet beide Zweige und die
eigenständige Seminarabnahme AP9. Empfohlene Folge: AP10 → AP11 → AP13 → AP12 → AP14;
AP12/AP13 haben untereinander keine Lieferabhängigkeit, die Reihenfolge ist
eine Priorität, keine neue Parallelisierungszusage.

Geprüfter main: `81146aa8657e2d507cc51c921207e80895f78340`, Merge #291. AP1–AP3
übernommen; AP4–AP9 als Planung angenommen, aber noch `planned`, ohne Umsetzung-
freigabe oder Abschlussbelege. Beim Start waren keine PRs offen und der primäre
Checkout sauber. Dieser Planungs-PR setzt kein Produktpaket in Arbeit.

Der angenommene [AP4–AP9-Plan](ims_explainable_market_2026_10.md) bleibt
unverändert, einschließlich Reihenfolge AP4 → AP5 → AP6 → AP7 → AP8 → AP9,
Top-40-Abgrenzung, Entscheidungstore und historischer Belege. AP10 kann nach AP7
eingeschoben werden, falls der Auftraggeber dies priorisiert; AP8/AP9 sind keine
Vorbedingung des kleinen Falls. Ihre Verpflichtungen werden dadurch nicht gestrichen.

## Evidenz vor Umfang

Die [versionierte Wettbewerbsprüfung](../research/ims_competition_review_2026_10.md)
enthält sieben Anbieter-/Forschungsgruppen, neun Dimensionen, fünf getrennte
Belegebenen sowie 22 Primärquellen mit Datum, Abruf und Fundstelle. Bestehende
Planspielmethoden und quantitative Versicherungssimulationen sind belegt;
praktische Zugänglichkeit, aktuelle Versionen und tiefe Markt-/ICT-Kopplungen
sind teilweise offen. Ein Alleinstellungsmerkmal ist nicht nachgewiesen.

Die Nutzenhypothese von IMS ist eine nachprüfbare Entscheidungskette und ein
wiederholbarer begrenzter Modellmarkt. Für ein Forschungs-/Seminarwerkzeug kann
das sinnvoll sein. Kommerzielle Differenzierung braucht einen tatsächlichen
Vergleich und Nutzerbedarf; unternehmensspezifische Entscheidungen zusätzlich
kalibrierte Daten und unabhängige Modellvalidierung. Planung, technische
Machbarkeit, Modellvalidierung, Benutzerabnahme und kommerzieller Nutzen erhalten
getrennte Evidenz; sie lassen sich nicht gegenseitig ersetzen.

Die [Bestandsläufe](../reports/ims_board_baseline_2026_10.md) rechnen sechs vorhandene
ICT-Eingaben und den AP3-Preisfall frisch mit Replay. Ausfall/Queue/Overlay und
Fokus-VU-Preisabrechnung funktionieren in ihren bisherigen Grenzen. Kein Lauf
belegt schon den vollständigen [Drei-VU-DORA-Fall](ims_dora_reference_case.md).

## Mehrnutzen, Lücken und Wiederverwendung

| Entscheidung | Heute ausreichend / wiederverwenden | Minimal fehlend | Abnahme des Mehrnutzens |
| --- | --- | --- | --- |
| Vorsorge rechtzeitig kaufen | ICT-Ereigniszeiten, Queue, Kostenallokation, AP7-Brücke künftig | Capability-Status, echter Ersatzpfad, Umsetzungsvorlauf | F0/F1/F2 bei gleichem Budget mit/ohne Schock, später Verfügbarkeit und gemeinsamem Unterlieferanten |
| Wechselgeschäft annehmen | Kartierte Angebots-/VN-Kerne; AP5-Mehr-VU-Vertrag künftig | Begrenzte Aufnahme, Risiko-/Kundenfortbestand, verzögertes Wissen, Rivalenregeln | Wachstum kann günstig, nachteilig oder wirkungslos sein; jede Differenz bis Buchung erklärt |
| Cash sichern | Vorhandene Bilanz-/Policenflüsse | Kleines Markt-Cash-Ledger, getrennte Reservierung/Zahlung | Forderung ist kein Cash, A=L+E, kein zweiter ICT-Abzug |
| Katastrophen/RV beurteilen | Forschung begründet Mechanismen; externe Daten später | Jahrgänge, limitierte Deckung und verzögerte Zahlung AP11 | Zweitereignis und Restdeckung handprüfbar |
| Anlagen-/Rückkaufkrise | Begrenzte Lebens-Policenrechnung | Bewertungs-/Rückkauf-/Liquiditätsvertrag AP12 | Positives Eigenkapital bei zahlungsunfähigem Cash-Zeitpunkt |
| Digitale gemeinsame Fehler | ICT-Typen; AP10-Maßnahmenvertrag; Risikomodellforschung | Versicherter Cyber-Kumul, Integritätszustände, gemeinsame Modellfehler AP13 | Eigener Verlust und Kundenschaden getrennt, keine Benchmark-Wahrscheinlichkeiten |
| Strategie robust auswählen | Reproduzierbare Eingaben/Digests | Matrix, Prüfpfade, Informationsspiel und Dossier AP14 | Empfehlung samt Gegenbeispielen, begrenztem Suchraum und gemessener Verständlichkeit |

Regulatorische Vollmodelle, umfassende Rückversicherungsoptimierung und externe
Kapitalmarkt-Nachbildung werden hier nicht nachgebaut. AP12 prüft einen
versionierten Daten-/Ergebnisadapter zu tatsächlich zugänglichen validierten
Kapitalmodellen; öffentliche Aon-Beschreibungen belegen noch keinen für IMS
verwendbaren API-Vertrag. Grenzen, Einheiten, Stichtag und Validierungsverantwortung
bleiben sichtbar. Fremde Forschung wird methodisch verglichen, nicht ungeprüft
als Code oder Kalibrierung übernommen. Keine Anbieteransprache in diesem Auftrag.

## Vorschläge zu AP4–AP9

| Paket | Angenommene Lieferung | Kandidat / Verbleib |
| --- | --- | --- |
| AP4 | Erklärbare Rollen/Einsteigerpfad | Keine zusätzliche fachliche Lieferung |
| AP5 | Mehr-VU-/Risiko-/Strategiegruppenvertrag | E05-01/02: Maßnahmenkosten, Vorlauf, Dauer und beobachtbarer Informationsstand ergänzen |
| AP6 | Belegte deutsche Top 40 | Keine zusätzliche fachliche Lieferung; Namen liefern keine tatsächlichen Strategien/Provider |
| AP7 | Vier Demos, Markt-/ICT-Brücke, transitive Ausfälle/Fallback-Abnahme | E07-01: gemeinsame Ereignishülle für Sequenzen; physische Zeit-/Buchungstore erhalten |
| AP8 | Verknüpfte Markt-/Familienansichten | E08-01: Fokus absolut und relativ zu Rivalen/Modellmarkt explizit nebeneinander |
| AP9 | Gemeinsame AP4–AP8-Seminarabnahme | E09-01: eigenständiger Abschluss; neue Vorstandsgesamt-Abnahme erst AP14 |

Ergänzungen stehen separat als `candidate_amendments.status=accepted` und wurden
am 02.10.2026 mit diesem Plan angenommen. Vor einer späteren AP5-/AP7-/AP8-
Umsetzung sind sie mit eigener Herkunft und eigenen Belegen in den konkreten
Paketumfang einzuarbeiten. Ein allein aus dem alten AP4–AP9-Manifest erzeugter
Auftrag übernimmt sie noch nicht. Ist AP5/AP7/AP8 schon in
Arbeit/fertig oder bleibt eine Ergänzung unangenommen, nimmt AP10 nur den für
seinen Referenzfall fehlenden Umfang auf. Alte Abschlussbelege bleiben unverändert.

## AP10–AP14: Liefervertrag

Jedes Produktpaket ist ein eigener Branch/Draft-PR mit Implementierung, API,
bedienbarer Oberfläche, Tests, Anleitung und höher versioniertem Windows-
Installer. Zwischenmeilensteine bleiben im selben PR. Der Planungs-PR liefert
Dokumente und Generator, keinen neuen Produkt-Installer.

**AP10 – eigenes Haus und minimaler DORA-Fall.** Profileingabe mit expliziter
Gruppe/Gesellschaft, Kunden-/Risikomix, Startbilanz und Kapazitäts-/Entscheidungs-
grenzen. Fünf einfache Rivalenregeltypen, keine vorgetäuschten LLM-Agenten.
Erster Lieferfall sind sechs Stunden, drei synthetische Häuser und zwölf
kontrollierte Varianten. Gleiches Vorsorgebudget, reale Unabhängigkeit des Q-
Pfads, dokumentiert/verfügbar/getestet, kleine Cash-Buchung, no-shock-Kosten und
Umsteuersignale. Keine vollständige Kapitalanlage/RV nötig. Meilensteine:
Vertrag/Handfall → gekoppelte Buchung/Replay → drei Rivalenmodi/Gegenbeispiele →
API/UI/Anleitung/Nutzenmessung/Installer. Tor: Mengen-/Risiko-/Zeit-/Cashvertrag
und Informationszugang freigeben; AP7 in main belegt. Abnahme REF-01–12.

**AP11 – Jahrgänge, Schadeninflation und begrenzte RV.** Aufwand/Reserve/Zahlung,
Retention/Limit/Restdeckung, Erneuerung und Maßnahmen. Erst Jahrgangs-Handfall,
dann zwei Katastrophen mit verspäteter RV-Zahlung, danach Erneuerung/UI/Installer.
Tor: begrenzten Zahlungs-/Deckungsvertrag nach AP10 prüfen. Keine volle
Rückversicherungsplattform. Forderungen dürfen keine Liquidität vortäuschen.

**AP12 – Anlagen, Liquidität und Vertrauen.** Vereinfachte Anlageklassen;
Bewertung/Ertrag/Verkauf getrennt, produktspezifischer Lebens-Rückkaufvertrag,
verfügbare Finanzierung und CFO/CRO-Sichten. Optional gemeinsame Verkäufe mit
expliziter externer Marktliquidität. Meilensteine: Anlage-/Cash-Handfall →
Lebensvertrag/Tor → Vertrauens-/Verkaufskanal → Produktauslieferung. Voraussetzungen
AP11 und geprüfte Auszahlung; vorhandene exogene Todes-/Ablaufleistungen ersetzen
den Rückkaufvertrag nicht. Kein SCR-Etikett ohne passende Methodik.

**AP13 – digitale/cyber-/Modell-Kumule.** AP10-Provider/Capability-Vertrag
wiederverwenden; Ransomware/Integrität, eigene vs versicherte Cyberverluste,
gemeinsame Modellfehler und spätere Tarifkorrektur. Meilensteine: Trennungstor →
Integrität/Cyber-Kumul → Modellhomogenität/Kontrollen/Benchmarkregister → Produkt.
Voraussetzungen AP10 und AP11 wegen versicherter Schäden/RV; AP12 ist nicht nötig.
Gleiches Budget und echte Fallback-Tests bleiben Regressionen. Fehlende Benchmark-
PDF ist G-BENCH: Quelle, Frage, Seite, Bezugsgruppe und Version bleiben bis zur
Prüfung offen; keine Prozentwerte übernommen. Register kann mit offener Quelle
geliefert werden, ein benchmarkgestützter Fall braucht zuvor Datenprüfung.

**AP14 – robuste Strategien und Vorstandsdossier.** Faire Strategie×Schock×Rivalen-
Matrix, Sensitivitäten, mehrere stabile Zufallspfade, Grenzverletzungen, Vorlauf
und verzögertes Handeln. Informationssnapshots, Frühindikatoren/Umschaltregeln
und von der Auswahl getrennte Prüfszenarien. Meilensteine: Experimentvertrag →
Suchraum/Prüfpfade → Informationsspiel/Dossier → Benutzer-/Gesamtabnahme/Installer.
Voraussetzungen AP9, AP12, AP13. Keine realen Szenariowahrscheinlichkeiten oder
Kipppunktbehauptungen außerhalb des untersuchten Parameterraums.

## Stabile Anforderungen und Änderungen

Das Manifest ordnet **65 eindeutige IDs** zu: sieben AP10-, sieben AP11-, acht
AP12-, acht AP13-, acht AP14-Anforderungen; sieben E-Ergänzungs-/Erhaltungs-IDs;
zwölf REF-, fünf RES- und drei DEF-IDs. Jede hat ursprüngliche/neue Zuordnung,
Disposition, Begründung und Abnahmeauswirkung. Die folgenden Änderungen sind
entscheidungsrelevant; alle übrigen Kandidaten verbleiben im genannten Paket.

| Alte Zuordnung | Neue Zuordnung | Grund / Abnahmeauswirkung |
| --- | --- | --- |
| AP10 nach AP9 | AP10 nach AP7 | Der kleine Fall benötigt die Brücke; AP9 bleibt eigenständig |
| AP13-R01 Provider/Ransomware/Integrität | AP7/AP10 Providerbasis, AP13 weitere Ereignisse | Bestehende Typen und AP7-Brücke wiederverwenden; keine doppelte Neuentwicklung |
| AP13-R04/05/07/08 | Minimalvertrag AP10, Ausbaugrenzen AP13 | Budget, getestete Fähigkeit, Fallback und einmalige Buchung müssen vor dem ersten DORA-Fall prüfbar sein |
| AP13 nach AP12 | AP13 nach AP10/AP11 | Versicherte Cyber-Verluste brauchen Schaden/RV, keine vollständige Anlagekrise |
| AP14 nach AP13 | AP14 nach AP9/AP12/AP13 | Beide fachlichen Zweige und Seminarabschluss ausdrücklich erforderlich |
| Demografie/Langlebigkeit/Morbidität | DEF-01/02/03, `deferred` | Eigener Biometrie-/Bestandsvertrag und Datenprüfung nötig; keine heutige Abnahme |

Historische AP1–AP3-Anforderungs-IDs und angenommene R01–R13 werden nicht ersetzt.
Der Generator übernimmt deren Manifeste gesondert und prüft den gemeinsamen
Abhängigkeitsgraphen. Daten, Modellkanäle und Altquellen werden je Produktpaket
kartiert; neue Semantik erhält einen neuen Vertrag, bestehende Resultate bleiben
Regressionen. Reale Firmennamen begründen keine tatsächliche Strategie oder
Providerabhängigkeit.

## Status und Arbeitsauftrag

Vier getrennte Nachweise: Planannahme, ausdrückliche Paket-Umsetzungsfreigabe,
technische Fertigstellung mit Abschlussbelegen, Übernahme in main. Ein Vorschau-
Auftrag ist sichtbar unfreigegeben. Angenommene Planung allein erzeugt keinen
freigegebenen Auftrag. Auch technisch `done` im Branch ist keine erledigte
Abhängigkeit für Folgepakete; dafür muss der Paketstatus mit Belegen in main sein.

Ausführbare Befehle und Freigabeformat stehen in
[Generator-Anleitung](ims_work_order_generator.md). Die Standardaufrufe für AP1–AP3
bleiben kompatibel. Folgepläne werden mit `--plan` gewählt und standardmäßig
als Vorschau behandelt. Eine AP10-Vorschau ist möglich; ein freigegebener AP10-
Auftrag scheitert weiterhin an offenem AP7 und fehlendem Umsetzungsauftrag.

Der Auftraggeber hat am 02.10.2026 den Planungsmerge und anschließend AP4
beauftragt. AP4 benötigt die Benchmark-PDF nicht: Oberfläche, Rollenwege und
Anleitung verwenden vorhandene AP3-Fälle. Nach Übernahme von #292 AP4 im eigenen
Paket-PR mit API/UI/Tests/Anleitung/Installer umsetzen. Fachliche Tore späterer
Pakete bleiben offen. Der Planungsmerge allein autorisiert keine Folgeumsetzung;
die gesonderte AP4-Freigabe ist im Handoff und lokalen Auftragsbeleg dokumentiert.
