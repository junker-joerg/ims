# DORA-Benchmark: Quellenaufnahme Juni 2026

Geprüft am 02.10.2026 aus der vom Auftraggeber bereitgestellten PDF.
Originaltitel **DORA Implementation Survey – 2026 Benchmarking Exercise**,
KPMG, Ausgabe Juni 2026, 32 Seiten. Dateiname:
`260630_DORA_Implementation_Benchmark_Report_BF_SEC (1).pdf`.
6.478.853 Bytes, SHA-256
`b0f56062dfb70c3c247bd82bb29f3f9e981727f1edbd4589f54d1731023602a8`.
Das Original und seine vollständige Textextraktion werden nicht in dieses
öffentliche Repository übernommen. Der Hash identifiziert die geprüfte Quelle.

## Methode und Bezugsraum

Seiten 4–5: Befragung Februar–März 2026, mehr als 70 Finanzinstitute aus
17 Ländern, vier Größenklassen, 42 Fragen. Die berichtete Zusammensetzung
enthält 48 % Banken und 29 % Versicherungs-/Rückversicherungsunternehmen.
Die Länder umfassen auch Großbritannien und die Schweiz. Die Erhebung wird
deshalb nicht als repräsentativer deutscher Versicherungsmarkt ausgegeben.
Ein gemeinsamer exakter Nenner für sämtliche Fragen ist nicht ausgewiesen.
Fragebezogene Untergruppen und Mehrfachantworten müssen erhalten bleiben.

## Verwendbare Beobachtungen mit Grenzen

Die folgenden Kurzfassungen sind Quellenbeobachtungen, keine IMS-Parameter.
Fragenbezug und Nenner stehen zusätzlich im maschinenlesbaren Register.

| ID | Seite / Frage | Berichteter Befund | Bezugsgruppe und Grenze |
| --- | --- | --- | --- |
| B17 | 17 / Kennzahlen und Vorstandsberichte | 32 % haben Kennzahlen umgesetzt; 51 % berichten quartalsweise, 19 % monatlich. | Zwei verschiedene Fragen; Kennzahlenfrage erlaubt Mehrfachantworten. Berichtsfrequenz belegt keine Wirksamkeit. |
| B20 | 20 / Incident-Daten und Einstufung | 48 % nennen rechtzeitige Datensammlung, 47 % Schwellen-/Kriterieneinordnung als Herausforderung. | Mehrfachantworten; im gesonderten Kreis von 41 Instituten mit verbessertem SIEM beträgt die Einstufungsangabe 51 %. |
| B21 | 21 / Berechnung betroffener Kunden und Transaktionen | Bei Kunden nennen 21 % Unkenntnis und 17 % keine definierte Methode. Bei Transaktionen nennen 30 % eine Dienstebasis, 22 % Unkenntnis. | Getrennte Fragen; die 52-%-Zusammenfassung betrifft die beiden Transaktionskategorien. Kein Anteil tatsächlicher Vorfälle. |
| B24 | 24 / Vertragsnachverhandlung | Für kritische/wichtige Funktionen sind 51 % über 75 % oder abgeschlossen; für andere Verträge nennt die Zusammenfassung 32 %. | Die gerundeten Einzelzellen anderer Verträge ergeben 23 + 8 = 31 %. Berichtete Rundungsdifferenz bleibt sichtbar. |
| B26 | 26 / Monitoring und Prüfnachweise | 66 % nennen Zertifikate/Prüfberichte. Unter 27 Instituten mit zentralem Monitoring sämtlicher Dienste sind es 85 %. | Mehrfachantworten in der Auditfrage; 85 % hat ausdrücklich den Untergruppen-Nenner 27. Kein Widerspruch zu 66 %. |
| B27 | 27 / Auditfrequenz | 31 % geben jährliche Audits an. | Laut Erläuterung nur Institute mit angegebener Auditfrequenz; deren genaue Zahl ist nicht ausgewiesen. |
| B28 | 28 / Exit-Pläne und Exit-Tests | 29 % haben Pläne für alle kritischen/wichtigen Funktionen dokumentiert, 34 % entwickeln sie; 36 % testen ohne strukturierte Methode, 30 % gar nicht. | Zwei Fragen: 63 % Planung und 66 % fehlende Teststruktur dürfen nicht zu einer gemeinsamen Quote oder Ausfallchance verbunden werden. |
| B31 | 31 / interne Revision und TLPT | 44 % jährliche plus 19 % mehrjährige interne Revision; 85 % mindestens jährliche funktionsbezogene Tests bei offiziell TLPT-designierten Instituten. | 85 % ist bedingt auf die TLPT-Untergruppe; ihre genaue Größe ist nicht ausgewiesen. Testkalender erlaubt Mehrfachantworten. |

Ganzzahlige Prozente sind gerundet; Summen können dadurch abweichen.
Mehrfachantworten sind keine disjunkte Partition. Unbekannte Frage-Nenner
werden nicht aus Prozentwerten zurückgerechnet. Auch die auf Seite 12 genannte
Zahl 73 für eine Rollenfrage wird nicht als Nenner aller 42 Fragen eingesetzt.

## Bedeutung für die Lieferplanung

Die Zugangslücke **G-BENCH** ist durch den bereitgestellten, geprüften Beleg
geschlossen. Historische Plantexte zur damals fehlenden PDF bleiben als
datierte Herkunft erhalten; dieser Nachtrag dokumentiert den heutigen Zugang.
Die vollständige AP13-Abnahme und ein benchmarkgestützter Modellfall bleiben
offen. Das Register begründet insbesondere die spätere Unterscheidung zwischen
dokumentierter, verfügbarer und getesteter Fähigkeit. Es kalibriert weder
Provider-Ausfälle noch Schadenhöhe, Wiederanlauf oder reale Versichererprofile.

AP5 nutzt keine dieser Prozentwerte im Lauf. Seine neue Markt-/Risikozuordnung
wird anhand eigener synthetischer Handfälle geprüft. AP7/AP10/AP13 müssen jede
spätere Verwendung als beobachtet, abgeleitet oder angenommen kennzeichnen.

## Prüfnachweis

Alle 32 Seiten wurden textlich gelesen und gerendert. Die maßgeblichen Tabellen
und ihre Erläuterungen auf Seiten 4, 5, 9, 12, 17, 20, 21, 24, 26, 27, 28 und
31 wurden zusätzlich visuell geprüft. Das ist notwendig, weil die reine
Textextraktion einzelne grafische Erläuterungen auslässt. Dateigröße, Seitenzahl
und Hash wurden am Original geprüft. Kein neuer regulatorischer oder
statistischer Modellvertrag wird durch diese Aufnahme angenommen.
