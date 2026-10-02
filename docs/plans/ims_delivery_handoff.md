# IMS-Lieferübergabe

## AP5-Vertrag angenommen; gemeinsamer Produktmarkt angeschlossen

02.10.2026: Der Auftraggeber bestätigt den konkreten Vertrag in Draft-PR #294
mit „Vertrag annehmen und umsetzen“. Beleg `../reports/ims_ap5_contract_acceptance.md`,
Vorschlagscommit `0a21cf8f6718a4b1188da92587a820058ca7c0a3`. Das fachliche Tor
ist angenommen; keine Produktabnahme, kein AP5-Merge/Public-Release.

M2/M3 umgesetzt: `ims.market` mit eigenem Vertrag, gemeinsamem Risikobuch,
allen VU-Bilanzen, disjunkten Familien und überlappenden Peers. API in beiden
Backendpfaden, Marktsicht `#market`, Strategie-/Maßnahmeneditor, ausgewählte
VU in Excel, geprüfte Marktquelle in JSON. Zwölf anfängliche Modell-/APItests
bestanden; zusätzliche Rand- und Desktopanschlussregressionen ergänzt.
Die Browserfälle zu Handrechnung, Filtern, Änderungen und sechs Kontrast-/
Tastaturansichten bestanden; der komplette 41×100-Lauf ebenso.

Gemessene vollständige 40/41×100-Rechnungen: 15,696/16,124 Sekunden,
Antworten 35.369.741/36.239.738 Bytes. Verlustloser Spaltentransport;
16-MiB-Eingang/48-MiB-Ergebnisgrenzen, ein gleichzeitiger Auftrag.
`../migration/ap5_common_market.md` erklärt Herkunft, Adapter und Grenzen.
Einsteigeranleitung `../handbook/market_ap5.md`/`.html`, Releasekennung
`2.0.0-alpha.5` / Windows `2.0.0.5` konsistent. Denselben Draft-PR fortsetzen.

Nächster Schritt: vollständige Python-/Browser-/Planregressionen, Screenshot-
Einbindung und tatsächlichen Installer bauen; Ergebnisse und CI im selben
PR dokumentieren. AP5 bleibt in_progress; AP6–AP14 nicht begonnen.
Der untenstehende frühe Arbeitsstand bleibt historischer Meilenstein.

## AP4 übernommen; AP5 im eigenen Paket begonnen

02.10.2026, 10:49:21 Uhr Europe/Berlin: PR #293 gemäß Anwenderabnahme/Mergeauftrag
übernommen. Geprüfter Head `c11a01dcd13c43119b7e480b3bdeed1a21f14448`, alle vier
erforderlichen Checks erfolgreich. Merge/main
`9b0d45a22be4314eda8e9ab1db61c506a44160f7`, Tree
`ce44dc41f73e33d8d05240a85d6c7ef1663bf8d3` identisch mit geprüftem Head.
Primärer Checkout sauber per Fast-forward aktualisiert. AP4 done/merged,
Release `2.0.0-alpha.4`; kein öffentliches Release erstellt.

Der konkrete anschließende AP5-Auftrag wurde vor Paketmanifeständerungen mit
authorized-Generator gegen dieses main bestätigt. Archiv:
`ims_ap5_work_order.md`; angenommene Ergänzungen E05-01/E05-02 mit eigener
Herkunft in `ims_ap5_implementation.md`. Geeigneten verwalteten Worktree mit
eigener editable Umgebung weiterverwendet, Branch `codex/ims-market-strategy-groups`.

Fachvertragsvorschlag `ims_ap5_market_contract.md`: neue gemeinsame Periodenphasen,
prospektiv mitwechselnde Kohortenrisiken, Altreserve beim alten Träger,
ganze Kohorten bei expliziter Kapazität, disjunkte Familien/überlappende Peers,
Maßnahmenkosten/Vorlauf/Dauer und beobachtbarer Informationsstand.
**Fachliche Annahme noch offen**, keine AP5-Produktfertigstellung oder Mergefreigabe.
Fortschritt und tatsächliche Hand-/Kernelproben:
`../reports/ims_ap5_fortschritt.md`, `ims_ap5_contract_probes.json`.
Skript `scripts/planning/probe_ap5_contract.py` bestand: H1/H2, Carryover,
40/41-Angebotskerne ×100 und Replay. Der alte Bilanzvalidator weist ID41
weiterhin erwartungsgemäß zurück; neue gemeinsame Rechnung/API/UI noch offen.
35 Plan-/Freigabeprüfungen bestanden (5,365 s), bestehende alpha.4-Metadaten
konsistent; Diffprüfung bestanden. AP5-Produkt-/Browser-/Installerprüfungen
stehen erst nach Umsetzung an.

DORA-PDF vollständig gelesen/gerendert; relevante Diagramme visuell geprüft.
Register `../research/dora_benchmark_2026_06.md`/`.json` mit Hash, Frage,
Seite, Bezugsgruppe, Mehrfachantworten und Rundungsgrenzen. Zugangslücke G-BENCH
geschlossen; historische Zugangsnotizen bleiben erhalten. Keine Runtime-
Kalibrierung, Ausfallwahrscheinlichkeiten oder AP13-Abnahme daraus abgeleitet.

Nächster Schritt: konkreten Fachvertrag annehmen lassen, echte Zustimmung
dokumentieren und M2–M4 im selben AP5-Draft-PR ausführen. Bei Änderungen
zuerst Handfälle nachziehen. Paket bleibt in_progress mit leeren Abschlussbelegen;
AP6–AP14 werden nicht gestartet. Evernote-Werkzeuge aktuell nicht aufrufbar,
AP4-/AP5-Berichte sind im Repository und PR gesichert; Ablage ausstehend.

Die folgenden Abschnitte sind datierte Zwischenstände und historische Belege.

## AP4 abgenommen, Merge und anschließendes AP5 beauftragt

02.10.2026: „Anwenderabhnahme erfolgt - Freigabe zum Merge erteilt“ und
„Fahre dann mit AP5 fort“. Beleg `../reports/ims_ap4_user_acceptance.md`.
Alle vier CI-Prüfungen am gelieferten Head `d01d480` erfolgreich. AP4 im Manifest
technisch done mit tatsächlichen Abschlussbelegen; vor dem aktuellen Merge
`merged_to_main=false`. Den Abnahmekommitt nach aktueller grüner CI übernehmen,
Merge/Tree verifizieren und primären main per Fast-forward aktualisieren.
Danach freigegebenen AP5-Auftrag gegen diese Basis erzeugen und im eigenen
Branch/Draft-PR beginnen. Die Markt-/Risiko-/Gruppentore sowie E05-01/E05-02
bleiben verbindlich. Keine Freigabe für AP5-Merge oder Veröffentlichung.

DORA-PDF jetzt lesbar: 32 Seiten, 6.478.853 Bytes, SHA-256
`b0f56062dfb70c3c247bd82bb29f3f9e981727f1edbd4589f54d1731023602a8`.
Eingang hebt den Zugangsblocker auf; keine Ausfallparameter ungeprüft übernehmen.
Anwender-Testdauer und genauer AP3-Updateablauf bleiben unbekannt. Evernote-
Werkzeuge derzeit nicht aufrufbar; Bericht vollständig im Repository/PR gesichert.

## AP4 begonnen nach verifiziertem Planmerge #292

02.10.2026: #292 nach vier grünen Checks übernommen, main
`de3d1de330df81ec948491dbcfbc97ca00a70c60`. Übernommener Tree entspricht
`88790e3`. Primärer main sauber aktualisiert; verwalteter Worktree mit eigener
Umgebung im Branch `codex/ims-explainable-roles` weiterverwendet. Tatsächlicher
AP4-Auftrag im authorized-Generator gegen diese main-Basis bestätigt.
AP4 in_progress; keine Abnahme/Produkt-Merge-/Releasefreigabe.
Plan `ims_ap4_implementation.md`, archivierter Auftrag `ims_ap4_work_order.md`,
laufender Bericht `../reports/ims_ap4_abschlussbericht.md` und Prüfprotokoll
`../reports/ims_ap4_verification.json`. [Draft-PR #293](https://github.com/junker-joerg/ims/pull/293)
enthält Rollen-/Übersichtsanschluss, Erklärweg, drei Bestandsdemos,
Offlineanleitung und acht Browserbilder. Produktversion `2.0.0-alpha.4`.

Produkthead `e6b546c`: lokal 35 Plan-, 48 Backend-/Desktop- und alle 40
Browserprüfungen bestanden; tatsächlicher Installer gebaut. Windows-CI am
identischen PR-Mergetree: 14 Lifecycle- und alle 40 installierten Browserfälle
bestanden. Separater Browser-CI-Erstversuch 39/40: CSS-Laden scheiterte in Chromium
mit `ERR_NO_BUFFER_SPACE`, belegt per Screenshot/Networktrace; Wiederholung 40/40
bestanden. Alle vier erforderlichen Checks am Produkthead grün. Python-Release-
Gate mit 2.699 Tests und 14 Untertests bestanden. Nachfolgender Berichtskommitt
ändert nur Nachweise/Übergabe; seinen aktuellen CI-Stand separat prüfen.
Installer und SHA-256 im Bericht; keine
unabhängige Windows-Anwenderabnahme. Lokaler echter AP3→AP4-Updateversuch vom
Sicherheitscheck vor Installation wegen vorhandener Startmenüverknüpfungen
abgebrochen; Verknüpfungen erhalten. CI-Vorgänger ausdrücklich synthetisch.

Nächster Schritt im selben Draft-PR: aktuelle CI prüfen und geführte
Benutzerübung samt tatsächlicher Dauer sowie echtes AP3→AP4-Update belegen.
Evernote-Ablage noch ausstehend. Fehlende DORA-PDF blockiert AP4 nicht;
AP13 bleibt offen. Kein AP4-Merge/Release, kein AP5-Start autorisiert.

## Planungsauftrag vom 02.10.2026: zum Merge freigegeben

Aktuelle Mergeprüfung: Head `20bdcd6` hatte grüne Plan-, Browser- und echte
Installerprüfungen. Das Windows-Release-Gate scheiterte mit 24 Plan-Testfehlern
bei fehlendem `origin/main` im flachen PR-Checkout; 2.675 andere Tests bestanden
(1.072,35 Sekunden, eine bekannte Starlette-Warnung). Der Release-Gate-Workflow
holt nun die Historie einschließlich main und prüft die Referenz vor dem langen
Gate. Keine Freigabeprüfung abgeschwächt; 35 Planprüfungen nach der Korrektur
lokal erneut bestanden. Aktuellen Korrekturhead vollständig in CI abwarten.

Neuer Auftrag: „Merge den Plan auf Main / Falls ohne die Dora pdf möglich :
starte dann ap4“. PR #292 wird nach grünen aktuellen Checks übernommen. Planung
einschließlich Ergänzungen angenommen mit ihrem Merge; Umsetzung ausschließlich
AP4 anschließend beauftragt. Die DORA-PDF ist G-BENCH für AP13, keine AP4-
Voraussetzung. Produkt-Merge und Veröffentlichung bleiben separat. AP10–AP14
planned/accepted bedeutet Planannahme; ihre Abschlussbelege bleiben leer.

Produkt-main `81146aa8657e2d507cc51c921207e80895f78340` (#291) frisch geprüft;
primärer Checkout sauber, keine offenen PRs beim Start. Vorhandener verwalteter
Worktree mit eigener editable Python-3.12-Umgebung wiederverwendet. Arbeitsbranch
`codex/ims-board-strategy-plan`, Draft-PR
https://github.com/junker-joerg/ims/pull/292. Erster Liefercommit `ff784ff`.
Keine neue Simulation, kein Merge/Release.

Lieferung: 22 Primärquellen und versionierte neun-dimensionale Evidenzmatrix,
synthetischer Drei-VU-DORA-Vertrag, sechs tatsächliche Bestands-ICT-Läufe plus
AP3-Preis-Replay, Nutzen-/Lückenbewertung, 65 nachvollziehbare Anforderungen und
AP10–AP14 als proposed mit leeren Abschlussbelegen. Empfehlung: kleiner AP10-Fall
nach AP7; AP13 nach AP10/AP11 ohne AP12; AP14 nach AP9/AP12/AP13. AP4–AP9 bleiben
angenommen/unverändert, vorgeschlagene Ergänzungen separat; AP4 bleibt das nächste
Produktpaket und wurde hier nicht gestartet.

Quellen: `docs/research/ims_competition_review_2026_10.md` samt JSON;
`docs/plans/ims_dora_reference_case.md`, `ims_board_strategy_2026_10.md` und
`ims_board_strategy_plan.json`; echte Bestandsläufe in
`docs/reports/ims_board_baseline_2026_10.md`/`.json`.
Generator kompatibel für AP1–AP3 und Folgepläne, Vorschau vs freigegebener Auftrag
mit echten Plan-/main-/Umsetzungsbelegen. Befehle in `ims_work_order_generator.md`.

Offen: Benchmark-PDF G-BENCH nicht zugänglich; keine Zahlen übernommen.
Proprietäre Werkzeuge nicht getestet, aktuelle API-/Kalibrierungs-/Kundennachweise
teilweise unbekannt; kein Alleinstellungsnachweis. Neue Risiko-/Zeit-/Cash-/
Capability- und Lebens-/RV-Verträge bleiben fachliche Tore.
35 Plan-/Status-/Kompatibilitätsprüfungen und 27 bestehende ICT-/Seminar-API-Tests
bestanden (155,80 Sekunden; vorhandene Starlette-Deprecation-Warnung).
Echte CLI-Läufe: legacy auto kein Paket, Board auto AP4, AP4/AP10-Vorschauen;
AP10 authorized erwartungsgemäß abgewiesen. CI-Plancheck für `ff784ff` bestanden:
https://github.com/junker-joerg/ims/actions/runs/36968923867.
Browser-/Installer-/Release-Gate-Checks zu diesem Zeitpunkt noch laufend;
keine grüne Gesamtabnahme behauptet. Abschlussdokumentation und gezielte
Prüfverbesserung sind im selben PR ergänzt; aktuellen Head und seine CI beim Review
erneut prüfen. Keine zusätzliche externe Windows-/Benutzerabnahme in diesem Auftrag.
Mergeauftrag liegt nun vor. Danach AP4-Branch `codex/ims-explainable-roles` und
einen eigenen Draft-PR anlegen beziehungsweise fortsetzen, echten paketbezogenen
Auftragsbeleg aus der vorstehenden Nachricht erzeugen und Plan-/main-Gates prüfen.

Stand 01.10.2026. AP1 ist abgenommen und in main übernommen:
PR #288, Merge 965156caf02734cc47e93615c1f8ca91692d51fe um 07:20:42 Berlin.
Der Auftraggeber hat die unabhängige Windows-11-Abnahme, den Merge und das
nächste Paket AP2 ausdrücklich freigegeben. Planungs-PR #287 ist angenommen.

## Verbindliche Fortsetzung

- Vor Arbeit `AGENTS.md`, Sprintplan/Manifest und diese Datei lesen; origin
  aktualisieren, lokale Änderungen erhalten und Planprüfer ausführen.
- Ein Paket je Branch/Draft-PR, nachvollziehbare Zwischencommits. Beim
  Fortsetzen denselben PR verwenden, bis alle Abnahmen erfüllt sind.
- „Weiter so“ setzt ein unvollständiges Paket fort. Technisch abgenommen,
  aber noch nicht gemergt: ausstehende Freigabe melden, nicht selbst mergen.
- AP2 erst nach abgenommenem AP1 in main, AP3 erst nach AP2 in main.
  Ein kurzer Folgeauftrag autorisiert genau ein nächstes freigegebenes Paket.
- done und echte completion_evidence erst nach allen Produktabnahmen;
  Ready for review zusätzlich erst bei grünen erforderlichen CI-Checks.
- Merge und öffentliche Releases benötigen gesonderte Freigabe.

## Berichte und Nachweise

Vor Sitzungspause im selben PR und hier Ergebnis, Commit, Tests, Blocker und
konkreten nächsten Schritt sichern. Messwerte für Lauf-/Testzeiten separat
von Schätzungen; unbekannte Zeiten als unbekannt kennzeichnen.

Evernote: Notizbuch `MK | 80 IMS1995-2026`, ID
`ade45e59-57bd-4ada-abaf-dab970f2e126`. Bericht für denselben PR zuerst suchen,
dann aktualisieren; keine Dubletten zur GitHub-Abschlussautomatik.
Titel AP1: `IMS | AP1 Abschlussbericht – Windows-Installer`, AP2
`IMS | AP2 Abschlussbericht – Oberfläche`, AP3 entsprechend `– Fachliche Integration`.
Nach Speichern erneut lesen und Notizbuch prüfen. Bei fehlendem Zugriff
vollständigen Bericht im PR und `docs/reports/ims_apN_abschlussbericht.md`
sichern, Evernote-Ablage als ausstehend melden. Bei fehlenden Abnahmen
Zwischenstand statt Erfolgsbericht.

Bericht enthält Berlin-Zeit, Status, Anwendernutzen, PR/Branch/geprüften Commit,
ggf. Merge-Commit, Installer/Version, echten Artefaktlink und SHA-256 (lokale
Dateien als lokal markieren), Testmatrix mit eigener Clean-Windows-Abnahme,
Installation/Update/Deinstallation und Datenerhalt, Zeiten, Grenzen und
nächstes Paket samt Freigabestatus.

## AP1 übernommen

Produktcode 559f80e; zuletzt geprüfter PR-Head 13dc31a hatte drei grüne
Checks (Installer, Plan, Release-Gate). Merge nach main über GitHub ausgeführt
und aus origin/main erneut verifiziert. AP1 im Manifest done mit Nachweisen.
Bericht: `docs/reports/ims_ap1_abschlussbericht.md`, externe Bestätigung:
`docs/reports/ims_ap1_user_acceptance.md`. Lokale/CI-Lifecycle-Evidenz bleibt
in `ims_ap1_p52_evidence.json`/`ims_ap1_ci_evidence.json`.

Bestehende Evernote-Notiz `c8ca33d8-e050-45f2-931c-3e7a4e6dcefa`:
https://www.evernote.com/client/web#?n=c8ca33d8-e050-45f2-931c-3e7a4e6dcefa.
Die Aktualisierung mit Abnahme/Merge vom 01.10. ist mangels Evernote-Zugriff
ausstehend; diese Notiz aktualisieren, keine Dublette anlegen.

## AP2 übernommen und in Evernote dokumentiert

Branch `codex/ims-elegant-workbench`, PR
https://github.com/junker-joerg/ims/pull/289. Produkthead
`7dc368ec5defb5754ba037a80b2bfa2ae2251d60` hat vier grüne Checks:
Plan, Browser, Installer und Windows-Release-Gate. AP2 im Manifest done mit
echten Nachweisen. Ready erst nach erneut grünen aktuellen Checks des letzten
Dokumentations-Heads; der danach gültige Ready-Status ist im PR vermerkt.

Fünf Bereiche, Hell-/Dunkelmodus, gemeinsame Gestaltung, Zustandserhalt,
aufklappbare Details, Ergebnisansicht, responsive Navigation/Tabellen und
assistive Inhaltsgruppen sind umgesetzt. 12 Browserfälle bestanden,
66 Ansichten in drei Größen/zwei Modi ohne Seitenüberlauf; Mindestkontrast
6,13:1, sichtbare Aktionen/Checkbox-Labels mindestens 44×44. 14 echte
Installer-Lifecycle-Prüfungen inkl. Browser gegen die installierte aktuelle
EXE bestanden, lokal und CI. Windows-Gate: 2.597 Tests + 8 Subtests bestanden.
Die bekannte fachliche Produktionssperre bleibt bestehen.

Vollständiger Bericht: `docs/reports/ims_ap2_abschlussbericht.md`;
Nachweise: `ims_ap2_p52_evidence.json` und `ims_ap2_ci_evidence.json`.
Aktuelle Bedienhilfe: `docs/handbook/workbench_ap2.md`, 24 Bilder.
CI-Download: https://github.com/junker-joerg/ims/actions/runs/36824042759/artifacts/11144572266.
CI-EXE SHA-256: 1680b5521c61e51347de52bcd08669c83f50a6997c47942563a0ffb238756d24.

Der Auftraggeber bestätigt am 01.10.2026 den erfolgreichen AP2-Test auf einem
anderen Rechner und beauftragt AP3 nach ausführlicher Evernote-Ablage.
Einzelheiten des externen Tests wurden nicht angegeben; siehe
`docs/reports/ims_ap2_user_acceptance.md`. Weitere UI-Verbesserungen folgen später.
Abschließender Head 0148efc hatte vier grüne Checks. PR #289 wurde am 01.10.2026
um 09:48:11 Uhr Berlin gemergt: `2e70b8f814870807a7c8c34d8fc384f8f6a5bb3c`.
Merge und origin/main erneut verifiziert. Keine öffentliche Veröffentlichung.

Evernote-Webzugang funktioniert. Vor dem Anlegen gezielt AP2 im IMS-Notizbuch
gesucht; kein vorhandener Bericht. Vollständige neue Notiz:
https://www.evernote.com/client/web#/notebook/ade45e59-57bd-4ada-abaf-dab970f2e126/note/18c2dc8d-2534-6cd5-20ae-1c862506946c.
Nach Neuladen: Titel, vollständiger Inhalt und vorgesehene Notizbuch-ID geprüft;
„Alle Änderungen gespeichert“. Native Zusatzaufnahme wurde wegen nicht sicher
erkannter Browser-URL abgebrochen, keine weitere native UI-Eingabe.
AP1-Notiz bei späterer Bearbeitung nur aktualisieren, keine Dublette.

## AP3 technisch abgenommen und nach main übernommen

Versionsauftrag vom 01.10.2026: neuer AP3-Stand **2.0.0-alpha.3**, Windows-Version
**2.0.0.3**, Anzeige unten links auf dem Startbildschirm. Gemeinsame Quelle
`python_port/ims/release.py`; künftige höhere Nummer mit
`.venv\Scripts\python.exe scripts/installer/release_metadata.py --set-version VERSION`
vergeben. Paketmetadaten, Installer und CI werden zusammen geprüft. Keine
Wiederverwendung für geänderte ausgelieferte Produkte. Details:
`docs/plans/ims_release_numbering.md`. Lokal bestanden 45 gezielte Tests und
sieben Browserprüfungen der Anzeige; Installer und aktuelle vollständige CI
stehen im selben PR #290. Die folgenden alpha.1-Belege sind historisch.

Branch `codex/ims-management-integration`, ein Integrations-PR #290:
https://github.com/junker-joerg/ims/pull/290. Basis und erneut verifiziertes
origin/main: `2e70b8f814870807a7c8c34d8fc384f8f6a5bb3c`.
Der Auftraggeber bestätigte am 01.10.2026 ausdrücklich die moderne Kopplung.
M1–M5 sind im begrenzten modernen Workshopvertrag umgesetzt; alle 23 IDs
bleiben erhalten und sind im Manifest done mit einzelnen Belegen geführt.
Der Auftraggeber hat anschließend ausdrücklich „Übernehme AP drei in Main.“
beauftragt. PR #290 wurde am 01.10.2026 um 18:48:44 Uhr (Europe/Berlin) nach
main übernommen: `abc8a7e347e29bbd5059abd8b59df2a98eb9d78e`.
Der Merge-Tree entspricht exakt dem geprüften alpha.3-Produkthead
`ee4b659007d50e92058551fcc1f31a48b8ce8ba1`. Alle vier aktuellen CI-Prüfungen
waren erfolgreich: 2.675 Tests + 8 Subtests, 31 Browserfälle, 14 tatsächliche
Installer-Lifecycleprüfungen einschließlich 31 installierter Browserfälle.
Keine öffentliche Veröffentlichung beauftragt. Die nachfolgenden alpha.1-Belege
bleiben historische Nachweise.

Vollständiger geprüfter Produkthead `589689d63887058f5eb703e796d25d531dbfc9f7`:
alle vier CI-Checks grün, 2.672 Tests + 8 Subtests, 30 Browserfälle und 14
Installer-Lifecycleprüfungen mit 30 tatsächlichen installierten Browserfällen.
Lokaler sauberer 9d53a04-Build ebenfalls 14/14 und 30/30. Der anschließende
Fix 589689d betrifft den separaten älteren portablen Prüfpaketweg.
Details/Zeiten und vollständige 23er-Abnahme im Abschlussbericht und den
beiden Evidenzdateien unter `docs/reports/ims_ap3_*`.

CI-Testinstaller: https://github.com/junker-joerg/ims/actions/runs/36864280848/artifacts/11163416177.
EXE SHA-256: `7b07b79b33386fc898943cfa41eba4cfe4f717dca0cc4ff8891a07edd96d9305`.
Der GitHub-Prüfmerge 2dc26ef hat denselben Tree wie 589689d und ist kein
Merge nach main. Ressourcen/Text-Zeilenenden und ZIP/EXE-Integrität geprüft.
Installer unsigniert; neue externe Clean-Windows-AP3-Abnahme nicht durchgeführt.

Bedienung: `docs/handbook/seminar_ap3.md`/`.html`, drei vollständige Dateien
unter `seminar_cases/`; Mappings unter `docs/migration/ims_ap3_*`.
Preisfall 302 × 95 = 28.690 Eigenkapitaldifferenz, Kapitalstress 150;
Anlagefall zusätzlich deklarierter Kapitaldruck 550 > Verlustgrenze 200.
Historische Vollgleichheit, regulatorische Größen, DORA-Konformität und
endogene Gesamtmarktkopplung bleiben offen/gesperrt, keine stillen Änderungen.

Folgeplanung: Der Auftraggeber hat AP4–AP9 am 01.10.2026 geprüft und den Merge
von PR #291 einschließlich nötiger AGENTS.md-Anpassungen freigegeben.
Mit dessen Übernahme gilt `docs/plans/ims_explainable_market_2026_10.md`
und `docs/plans/ims_explainable_market_plan.json`. AP4 ist das nächste
Umsetzungspaket; der Planungsmerge startet es nicht. Der alte Auftragsgenerator
prüft nur die abgeschlossenen AP1–AP3. Die fachlichen Entscheidungstore und
ein vollständiger Branch/Draft-PR je Paket bleiben verbindlich.

Vollständiger AP3-Bericht in Evernote: https://www.evernote.com/client/web#/notebook/ade45e59-57bd-4ada-abaf-dab970f2e126/note/0083bd38-835b-8887-500c-7331d3014af8.
Titel „IMS | AP3 Abschlussbericht – Fachliche Integration“, Notizbuch
„MK | 80 IMS1995-2026“ und ID geprüft; nach vollständigem Neuladen
„Alle Änderungen gespeichert“. Alle 19.405 Textzeichen entsprechen dem
Bericht inklusive Tabellen; Vergleich ohne Layoutleerraum/Editor-
Überschriftenbedienelemente bestanden. Sichtbarer lokaler Bildnachweis
gespeichert; Kontenansicht nicht ins öffentliche Repository aufgenommen.
Rücklesezeit UTC: 2026-10-01T13:14:17.122Z. Keine Dublette; gezielte Suche
vorher ergab nur den AP1/AP2/AP3-Startauftrag. AP2-Bericht war bereits
vor AP3 vollständig abgelegt. Alte AP1-Notiz bleibt gesonderter Rückstand.
