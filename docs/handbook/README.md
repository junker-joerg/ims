# IMS-Benutzerhandbuch

Stand: 2026-09-18 | Handbuchstand: PR178a

**Hier beginnen:**

1. [Windows-Testpaket in zwei Seiten installieren](installation_test_package_windows.md)
   ([Druck-PDF](../../output/pdf/IMS-Installation-Windows.pdf)).
2. [IMS in zehn Seiten verstehen und bedienen](user_guide_test_package.md)
   ([Druck-PDF](../../output/pdf/IMS-Bedienungsanleitung.pdf)).

Die Bedienungsanleitung verbindet die Frage der [Dissertation](../../DISS.pdf)
mit einem heutigen Versuch: Marktprozess, Akteure, Schockarten, Bedienweg,
Ergebnisorte, Downloads, Vier-Sparten-Bilanz, Kapital-Modellwirkung und
fachliche Grenzen. Die zwei PDFs sind Bestandteil des Windows-Testpakets.

## Vertiefung

| Thema | Dokument |
| --- | --- |
| 90-Minuten-Workshop und Arbeitsblatt | [IMS im Managementseminar](management_seminar_guide.md) |
| Portabler Ordner und Entwickler-Checkout | [Windows installieren](installation_windows.md) und [Windows-Kurzstart](quickstart_windows.md) |
| Technische Workbench-Bedienung | [Workbench bedienen](operation.md) |
| Historische Referenzen | [Ergebnisse und historische Validierung verstehen](results_and_validation.md) |
| Lokale Ablage und Wechsel | [Daten, Backup und Updates](data_and_updates.md) |
| Quellen und Schnittstellen | [Technische Quellen und Nachweise](technical_reference.md) |

## Heutiger Funktionsstand

- `Dashboard` und `Szenarien` zeigen Betriebszustand und vorhandene Faelle.
- `Strategien` bietet vorbereitete VU-/VN-Regel-Kandidaten und kontrollierte
  Ein-, Zwei-, Fuenf- und 100-Perioden-Pfade. Der allgemeine 100er-Lauf ist
  fluechtig und setzt eine vorbereitete Kette voraus.
- `Bilanz`, `Leben`, `Kranken` und `Gesamtbilanz` sind eigene IMS-2.x-
  Modellfaelle. Kranken ist bis 100 Perioden bedienbar; die gemeinsame
  Vier-Sparten-Bilanz umfasst derzeit zwei Perioden.
- `Kapitalwirkung` zeigt aus der geprueften Gesamtbilanz deklarierte
  Modellstresse, zwei Managementgrenzen und JSON-/XLSX-Downloads. SCR, MCR,
  anrechenbare Eigenmittel und Bedeckungsquoten bleiben `nicht berechnet`.
- `Validierung` zeigt historische Diagnosen; `Runs` zeigt Betriebs- und
  Adapterverlauf. Keines davon ist automatisch ein neuer Modelllauf.

Ein erfolgreicher Start belegt **nur technische Erreichbarkeit**. Historische
Feldvollgleichheit, regulatorische Compliance und ein frei konfigurierbarer
100-Perioden-Mehrspartenmarkt sind nicht nachgewiesen. Heruntergeladene
Dateien landen im Downloadordner des Browsers; gespeichert wird nur nach
ausdruecklicher Freigabe in den dafuer vorgesehenen Teilansichten.

Der Installationsweg ist fuer Windows dokumentiert. Linux ist noch nicht
verifiziert (`not_verified`); iOS/Juno bleibt eine Machbarkeitsfrage
(`feasibility_open`). Ein Python-freies Windows-Ready-to-run-ZIP folgt erst
mit PR191/192. `incomming/` ist lokaler Pruefbestand, kein Anwenderimport.

Die [Produkt-Roadmap](../plans/ims_2x_all_lines_management_lab_roadmap.md)
nennt die naechsten Ausbauschritte. Sie ersetzt keine aktuell belegte
Bedienfunktion.
