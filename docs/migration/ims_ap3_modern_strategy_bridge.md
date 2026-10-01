# AP3 M4: Bestätigte moderne Strategie- und Abrechnungsbrücke

Der Auftraggeber bestätigt am 01.10.2026 die moderne Kopplung des Vorschlags
in `../plans/ims_ap3_strategy_gate.md`. Dies ist ein eigener Workshopvertrag.
Die historische Spartenidentität bleibt ungeklärt; PR154 und historische Runner
werden nicht still auf ausführbar umgestellt.

## Quellen, Einheiten und Reihenfolge

| Quelle | Verwendung im begrenzten modernen Adapter |
| --- | --- |
| IMS.E Vrvu01, Kapitel 3.3.1.1; `model.vu_rules.apply_vu_random_uniform_rule` | Preis- und Werbeziele aus vier vollständig enthaltenen Ziehungen. Periode 1 behält die expliziten Anfangswerte. Zwei moderne Kanäle werden ausdrücklich als Kfz/Sach deklariert; keine Behauptung historischer Identität der alten Positionen. |
| IMS.E Vrvn06, Kapitel 3.3.2.3; `model.vn_insurance_rules.apply_vn_best_info_insurance_rule` | Benannte VN-Gruppen erhalten denselben portierten Entscheidungsablauf: Anfangsvertrag in Periode 1; danach billigstes Angebot aktiver VU und Versicherung nur bei Schadenindikator <= Schwelle. Bei gleichem Preis entscheidet die aufsteigende VU-ID. |
| IMSDATA.C Pr/Wa/Rs/Vn/Sa/Sh | Preisziel, Werbung, Reserven, Versichertenanzahl und Schäden sind getrennte Größen. Preis ist keine gesamte Prämieneinnahme. |
| `accounting.non_life_model_balance` | Pro Gruppe Preis je gedeckter Exposition × Expositionsgewicht an die betrachtete VU buchen; Werbeziel dieser VU einmal pro Sparte als Aufwand. Schäden und Zahlungen bleiben exogene vollständige Periodenwerte, auch bei Wechsel. |
| `accounting.life_assumptions` / `life_period_chain` | Begrenzte VU-Anlageentscheidung als Satz auf tatsächliche Anfangsaktiva; vorhandene Garantien, Policen, Ablaufleistungen und exogene Todesfälle erhalten. |
| `accounting.health_period_sources` / `health_period_chain` | Begrenzte VU-Beitrags-/Neugeschäftsentscheidung sowie deklarierte VN-Abgänge; bestehende Abrechnung auf Anfangspolicen bleibt erhalten, Leistungen bleiben exogen. |
| `accounting.four_sector_balance` | Alle vier erzeugten Quellen frisch rechnen; Vorperioden-Carryover und A = L + E kontrollieren. Nur die betrachtete VU wird bilanziert; konkurrierende Angebote sind keine mitbilanzierten Unternehmen. |

Jede Periode führt in dieser Reihenfolge aus: vollständigen Kontext prüfen,
aktive inklusive Strategiefenster auflösen, VU-Angebote berechnen, VN-Auswahl
berechnen, Exposition/Prämie/Werbeaufwand buchen und Spartenbilanz rechnen.
Fenster überschneiden sich je Akteur/Gruppe/Sparte/Kanal nicht. Außerhalb
eines Fensters gilt der explizite Ausgangsplan; kein verdecktes Fortschreiben
des letzten Strategieparameters. Beide Varianten teilen denselben vollständigen
Anfang und dieselben exogenen Quellen; Änderungen beginnen erst ab Periode 6.

Alle modernen Gruppen, Gewichte, Anfangsverträge, Parameter, Fenster,
Zufallswerte und wirtschaftlichen Einheiten stehen im Eingabevertrag. Kein
versteckter RNG oder I/O im Adapter. Regelkerne rechnen wie bislang mit float;
Übergabe an die Modellwährung wird ausdrücklich auf vier Nachkommastellen
mit ROUND_HALF_EVEN gerundet. Jede Gruppenprämie wird ebenfalls auf vier
Nachkommastellen gebucht, danach werden die Buchungen addiert. Buchungsrechnung
erfolgt mit Decimal. Informationskosten sind im begrenzten VN-Schnitt explizit
null; keine ungebuchte Kostenwirkung wird vorgetäuscht. Historische Reserven-
Verzinsung aus dem VU-Kernel wird nicht doppelt in die neue Bilanz gebucht.

## Grenzen und Risiken

Nur Vrvu01 und Vrvn06 werden hier aus dem historischen Katalog verwendet;
andere Regeln sind für diese Brücke gesperrt. Lebens-/Kranken-Entscheidungen
sind ausdrücklich moderne begrenzte Quellenentscheidungen. Lebens-VN-Verhalten,
endogene Mortalität/Schadenwahrscheinlichkeit, gegenseitige Spartenfinanzierung,
vollständiger Versicherungsmarkt und regulatorische Kapitalgrößen sind nicht
gekoppelt. Die vorhandenen Workshop-Kapitalgrenzen bleiben Modellannahmen.

Schutz gegen stille Mengenumrechnung: Gruppenreferenzen, Anfangsanbieter,
positive Expositionen, vollständige Perioden/Draws, benannte Parameter und
Zeitgrenzen vor allen Ergebnissen validieren. Ein ungültiger später Wert
liefert keine Teilrechnung, keinen Digest und keine Datenbankänderung.

Die Abnahme umfasst eine handprüfbare Entscheidung → VN-Auswahl → gebuchte
Prämie → 100er-Bilanz-Kette, inklusive Grenzen, Anfang 1–5, kürzere Prefixe,
Wiederholbarkeit, ungültige späte Quellen und tatsächliche API/UI/Exports.

Die drei vollständigen portablen Fälle werden reproduzierbar mit
`.venv\Scripts\python.exe scripts\planning\build_seminar_cases.py` erzeugt.
Originalquellen werden vor der Normalisierung geprüft. Ganzzahlige float-
Werte werden für portable JSON-Darstellung als Ganzzahlen geschrieben und
anschließend frisch geprüft; monetäre Dezimalzeichenfolgen bleiben exakt.
Historische globale Digest-/Speicherverträge werden nicht geändert.
