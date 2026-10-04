# AP8: Produktprüfung des gemeinsamen Marktcockpits alpha.10

Erfasst 2026-10-04 21:12:08 +0200 (Europe/Berlin).
**Technisch fertig** im bestehenden [Paket-PR #297](https://github.com/junker-joerg/ims/pull/297).
Produkt **2.0.0-alpha.10**, Windows **2.0.0.10**. Anwenderabnahme und Merge
bleiben offen; kein öffentlicher Release oder AP9–AP14-Auftrag.
[Maschinenlesbare Verifikation](ims_ap8_cockpit_verification.json),
[Abschluss](ims_ap8_cockpit_abschlussbericht.md),
[aktuelle Offline-Anleitung](../handbook/market_ap8.html).

## Tatsächlich gelieferte Benutzerführung

Ein gemeinsames Marktexperiment verbindet Quelle, endogene Anbieterentscheidungen,
Nachfrageverhalten, exogene Ereignisse und Ergebnis. Vier Schritte: Markt wählen,
Vorstand & Strategien, Umwelt & Schocks, Wirkung verstehen. Änderungen entwerten
Ergebnis und Export; Schritte, Rollen und Ansichtsfilter erhalten den Zustand.
Neue Vorstandsparameter werden bestehende ausführbare Maßnahmen mit expliziter
Entscheidung ab P6, Vorlauf, Dauer und einmaligen Kosten. Bereits deklarierte
Parametermaßnahmen bleiben erhalten. Nachfrage hat ihren eigenen VN-Regelkern.
Die Vergleichsachse erklärt gleiche Entscheidungen ohne/mit Schock beziehungsweise
gleichen Schock ohne/mit Gegenmaßnahme. Direkte BaFin-Referenzbindung bleibt erhalten.

Dunkle Hauptnavigation, gemeinsame Hell-/Dunkelgestaltung, Kennzahlen aus echten
Buchungen und getrennte Bereiche für Entscheidungen und Umwelt ersetzen die
bisherige verstreute Führung. Fallablage, Modellwerkzeuge und Ergebnisse sind
klar benannt; Ergebnisse zeigen den zuletzt geöffneten Modellfall. Das räumlich
gezeichnete ICT-Netz zeigt deklarierte Kanten und tatsächliche Ausfallstunden mit
Tastaturauswahl, Textalternative und konkretem Abhängigkeits-/Ersatzpfadnachweis.
Sechs Ansichten und E08-01 Fokus/Rivalen/Modellmarkt bleiben erhalten.
Die vier Mockupbilder sind Gestaltungsreferenzen; ihre fiktiven Kennzahlen wurden
nicht als IMS-Daten übernommen. [Plan](../plans/ims_ap8_experiment_cockpit.md),
[Gestaltungsregeln](../frontend_style_guide.md),
[C-/Python-/Oberflächenherkunft](../migration/ap8_market_explorer.md).

## Vier vollständige Produktchecks

Produktkommitt `11384cf69f14f52d3c0f0ae72537986a94484e57`, Tree `f29f977f5ec22ca7550ece7887d25034ad3dd8c3`.
CI-Prüfmerge `2c2e8d560f72666cd80f4d012e9c65e6984cc35b` hat denselben Tree und die Eltern
tatsächliches AP7-main `32ba3112d994f57f33e64e1bc318e7d095223cd0` und Produktkommitt. Der Prüfmerge
ist kein AP8-Merge nach main.

- [Planprüfung](https://github.com/junker-joerg/ims/actions/runs/37225523171/job/111504258596): erfolgreich.
- [Windows-Release-Gate](https://github.com/junker-joerg/ims/actions/runs/37225523181/job/111504258605): **2.764 Python-Tests + 14 Subtests**,
  1 bestehende Warnung, 662.07 s; Frontend, Paket und Portable-Prüfungen bestanden.
- [Checkout-Browser](https://github.com/junker-joerg/ims/actions/runs/37225523147/job/111504288798): **91 Fälle**, 1383.845 s.
- [Installer](https://github.com/junker-joerg/ims/actions/runs/37225523136/job/111504329729): **14 Lifecycle-Prüfungen**, 1400.203 s,
  darin **91 Browserfälle am tatsächlich installierten Produkt**,
  1381.702 s.

Beide Browserumgebungen: keine übersprungenen, fehlgeschlagenen oder instabilen
Fälle, kein Retry. Darunter 13 vollständige AP8-Projektionsfälle, sechs
Navigations-/Tastatur-/Darstellungsfälle und zwei neue gemeinsame Eingabewege.
Die neuen Fälle prüfen echte Quellenänderung, VN-Schwelle, einmalige P6-Buchung,
frischen If-Match-Export, frühe Entscheidungssperre, erhaltene Vorstandssicht,
exogenen ICT-Ausfall, ausführbaren Ersatzpfad und Fehlerentwertung.
Alle älteren Modellwege wurden erhalten und vollständig erneut geprüft.

Vier frische 100er-Fälle und exakte 25er-Prefixe erhalten die AP7-Modell-Digests.
Alle sechs Ansichten werden gegen Originalbuchungen, Gewichte, Nenner und
wirksame Kundenwechsel geprüft. Checkout und installiertes Produkt liefern
dieselben Modell-/Ansichtsdigests und Antwortbytes. Horizontabhängige
`terminal_process_rows` werden ausdrücklich nicht als gleiche Prefixe behauptet.

| Fall | Checkout-Rechnung/Prüfung | Installierte Rechnung/Prüfung | Antwortbytes | Erhaltener AP7-Modell-Digest |
| --- | --- | --- | --- | --- |
| `us_hyperscaler_outage` | 87.323 s | 86.126 s | 27.994.700 | `7ee786bf1266f74c4e95aaca4f01bd50e60c1a9c708cea6169d1be32b8b10c66` |
| `google_motor_entry` | 84.265 s | 84.064 s | 27.920.690 | `8d5e165ab934891c5abedf1d10dce231d06e0bcbc5b69844b98dc7514611225f` |
| `life_demand_shock` | 83.407 s | 83.663 s | 27.561.354 | `b5e4dcc1f876e5f76ec6ebf6abdef705eec1a975a1d750a36205dbfb191ae96a` |
| `dora_2_workshop` | 82.131 s | 80.003 s | 28.024.102 | `f2a21bdc95f946eb77b479f489dd81b7ec0308ccbde9fabe8e1f48fc2c3c2a38` |

Jede Antwort bleibt unter 40 MiB. Zeiten sind einzelne CI-Messungen einschließlich
Ansichts- und Prefixprüfung, keine allgemeine Laufzeitgarantie.
Hell/Dunkel × 1440×900, 1024×768, 390×844: kein Seitenüberlauf,
keine AXE-Verstöße in den geprüften Wegen, niedrigster AP8-Textkontrast
**5.30:1**. Die Anleitung enthält 22 tatsächlich erreichbare Bildreferenzen;
neue und historische Aufnahmen sind bezeichnet. 34 AP8-PNGs sind gebunden.

## Geprüfter Installer und Ressourcen

[Authentisches CI-Artefakt](https://github.com/junker-joerg/ims/actions/runs/37225523136/artifacts/11311894572). EXE **26.654.752 Bytes**, SHA-256
`344df0716f8c53e7fa6672b99d1123a0d9482d94df8d16bd060bcc963c3fc9c8`. GitHub-Archiv und EXE wurden nach Größe und SHA unabhängig
mit Build/Lifecycle abgeglichen. Sauberer Build, Versionsanzeige und Windows-
Dateiversion stimmen überein. **409 Ressourcen** entsprechen dem eingefrorenen
Git-Tree: 80 unveränderte Git-Blobs,
329 ausschließlich Windows-Zeilenendenkonvertierungen.
Der lokale Download `dist/installer/IMS-Setup-2.0.0-alpha.10-win-x64.exe` ist diese geprüfte CI-EXE.

Installation, reale API-/Modellausführung, Exporte, Update, Datenerhalt und
Deinstallation wurden automatisiert auf CI-Windows ausgeführt. Der Vorgänger
ist ausdrücklich ein synthetischer Vorgänger desselben aktuellen Bundles;
ein historischer alpha.8→alpha.10-Upgradepfad wurde damit nicht bewiesen.
CI hat Entwicklerwerkzeuge; der ausführbare PATH war auf System32 beschränkt.
Keine zusätzliche externe Clean-Windows-Anwenderabnahme. Installer unsigniert.
Vorhandene lokale Benutzer-Startmenülinks wurden nicht entfernt und der lokale
Lifecycle-Schutz wurde nicht umgangen.

## Iterationen und fachliche Grenzen

Alpha.8 besitzt eigene erfolgreiche historische Produktbelege. Alpha.9 hatte
sechs gescheiterte Browserwege bei verdeckten Werkzeuglinks beziehungsweise
Bereichsauswahl nach Reload. Diese Wege sind korrigiert und jetzt im vollständigen
91er-Lauf bestanden; keine Fälle wurden entfernt oder übersprungen. Frühe
alpha.10-Läufe wurden bei tatsächlichen letzten Eingabe-/Rollenänderungen ersetzt.
Die lokale Zusatzprüfung enthält 44 Python-Tests/14 Subtests, 13 AP8-Fälle,
neun abschließende Eingabe-/Navigationsfälle und 19 erfolgreiche frühere
globale Fälle; deren damaliger verdeckter Rollenpfad wurde separat korrigiert.
Erst die vier vollständigen Checks oben belegen den technischen Abschluss.

Kein Kern-, Scheduling-, RNG-, Garantie- oder Buchungsvertrag geändert.
Exakte Addition, belegter Kanal, Wechselwirkung und Korrelation bleiben getrennt.
BaFin bleibt verdiente Beiträge einschließlich Ausland/Rückversicherung mit
redaktionellen Gruppen und angenommenem Spartenmix. Deutscher Direktmarkt,
reale Providerprofile und Kalibrierung bleiben offen. Lebens-Nachfrage betrifft
Neugeschäft; Altgarantien bleiben erhalten. Claims/Service wirken auf administrative
Arbeit und Kosten, nicht auf neu abgeleitete Zahlungsverzögerungen. Hypothetische
Regulierung ist keine Complianceprüfung. Wissenschaftliche Produktionsfreigabe
und historische Vollgleichheit bleiben gesperrt; das technische Release-Gate
ersetzt diese nicht. Technische Bedienprüfung ersetzt keine menschliche Abnahme.
AP8-Anwenderabnahme pending, Merge nicht autorisiert. AP9 erst nach tatsächlichem
AP8-Merge und eigenem Folgeauftrag.
