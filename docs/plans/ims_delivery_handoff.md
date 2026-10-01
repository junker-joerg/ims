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

## AP2 in Umsetzung

Branch `codex/ims-elegant-workbench`, Draft-PR
https://github.com/junker-joerg/ims/pull/289. Basis main 965156c, Plan-/Startcommit
f988d2b. Plan: `docs/plans/ims_ap2_implementation.md`.

Umgesetzt: fünf Bereiche, gemeinsame Shell/Details, Hell-/Dunkelmodus,
Zustandserhalt durch gemountete Modellinstanzen, lokale Ergebnisansicht,
Gestaltungsvariablen, Tastaturfokus, responsive Navigation und Tabelle.
Gepinnte Playwright-/axe-Werkzeuge und Windows-Browser-CI; bestehende drei
Modell-Browsernachweise an Navigation angepasst. Installer-Lifecycle kann die
ganze Browserabnahme gegen die installierte aktuelle EXE ausführen.
Bedienhilfe: `docs/handbook/workbench_ap2.md`; Vorher-/Nachher-Bilder dort.

Gezielte Quelle-/Handbuch-/Planprüfungen: 46 Tests + 8 Subtests bestanden.
Browser-Abnahme läuft; die entdeckten Überläufe, kleine Aktionen und nicht
fokussierbaren Tabellen wurden korrigiert. Noch keine AP2-done-Behauptung.

Nächster Schritt: Browsermatrix vollständig abschließen und Bilder prüfen;
Produktcommit sichern/pushen; sauberen Installer bauen und echten Lifecycle
mit Browserprüfung ausführen; vorhandenen Windows-Release-Gate und CI prüfen.
Dann vollständigen AP2-Bericht/Nachweise und Manifest fertigstellen und
denselben PR Ready stellen, sobald alle Checks grün sind. AP2-Merge und
AP3-Start sind nicht freigegeben. Evernote-Plugin fehlt in dieser Sitzung;
Berichtsablage bleibt entsprechend der oben erlaubten Alternative offen.
