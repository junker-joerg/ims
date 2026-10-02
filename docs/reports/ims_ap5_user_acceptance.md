# AP5 – bestätigte Anwenderabnahme und Mergeauftrag

Am 02.10.2026 bestätigt der Auftraggeber in dieser Sitzung die konkrete Frage:

> Gibst du AP5 zur Anwenderabnahme und zum Merge frei? Ja

Die Frage bezog sich auf die gelieferte Produktfassung **2.0.0-alpha.5** in
[PR #294](https://github.com/junker-joerg/ims/pull/294), endgültiger Head
`417a0ca4f665c28a94f551aa55a3b05c08d4f125`. Damit sind die allgemeine
Anwenderabnahme und der Mergeauftrag für AP5 ausdrücklich erteilt.
Der vorangehende Auftrag „Fahre mit dem nächsten IMS AP fort“ wird nach
Übernahme von AP5 in main als AP6-Auftrag fortgesetzt. Die Daten-/Methodentore
von AP6 bleiben verbindlich; AP6-Merge, Veröffentlichung und AP7–AP14 sind
damit nicht freigegeben.

Alle vier erforderlichen Checks am genannten Head wurden erneut erfolgreich
geprüft. Der CI-Mergecommit `b430537a090b74f1946da8379aea0ca088f6dab4` hat
die Eltern AP4-main `9b0d45a22be4314eda8e9ab1db61c506a44160f7` und den
genannten AP5-Head. Sein Tree `948cb8cbd7dc38cf0d9018974a791722007207f0`
entspricht exakt dem AP5-Head.

Der tatsächlich heruntergeladene CI-Installer hat 19.914.623 Bytes und
SHA-256 `b861db3c9b79868f5e2c276ba275ddac8381721adf90ea2e9dac5be720a81304`.
Seine 14 Lifecycle-Prüfungen sowie 50 installierten Browserfälle sind
bestanden. Beide Handfälle wurden erneut frisch gerechnet; die bekannten
P6-Werte 172 = 15 + 157 und 315 = 0 + 315 stimmen überein.

Die Bestätigung nennt keine Testdauer, Rechnerdetails oder konkret ausgeführte
Updatefolge. Diese Einzelheiten bleiben unbekannt; eine unabhängig gemessene
Clean-Windows-Abnahme oder ein echter alpha.4→alpha.5-Updateversuch wird nicht
aus der allgemeinen Zustimmung abgeleitet. Der technische Befund zu seltenen
HTTP-Verbindungsresets bleibt mit offener Ursache im PR dokumentiert.

Dieser Abnahmebeleg ändert kein Modell und keine Oberfläche. Der tatsächliche
Merge wird erst nach erfolgreichen Checks des Abnahmekommitts ausgeführt und
anschließend mit Commit und Tree im AP6-Fortsetzungsstand nachgewiesen.
