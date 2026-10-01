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

## AP3: moderne Kopplung bestätigt, Gesamtabnahme läuft

Branch `codex/ims-management-integration`, ein Draft-PR #290:
https://github.com/junker-joerg/ims/pull/290. Basis tatsächliches main
`2e70b8f814870807a7c8c34d8fc384f8f6a5bb3c`; origin erneut aktualisiert.
Alle 23 alten Anforderungs-IDs bleiben im Umfang. Der Auftraggeber bestätigt
am 01.10.2026 ausdrücklich: „Ich bestätige den Vorschlag der modernen
Kopplung. Fahre fort.“ M4 ist damit fachlich freigegeben; keine Mergefreigabe.

M1–M3 sind umgesetzt. Der letzte frühere geprüfte Produktstand d2021fc
bestand vier CI-Checks, 2.651 Tests + 8 Subtests, 26 Browserfälle und 14
Installer-Lifecycleprüfungen mit 26 installierten Browserfällen. Dieser
Nachweis belegt den damaligen Zwischenstand und ersetzt M4/M5 nicht.

M4 ist implementiert: moderner benannter Quellen-/Zeitvertrag,
quellenkartierte Vrvu01/Vrvn06-Kerne, Preis × gedeckte Exposition, separater
Werbeaufwand, begrenzte Lebens-/Kranken-Quellenentscheidungen, atomare
100er-Rechnung und bedienbare Gruppen/Parameter/Zeitfenster. Mapping:
`docs/migration/ims_ap3_modern_strategy_bridge.md`; bestätigtes Tor:
`docs/plans/ims_ap3_strategy_gate.md`. Historische Spartenidentität bleibt offen.

M5 ist implementiert: drei vollständige 100er-Fälle, portable Quellenbündel
mit allen modernen/ICT/historischen Eingaben, festen Kapitalannahmen und
frisch geprüfter schreibfreier Demo. Browser/Python-Ganzzahldarstellung wurde
nach tatsächlichem Transportfehler vereinheitlicht, ohne ursprüngliche
Validierung oder historische Digests global umzuschreiben. Preisfall:
P100 Eigenkapital 116.015,7633 / 87.325,7633, handprüfbare Differenz
302 × 95 = 28.690. Preisfall-Kapitalstress 150; Lebens-Anlagefall zusätzlich
Kapitaldruck 550 gegenüber deklarierter Verlustgrenze 200.

16 neue Kernfälle und API-/Export-/Importprüfung mit beiden Backends sowie
aktuelle Ressourcen bestanden. Vier Seminarbrowserfälle bei 1440/390 Pixeln
in Hell/Dunkel bestanden nach Breiten- und Bündelkorrektur. Gesamte
30er-Browsermatrix davor 29 bestanden; kuratierte Demo danach gezielt und
im vollständigen Seminarpfad bestanden. Aktueller zusätzlicher Kapitaldruck-
und Handbuchpfad läuft. Die fertigen Bündel liegen in `seminar_cases/`;
Anleitung `docs/handbook/seminar_ap3.md` und `.html`, tatsächliche Bilder.

Nächster Schritt im selben PR: aktuellen Produktstand einschließlich aller
Bilder committen; vollständige CI, Windows-Release-Gate und neu gebauten
Installer mit allen 30 Browserfällen abnehmen. Erst danach Abschlussbericht,
23 konkrete completion_evidence-Einträge und Ready bei grünen aktuellen
Checks. Kein AP3-Merge und keine öffentliche Veröffentlichung freigegeben.
Unabhängige frische Windows-AP3-Abnahme ist nicht durchgeführt.

Der ausführliche AP2-Bericht ist vor AP3 in Evernote gespeichert und nach
Reload geprüft. Aktueller Evernote-Browserzugang ist vorhanden; gezielte
AP3-Titelsuche im IMS-Notizbuch ergab nur den Startauftrag, keinen AP3-Bericht.
Nach technischer Abnahme vollständigen AP3-Bericht dort anlegen und erneut
lesen; keine Dublette. Die ältere AP1-Notiz benötigt gesonderte Aktualisierung.
