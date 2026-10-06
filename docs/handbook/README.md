# IMS-Benutzerhandbuch

Stand: 06.10.2026 | Aktueller AP8-Arbeitsstand: alpha.11 im Paket-PR #297.
AP8-Anwenderabnahme und Merge bleiben offen. Frühere Prüfberichte und Bilder behalten ihre ursprüngliche Version.

**Aktueller Einstieg:** [Gemeinsames Marktexperiment](market_ap8.md) ([Offline-HTML](market_ap8.html)), [notwendige Eingaben](eingabeinventar.md), [Rechenkern und fachliche Abweichungen](rechenkern.md). In der Hauptnavigation **Markt und Strategien**, dann **Markt verstehen** wählen. Dort stehen vier Arbeitsschritte sowie **Modellwelt**, **Unternehmen** und **Laufansicht**. Die Laufansicht gibt vollständig berechnete Perioden wieder; sie pausiert keinen Kernzustand.

Die sechs Hauptbereiche heißen **Übersicht**, **Markt und Strategien**, **Fallablage**, **Modellwerkzeuge**, **Ergebnisse** und **Hilfe**. Die zusätzliche [Workbench-Bedienhilfe](workbench_ap2.md) beschreibt die weiter vorhandenen Fachwerkzeuge.

Die folgenden AP3-/Testpaket-Anleitungen betreffen ihre eigenen älteren Modellpfade, keine automatische Übernahme ihrer Eingaben in das gemeinsame Marktexperiment.

**Hier beginnen:**

Das [aktuelle Managementseminar](seminar_ap3.md) führt ohne Quellcode durch
drei vollständige 100er-Fälle, moderne Gruppen/Strategien, Vier-Sparten-Bilanzen,
Modellkapital, ICT und den kontrollierten historischen Lauf. Die
[offline lesbare HTML-Anleitung](seminar_ap3.html), geprüften Musterbündel und
echten Browserbilder werden mit dem AP3-Installer geliefert.

Die [aktualisierte Workbench-Bedienhilfe](workbench_ap2.md) beschreibt die aktuellen Bereiche sowie
Hell-/Dunkelmodus, Navigation, Fehlerkorrektur und unveränderte Freigaben.

Der neue [AP1-Windows-Installer](installer_windows.md) bündelt die Laufzeit.
Er wurde am 01.10.2026 auf einem unabhängigen Windows-11-Rechner durch den
Auftraggeber abgenommen; [Abnahmebeleg](../reports/ims_ap1_user_acceptance.md).
Der folgende ältere Testpaketweg
bleibt für bestehende Entwickler-/Testinstallationen dokumentiert.

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
| Aktueller 90-Minuten-Workshop und Arbeitsblatt | [Managementseminar mit AP3](seminar_ap3.md) |
| Früherer Seminarstand PR178a | [IMS im Managementseminar](management_seminar_guide.md) |
| Portabler Ordner und Entwickler-Checkout | [Windows installieren](installation_windows.md) und [Windows-Kurzstart](quickstart_windows.md) |
| Technische Workbench-Bedienung | [Workbench bedienen](operation.md) |
| Historische Referenzen | [Ergebnisse und historische Validierung verstehen](results_and_validation.md) |
| Lokale Ablage und Wechsel | [Daten, Backup und Updates](data_and_updates.md) |
| Quellen und Schnittstellen | [Technische Quellen und Nachweise](technical_reference.md) |

## Vorhandene Funktionen und frühere Bereichsnamen

Die folgenden Bezeichnungen gehören zu den älteren Bildern/Anleitungen.
Einzelmodellfälle, Strategien und historische Ausführung stehen heute unter **Modellwerkzeuge**,
Diagnosen unter **Hilfe**, Metadaten unter **Fallablage** und Resultate unter
**Ergebnisse**. Historische Direktlinks werden weiterhin aufgelöst.

- `Dashboard` und `Szenarien` zeigen Betriebszustand und vorhandene Faelle.
- `Strategien` bietet vorbereitete VU-/VN-Regel-Kandidaten und kontrollierte
  Ein-, Zwei-, Fuenf- und 100-Perioden-Pfade. Der allgemeine 100er-Lauf ist
  fluechtig und setzt eine vorbereitete Kette voraus.
- `Bilanz`, `Leben`, `Kranken` und `Gesamtbilanz` sind eigene IMS-2.x-
  Modellfaelle. Kranken ist bis 100 Perioden bedienbar; die gemeinsame
  Vier-Sparten-Bilanz umfasst dort zwei Perioden. AP3 ergänzt einen eigenen
  vollständigen 100er-Quellenvertrag und den ausdrücklich modernen Strategiepfad.
- `Kapitalwirkung` zeigt aus der geprueften Gesamtbilanz deklarierte
  Modellstresse, zwei Managementgrenzen und JSON-/XLSX-Downloads. SCR, MCR,
  anrechenbare Eigenmittel und Bedeckungsquoten bleiben `nicht berechnet`.
- `Validierung` zeigt historische Diagnosen; `Runs` zeigt Betriebs- und
  Adapterverlauf. Keines davon ist automatisch ein neuer Modelllauf.

Ein erfolgreicher Start belegt **nur technische Erreichbarkeit**. Historische
Feldvollgleichheit und regulatorische Compliance sind nicht nachgewiesen. Der gemeinsame AP5-/AP7-Markt rechnet gültige deklarierte Quellen bis 100 Perioden; daraus folgt kein beliebiger historischer Mehrspartenvertrag. Heruntergeladene
Dateien landen im Downloadordner des Browsers; gespeichert wird nur nach
ausdruecklicher Freigabe in den dafuer vorgesehenen Teilansichten.

Der Installationsweg ist fuer Windows dokumentiert. Linux ist noch nicht
verifiziert (`not_verified`); iOS/Juno bleibt eine Machbarkeitsfrage
(`feasibility_open`). AP1 liefert den Python-freien Windows-Installer;
der ältere ZIP-Lieferplan gilt als historische Referenz. `incomming/` ist
lokaler Pruefbestand, kein Anwenderimport.

Die [Produkt-Roadmap](../plans/ims_2x_all_lines_management_lab_roadmap.md)
nennt die naechsten Ausbauschritte. Sie ersetzt keine aktuell belegte
Bedienfunktion.
