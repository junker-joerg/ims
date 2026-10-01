# IMS | AP1 Abschlussbericht – Windows-Installer

**Technisch abgenommen – Merge offen.** Stand: 01.10.2026,
07:03 Uhr Europe/Berlin (UTC+02:00). Der Auftraggeber hat AP1 auf einem
unabhängigen Windows-11-Rechner getestet, das gewünschte Verhalten bestätigt
und den Merge sowie die anschließende Umsetzung von AP2 ausdrücklich
freigegeben. Die Bestätigung steht in
[ims_ap1_user_acceptance.md](ims_ap1_user_acceptance.md).
AP1 ist im Arbeitsmanifest done; die nach main übernommene Abhängigkeit
ist erst nach dem tatsächlichen Merge erfüllt. Keine öffentliche Veröffentlichung.

## Änderungen und Nutzen

Ein versionierter Setup-Installer bündelt Python-Laufzeit, bestehendes IMS-
Backend, React-Oberfläche, Profile, Beispiele, kuratierte Diagnose-Referenzen,
Hilfe und Lizenztexte. Anwender benötigen auf Windows 11 x64 kein separates
Python, Node.js, npm oder Git. Installation erfolgt im Benutzerkonto; Start,
Hilfe, Datenübernahme und Beenden sind über das Startmenü verfügbar.
Ein Launcher-Fenster ergänzt Browseröffnung, Diagnoseexport und Beenden.

Loopback und Health-Check, Einzelinstanz und belegter Port werden explizit
behandelt. Nutzerdaten liegen getrennt von Programmdateien. Fachlogik, Seeds,
historische Regeln, bestehende Ausführungsfreigaben und Modellgrenzen bleiben
unverändert. Keine historische Vollgleichheit oder regulatorische Freigabe.

## PR, Commit und Artefakt

- [AP1-PR #288](https://github.com/junker-joerg/ims/pull/288),
  Branch `codex/ims-single-installer`, Basis Planungs-PR #287/main e00f8e7.
- Geprüfter Produktcode: **559f80edecd1dff8d3f6c3308b98d04bd83daa24**.
  Zwischencommits: 0d49edf (Plan/Übergabe), 1278f66 (Bundle/Lifecycle),
  559f80e (CI, Abnahmeskript, Lizenzen/Anleitung).
- Kein Merge-Commit für AP1 vorhanden. CI prüft den temporären PR-Testmerge
  **6767405f01901811945f237d72b3cd491279c9bd**, nicht einen Merge nach main.
- Installer: **IMS-Setup-2.0.0-alpha.1-win-x64.exe**; PyInstaller 6.22.3,
  Inno Setup 6.7.3, CPython 3.12.10 x64. Unsigniert.
- Tatsächlicher [CI-Download mit Installer und Nachweisen](https://github.com/junker-joerg/ims/actions/runs/36750792794/artifacts/11114806812)
  aus dem [grünen Installer-Run](https://github.com/junker-joerg/ims/actions/runs/36750792794).
  Actions liefert ein ZIP mit EXE/SHA-256 und Evidenz, kein öffentliches Release.
  Artefaktablauf laut GitHub: 30.10.2026; danach erneut bauen.
- **CI-Installer SHA-256:**
  `4809eee6a733d4153bda4457b272a271529e7eb7c11f745e285f21197630c833`.
  Dies ist die EXE-Prüfsumme aus dem erfolgreichen Installer-Testlog.
- ZIP-Artefakt SHA-256 (andere Datei):
  `b51899b4648cbc83d0c2d7f7d835b7df6a905bf9558a9f57532f3532385ef532`.
- **Nur lokal auf P52:** `C:\Users\P52\source\ims\dist\installer\IMS-Setup-2.0.0-alpha.1-win-x64.exe`;
  18.250.948 Bytes, SHA-256
  `71a7f6e8b3915c068ee975bdfdf840af91dcd501fd49609e9b270d547bb2cc15`.
  Sauberer Build von 559f80e (`dirty=false`). Lokal und CI sind getrennte Builds;
  bitidentische PE-Dateien werden nicht behauptet.

## Testmatrix

| Prüfung | Umgebung | Ergebnis | Nachweis |
| --- | --- | --- | --- |
| Bestehender Windows-Release-Gate | P52, Windows 11 Pro 10.0.26100, Checkout-.venv | Bestanden; 2.597 Tests + 8 Subtests, bestehende fachliche Produktionssperre bleibt erhalten | `ims_ap1_p52_evidence.json`, lokal `.tmp-pr-ap1/release-gate.log` |
| Gezielte Desktop-/Planprüfungen nach Korrekturen | P52, Python 3.12.10 | 18 Tests + 8 Subtests bestanden | lokal `.tmp-pr-ap1/final-unit-tests.log` |
| Installation/Start/Einzelinstanz/Portkonflikt | Tatsächlicher Installer auf P52; EXE-PATH nur System32, Proxies unerreichbar, nicht erhöhtes Prozesstoken | Bestanden, Umlaut-/Leerzeichenpfade | `ims_ap1_p52_evidence.json`, Installer-Setup-Logs im dort angegebenen lokalen Testordner |
| Bestehender Kranken-Zwei-Perioden-Fall, explizite Speicherung, JSON/CSV/XLSX | Eingefrorene P52-Anwendung | Bestanden; Ergebnis-Digest `sha256:44474a6edeaf262732204e44b0498b9c6b53e833e364c03d5104f9c75d8bd5f5` | Installer-Evidenz und lokale Exportdateien |
| Übernahme mit Quell-/Zielbackup und Datenerhalt | Eingefrorene Anwendung | Bestanden, Quelle unverändert | Installer-Evidenz, lokale Backups |
| Update, Deinstallation bei laufendem IMS, Neuinstallation | Tatsächlicher Installer; synthetischer Vorgänger mit älterer Setup-Version desselben Bundles | Bestanden; gespeichertes Ergebnis nach Neuinstallation erneut geprüft | Installer-Evidenz; keine fachliche Versionsmigration behauptet |
| Live-Diagnoseexport | Eingefrorene Anwendung | Bestanden; ohne Datenbank/Instanzschlüssel | Abnahmeskript und ZIP-Inhaltsprüfung |
| Dynamische Strategie-Imports, Profil und Diagnose-Referenzen | P52-Bundle, fünf echte GET-Endpunkte | HTTP 200; Kernüberblick behält fachlichen Warnstatus und keine Issues | `ims_ap1_p52_evidence.json` |
| Browser-Modellfall | Installierte P52-EXE, Codex In-app Browser | Zwei Perioden berechnet und Variante nach expliziter Freigabe gespeichert; vorhandene Exportaktionen sichtbar | Browser-Protokoll dieses Chats, lokale Testablage `.tmp-pr-ap1/gui/Daten` |
| Native Launcher-Sicht-/Klickprüfung | P52 | Lokale Tool-Testlücke vom 30.09.: Windows-Aktivierung meldete `GetCursorPos failed: Zugriff verweigert (0x80070005)`; externe Produktfreigabe inzwischen erteilt | Chat-Toolprotokoll und `ims_ap1_user_acceptance.md` |
| Installer-Build und kompletter Lifecycle | GitHub windows-latest mit Entwicklerwerkzeugen | Bestanden, 13 dokumentierte Prüfungen | Grüner Installer-Run 36750792794, Artefakt-Evidenz |
| Plancheck | GitHub | Bestanden | [Plan-Run 36750792442](https://github.com/junker-joerg/ims/actions/runs/36750792442) |
| Windows-Release-Gate für Produktcommit in CI | GitHub | Bestanden; 2.597 Tests + 8 Subtests, Produktionsfreigabe weiterhin false | [Release-Gate-Run 36750792551](https://github.com/junker-joerg/ims/actions/runs/36750792551), `ims_ap1_ci_evidence.json` |
| **Unabhängige Windows-11-Produktabnahme** | Unabhängiger Rechner des Auftraggebers; weitere Umgebungsdetails nicht mitgeteilt | **Gewünschtes Gesamtverhalten bestätigt und freigegeben am 01.10.2026**; keine erfundenen Einzelprotokolle | [Bestätigung und Nachweisgrenzen](ims_ap1_user_acceptance.md), [vorbereitete Abnahmematrix](ims_ap1_clean_windows_acceptance.md) |

## Installation, Update und Deinstallation

Programm: `%LOCALAPPDATA%\Programs\IMS Workbench`.
Daten: `%LOCALAPPDATA%\IMS\Workbench`. Setup beendet die eigene laufende Instanz
kontrolliert und wartet auf die Instanzsperre. Update und Deinstallation
entfernen keine Nutzerdaten/Backups; Neuinstallation verwendet diese wieder.
Die Übernahme einer alten `.ims_workbench/metadata.sqlite` erfolgt ausdrücklich
über die Startmenüaktion, einschließlich SQLite-Backup der bisherigen
Zieldatenbank und importierten Quelle. Quelle bleibt unverändert; externe
Quellpfade/andere Dateien werden nicht automatisch migriert.

## Tatsächliche Zeiten

Messwerte, keine Schätzungen:

| Vorgang | Dauer |
| --- | ---: |
| Erster PyInstaller/Inno-Build | 84,010 s |
| Sauberer lokaler Produktbuild 559f80e | 71,272 s |
| Vollständige lokale Installer-Abnahme des sauberen Builds | 73,341 s |
| Start des installierten sauberen Builds | 2,606 s |
| Zweitstart | 0,274 s |
| Update bei laufendem IMS | 16,964 s |
| Deinstallation bei laufendem IMS | 2,071 s |
| Neuinstallation / Wiederstart | 6,834 s / 2,327 s |
| Bestehender Windows-Release-Gate P52, insgesamt | 927,242 s (15 min 27 s) |
| Darin pytest | 878,57 s |
| Gezielte Abschluss-Unit-Tests | 0,87 s |
| CI-Installer-Test | 23,286 s |
| CI-Release-Gate: pytest | 983,49 s (16 min 23 s) |
| py2exe Minimalversuch: bundle_files=1 / =3 | 0,402 s / 7,250 s |

Gesamte aktive Bearbeitungszeit, Nacharbeitszeit und Clean-Windows-Testzeit:
**unbekannt**. Keine Aufwandsschätzung als Messung
ausgegeben. Prüfläufe sind Teilmengen/Überlappungen und nicht einfach addierbar.

## Offene Punkte und nächster Schritt

1. Abnahme und Merge sind durch den Auftraggeber freigegeben. Aktuelle
   Checks des Abnahme-Dokumentationscommits prüfen, PR Ready stellen und mergen.
   Letzter bisheriger PR-Stand c581e26 hat 3/3 grüne Checks.
2. GitHub-Schreibzugriff fehlt beim Erfassen dieses Standes: Plugin-Werkzeuge
   sind in dieser Sitzung nicht verfügbar, der In-app Browser ist abgemeldet.
   Die Freigabe liegt vor; ausstehend ist der technische Zugriff.
3. Nach verifiziertem Merge main aktualisieren und AP2 auf
   `codex/ims-elegant-workbench` in einem eigenen Draft-PR umsetzen.
4. Windows 10/ARM64 ungetestet; Signierung und IMS-/Referenzdaten-
   Distributionsrechte vor öffentlicher Veröffentlichung klären.

Der Zwischenbericht vom 30.09. wurde über das Evernote-Plugin im Notizbuch
`MK | 80 IMS1995-2026` gespeichert und durch erneutes Lesen bestätigt
(Notizbuch-ID `ade45e59-57bd-4ada-abaf-dab970f2e126`).
[Evernote-Bericht](https://www.evernote.com/client/web#?n=c8ca33d8-e050-45f2-931c-3e7a4e6dcefa),
Notiz-ID `c8ca33d8-e050-45f2-931c-3e7a4e6dcefa`.
Die Aktualisierung mit Abnahme/Merge vom 01.10. ist mangels aktuellem
Evernote-Zugriff noch ausstehend. Diese Notiz aktualisieren, keine Dublette
zur GitHub-Abschlussautomatik anlegen.
