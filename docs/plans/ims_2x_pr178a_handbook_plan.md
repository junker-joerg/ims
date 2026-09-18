# PR178a: Gut lesbares Benutzer- und Installationshandbuch

Stand: 2026-09-18
Status: geplant, direkt nach PR178 und vor PR179

## Ziel und Leserschaft

Eine zusammenhaengende, druckbare Erstausgabe fuer Anwender ohne
Kenntnis der Dissertation sowie fuer den ehemaligen IMS-Programmierer:
Das alte Modell soll wiedererkennbar sein, aber niemand muss Python,
HTTP, Git oder die heutige Webarchitektur verstehen. Die Anleitung
beschreibt nur Funktionen, die nach PR178 im Browser tatsaechlich
bedienbar und getestet sind. Sie ist kein Entwicklerhandbuch.

Der Rohbestand ist bereits vorhanden: `docs/handbook/README.md`,
`user_guide_test_package.md`, `installation_test_package_windows.md`,
`management_seminar_guide.md` und die fachlichen Einzelkapitel. PR178a
konsolidiert, korrigiert und kuerzt diese Dokumente zu **einer** klaren
Einstiegsfolge. Keine zweite widerspruechliche Parallel-Anleitung.

## Liefergegenstand

1. **Installation, 1-2 Seiten:** aktueller belegter Windows-Testweg,
   Voraussetzungen, Start, Stopp, Portkonflikt, Ergebnis- und
   Downloadort, Entfernen. Ein Python-freies Doppelklick-ZIP ist erst
   fuer PR191/192 geplant. Linux bleibt bis HB4 ungeprueft,
   iOS/Juno bis HB5 eine Machbarkeitsfrage.
2. **Bedienung, maximal 10 Seiten einschliesslich Bilder:** Was kann
   das historische Marktmodell? Wer entscheidet wann? Was sind
   Baseline, Variante und ein Schock? Historische Aktivierung/
   Regelwechsel/indirekte Wirkung und die neuen Modell-Bilanzstresse
   werden klar unterschieden. Ein belegter Beispielpfad zeigt
   Eingaben, Start, Zeitreihe, Bilanz/Kapitalbild, Vergleich und
   CSV/JSON/XLSX-Download. Die Anleitung sagt jeweils klar, was nur
   im Browser sichtbar, was im App-Verlauf gespeichert und was als
   Datei im Browser-Download zu finden ist; sie erfindet keinen
   festen lokalen Ausgabepfad.
3. **Bruecke 1995-2026:** eine kurze Tabelle benennt Altbegriffe wie
   VU, VN, Sparte, Regel, Periode, Reserven und Aggregat sowie ihre
   heutigen Ansichten. Neu ist die Browser-Workbench; die fachliche
   Idee des periodischen Marktprozesses bleibt erkennbar. Fachliche
   Abweichungen und nicht uebertragene historische Funktionen werden
   deutlich markiert.
4. **Echte Bildschirmbilder:** lesbare, aktuelle breite und schmale
   Ansichten aus einem reproduzierbaren Beispiel; keine erfundenen
   Knopfnamen. Abbildung und Schritttext muessen zueinander passen.
   Druck/PDF und Bildschirmlayout werden visuell kontrolliert.

## Abnahme und Grenzen

- Zwei fachliche Probeleser-Pfade: eine Person ohne IMS-Vorkenntnis
  findet einen Beispielversuch und dessen Ergebnis; der fruehere
  Programmierer kann Altbegriff, neuen Ort und bewusst fehlende
  Entsprechung ohne Quellcode nachvollziehen.
- Keine unbelegte historische Vollgleichheit, keine Behauptung
  regulatorischer Solvency-II- oder DORA-Konformitaet.
- Aktuelle Start- und Downloadschritte werden auf einem frischen
  Windows-Testpfad sowie im Browser geprueft; tote Links, falsche
  Screenshots und veraltete Bediengrenzen werden entfernt.
- Der nach PR178 gueltige Funktionsstand wird eingefroren. PR186
  ergaenzt die DORA-Bilder, PR187f den 100er-Mehrspartenpfad und
  PR190 nimmt das Handbuch zusammen mit dem Seminarfall erneut ab.
  PR192 aktualisiert spaeter ausschliesslich die Windows-Installation
  fuer das Ready-to-run-ZIP.

Die historische Grundlage ist `DISS.pdf` und die dokumentierte
`IMSDATA.C`-Semantik; die heutige Funktion muss separat durch Tests
und Browserbeobachtung gedeckt sein.
