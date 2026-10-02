# AP4 – bestätigte Anwenderabnahme und Mergeauftrag

Am 02.10.2026 bestätigt der Auftraggeber in dieser Sitzung:

> 1) anbei DORA PDF
> 2) Anwenderabhnahme erfolgt - Freigabe zum Merge erteilt
> 3) Fahre dann mit AP5 fort

Die Bestätigung gilt dem gelieferten AP4-Produkt **2.0.0-alpha.4** in
[PR #293](https://github.com/junker-joerg/ims/pull/293). Sie erteilt die
Anwenderabnahme und den Mergeauftrag für AP4 sowie den anschließenden
Umsetzungsauftrag für AP5. Die fachlichen AP5-Entscheidungstore bleiben
verbindlich. Eine Veröffentlichung oder Umsetzung von AP6–AP14 wird damit
nicht behauptet.

Der vor dieser Dokumentation geprüfte PR-Head ist
`d01d480b21178de384fc9da13318019fe69ffd23`. Alle vier erforderlichen Checks
waren erfolgreich: Plan, Browser, tatsächlicher Windows-Installer und
Windows-Release-Gate. Die bereits dokumentierten Produktprüfungen gelten
weiter; dieser Abnahmebeleg ändert weder Oberfläche noch Modellrechnung.

Die tatsächliche Dauer der Einsteigerübung, Rechner-/Betriebssystemdetails,
benutzter Installerhash und ein konkreter AP3→AP4-Updateablauf wurden in der
Bestätigung nicht genannt. Diese Einzelheiten bleiben unbekannt. Der lokale
AP3-Updateversuch wurde zuvor vom Sicherheitscheck abgebrochen; der bestätigte
Anwendertest ersetzt keine behaupteten lokalen Messungen. Die generelle
Anwenderabnahme wird nach der ausdrücklichen Bestätigung als erfüllt erfasst.

Die gelieferte DORA-Benchmark-PDF ist jetzt lesbar. Ihr Eingang gehört zur
Quellenprüfung für die Folgearbeit; AP4 benötigt weiterhin keine neuen
DORA-Zahlen. Aus einer Umsetzungserhebung werden keine Ausfallwahrscheinlichkeiten
oder automatische Modellparameter abgeleitet.

Nächster Schritt: den Abnahmekommitt nach grüner aktueller CI gemäß Auftrag
übernehmen, main aktualisieren und den tatsächlichen AP5-Auftrag gegen diese
übernommene Basis erzeugen. Mergecommit und Fortsetzungsstand werden nach dem
tatsächlichen Merge in der Lieferübergabe festgehalten.
