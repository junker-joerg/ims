# AP8: gemeinsames Marktexperiment und moderne Benutzerführung

04.10.2026. Konkreter Auftrag des Anwenders dieser Sitzung: „Überarbeite die
Gesamte Benutzerführung“ mit endogenen Vorstandsstrategien, exogenen
Schocks/Regulierungen/Trends und moderner Gestaltung anhand vier bereitgestellter
Cockpit-Referenzbilder. Umsetzung im bestehenden Paket-PR #297. Keine AP9-
Umsetzung, kein Merge und keine öffentliche Veröffentlichung. Neue Produktfassung
alpha.10; alpha.8 und alpha.9 behalten ihre historischen Nachweise.

## Fachlicher Ablauf

Ein gemeinsamer Zustand enthält Marktquelle, Anbieter-/Nachfragestrategien,
Umweltereignisse und das frisch berechnete Ergebnis. Vier Schritte: Markt wählen,
Vorstand entscheiden lassen, Umwelt beschreiben, Wirkung auswerten. Ansichtswechsel
erhalten Eingaben und Ergebnis. Jede Quellenänderung entwertet das Ergebnis und
seine Exportberechtigung. Vorlagen werden ausdrücklich als eigene Sitzung übernommen.

Anbieterparameter und ausführbare Gegenmaßnahmen sind endogen. Nachfrageseitige
Entscheidungsparameter gehören zum erklärten VN-Verhalten. Ereignisse und
Risikoannahmen sind exogen. Beides wirkt über bestehende Regel-/Prozesskanäle
auf Verträge, Marktposition und Buchungen. Im Vergleich ohne/mit Schock gelten
dieselben Vorstandsentscheidungen auf beiden Seiten. Im Vergleich mit/ohne
Gegenmaßnahme haben beide Seiten denselben Schock. Sichtbare Bezeichnungen
verhindern die Vermischung dieser Vergleichsachsen.

## Umsetzung und Ursprung

| Herkunft | Vorhandene Semantik | Oberfläche |
| --- | --- | --- |
| IMSDATA.C 312–335, classBAV | VU-/VN-Kontext und Marktinformation | Gemeinsamer Markt, klare Rollen und Modellumfang |
| IMS.E 3533–3591, Vrvn06 | Nachfrage wählt das Minimum erreichbarer Prämien unter Versicherungsschwelle | VN-Parameter getrennt von Vorstand und Umwelt |
| AP5 contract/runner | Familien, Parameter, Maßnahmen mit Entscheidung/Vorlauf/Kosten | Vorstandsbereich, wirksame Parameterfenster |
| AP7 shock_contract/shock_plan/process | Ereignisse, 24 Prozessstunden, Ressourcen, wirksame Verträge und Kosten | Umweltbereich und erklärbares ICT-Netz |
| AP8 explorer | Reine Projektion, sechs Ansichten, unveränderter Modelldigest | Cockpit, Kennzahlen, Verlauf und nachvollziehbare Wirkung |

Keine Änderungen an Regelkernen, Scheduling, RNG, Garantien oder Finanzbuchungen.
Keine frei erfundenen SCR-/NPS-/Regional-Kennzahlen aus den Mockups. Bestehende
BaFin-Referenzbindung bleibt erhalten; ihre Transformation wird im Quellenwerkzeug
bearbeitet. Ein hypothetisches Regulierungsszenario ist kein Complianceurteil.
Neue Trend- oder Regulierungskanäle werden nicht durch grafische Regler erfunden.

## Gestaltung und Prüfung

Einheitliches Design mit dunkler Navigation, klarer Typografie, türkisen
Strategie- und bernsteinfarbenen Umweltmarkierungen, großzügigem Cockpit und
SVG-Graph aus tatsächlichen Abhängigkeiten. Hell/Dunkel, Tastatur und kleine
Bildschirme gehören zur Lieferung. Die vorhandenen Fachwerkzeuge bleiben erreichbar.

Nachweise: echter Browserablauf mit Quellenübernahme, getrennten Eingaben,
Ergebnisentwertung und frischer Rechnung/Export; zugängliche Graphalternative;
sechs Ansichten mit gemeinsamen Filtern; erhaltene vier AP7-Ergebnisdigests;
vollständige Produktprüfungen, neue Offline-Anleitung und Installer. Aktuelle
alpha.9-CI-Fehler werden anhand ihrer tatsächlichen Berichte behoben. Anwenderabnahme
und Merge bleiben offen.

## Technischer Abschluss

04.10.2026: Vier vollständige Produktchecks am Kommitt `11384cf69f14f52d3c0f0ae72537986a94484e57`
bestanden. [Produktprüfung](../reports/ims_ap8_cockpit_produktpruefung.md) und
[Verifikation](../reports/ims_ap8_cockpit_verification.json) belegen den gelieferten
Installer und beide Browserumgebungen. Anwenderabnahme/Merge bleiben offen.
