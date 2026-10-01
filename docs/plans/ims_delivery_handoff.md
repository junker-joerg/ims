# IMS-Lieferübergabe

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
