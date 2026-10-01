# AP3 M4 / PR187g: Entscheidung vor dem Strategieadapter

Stand 01.10.2026. Der Auftraggeber hat den Vorschlag der modernen Kopplung
ausdrücklich bestätigt: „Ich bestätige den Vorschlag der modernen Kopplung.
Fahre fort.“ Das Entscheidungstor ist damit geschlossen. Die Bestätigung
betrifft die deklarierte Modellgrundlage; Implementierung und Abnahme folgen.
M1–M3 können unabhängig davon technisch geprüft werden. PR187h–k und die
darauf aufbauende vollständige Seminarabnahme bleiben im AP3-Umfang.

## Quellenbefund

- `IMSDATA.C:199–226` trennt Prämienziel `Pr`, Werbung `Wa`, Reserven `Rs`,
  Versichertenzahl `Vn`, Schadenanzahl `Sa` und Schadensumme `Sh` in zwei
  anonymen Positionen. Die Symbole LV/KV allein belegen keine Kfz-/Sach-Zuordnung.
- `IMS.E:1083–1169`, `Vrvu01`, und
  `ims.model.vu_rules.apply_vu_random_uniform_rule` berechnen Prämienziele und
  Werbung aus Parametern und vier expliziten Zufallswerten. Das Ergebnis ist
  keine automatisch gebuchte Gesamtprämieneinnahme.
- `ims.strategies.sector_strategy_plan` (PR154) prüft benannte Nichtleben-
  Entwürfe für Katalogstrategien, erklärt aber ausdrücklich
  `legacy_sector_binding_enabled = False`, `execution_enabled = False`.
- `ims.model.sector_taxonomy.LEGACY_SECTOR_POSITIONS` enthält keine belegte
  Zuordnung der beiden Positionen zu den benannten modernen Sparten.
- `non_life_model_balance` verlangt Gesamtflüsse in Modellwährung, besitzt
  aber keinen individuellen VN-Bestand oder Preis-/Nachfragevertrag.
  Lebens-/Krankenketten haben eigene Policen-/Bestands- und Annahmeverträge.

Ein Strategieergebnis direkt als `premium_income` zu buchen würde Preis und
Gesamtfluss still gleichsetzen. Einfügen von VN-Entscheidungen in die moderne
Bilanz ohne deklarierten Bestand, Einheiten und Abrechnung wäre eine neue
fachliche Regel. Die aktuelle additive Vier-Sparten-Variante ist deshalb als
exogener Eingabevergleich beschriftet, nicht als ausgeführte PR154-Strategie.

## Konkreter Vorschlag: expliziter moderner Workshopadapter

Für den begrenzten Seminarpfad wird ein eigener versionierter Vertrag ergänzt:

| Gegenstand | Ausdrückliche Erklärung / Prüfung |
| --- | --- |
| Population | Moderne benannte VU-/VN-Gruppen, IDs und Expositionsgewichte; keine Behauptung, dies sei der historische Vdefmd6-Bestand. |
| Einheit | Preis je gedeckter Exposition und Periode; Gesamtprämie = gebuchter Preis × tatsächlich gedeckte Expositionen. Werbung als eigener deklarierter Aufwand. |
| Strategiequelle | Nur benannte, quellenkartierte PR154-Regelkerne; Parameter und bereits enthaltene Zufallswerte. Kein Ersatz historischer Vektorpositionen durch Kfz/Sach. |
| Fenster | Inklusiver Beginn/Schluss, gleicher Anfang 1–5, Aktion vor der periodischen Abrechnung; keine rückwirkende Änderung bestehender Garantien. |
| Schaden/Leistung | Explizit exogen; Bestands-/Abrechnungspolitik und vorhandene Verpflichtungen getrennt. Kein erfundener Rückschluss aus Versicherungsauswahl auf Schadenwahrscheinlichkeit. |
| Leben/Kranken | Begrenzte Anlage-/Neugeschäfts-/Beitragsentscheidungen an vorhandene Quellen; Mortalität und Leistungsannahmen weiter ausdrücklich exogen. |
| Rechnung | Frische Baseline/Variante, nachvollziehbare Entscheidung → Exposition/Fluss → periodische Modellbilanz; atomare Grenzen und unveränderte alte Runner. |
| Nicht gekoppelt | Vollständiger All-Sparten-Markt, historische Spartenidentität, regulatorische Kapitalrechnung und alle nicht belegten Strategien bleiben ausdrücklich offen. |

Der bestätigte Vorschlag wird als neue, klar bezeichnete Workshop-Kopplung
unter Wiederverwendung belegter Regelkerne umgesetzt. Expositions-, Einheiten-
und Abrechnungsannahmen sind sichtbare und änderbare Eingaben. Eine historische
Kfz-/Sach-Identität oder Gleichwertigkeit der ursprünglichen PR154-Ausführung
wird nicht behauptet. Die Bestätigung der Modellgrundlage ist keine Merge-
oder Veröffentlichungserlaubnis.

## Fortsetzung

Quellen-/Zeitvertrag und konservatives C-/Python-Mapping sind in
`../migration/ims_ap3_modern_strategy_bridge.md` festgehalten. Der Adapter
`ims.strategies.modern_bridge` verbindet quellenkartierte Preis-/VN-Regeln
mit ausdrücklich modernen Mengen/Flüssen; begrenzte Lebens-/Kranken-
Entscheidungen verwenden vorhandene Quellenmodi. Handprüfbarer Preisfall:
3,60 statt 3,00 führt bei konkurrierendem Angebot 3,20 zu eigener gedeckter
Exposition null, 300 weniger Prämie und 2 Werbung je Periode; über P6–100
28.690 weniger Modell-Eigenkapital. M5 verwendet vollständige portable
Quellen und frische Demo-Prüfungen. Gesamtabnahme und konkrete Installer-
Nachweise werden im AP3-Bericht ergänzt; alle 23 IDs bleiben erhalten.
