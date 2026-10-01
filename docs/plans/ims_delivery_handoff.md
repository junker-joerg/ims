# IMS-Lieferübergabe

Stand 01.10.2026; AP1 auf `codex/ims-single-installer`, technisch abgenommen
und durch Auftraggeber zum Merge freigegeben. Planungs-PR #287 ist in main
übernommen (e00f8e7). PR: https://github.com/junker-joerg/ims/pull/288.
AP1-Merge noch zu verifizieren; AP2 ist anschließend ausdrücklich beauftragt.

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
Der bisherige letzte Dokumentationscommit c581e26 hat 3/3 grüne Checks;
neue Checks des Abnahme-Dokumentationscommits vor Ready/Merge erneut prüfen.

Vollständiger Bericht: `docs/reports/ims_ap1_abschlussbericht.md`;
gemessene lokale Evidenz: `docs/reports/ims_ap1_p52_evidence.json`.
CI-Evidenz: `docs/reports/ims_ap1_ci_evidence.json`.
CI-Download: https://github.com/junker-joerg/ims/actions/runs/36750792794/artifacts/11114806812.
Evernote-Zwischenbericht gespeichert und durch erneutes Lesen im vorgegebenen
Notizbuch bestätigt: https://www.evernote.com/client/web#?n=c8ca33d8-e050-45f2-931c-3e7a4e6dcefa.
Notiz-ID `c8ca33d8-e050-45f2-931c-3e7a4e6dcefa`; diese bei Fortsetzung
aktualisieren und keine Dublette anlegen.

Externe Abnahme: Auftraggeber bestätigte am 01.10.2026 den erfolgreichen
Test auf einem unabhängigen Windows-11-Rechner und erteilte ausdrücklich die
Merge-Freigabe sowie den Folgeauftrag AP2. Originalerklärung und Grenzen der
mitgeteilten Details: `docs/reports/ims_ap1_user_acceptance.md`.
AP1 ist im Arbeitsmanifest done mit echten completion_evidence.
Die frühere lokale Launcher-Tool-Testlücke bleibt im Bericht als solche
erkennbar; sie ist keine eigene Beobachtung des externen Tests.

Aktueller technischer Blocker: GitHub-/Evernote-Plugin-Werkzeuge in dieser
Sitzung nicht verfügbar; In-app Browser auf GitHub abgemeldet. Auftraggeber
hat die Wiederaktivierung des GitHub-Plugins gewählt. Keine Freigabe fehlt.
Evernote-Aktualisierung der bestehenden Notiz mit Abnahme/Merge ausstehend.

Nächster Schritt: Abnahme-Dokumentationscommit in denselben PR pushen,
aktuelle CI prüfen, Ready stellen und den bereits freigegebenen Merge
durchführen. Merge-Commit verifizieren, origin/main aktualisieren und dort
AP1=done samt Nachweisen prüfen. Erst dann den AP2-Arbeitsauftrag erzeugen
und `codex/ims-elegant-workbench`/eigenen Draft-PR verwenden. AP2 umfasst
die vollständigen vereinbarten UI-/Browser-/Installer-Abnahmen; kein AP3-Start.
