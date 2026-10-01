# AP1: unabhängige Windows-11-Abnahme und Merge-Freigabe

Erfasst am 01.10.2026 um 07:03 Uhr Europe/Berlin (UTC+02:00).
Bezug: [AP1-PR #288](https://github.com/junker-joerg/ims/pull/288),
Produktcode `559f80edecd1dff8d3f6c3308b98d04bd83daa24`,
bisheriger PR-Stand `c581e2670a7dd336007cd637650d1e53c1693e10`.

## Bestätigung des Auftraggebers

Der Auftraggeber hat in diesem Codex-Chat am 01.10.2026 erklärt:

> Ap1 wurde auf einem unabhängigen Windows 11 Rechner getestet. Es funktioniert wie gewünscht. Freigabe ist erteilt. Für den Merge auf Main durch. Setze dann die Arbeit mit AP zwei fort.

Diese Erklärung ist die externe Produktabnahme und ausdrückliche Freigabe
für den Merge von AP1. Sie hebt den bisherigen Abnahmeblocker auf.
AP2 ist anschließend zur Umsetzung beauftragt; seine Abhängigkeit ist erst
nach dem tatsächlichen AP1-Merge nach main erfüllt.

## Umfang des Nachweises

Die Erklärung bestätigt einen unabhängigen Windows-11-Rechner und das
gewünschte Gesamtverhalten. Die einzelnen Schritte der vorbereiteten Matrix
wurden nicht separat im Chat protokolliert. OS-Build, Kontotyp, Offline-Status,
installierte Entwicklerwerkzeuge, getestete EXE-Prüfsumme, Screenshots und
Testdauer wurden nicht mitgeteilt. Diese Angaben werden nicht ergänzt oder
als eigene Beobachtung von Codex ausgegeben.

Die lokale native Launcher-Sichtprüfung vom 30.09. bleibt als damalige
Tool-Testlücke dokumentiert. Die Produktfreigabe stammt vom Auftraggeber.
Automatisierte Tests, Installer-Lifecycle und Digests stehen zusätzlich in
`ims_ap1_p52_evidence.json` und `ims_ap1_ci_evidence.json`.

## Prüfung des bisherigen letzten PR-Standes

Am 01.10.2026 zeigte die GitHub-PR-Seite für Commit `c581e26`
**3 / 3 checks OK** (Plancheck, Windows-Installer und Windows-Release-Gate).
Nach dem Dokumentationscommit zur Abnahme werden die aktuellen Checks vor
Ready/Merge erneut geprüft. Die Produktimplementierung wird dabei nicht geändert.

Merge-Status: noch offen beim Erfassen dieses Nachweises. Keine öffentliche
Release-Veröffentlichung beauftragt.
