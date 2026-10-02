# AP4 – Zwischenbericht: Erklärbares IMS Managementlabor

Stand 02.10.2026, Beginn nach Planmerge #292. Status: **in Arbeit**, keine
Produktabnahme, kein AP4-Merge und keine Veröffentlichung. Branch
`codex/ims-explainable-roles`; ein zusammenhängender Draft-PR wird verwendet.

## Auftrag und Grundlage

Der Auftraggeber hat den Planmerge und anschließend ausschließlich AP4
beauftragt. Die fehlende Benchmark-PDF ist G-BENCH für AP13. AP4 benötigt
keine neuen DORA-Daten. Der Generator hat den echten Auftrag gegen main
`de3d1de330df81ec948491dbcfbc97ca00a70c60` geprüft. Planhead `88790e3` hatte
vier grüne CI-Checks; der übernommene Tree ist identisch.

## Anwendernutzen und Umsetzung

Vorgesehen sind eine Übersicht mit echten Ergebnissen, vier Rollenwege,
direkt ladbare bestehende Demos und eine nachvollziehbare Kette von Eingabe
bis Buchung. Die Kennzahlen trennen Periodenergebnis, Eigenkapital und
kumulierte gezeigte Flüsse. Die Einsteigeranleitung erklärt die alten Begriffe
und heutige Grenzen. AP4 verändert keine fachliche AP3-Regel oder Bilanz.

## Nachweise und offener Stand

Eigene Worktree-Umgebung: CPython 3.12.10, editable ims-port, gepinnte Freezer-
Abhängigkeiten, npm ci, Chromium, Inno Setup 6.7.3 mit Hash-/Signaturprüfung.
Vorbereitete Ansichten und Tests sind noch als Produkt zu prüfen. Drei frisch
gerechnete Bestandsfälle bestätigen die bekannten Endwerte. Preisvariante:
87.325,7633 Eigenkapital, 61.500 Prämien, 190 Werbung, 1.015,7633 Lebens-
Anlageertrag über P1–P100. Der tatsächlich gültige Null-Baseline-Fall liefert
Baseline 0,0000 und Variante −28.690,0000; keine künstliche API-Antwort nötig.

Browserbilder, vollständige Produktprüfungen, neue Installerdatei, SHA-256,
Lifecycle/Datenerhalt und installierte Offlinehilfe stehen noch aus.
Unabhängige Benutzerabnahme und tatsächliche Dauer der 15-Minuten-Zielübung
sind nicht erfolgt. Evernote-Ablage ist noch ausstehend; der vollständige
Zwischenstand wird hier und im Draft-PR gesichert.

Nächster Schritt: vorbereitete UI anschließen, Offlinehilfe/Release ergänzen,
gezielte Browserprüfungen durchführen und das zusammenhängende Paket abnehmen.
