# AP6: bestätigte Anwenderabnahme und Mergeauftrag

Am 03.10.2026 bestätigt der Auftraggeber in dieser Sitzung wörtlich:

> Gibst du AP6 zur Anwenderabnahme und zum Merge frei? Freigabe erteilt - fahre fort

Die Frage bezog sich auf die gelieferte Fassung **2.0.0-alpha.6** in
[PR #295](https://github.com/junker-joerg/ims/pull/295), Head
`70c04312375a66c6988d26e76d69236bac734780`. Damit sind Anwenderabnahme und
Mergeauftrag ausdrücklich erteilt. „Fahre fort“ beauftragt nach tatsächlicher
Übernahme von AP6 in main das nächste angenommene Paket AP7. Seine fachlichen
Tore bleiben erhalten; kein AP7-Merge, öffentliches Release oder AP8–AP14-Auftrag.

Die Abnahme gilt für den separat [angenommenen BaFin-Referenzumfang](ims_ap6_scope_acceptance.md).
Keine vollständige deutsche Direktmarktrangfolge, historische Konzernkonsolidierung,
beobachtete Firmenstrategie oder tatsächliche Providerbelegung wird nachträglich
bestätigt. Quellen-/Modellgrenzen bleiben am Fall sichtbar.

Alle vier Checks des Heads wurden am 03.10.2026 erneut erfolgreich geprüft.
Der CI-Mergekommitt `72f12909edba578c7bd9c0dfefdb93349924fa99` hat die Eltern
AP5-main `03f87662e85e6081998bab79e32ee12baac52da1` und den genannten Head;
Tree `271f7b9caa7f93be88a43fbed5a4e410a0072c1e` ist identisch zum Head.
Die letzte Dokumentation veränderte weder Produktcode noch die 357 mitgelieferten
Ressourcen gegenüber dem geprüften Produktkommitt 1874835.

Der wirklich heruntergeladene [CI-Installer](https://github.com/junker-joerg/ims/actions/runs/37026925286/artifacts/11235678838)
hat 20.348.554 Bytes und SHA-256
`db75882bd11fda0a9c313b6e2c665d603ad9b5dc873052d82cd6e86395266ef0`.
14 Lifecycle- und 59 installierte Browserfälle bestanden; ebenso 2.735
Python-Tests und 14 Subtests sowie 59 separate Browserfälle. Genaue Metadaten
des aktuellen gelieferten Stands sind im [Prüfprotokoll](ims_ap6_verification.json)
mit eigenem Commit-/Hashbezug ergänzt.

Die allgemeine Zustimmung nennt keine Anwender-Testdauer, Rechnerdetails oder
konkret durchgeführte Updatefolge. Diese Details bleiben unbekannt. Der CI-
Vorgänger ist ein synthetischer Installer desselben Bundles; ein echter
alpha.5→alpha.6-Updateversuch oder unabhängig gemessener Clean-Windows-Test
wird nicht aus der Zustimmung abgeleitet. Kein öffentliches Release erstellt.

Erfasst am 03.10.2026 ab 06:00:19 UTC; dies ist die beobachtete Erfassungszeit,
kein behaupteter sekundengenauer Nachrichtenzeitpunkt. Der tatsächliche Merge
wird erst nach erfolgreicher Übernahme separat nachgewiesen.
