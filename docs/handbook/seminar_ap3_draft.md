# AP3: Moderationsentwurf für die technisch geprüften Teilpfade

Stand 01.10.2026, **Arbeitsentwurf, keine Seminarfreigabe**. Der durchgängige
Strategiepfad und die Abnahme im neu gebauten Installer fehlen noch. Die
Entscheidung vor dem Strategieadapter ist in
`../plans/ims_ap3_strategy_gate.md` dokumentiert. Die folgenden Teilpfade können
für Review und Vorbereitung genutzt werden; sie ersetzen M4/PR187g–k nicht.

## Vorbereitung

Nutzen Sie die lokale Workbench auf dem AP3-Branch und die drei Anleitungen
`ict_ap3.md`, `hundred_ap3.md` und `management_ap3.md`. Halten Sie den Seed,
die jeweiligen Quellen und Inhaltsnachweise zusammen mit den Ausgaben fest.
Verwenden Sie deklarierte Beispiele; keine vertraulichen Unternehmensdaten.
Eine installierte AP2-Version enthält diese AP3-Erweiterungen noch nicht.

## Gespräch und technische Demonstration

| Schritt | Bedienpfad und Beobachtung | Frage für die Moderation |
| --- | --- | --- |
| Gemeinsamer Anfang | 100er-Gesamtbilanz, Schaden-/Leistungskosten, 100 Perioden; Baseline/Variante in Periode 2 und 5 betrachten. | Welche Annahmen halten wir für beide Seiten gleich? Welche neue Quelle wäre nötig, um diese Annahmen als historische Werte zu bezeichnen? |
| Exogener Kostenanstieg | In derselben Rechnung Periode 6 und 100 vergleichen. Baseline schließt mit 87.500,0000, Variante mit 72.300,0000 Modell-Eigenkapital. | Wo entsteht die Differenz im Periodenergebnis, und wie trägt sie sich in das Eigenkapital fort? |
| Prämien-/Anlageeingabe | Separate Vorlagen „Deklarierte Prämienvariante“ und „Deklarierter Anlageertrag“ neu rechnen und exportieren. | Weshalb beweist eine geänderte Eingabe noch keine ausgeführte Preis- oder Anlagestrategie? |
| Operative ICT-Kette | ICT-Wirkung, gemeinsamer Anbieter, Ausfall um Periode 50; Rückstand, Erholung und Bilanzwirkung betrachten, dann eine lokale Gegenmaßnahme neu rechnen. | Welche Dienste hängen wirklich am Anbieter? Warum beseitigt eine lokale Maßnahme nicht den Ausfall anderer VU? Welche Kosten bleiben nach Aufholen des Rückstands? |
| Frischer 100er-Lauf | 100-Perioden-Lauf: Seed festhalten, 100 Kontexte prüfen, explizit speichern, echte 2er-/5er-Referenzen und 100er starten, ZIP sichern. | Was belegt ein bytegleicher Prefix? Warum sind die zwei anonymen Positionen hier keine benannten Kfz-/Sach-Sparten? |
| Modellkapital und Herkunft | Aus der geprüften Gesamtbilanz gewählte Seite öffnen, Periode 100 wählen und ausdrücklich deklarierte Modellannahmen rechnen. JSON/CSV/XLSX mit gleichem Digest sichern. | Welche Quelle und welche Workshopgrenze bestimmen das Ergebnis? Welche regulatorische Kennzahl dürfen wir daraus gerade nicht ableiten? |

Die Diagramme und Tabellen zeigen Modellfolgen unter den eingegebenen Annahmen.
Die Moderation trennt Preisentscheidung, gebuchte Gesamtprämie, operativen
Fluss und Bilanzwirkung. Eine Ergebnisdifferenz allein beweist keine Kausalität.

## Wiederholung und bewusster Fehler

Dieselben vollständigen Eingaben neu prüfen und ihre Digests vergleichen.
Im Expertenmodus eine späte Periodenidentität oder eine Quellenbindung ändern:
die Rechnung muss vollständig gesperrt bleiben. Die Korrektur wird erneut
geprüft und ausdrücklich freigegeben; das alte gespeicherte Bündel wird nicht
überschrieben. Ergebnis-JSON enthält die Managementquellen, das ICT-Dossier die
deklarierte Wirkungskette. Eine automatische portable Seminarbündel-Import-/
Demooberfläche gehört zum noch offenen M5-Abschluss.

## Noch erforderlicher Abschluss

Nach der fachlichen M4-Entscheidung folgen der begrenzte Quellen-/Zeitvertrag,
eine belegte Entscheidung → Fluss → 100er-Bilanz-Reaktion und deren Bedienung.
Danach Seminarbündel und Demo-/Importpfad, aktualisierte Bilder, neu gebauter
Installer sowie der gesamte installierte Seminarpfad. Erst dessen tatsächliche
Abnahme darf PR188–190 und AP3 als abgeschlossen dokumentieren.
