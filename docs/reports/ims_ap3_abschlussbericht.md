# AP3: Zwischenbericht – Fachliche Integration

Stand: 01.10.2026, 12:32 Uhr Europe/Berlin. **AP3 läuft, keine Abschluss- oder
Seminarfreigabe.** Der Bericht hält einen implementierten, technisch geprüften
Zwischenstand und ein konkretes fachliches Entscheidungstor fest.

## Auftrag, Grundlage und Ablage

Der Auftraggeber hat AP2 auf einem anderen Rechner erfolgreich getestet und
AP3 beauftragt; weitere Verbesserungen der Oberfläche folgen später.
AP2-PR #289 wurde um 09:48:11 Uhr Berlin nach vier grünen Checks gemergt,
Merge `2e70b8f814870807a7c8c34d8fc384f8f6a5bb3c`. GitHub und origin/main
wurden erneut geprüft. Angaben zu OS, Checkliste und Prüfdauer des externen
AP2-Tests fehlen; sie werden nicht als bekannte Einzelabnahmen ausgegeben.

Der ausführliche AP2-Bericht wurde **vor AP3** im Evernote-Notizbuch
`MK | 80 IMS1995-2026` gespeichert und nach vollständigem Neuladen erneut
gelesen: Titel, vollständiger Bericht, Merge, Prüfsummen, Testmatrix und
Notizbuch-ID `ade45e59-57bd-4ada-abaf-dab970f2e126` geprüft;
„Alle Änderungen gespeichert“. Die
[AP2-Notiz](https://www.evernote.com/client/web#/notebook/ade45e59-57bd-4ada-abaf-dab970f2e126/note/18c2dc8d-2534-6cd5-20ae-1c862506946c)
ist der Ablagenachweis. Eine zusätzliche native Bildschirmaufnahme wurde
wegen nicht sicher erkannter Browser-URL abgebrochen. Keine weitere native
UI-Eingabe und keine behauptete Bilddatei. Die ältere AP1-Notiz ist gesondert
mit dem Merge-/Abnahmestand zu aktualisieren.

AP3 bleibt ein Branch `codex/ims-management-integration` und ein
[Draft-PR #290](https://github.com/junker-joerg/ims/pull/290).
Implementierung: M1 `bcfe3de`, vollständiges großes ICT-Excel-Dossier
`1d7eada`, geführte Ketten und Vier-Sparten-Rechnung
`a0e1c279048f3e6b14335d4a446f028510c486fd`; anschließend Spawn-Bootstrap
für den eingefrorenen 100er-Worker `762782a`. Die Berechnungs-/API-Module
bleiben beim Bootstrap-Fix unverändert.
Danach parallele Metadatenabfragen unter CPython 3.12 abgesichert:
`d2021fcd0adaaed42be0e65dd696df01f1f6efe2`. Die neu beobachtete Verbindungs-/Statementcache-Konkurrenz ist
reproduziert und durch vollständige Serialisierung der Repositoryzugriffe
einschließlich erster Lazy-Erzeugung behoben; keine Änderung fachlicher
Modellregeln oder Metadaten-IDs.
Alle 23 bisherigen Anforderungs-IDs bleiben erhalten; Manifeststatus
`in_progress`, Gesamtabnahmebelege noch leer. Kein AP3-Merge freigegeben.

## Anwendernutzen und tatsächlicher Produktstand

| Meilenstein | Tatsächliches Verhalten | Grenze / Restpunkt |
| --- | --- | --- |
| M1, PR179–186 | Services hängen gerichtet von Assets/Anbietern ab; ausdrückliche Ereignisse wirken auf Stunden, Kapazität, ursprünglichen Rückstand und Nacharbeit. Gemeinsamer Ausfall, Erholung, Prävention/Fallback/Wiederanlauf und Kosten sind prüfbar. UI und Quellen-Dossier zeigen Modellbilanz und Anbieterabhängigkeiten. | Eigene deklarierte ICT-Workshop-Schicht mit Bilanzoverlay; noch keine automatische historische Markt-/Vier-Sparten-Kopplung. |
| M2, PR187/187a–c | Seed erzeugt 100 vollständige, änderbare Kontexte. 107 Kandidaten für 2/5/100 Perioden werden frisch gebaut; eine falsche späte Quelle blockiert atomar. Explizite SQLite-Speicherung ist unveränderlich/idempotent; echte Prefixläufe und PR151-100er mit ZIP anschließbar. | Ein VU/ein VN und zwei anonyme Vdefmd6-Positionen im synthetischen Fall. Gemeinsamer Prefixweg ausdrücklich nur Laufindex 0. |
| M3, PR187d–f | Vollständige gemeinsame Quellen binden jede Sparte per Digest und wirtschaftlicher Erklärung. Beide Seiten werden frisch gerechnet; periodische Bilanz, Carryover und kurze Prefixe stimmen. UI, CSV, JSON und Excel stammen aus derselben Rechnung. Gewählte geprüfte Seite geht an die Modellkapitalansicht. | Additive Vier-Sparten-Modelle, keine endogene All-Sparten-Marktreaktion. Vorlagen ändern exogene Eingaben ab Periode 6 und führen noch keine Katalogstrategie aus. |
| M4, PR187g–k | Quellenbefund und prüfbarer konkreter Workshop-Vertragsvorschlag vorhanden. | Fachliche Modellgrundlage vor Adapter offen; angefragt, keine Antwort. Kein Strategieadapter oder 100er-Strategiewirkungsnachweis behauptet. |
| M5, PR188–190 | Drei Eingabevorlagen, ICT-Fall, reale Teilpfad-Anleitungen/Bilder und Moderationsentwurf für Review vorhanden. | Strategieabhängige Seminarfälle, portable Bündel/Import-/Demopfad und vollständiger installierter Seminarpfad fehlen. |

Die deklarierte Vier-Sparten-Baseline endet nach 100 Perioden bei Aktiva
89.700,0000, Verpflichtungen 2.200,0000 und Eigenkapital 87.500,0000
Modellwährung. Der Kostenfall endet in der Variante bei Eigenkapital
72.300,0000. Diese Werte sind geprüfte Workshop-Annahmen, keine historischen
Unternehmensdaten oder Kalibrierung.

## Quellen und Migrationsannahmen

ESS.C `main/sy_simltp`, IMSDATA.C Perioden-/Schockstrukturen und IMS.E
VU-/VN-Regeln wurden gelesen. Diskrete alte Perioden belegen keine reale
Stundenlänge. Die neue ICT-Schicht deklariert diese Übersetzung ausdrücklich.
M2 verwendet die bestehenden Kandidaten-/Profilmaterialisierer und
Kettenprüfer, ohne Testmodule aus dem Produkt zu importieren. In-memory-Profile
erhalten dieselben Prüfungen wie der bisherige Dateiprofilweg. SQLite-/
Referenzläufe laufen über die bestehenden kontrollierten Wege.

M3 nutzt die vorhandenen Nichtleben-, Lebens-, Kranken- und Vier-Sparten-
Modelle. Nichtleben und Leben bekommen keine erfundene gemeinsame technische
Szenario-ID; der gemeinsame Vertrag bindet den genauen Inhalt ausdrücklich.
Mortalität, Schäden und Leistungsannahmen bleiben als exogen erkennbar.

Fachliche Details: `docs/migration/ims_ap3_ict_workshop.md`,
`ims_ap3_guided_period_chain.md`, `ims_ap3_management_case.md`.
Bedienung: `docs/handbook/ict_ap3.md`, `hundred_ap3.md`, `management_ap3.md`.
Moderation: `docs/handbook/seminar_ap3_draft.md`, ausdrücklich Arbeitsentwurf.

## Prüfstand und gemessene Zeiten

| Prüfung | Ergebnis / Messung |
| --- | --- |
| M1 neue Kern-/API-Prüfungen inkl. großem Excel-Quellenvertrag | 23 bestanden, 3,12 s |
| M2 neue Kern-/API-Prüfungen inkl. tatsächlichem 100er/Prefix und ungültiger Profil-ID | 16 bestanden, 36,39 s |
| M3 neue Kern-/API-Prüfungen | 13 bestanden; mit 36 bestehenden Bilanzprüfungen 49 bestanden, 70,98 s |
| Weitere vorhandene Regressionen | 70 Bilanz-/API- und 30 Kandidaten-/Kettenprüfungen bereits bestanden; keine Summierung als Gesamtzahl unterschiedlicher Tests |
| TypeScript-/Vite-Build | bestanden; Größenwarnung zum Haupt-Chunk knapp über 500 kB |
| Erste vollständige Browsermatrix | 25/26 bestanden; Fehler der leeren Ergebnisübersicht gefunden und behoben |
| Gezielte Wiederprüfung danach | Navigation/Invalidierung und neuer Vier-Sparten-Übersichtsweg beide bestanden, 57,6 s |
| Parallele Metadaten-/Import-/Desktop- und Run-Control-Prüfungen | 73 + 14 passende Tests bestanden (2,58 s / 1,09 s); 7.200 parallele Lesegruppen mit bis zu vier Abfragen: vor Fix 1.220 fehlerhafte Gruppen, danach alle 28.800 Abfragen ohne Fehler |
| Vollständige Browsermatrix a0e1c27 | alle 26 bestanden: lokal 426,536 s, CI 280,091 s; keine übersprungenen/flaky Fälle |
| Vollständiger lokaler Windows-Release-Gate a0e1c27 | 2.649 Tests und 8 Subtests bestanden, pytest 895,99 s; Gate inkl. Build, Korpus-/Bundle-/Staging-/Paketprüfungen bestanden, gesamte Gate-Dauer 931,196 s |
| Letzter CI-Produktstand d2021fc | alle vier Checks bestanden: Plan, Browser, Installer und Windows-Release-Gate; pytest 2.651 Tests und 8 Subtests, 781,93 s, eine bekannte Starlette-Deprecation; vollständige Entwicklungsbrowsermatrix 26/26 in 348,998 s |
| AP3-Installer nach Spawn-Fix 762782a | lokal 14 Lifecycleprüfungen inklusive aller 26 tatsächlichen Browserfälle bestanden (471,809 s); CI ebenfalls bestanden. Dieser Stand wurde anschließend durch d2021fc ersetzt. |
| Aktueller Installer d2021fc auf P52 | 14/14 Lifecycleprüfungen, eingebettete Browsermatrix 26/26; insgesamt 464,509 s, Browsermatrix 393,385 s. Keine übersprungenen/flaky Fälle; kein SQLite-InterfaceError oder unerwarteter API-500. Der erwartete Fehler beim absichtlich belegten Port bleibt im Log. |
| Aktueller CI-Installer d2021fc | 14/14 Lifecycleprüfungen, Browser gegen die installierte EXE 26/26; insgesamt 312,170 s, Browsermatrix 253,456 s. Vollständiger M4-/M5-Seminarpfad und unabhängige AP3-Abnahme weiter offen. |

Browser prüfen tatsächliche Rechnungen/Downloads, breite/schmale Ansichten,
Hell/Dunkel, Zustand, Fehler, Quellenfreigaben und axe. Der Übersichtsfehler
betraf die Sichtbarkeit des leeren Zustands, nicht fachliche Rechnungen oder
Exports. API-Prüfungen laufen mit beiden Backendvarianten. Ungültige Quellen
erzeugen keinen Digest und keine Teilresultate oder stille Datenbankanlage.

CI-Browserbericht:
[Run 36844444210](https://github.com/junker-joerg/ims/actions/runs/36844444210),
[Artefakt 11153072036](https://github.com/junker-joerg/ims/actions/runs/36844444210/artifacts/11153072036).
Der heruntergeladene ZIP-Digest stimmt mit GitHub überein:
`15c5e745a7d33e4f5066db1510d66faa1d784c7e1451f6642632942ca6cbebce`.
Der CI-SHA `7673bc083038b7b20477d5693de0f26f1c1e34f9` ist GitHubs synthetischer
PR-Prüfmerge, keine Übernahme nach main. Seine Eltern sind main 2e70b8f und
Produkthead a0e1c27; vollständiger Tree `cb23a042e2862e67b5d7cbd3914478cbdeb8bbe1`
identisch mit dem Produkthead, über die GitHub-Commitdaten geprüft.

Die erste CI-Installerprüfung
[Run 36844444142](https://github.com/junker-joerg/ims/actions/runs/36844444142)
belegte die fehlende Behandlung der Multiprocessing-Workerargumente. Der
EXE-Einstieg ruft nun vor dem Desktop-Import `freeze_support()` auf, entsprechend
der [PyInstaller-Vorgabe](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html#multi-processing)
und dem lokalen Runtime-Hook 6.22.3. Keine Umgehung der Workerisolation oder
Zeit-/RSS-/Prefixgrenzen. Der fehlerhafte erste Installer ist kein empfohlenes
AP3-Testartefakt; der aktuelle Build besteht den tatsächlichen 100er-Pfad.

Aktuelle technische Nachweise für d2021fc:
[vier Checks](https://github.com/junker-joerg/ims/commit/d2021fcd0adaaed42be0e65dd696df01f1f6efe2/checks),
[Release-Gate](https://github.com/junker-joerg/ims/actions/runs/36847659358),
[Browserartefakt](https://github.com/junker-joerg/ims/actions/runs/36847659386/artifacts/11154612079).
Browser-ZIP SHA-256:
`c6085ca341207b70b038750614ac66ca5be3c62485fc7b21330cf5a485f08f9c`.
Der aktuelle synthetische PR-Prüfmerge
`3d9637a97548b21c8472f92ba24dfbdebab8d3e3` hat Eltern main 2e70b8f und
d2021fc; Tree `c45c0cde666fc5c922d2d1ef538fa62b9e796344` stimmt vollständig
mit d2021fc überein. Er ist kein Merge nach main.

## Installer für den technischen Zwischenstand

Der tatsächliche CI-Installer steht mit Originalnachweisen im
[Artefakt 11154965440](https://github.com/junker-joerg/ims/actions/runs/36847659449/artifacts/11154965440).
Im heruntergeladenen ZIP wurden Dateigröße, SHA-256 der EXE, Build-Commit,
14 bestandene Lifecycleprüfungen, 26 bestandene installierte Browserfälle
und Ressourceninventar erneut geprüft; keine fremde EXE lokal ausgeführt.

| Merkmal | CI-Artefakt | Lokaler P52-Build |
| --- | --- | --- |
| Datei / Version | IMS-Setup-2.0.0-alpha.1-win-x64.exe / 2.0.0-alpha.1 | gleicher Dateiname / gleiche Version |
| Größe | 18.294.558 Byte | 18.325.751 Byte |
| EXE SHA-256 | `0c5c57d8a6a35082e60d8adb05792b2f4f91e29aaf096941dd51cef7c16f8867` | `5854d0cdb2444b0f4d95ee463d93c54c52c3cfa9e444005d1261e740978e9dfd` |
| ZIP SHA-256 | `34452702fd9637f8434035a404933ed0335ea1f25631e37cb1534fcd9eb72bbe` | kein entsprechendes Archiv erzeugt |
| Build-SHA | synthetischer Prüfmerge 3d9637a, Tree identisch d2021fc | d2021fc; dirty=true wegen ausstehender Dokumentationsänderungen |
| Builddauer | 67,579 s | 63,548 s |
| Buildwerkzeuge | CPython 3.12.10, Node 22.23.3, Inno 6.7.3 | CPython 3.12.10, Node 22.23.2, Inno 6.7.3 |

Lokale Datei: `dist/installer/IMS-Setup-2.0.0-alpha.1-win-x64.exe` im P52-Checkout.
Beide Builds sind unsigniert. Die Installerbezeichnung bleibt bei dieser
Entwicklungsfassung; sie ist keine neue öffentliche AP3-Version. Das CI-Artefakt
enthält die Ressourcen bis zum geprüften d2021fc-Stand; spätere Bericht-/Bild-
Änderungen sind dadurch nicht nachträglich als eingebettet bestätigt.
Artefaktaufbewahrung laut GitHub bis 31.10.2026.

Installation in Pfaden mit Leerzeichen/Umlauten, Einzelinstanz, tatsächliche
Modellberechnung und Exporte, Update der laufenden Anwendung, Neustart,
belegter Port, explizite Datenübernahme mit Backups, Deinstallation bei laufender
Anwendung, Reinstallation und Erhalt gespeicherter Ergebnisse sind geprüft.
Der Updatevorgänger ist ausdrücklich eine synthetische Version alpha.0; der
Test behauptet keine eigene komplette Migration eines externen AP2-Datenbestands.
Die Harness-Umgebung besitzt Entwicklerwerkzeuge, beschränkt den EXE-PATH
auf System32 und verwendet isolierte Testdaten. Eine unabhängige frische
Windows-Abnahme von AP3 ist **nicht** durchgeführt. Der gesamte installierte
Seminarpfad mit M4/M5 ist ebenfalls offen.

Dauerhafte strukturierte Nachweise:
`docs/reports/ims_ap3_ci_evidence.json` und `ims_ap3_p52_evidence.json`.
Nachfolgende reine Dokumentationscommits ersetzen den hier ausdrücklich
geprüften Produkt-SHA nicht; AP3 bleibt Draft.

Gesamte aktive Bearbeitungszeit und fachliche Nacharbeitszeit: unbekannt.
Parallel laufende Prüfdauern werden nicht zur Arbeitszeit addiert.

## Konkretes fachliches Entscheidungstor und Fortsetzung

Die angenommenen Lieferpläne verlangen vor PR187h–k ein belegtes Quellen-/
Zeitmapping. `IMS.E:Vrvu01` erzeugt Prämienziele und Werbung, keine gesamte
gebuchte Prämieneinnahme. PR154 erklärt Ausführung und historische
Spartenbindung ausdrücklich als deaktiviert. Die moderne Nichtlebenbilanz
erwartet Gesamtflüsse, besitzt aber keine eigene VN-Preis-/Expositions-/
Abrechnungsgrundlage. Die historischen anonymen Positionen haben weiterhin
keine belegte Kfz-/Sach-Zuordnung.

Der konkrete Vorschlag in `docs/plans/ims_ap3_strategy_gate.md` deklariert
moderne VU-/VN-Gruppen, Expositionsgewichte, Preis je Exposition und Periode,
Gesamtprämie als Preis × gedeckte Exposition sowie Werbung als separaten
Aufwand; nur quellenkartierte Regelkerne, inklusive Fenster und sichtbar
exogene Schäden/Leistungen. Begrenzte Leben/Kranken-Kanäle würden an vorhandene
Quellen anschließen. Der Auftraggeber wurde nach genau dieser neuen
Modellgrundlage gefragt; alternativ wären historische Belege erforderlich.
Keine Antwort und kein Ersatz durch still erfundene Abrechnung.

Nach der fachlichen Antwort im selben PR vollständigen Quellen-/Zeitvertrag,
belegten begrenzten Adapter, Bedienung und 100er-Wirkungskette umsetzen.
Anschließend portable Seminarbündel, kuratierte Fälle mit Strategiepfad und
aktuelles Handbuch vervollständigen; AP1-Installer mit diesem Produkt neu bauen
und gesamten installierten Seminarpfad samt Gate abnehmen. Keine Anforderung
streichen und AP3 nicht vorzeitig auf done setzen.

Keine historische Vollgleichheit, gesetzliche Bilanz, regulatorischen
SCR/MCR-/Bedeckungsquoten, DORA-Konformität oder endogene All-Sparten-
Marktkopplung behauptet. Der angebotene Installer ist ein technisch geprüfter
Zwischenstand; er ersetzt die noch offene AP3-Gesamtabnahme nicht.

Dieser vollständige Zwischenbericht wird im Repository und PR gesichert.
Eine neue AP3-Evernote-Ablage ist in dieser Sitzung nicht verifiziert; nach dem
URL-Sicherheitsabbruch wird kein weiterer nativer Zugriff versucht. Bei der
späteren Ablage zuerst den Bericht im vorgesehenen IMS-Notizbuch suchen und
aktualisieren, keine Dublette. Der angeforderte AP2-Bericht ist bereits
vollständig und vor AP3 in Evernote verifiziert gespeichert.
