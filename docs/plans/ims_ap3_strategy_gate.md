# AP3 M4 / PR187g: Entscheidung vor dem Strategieadapter

Stand 01.10.2026. Noch kein Adapter implementiert und keine Strategieabnahme.
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

Dies wäre eine neue, klar bezeichnete Workshop-Kopplung unter Wiederverwendung
belegter Regelkerne. Ihre Expositions-, Einheiten- und Abrechnungsannahmen wären
sichtbare und änderbare Eingaben. Sie würde keine historische Kfz-/Sach-
Identität behaupten und die ursprüngliche PR154-Ausführung nicht als historisch
gleichwertig ausgeben. Der Auftraggeber muss die fachliche Grundlage bestätigen,
bevor diese neuen Abrechnungsannahmen als ausführbare Strategiebrücke umgesetzt
werden; das ist die Entscheidung zu den fehlenden Modellgrößen, keine Merge-
oder Veröffentlichungserlaubnis.

Alternative: Nur eine historische Kopplung ausführen. Dafür werden belastbare
Belege zu Spartenidentität, VN-/VU-Bestand, Prämieneinheiten und Abrechnung
benötigt. Bis dahin bleiben PR187h–k und die vollständige Seminarabnahme offen.

## Fortsetzung

Die fachliche Antwort wird hier und im PR dokumentiert. Danach vollständigen
Quellen-/Zeitvertrag ausarbeiten, erst anschließend Adapter, UI, belegte
100er-Reaktionskette und M5/Installerabnahme umsetzen. Keine Anforderung wird
aus dem Manifest gestrichen und AP3 wird nicht vorzeitig auf done gesetzt.
