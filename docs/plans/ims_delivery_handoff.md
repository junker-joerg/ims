# IMS-Lieferübergabe

Stand 30.09.2026; AP1 auf `codex/ims-single-installer`, implementiert,
Clean-Windows-Abnahme offen. Planungs-PR #287 ist in main übernommen (e00f8e7).
Draft-PR: https://github.com/junker-joerg/ims/pull/288.

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
Titel AP1: `IMS | AP1 Abschlussbericht – Windows-Installer`, AP2 entsprechend
`– Oberfläche`, AP3 `– Fachliche Integration`. Nach Speichern erneut lesen
und Notizbuch prüfen. Bei fehlendem Zugriff vollständigen Bericht im PR und
`docs/reports/ims_ap1_abschlussbericht.md` sichern, Ablage als ausstehend melden.
Bei fehlenden Abnahmen Zwischenstand statt Erfolgsbericht.

Bericht enthält Berlin-Zeit, Status, Anwendernutzen, PR/Branch/geprüften Commit,
ggf. Merge-Commit, Installer/Version, echten Artefaktlink und SHA-256 (lokale
Dateien als lokal markieren), Testmatrix mit eigener Clean-Windows-Abnahme,
Installation/Update/Deinstallation und Datenerhalt, Zeiten, Grenzen und
nächstes Paket samt Freigabestatus.

## Aktueller nächster Schritt

Geprüfter Produktcommit: `559f80edecd1dff8d3f6c3308b98d04bd83daa24`.
PyInstaller-/Inno-Installer, Lifecycle, Ressourcen, Datentrennung, Backups,
Anleitung, Lizenzinventar und CI sind umgesetzt. Der saubere P52-Build und
der tatsächliche CI-Installer haben die Lifecycle-Prüfungen bestanden.
Lokal und in CI bestand der bestehende Release-Gate mit 2.597 Tests und
8 Subtests; Installer-, Plan- und Release-Gate-Checks für 559f80e sind grün.
Neue Checks des abschließenden Dokumentationscommits vor Ready erneut prüfen.

Vollständiger Zwischenbericht: `docs/reports/ims_ap1_abschlussbericht.md`;
gemessene lokale Evidenz: `docs/reports/ims_ap1_p52_evidence.json`.
CI-Evidenz: `docs/reports/ims_ap1_ci_evidence.json`.
CI-Download: https://github.com/junker-joerg/ims/actions/runs/36750792794/artifacts/11114806812.
Evernote-Zwischenbericht gespeichert und durch erneutes Lesen im vorgegebenen
Notizbuch bestätigt: https://www.evernote.com/client/web#?n=c8ca33d8-e050-45f2-931c-3e7a4e6dcefa.
Notiz-ID `c8ca33d8-e050-45f2-931c-3e7a4e6dcefa`; diese bei Fortsetzung
aktualisieren und keine Dublette anlegen.

Konkreter Abnahmeblocker: keine zugängliche frische Windows-11-x64-Umgebung
ohne Entwicklerwerkzeuge. Auf P52 weder Windows Sandbox noch eine verfügbare
VM nachgewiesen. Native Launcher-Sicht-/Klickprüfung zusätzlich offen, weil
Windows-Fensteraktivierung im Tool mit Zugriff verweigert scheiterte.
Keine Windows-Funktion oder VM dafür ungefragt installiert/aktiviert.

Nächster Schritt: offline im Standardbenutzerkonto anhand
`docs/reports/ims_ap1_clean_windows_acceptance.md` prüfen und echte Belege
ergänzen. Lokales Abnahmekit: `.tmp-pr-ap1/clean-windows-kit`.
Danach letzte PR-Checks prüfen, erst bei vollständiger Abnahme done und
completion_evidence setzen und Ready for review stellen. Bis dahin AP1
in_progress und PR Draft lassen; AP2 bleibt gesperrt. Bei Fortsetzung
Produktcommit und Dokumentationscommit unterscheiden; kein erneuter
Produktbuild nötig, solange sich nur Bericht/Übergabe geändert haben.
