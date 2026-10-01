# AP3 Abschlussbericht – Fachliche Integration

Stand: 01.10.2026. **M1–M5 sind im bestätigten modernen Workshopumfang umgesetzt und technisch abgenommen.** AP3 bildet einen Integrations-PR #290. Merge und öffentliche Veröffentlichung sind noch nicht freigegeben. Dieser Bericht ersetzt den früheren Zwischenbericht mit dem inzwischen beantworteten M4-Entscheidungstor.

Nachtrag zum Versionsauftrag vom 01.10.: Der aktuelle AP3-Stand erhält die eindeutige
Releasenummer **2.0.0-alpha.3**, Windows-Dateiversion **2.0.0.3** und den Installer
`IMS-Setup-2.0.0-alpha.3-win-x64.exe`. Auf dem Startbildschirm steht die Nummer
unten links; abweichende Oberflächen-/Anwendungsversionen werden dort erklärt.
Die [verbindliche Versionsregel](../plans/ims_release_numbering.md) gilt auch für
künftige Lieferungen. 45 gezielte Backend-/Versionsprüfungen und sieben echte
Browserprüfungen bestanden lokal, einschließlich drei Bildschirmgrößen, beiden
Farbmodi sowie API-Ausfall und Versionskonflikt. Der tatsächliche Installer und
die vollständigen Prüfläufe des aktuellen Heads sind im [selben PR #290](https://github.com/junker-joerg/ims/pull/290)
zugeordnet. Die unten dokumentierten alpha.1-Dateien, Hashes und Abnahmen bleiben
Belege ihres damaligen Produktstands; sie identifizieren nicht alpha.3.

## Auftrag und überprüfte Grundlage

Der Auftraggeber bestätigte den erfolgreichen AP2-Test auf einem anderen Rechner und verlangte vor AP3 den ausführlichen Bericht in Evernote. Diese Reihenfolge wurde eingehalten. AP2-PR #289 wurde am 01.10.2026 um 09:48:11 Uhr Berlin nach grünen Checks übernommen; tatsächliches main ist `2e70b8f814870807a7c8c34d8fc384f8f6a5bb3c`. Der [AP2-Bericht in Evernote](https://www.evernote.com/client/web#/notebook/ade45e59-57bd-4ada-abaf-dab970f2e126/note/18c2dc8d-2534-6cd5-20ae-1c862506946c) wurde vor AP3 gespeichert und nach Neuladen vollständig geprüft.

Die wissenschaftlich erforderliche neue Abrechnungsgrundlage wurde zunächst als konkreter Vorschlag dokumentiert. Der Auftraggeber bestätigte danach ausdrücklich: „Ich bestätige den Vorschlag der modernen Kopplung. Fahre fort.“ Das schließt das M4-Entscheidungstor für diesen begrenzten modernen Vertrag. Es belegt keine historische Identität der anonymen Schadenpositionen mit Kfz/Sach.

Branch: `codex/ims-management-integration`; [PR #290](https://github.com/junker-joerg/ims/pull/290). Geprüfter vollständiger Produkthead: `589689d63887058f5eb703e796d25d531dbfc9f7`. M4/M5 wurden in `9d53a04cd2da149ef515b2158b541ac35585754a` aufgenommen; 589689d ergänzt den vollständigen Ressourcenweg des älteren portablen Prüfpakets. Die nachfolgenden Bericht-/Manifeständerungen ändern die fachliche Rechnung nicht. Ready wird erst nach grünen Checks des aktuellen Dokumentations-Heads gesetzt.

## Nutzbarer Seminarpfad

Im Managementseminar können Anwender drei vollständige 100-Perioden-Fälle öffnen, einen VU-/VN-Kanal und eine Gruppe auswählen, Parameter sowie inklusive Aktivierungsfenster ändern und beide Seiten frisch berechnen. Die Perioden 1–5 bleiben gemeinsamer Anfang; Änderungen beginnen ab Periode 6. Eingabevergleich, Entscheidungskette, vier Sparten und Gesamtbilanz zeigen denselben geprüften Inhalt. CSV, JSON und Excel werden tatsächlich heruntergeladen und enthalten die vollständigen Quellen.

Die gewählte Bilanzseite lässt sich mit ihrem Quellen-Digest in die Modellkapitalansicht übergeben. Explizit bereitgestellte Begleitquellen öffnen die ICT-Wirkungskette und den geführten historischen 100er-Pfad. Ein unveränderliches Quellenbündel enthält alle drei Wege und deklarierte Kapitalannahmen. Sein Import wird frisch geprüft und zunächst als schreibfreie Demo geöffnet; Änderung und Speicherung erfordern die sichtbaren jeweiligen Aktionen.

Die Anleitung `docs/handbook/seminar_ap3.md` und das installierte Offline-HTML enthalten Bedienung, fachliche Deutung, einen 90-Minuten-Moderationsvorschlag und fünf tatsächliche aktuelle Seminarbilder. Die 90 Minuten sind eine Moderationsplanung, keine gemessene Nutzungsdauer. Ältere PR178a-Unterlagen bleiben als historische Modellhilfe gekennzeichnet.

## Umsetzung, Quellen und Migrationsannahmen

| Meilenstein | Ergebnis und Herkunft | Ausdrücklicher Umfang |
| --- | --- | --- |
| M1 | `ims/ict` erklärt gerichtete Services, Assets, Anbieter, Ereignisse, Zeitmaß, Kapazität, ursprünglichen Rückstand, Nacharbeit und Erholung. Prävention, Fallback, Wiederanlauf und Kosten wirken nachvollziehbar auf einen deklarierten Bilanzoverlay. ESS.C Zeitablauf und IMSDATA.C Perioden-/Schockstrukturen wurden kartiert. | Moderne ICT-Workshop-Erweiterung; keine portierte historische DORA-Funktion und keine automatische DORA-Konformitätsprüfung. |
| M2 | `api/guided_period_chain.py` baut aus Seed 1300 und 100 vollständigen Kontexten frisch 107 Kandidaten. Bestehende Profile/Kettenprüfer und der PR151-Runner werden genutzt. SQLite-Speicherung ist atomar, idempotent und unveränderlich; echte 2er-/5er-Prefixläufe und ein 100er-Lauf mit ZIP sind bedienbar. | Der synthetische historische Weg hat einen VU, einen VN und zwei anonyme Schadenpositionen. Der gemeinsame Prefixvertrag gilt ausdrücklich für Laufindex 0. |
| M3 | `accounting/management_case.py` verbindet ausdrücklich benannte vollständige Quellen der vorhandenen Nichtleben-, Lebens-, Kranken- und Vier-Sparten-Modelle. Beide Seiten werden frisch gerechnet; Carryover, A = L + E, Prefixe und digestgleiche Exporte sind geprüft. | Additive Modellbilanzen mit erklärten exogenen Quellen. Keine erfundene gemeinsame historische Szenario-ID oder endogene Marktgleichgewichtsrechnung. |
| M4 | `strategies/modern_bridge.py` deklariert Gruppen, gedeckte Expositionen, Einheiten, Ziehungen, Parameter und Zeitfenster. Kartierte Vrvu01-/Vrvn06-Kerne erzeugen Angebote und VN-Auswahl. Preis × gedeckte Exposition wird gebucht; Werbung einmal je betrachteter VU/Sparte als separater Aufwand. Begrenzte Lebens-/Krankenentscheidungen verändern tatsächliche vorhandene Quellenflüsse. | Zwei ausdrücklich moderne Nichtlebenkanäle; nur VU 1 wird bilanziert, Rivalen liefern Angebote. Die Lebens-/Krankenkanäle sind moderne Quellenentscheidungen. |
| M5 | `seminar_bundle.py`, `seminar_capital.py`, `modern_presets.py`, Seminar-API und `SeminarWorkbench.tsx` liefern drei komplette Fälle, portable Import-/Demoprüfung, Modellkapitalannahmen, Begleitquellen, aktuelle Anleitung und den installierten vollständigen Seminarpfad. | Die drei Rechenwege bleiben getrennt erkennbar. Das Bündel behauptet keine automatische gegenseitige Kopplung von ICT, altem Marktkern und moderner Bilanz. |

Die relevanten historischen Stellen sind IMS.E Vrvu01, Kapitel 3.3.1.1 (Zeilen 1083–1169), Vrvn06, Kapitel 3.3.2.3 (3517–3786), sowie IMSDATA.C Pr/Wa/Rs/Vn/Sa/Sh (199–226). Historische Preis-/Werbeziele sind keine gesamten Prämieneinnahmen. In Periode 1 bleiben Anfangsangebote und Anfangsverträge erhalten. Später wirkt die vollständig enthaltene Folge von vier Ziehungen je VU; der VN wählt das billigste Angebot und versichert bei Schadenindikator <= Schwelle. Gleiche Angebote werden nach aufsteigender VU-ID aufgelöst.

Der neue Vertrag heißt `ims.modern-strategy-input.v1`, das Resultat `ims.modern-strategy-result.v1`. Entscheidungen erfolgen vor der Periodenabrechnung, Strategiefenster sind inklusive. Ursprüngliche Pläne gelten außerhalb eines Fensters; kein verdecktes Fortschreiben letzter Parameter. Regelkerne erhalten ihre bisherige float-Semantik; beim Übergang zur Modellwährung wird explizit auf vier Nachkommastellen mit ROUND_HALF_EVEN gerundet. Einzelne Gruppenbuchungen werden gerundet und dann mit Decimal addiert. Informationskosten sind ausdrücklich null; alte Reservenverzinsung wird nicht doppelt gebucht.

Leben verzinst tatsächliche Anfangsaktiva. Policen, Garantien, Ablaufleistungen und exogene Todesfälle bleiben erhalten. Kranken rechnet Beiträge auf Anfangspolicen; Neugeschäft/Abgänge verändern den nächsten Bestand. Schäden und Leistungen bleiben vollständig erklärte exogene Quellen, auch wenn ein VN den Anbieter wechselt. Kein versteckter RNG und kein I/O im reinen Adapter.

Ausführliche Mappings: `docs/migration/ims_ap3_ict_workshop.md`, `ims_ap3_guided_period_chain.md`, `ims_ap3_management_case.md`, `ims_ap3_modern_strategy_bridge.md`. Das bestätigte Tor steht in `docs/plans/ims_ap3_strategy_gate.md`.

## Handprüfbare Reaktionen und vollständige Fälle

| Fall | Baseline-Eigenkapital P100 | Variante-Eigenkapital P100 | Belegte Deutung |
| --- | ---: | ---: | --- |
| Preis / Werbung | 116.015,7633 | 87.325,7633 | Ab P6 eigenes Kfz-Angebot 3,6 statt 3,0; Rivalenangebot 3,2. Alle 100 gedeckten Kfz-Expositionen wechseln zum Rivalen: eigene Prämie fällt von 300 auf 0, eigener Werbeaufwand steigt um 2. Differenz 302 je Periode × 95 Perioden = 28.690. |
| Inflation | 107.465,7633 | 118.865,7633 | Schäden/Leistungen steigen exogen auf beiden Seiten. Die Variante erzielt in den beiden Nichtlebenkanälen und Kranken zusammen 120 zusätzliche Einnahmen je Periode ab P6; 120 × 95 = 11.400. |
| Lebensanlage / Kapitaldruck | 116.015,7633 | 117.045,6230 | Der Lebenssatz steigt ab P6 von 0,0005 auf 0,001 auf tatsächliche Anfangsaktiva. Carryover und Zinswirkung werden periodisch verfolgt. Separat deklarierter Kapitalstress 550 verletzt die Verlustgrenze 200. |

Preisfall-Kapitalannahmen: Assetverlust 100 plus operationeller Modellverlust 50 = Netto-Stress 150; deklarierte Verlustgrenze 200 und Mindest-Eigenmittel-Proxy 1.000 werden eingehalten. Variante: verbleibender Eigenmittel-Proxy 87.175,7633. Im Anlagefall ergibt der getrennte Stress 550 einen verbleibenden Proxy 116.495,6230; die Verlustgrenze ist verletzt, die Mindesthöhe weiterhin erfüllt. Diese Annahmen sind unkalibriert, fest datiert und vollständig im Bündel enthalten. Sie verändern nicht nachträglich die gebuchte Bilanz. Eigene geänderte Kapitalparameter werden getrennt exportiert; das Seminarbündel enthält seine kanonischen Vorlagenannahmen.

Alle drei Dateien unter `seminar_cases/` enthalten 100 vollständige moderne, ICT- und historische Kontexte sowie alle Profil-/Zufallswerte. Erzeugung: `.venv\Scripts\python.exe scripts\planning\build_seminar_cases.py`. Bündel- und Quellen-Digests werden beim Import neu geprüft. Das Quellenbündel ist kein Link auf versteckte lokale Datenbanken.

## Abnahme aller 23 Anforderungs-IDs

| ID | Konkreter Abnahmebeleg |
| --- | --- |
| PR179 | Gerichtete Service-/Asset-/Anbieterbeziehungen, Eigentümer und vollständiger Quellenvertrag; ICT-Kern/API/UI. |
| PR180 | Ereignistypen und ihre Wirkungen getrennt erklärt und negativ geprüft. |
| PR181 | Explizite Stunden-/Periodenübersetzung; keine erfundene historische Stundenlänge. |
| PR182 | Nachfrage, Kapazität, ursprünglicher Rückstand, Nacharbeit und Erholung über Perioden; deterministische Tests. |
| PR183 | Gemeinsame Anbieter-/Ausfallwirkung ohne doppelte Verlustzählung. |
| PR184 | Inklusive Präventions-/Fallback-/Wiederanlauffenster und gebuchte Kosten. |
| PR185 | Deklarierter Bilanzoverlay, Eigenmittel-Proxy und Workshop-Grenzen; regulatorische Größen gesperrt. |
| PR186 | ICT-Zeitlinie, vollständiges Quellen-Dossier und echte CSV-/JSON-/Excel-Ausgabe. |
| PR187 | Geführte 100er-Eingabe mit geprüftem Expertenweg, Fehler- und Freigabezuständen. |
| PR187a | Alle 100 Kontexte/99 Übergänge und deterministischer Seedkanal; fehlerhafter später Kontext sperrt vollständig. |
| PR187b | 107 frisch gebaute Kandidaten, atomare idempotente unveränderliche Speicherung. |
| PR187c | Tatsächliche 2er-/5er-Prefixläufe und PR151-100er-Worker mit ZIP im installierten Browserpfad. |
| PR187d | Erklärter gemeinsamer vollständiger Vier-Sparten-Quellenvertrag mit Inhaltsbindungen. |
| PR187e | Frische Rechnung beider Seiten bis P100, Carryover, Bilanzinvarianten und echte kürzere Prefixe. |
| PR187f | Vier Sparten plus Gesamtbilanz in UI und gleichen CSV-/JSON-/Excel-Ergebnissen. |
| PR187g | Bestätigter moderner Gruppen-/Einheiten-/Zeitvertrag und kartierte Regelquellen; historische Spartenidentität offen benannt. |
| PR187h | Zwei begrenzte moderne Nichtlebenkanäle mit Vrvu01/Vrvn06 und expliziter Preis-/Mengenabrechnung. |
| PR187i | Lebens-Anfangsaktiva und Kranken-Anfangspolicen/Neugeschäft/Abgänge; vorhandene Garantien und exogene Flüsse erhalten. |
| PR187j | Regel-/Gruppen-/Parameter-/Fenstereingabe bei 1440/390 Pixeln, Hell/Dunkel; alte Resultate/Freigaben werden invalidiert. |
| PR187k | Handprüfbare Entscheidung → VN-Wechsel → Prämie/Werbung → P100-Bilanz: 302 × 95. |
| PR188 | Drei kuratierte vollständige Fälle mit Preis-/Inflations-/Anlagewirkung, tatsächlichem Kapitaldruck 550 und ICT-Begleitquelle. |
| PR189 | Vollständige portable Quellenbündel, frische schreibfreie Demo, fünf aktuelle Bilder und Offline-Moderationsanleitung. |
| PR190 | Neu gebauter tatsächlicher Installer: kompletter Seminarpfad samt Bilanz, Kapital, ICT, 100er-Lauf, Export; vollständiger Release-Gate bestanden. |

Alle IDs stehen unverändert im Manifest. Die Abnahme gilt für die konkret bestätigten begrenzten Reaktionskanäle. Abhängige neue Pakete dürfen erst den nach main übernommenen Status verwenden.

## Technische Prüfungen und Messzeiten

| Prüfung | Ergebnis |
| --- | --- |
| CI-Produkthead 589689d | Vier Checks bestanden: Plan, Browser, Installer, Windows-Release-Gate. |
| Vollständiger CI-Windows-Gate | 2672 Tests und 8 Subtests bestanden; pytest 812,450 s; eine bekannte Starlette-Deprecation. Build, Korpus, Bundle, portables Staging, Release-Smoke und Benutzerpaket ebenfalls bestanden. |
| Vollständige CI-Browsermatrix | 30/30 bestanden in 442,775 s; keine übersprungenen, unerwarteten oder flaky Fälle. |
| CI-Installer | 14/14 Lifecycleprüfungen in 488,621 s; darin alle 30 tatsächlichen Browserfälle gegen die installierte EXE in 461,931 s. |
| Lokaler P52-Installer 9d53a04 | 14/14 Lifecycleprüfungen in 603,088 s; 30/30 installierte Browserfälle in 534,269 s. Build sauber, 63,588 s. |
| Lokaler Entwicklungs-Gate | 2.671 Tests + 8 Subtests, pytest 1.073,87 s; zunächst fehlende Seminarressourcen im portablen Paket. Nach 589689d bestehen 50 passende Verpackungstests in 16,06 s und alle restlichen ursprünglichen Gate-Schritte in 28,863 s. Zusammengesetzter Nachweis, kein behaupteter einzelner kompletter finaler lokaler Lauf. |
| Gezielte moderne Prüfungen | 16 neue Kernfälle; vier Seminar-API-Fälle mit beiden Backendvarianten inkl. vollständiger Quellen/Exporte/Import und Grenzen. Vier Seminarbrowserfälle bei zwei Breiten/zwei Modi bestanden. |

Die neue volle CI zählt den zusätzlichen portablen Ressourcenregressionstest mit. Gezielte und vollständige Prüfmengen überlappen und werden nicht zur Testanzahl addiert. Der bekannte Vite-Haupt-Chunk knapp über 500 kB ist eine Größenwarnung; keine fehlgeschlagene Rechnung. Aktive Bearbeitungszeit ist unbekannt. Parallel laufende Messzeiten sind keine summierbare Arbeitszeit.

Browser prüfen echte Entscheidungen, Rechnungen, Downloads, Quellenfreigaben, Fehler/Invalidierung, responsive Ansichten, axe und das Offline-Handbuch samt Bildern. API-Prüfungen umfassen FastAPI und Starlette-Fallback, 16-MiB-Grenze, ungültiges JSON, stale If-Match, Quellenmanipulation und späte Fehler. Fehlerhafte Eingaben erzeugen keine Teilresultate, keinen Digest und keine stille Datenbankanlage.

### Gefundene und behobene technische Ursachen

- Der eingefrorene 100er-Worker benötigte `freeze_support()` vor Desktop-Imports. Die Isolation sowie Zeit-/RSS-/Prefixgrenzen bleiben erhalten.
- Parallele SQLite-Metadatenzugriffe einschließlich erster Lazy-Erzeugung benötigten vollständige Serialisierung. Vorher waren 1.220 von 7.200 parallelen Lesegruppen fehlerhaft; danach bestanden alle 28.800 Einzelabfragen. Keine geänderten Modellregeln oder IDs.
- Ein kuratiertes Bündel scheiterte tatsächlich nach Browsertransport: integrale float-Werte wurden in JSON von 1,0 auf 1 umgeschrieben. Ursprüngliche Quellen werden jetzt zuerst vollständig validiert, ihre portable Ganzzahldarstellung anschließend frisch geprüft. Monetäre Decimalzeichenfolgen und historische globale Digestverträge bleiben erhalten. Das ganze installierte 30er-Programm besteht anschließend.
- Die neue Gruppenwahl überschritt zunächst die schmale Ansicht; kontrollierte Select-Breite behebt den Seitenüberlauf. Kapital-/Anlagebilder erhalten unterschiedliche Dateinamen, damit tatsächliche Ansichten nicht gegenseitig überschrieben werden.
- Der ältere portable Prüfpaketweg enthielt zunächst kein neues Handbuchverzeichnis. Die vollständigen zehn Seminarressourcen werden nun auch dort inventarisiert und unter dem richtigen Anwendungswurzelpfad bereitgestellt; der Regressionstest lädt im frisch gestagten Paket das echte Backend und alle drei Fälle.

## Tatsächlicher Installer und Artefaktintegrität

[Aktuelles CI-Installationsartefakt](https://github.com/junker-joerg/ims/actions/runs/36864280848/artifacts/11163416177) mit EXE, Build-, Ressourcen- und Abnahmenachweisen. [Browserartefakt](https://github.com/junker-joerg/ims/actions/runs/36864280830/artifacts/11163640140); [vollständiger Release-Gate](https://github.com/junker-joerg/ims/actions/runs/36864280822).

| Merkmal | CI | Lokaler P52-Build |
| --- | --- | --- |
| Datei / Version | IMS-Setup-2.0.0-alpha.1-win-x64.exe / 2.0.0-alpha.1 | gleicher Dateiname / gleiche Version |
| EXE-Größe | 19.099.361 Byte | 19.127.163 Byte |
| EXE SHA-256 | `7b07b79b33386fc898943cfa41eba4cfe4f717dca0cc4ff8891a07edd96d9305` | `89bb73e8724c98b7ad4d8622a1b251a654f9858dcdcaf15c0ced9ab0dbe143ba` |
| CI-ZIP SHA-256 | `5e54b7290ba069c5256ed6fd84f17a78e66cc08a063036add7f6950e90213dde` | kein entsprechendes Archiv erzeugt |
| Build-SHA | synthetischer PR-Prüfmerge `2dc26ef943fc7d558958e350893426fe23372f6c` | `9d53a04cd2da149ef515b2158b541ac35585754a` |
| Builddauer | 55,345 s | 63,588 s |
| Werkzeuge | CPython 3.12.10, Node 22.23.3, Inno Setup 6.7.3 | CPython 3.12.10, Node 22.23.2, Inno Setup 6.7.3 |

GitHub-ZIP-Digest, EXE-Größe und EXE-SHA wurden nach Download gegen Originalmetadaten und Testevidenz geprüft. Der synthetische CI-Merge hat Eltern main 2e70b8f und Produkthead 589689d; sein vollständiger Tree ist identisch zum Produkthead. Er ist keine Übernahme nach main. Neun Seminarressourcen stimmen bytegenau per SHA mit dem Checkout überein; die Markdown-Anleitung entspricht demselben Text mit CRLF-Zeilenenden im CI-Checkout. Dieser Unterschied ist im Inventarabgleich festgehalten. Rohe Altarchive sind nicht eingebettet. Lokaler 9d-Build enthält die vollständige Seminaranwendung; der folgende Fix 589 betrifft den separaten älteren portablen Prüfpaketweg. Beide Builds sind sauber und unsigniert. Die Entwicklungsbezeichnung alpha.1 ist keine öffentliche neue AP3-Version. GitHub bewahrt diese Artefakte 30 Tage auf.

Die Lifecycleprüfung installiert in isolierte Pfade mit Leerzeichen/Umlauten, prüft Zweitstart, tatsächliche Modellberechnung und JSON/CSV/Excel, Update bei laufender Anwendung, Neustart, absichtlich belegten Port, explizite Datenübernahme mit Backups, Deinstallation bei laufender Anwendung, Reinstallation und Erhalt gespeicherter Ergebnisse. Der vorherige Installer ist ausdrücklich die synthetische Version alpha.0. Das lokale Log enthält nur den erwarteten absichtlichen Portkonflikt; keinen SQLite-InterfaceError oder unerwarteten API-500.

Lokale EXE: `dist/installer/IMS-Setup-2.0.0-alpha.1-win-x64.exe`. Die Umgebung besitzt Entwicklerwerkzeuge; der EXE-PATH wird für die Prüfung auf System32 beschränkt. Eine neue unabhängige frische Windows-11-Abnahme von AP3 wurde nicht durchgeführt. AP1 und AP2 haben die zuvor dokumentierten externen Bestätigungen; daraus wird kein neuer externer AP3-Test abgeleitet.

Dauerhafte strukturierte Belege: `docs/reports/ims_ap3_ci_evidence.json` und `ims_ap3_p52_evidence.json`. Die alten 26er-/2.651er-Belege zu d2021fc gehören zum historischen M1–M3-Meilenstein und werden nicht als aktuelle M4/M5-Abnahme ausgegeben.

## Verbindliche Grenzen und nächster Entscheidungspunkt

Historische Vollgleichheit, regulatorisches SCR/MCR, echte Bedeckungsquote, gesetzliche Bilanz und DORA-Konformität bleiben gesperrt. Nicht gekoppelt sind Lebens-VN-Verhalten, endogene Mortalität/Schadenwahrscheinlichkeit, gegenseitige Spartenfinanzierung, vollständiger Versicherungsmarkt und eine automatische Kopplung der drei Seminarrechenwege. Die bestehenden historischen Strategieverträge werden nicht still ausführbar gestellt. Der Korpus-Gate meldet weiterhin 15 fehlende berechnete Vergleichsexporte und keine fachliche Produktionsfreigabe; technische Paket-/Seminarreife bleibt davon getrennt.

AP3 ist technisch reviewbar. Der nächste Entscheidungspunkt ist die gesonderte Merge-Freigabe nach Review; keine automatische Übernahme nach main und kein neues Paket. Der vollständige Bericht wird im vorgesehenen Evernote-Notizbuch gespeichert und nach Neuladen anhand Titel, Notizbuch, vollständigem Text und Speicherstatus geprüft. Der Ablagenachweis wird anschließend in der Übergabe festgehalten. Eine gesonderte Aktualisierung der älteren AP1-Notiz bleibt außerhalb dieses AP3-Abschlusses.
