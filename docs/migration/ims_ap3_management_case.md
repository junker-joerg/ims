# AP3 M3: gemeinsamer 100er-Vier-Sparten-Quellenvertrag

Der neue Vertrag `ims.management-case-input.v1` enthält Baseline und Variante
jeweils mit vollständiger Vier-Sparten-Eingabe und eigener Inhaltsbindung.
`ims.management-common-sources.v1` benennt VU, Szenario, Variante, Horizont,
wirtschaftliche Annahme und einen SHA-256-Digest jeder einzelnen Spartenquelle.
VU-/Szenario-/Horizontidentität und alle Bindungen werden vor einer Ausgabe
geprüft. Falsche Quellen bis zur letzten Periode liefern weder Digest noch
Teilbilanz; die API schreibt keine Metadatenbank.

## Fachliche Zuordnung

| Ursprung / bestehende Komponente | Neue Verbindung | Fachliche Grenze |
| --- | --- | --- |
| `IMSDATA.C`, `IMS.E`: anonyme historische Zustandspositionen | Keine neue Spartenidentität angenommen | Historische Positionen werden nicht in Kfz/Sach umbenannt; kein historischer Runner gestartet. |
| `non_life_model_balance`: deklarierte Gesamtflüsse für Kfz/Sach-Haftpflicht | Vollständige Eingaben je Seite im neuen Quellenvertrag | Prämieneingang ist ein Gesamtfluss, keine still umgedeutete VU-Preisentscheidung. |
| Vorhandene Lebens-Policen-/Periodenkette | Policen, Garantie, Anlage- und Mortalitätsquellen unverändert neu gerechnet | Keine rückwirkende Garantienänderung; Mortalität ausdrücklich exogen. |
| Vorhandene Kranken-Bestands-/Quellenkette | Eigene Szenario-/Variantenbindung und komplette Periodenquellen geprüft | Bestandsentscheidungen und Leistungskosten bleiben getrennte deklarierte Quellen. |
| `four_sector_balance.build_four_sector_balance` | Beide Seiten frisch über dieselben bestehenden Modelle gerechnet | Additive abgestimmte Modellbilanz, keine endogene All-Sparten-Marktreaktion. |
| `CapitalWorkbench` / bestehende Modellkapital-API | Gewählte geprüfte Seite mit tatsächlichem Teilrechnungsdigest weitergereicht | Modellkapital; SCR, MCR und regulatorische Bedeckung bleiben gesperrt. |

Nichtleben und Leben besitzen hier keine gemeinsame technische Szenario-ID.
Der neue Vertrag erfindet keine solche ID in den Teilquellen, sondern bindet
den genauen Inhalt und verlangt die ausdrückliche wirtschaftliche Erklärung
seiner Zusammengehörigkeit. Nach Quellenänderungen muss der Anwender diese
Erklärung erneuern; `declare-sources` prüft zuerst alle bestehenden Teilmodelle,
erneuert dann die Inhaltsbindungen und erhält ihre ursprünglichen Identitäten.

## Reproduzierbare Vorlagen und Exporte

Horizonte 2, 5, 10, 25, 50 und 100 sind freigegeben. Drei unkalibrierte
Vorlagen ändern ab Periode 6 ausschließlich deklarierte Schaden-/Leistungskosten,
Kfz-Prämieneingänge oder Lebens-Anlageerträge. Sie sind keine PR154-Ausführung
und ersetzen PR187g–k nicht. Eine Lebenspolice läuft bis Periode 100 aus;
alle Garantien und Kapitalflüsse stehen im vollständigen Input.

Die unveränderte Baseline schließt nach 100 Perioden mit Modellaktiva
89.700,0000, Verpflichtungen 2.200,0000 und Eigenkapital 87.500,0000.
Jeder Periodenabschluss geht bilanziell auf und wird in die nächste Periode
übernommen. Die ersten zwei und fünf Perioden bleiben auch bei kürzerem
Horizont gleich. Die Modellwährung und Anfangsbilanzen sind Workshopannahmen,
keine Kalibrierung eines historischen Unternehmens.

Anzeige und CSV/JSON/XLSX stammen aus demselben vollständig neu berechneten
Ergebnis. Der Export benötigt dessen exakten Digest als `If-Match`; veraltete
Bindungen werden abgewiesen. CSV enthält 1.000 Zeilen (zwei Seiten, vier Sparten
und Gesamt, 100 Perioden). JSON enthält vollständige Quellen und Resultate.
Excel enthält beide Seiten und Herkunft samt vollständigem, für die Zellgrenze
aufgeteiltem Quellen-JSON. Dezimalwerte und Provenienz werden als Text erhalten.

Alle API-Eingaben sind auf 4 MiB begrenzt, jeweils eine Rechnung gleichzeitig;
kein DB-Schreibzugriff oder Ersatzlauf bei Fehlern. SHA-256 weist einen gleichen
Inhalt nach, nicht seine fachliche Richtigkeit.

## Technische Prüfung

13 neue Kern-/API-Prüfungen bestanden zunächst in 60,12 s. Nach Ergänzung
der Requestgrenzen bestanden gemeinsam 49 neue und bestehende Bilanzprüfungen
in 70,98 s: zwei API-Varianten, deterministische 100er, Carryover, Summen,
Prefixe, falsche Identitäten und späte Fehler, erneute Erklärung, drei echte
digestgleiche Exporte und keine Datenbankanlage. Die abschließende Browser-
und Gesamtprüfung wird im AP3-Zwischenbericht dokumentiert.

Die Fachentscheidung zu den zusätzlichen Strategie-Abrechnungsannahmen steht
in `docs/plans/ims_ap3_strategy_gate.md`. M3 ist ein prüfbarer Zwischenstand;
die vollständige AP3-Seminar-/Installerabnahme bleibt davon getrennt offen.
