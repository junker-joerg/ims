# AP4 – Zwischenbericht: Erklärbares IMS Managementlabor

Stand 02.10.2026, Beginn nach Planmerge #292. Status: **in Arbeit**, keine
Produktabnahme, kein AP4-Merge und keine Veröffentlichung. Branch
`codex/ims-explainable-roles`, [Draft-PR #293](https://github.com/junker-joerg/ims/pull/293).

## Auftrag und Grundlage

Der Auftraggeber hat den Planmerge und anschließend ausschließlich AP4
beauftragt. Die fehlende Benchmark-PDF ist G-BENCH für AP13. AP4 benötigt
keine neuen DORA-Daten. Der Generator hat den echten Auftrag gegen main
`de3d1de330df81ec948491dbcfbc97ca00a70c60` geprüft. Planhead `88790e3` hatte
vier grüne CI-Checks; der übernommene Tree ist identisch.

## Anwendernutzen und Umsetzung

Die neue Übersicht zeigt echte, frisch geprüfte AP3-Ergebnisse. Ein Anwender
öffnet eine der drei vorhandenen Demos direkt, wählt Baseline oder Variante
und verfolgt eine Modellperiode von der Eingabe bis zur Buchung. Der
Rollentausch erhält Eingaben, Ergebnisnachweise und vorhandene Bestätigungen.

| Rolle | Einstieg und Frage |
| --- | --- |
| CEO | Ergebnis, Eigenkapital und Kapitalwirkung vergleichen. |
| CIO | ICT-Abhängigkeiten und den vorhandenen DORA-/ICT-Workshop verstehen. |
| COO | Prozesse, Rückstand und Wiederanlauf im vorhandenen ICT-Workshop prüfen. |
| CSO Vertrieb | Preis, Kundenwahl und Prämienwirkung im Seminarfall erklären. |

Die Kennzahlen trennen Periodenergebnis, Schluss-Eigenkapital und kumulierte
gezeigte Flüsse. Diagramm und aufklappbare Verlaufstabelle lesen dieselben
geprüften Buchungen wie API und Export. Geldsummen und Differenzen erhalten
vier Dezimalstellen. Der Prozentvergleich verwendet die Differenz zwischen
Variante und Baseline relativ zum Betrag der Baseline; Baseline null erscheint
als „Nicht definiert (Baseline 0)“. Bei neuen Eingaben verschwinden alte
Übersichtskennzahlen. Laden, veraltetes Ergebnis und korrigierbare Fehler
haben eigene sichtbare Zustände.

Die Erklärung verbindet Parameter/Ziehungen, ausgeführte Regel,
Kundenentscheidung, Prämie/Werbung, Bilanzidentität und Carryover. Die Oberfläche
nennt den aktuellen Fall ausdrücklich **Seminarfall einer VU**. Exogene
Schäden/Leistungen, fehlende Lebens-Nachfrage und die separate ICT-Rechnung
bleiben sichtbar. Die vier neuen Schock-Demos gehören zu AP7; AP4 verwendet
„Preis und Anbieterwechsel“, „Kosten und Beitragsreaktion“ und
„Lebens-Anlageentscheidung“ aus AP3.

Die [Einsteigeranleitung](../handbook/management_ap4.md) ist auch als
[Offline-HTML](../handbook/management_ap4.html) aus IMS erreichbar. Sie enthält
die Begriffskarte VU/VN/BAV, einen geführten Einstieg, Fehlerkorrektur,
Interpretation und eine Übung mit dem Ziel von 15 Minuten. Acht echte
Browserbilder dokumentieren die Oberfläche und den Erklärweg.

## Herkunft und technische Einordnung

| Ursprung | Präsentation in AP4 | Fachliche Grenze |
| --- | --- | --- |
| ESS.C `sy_simltp` / `sy_xaktion`, bestehende AP3-Periodenrechnung | Periodenauswahl, Verlauf und Carryover-Erklärung | Keine neue Zeit- oder Scheduling-Logik. |
| IMS.E `Vrvu01` / `Vrvn06`, bestehender moderner AP3-Preis-/Kundenkern | Parameter, Kundenwahl und Preis × gedeckte Exposition | Keine zusätzliche Marktbilanz oder neue Regel. |
| Geprüfte AP3-Bilanzzeilen und Entscheidungstraces | Kennzahlen, Spartenvergleich, Differenzrechnung und Verlaufstabelle | Vorhandene Ein-VU-Bilanz unverändert. |
| Bestehender ICT-/DORA-Workshop | Sichtbare CIO-/COO-Aufgabenlinks | Keine gemeinsame ICT-/Marktrechnung oder Compliance-Aussage. |

`ManagementSession.tsx` hält den Präsentationskontext innerhalb der bestehenden
Workbench. Die Modellkomponenten bleiben montiert. `ManagementOverview.tsx`,
`SeminarExplanation.tsx` und `seminarPresentation.ts` präsentieren die geprüften
Werte; sie buchen und simulieren nicht. Backendverträge und fachliche Regeln
bleiben unverändert. Der Handbuchrenderer und die Ressourcenliste nehmen die
AP4-Anleitung samt Bildern in den Installer auf. Gemeinsame Produktfassung:
**2.0.0-alpha.4**, Windows-Dateiversion **2.0.0.4**, sichtbar unten links.

## Ausgeführte Prüfungen

Eigene Worktree-Umgebung: CPython 3.12.10, editable ims-port, gepinnte Freezer-
Abhängigkeiten, npm ci, Chromium, Inno Setup 6.7.3 mit Hash-/Signaturprüfung.

| Prüfung | Tatsächliches Ergebnis |
| --- | --- |
| Frontendbuild und gemeinsame Release-Metadaten | Bestanden; bestehender Hinweis auf JS-Bundle größer als 500 kB. |
| Plan-/Auftrags-/Statusprüfungen | 35 bestanden. Zwei Testfixtures wurden an den tatsächlich begonnenen AP4-Status angepasst; die Freigabegates bleiben erhalten. |
| Backend-/Desktopprüfungen | 48 bestanden in 8,06 Sekunden; bekannter Starlette-Testclient-Hinweis. |
| Vollständiges Windows-Release-Gate | 2.699 Tests und 14 Untertests bestanden in 1.035,96 Sekunden; ein bekannter Warnhinweis. |
| Vollständiger lokaler Browserlauf | 40 von 40 bestanden in 714,98 Sekunden; neun neue AP4-Fälle und 31 Bestandsfälle. |
| Größen und Farbmodi | 1440×900, 1024×768 und 390×844 jeweils Hell/Dunkel; Axe ohne Verstöße, gemessener Mindesttextkontrast 6,13:1 hell und 6,85:1 dunkel. |
| API-/Exportvergleich | Tatsächliche Werte, 100 Tabellenzeilen, Periodenauswahl und heruntergeladenes JSON stimmen überein. |
| Rollen und Zustände | Keine Neuberechnung beim Rollentausch; erhaltene Eingaben/Bestätigungen, Leer-/Lade-/Fehler-/veralteter Zustand sowie Fehlerkorrektur bestanden. |
| Offlinehilfe | HTML und alle referenzierten Bilder geladen, auch aus der installierten Anwendung in CI. |
| Tatsächlicher Windows-CI-Installer | 14 Lifecycle-Prüfungen bestanden in 392,78 Sekunden; darin alle 40 Browserfälle gegen die installierte Anwendung in 374,39 Sekunden. |
| Separate Browser-CI, Wiederholung | Alle 40 Fälle bestanden; Konsolendauer gerundet 10,3 Minuten. |

Drei frisch gerechnete Bestandsfälle bestätigen die bekannten Endwerte.
Preisvariante P100: Eigenkapital 87.325,7633; kumuliert über P1–P100 Prämien
61.500,0000, Werbung 190,0000 und Lebens-Anlageertrag 1.015,7633. Die
Periodendifferenz −302,0000 für P6–P100 ergibt −28.690,0000. Ein tatsächlich
gültiger Eingabefall liefert Baseline 0,0000 und Variante −28.690,0000;
die Nullvergleichsprüfung benötigt keine künstliche API-Antwort.

## Installer und CI-Belege

Geprüfter Produkthead ist `e6b546c725b557b612481189622be94bcff34bd8`.
GitHub testet den PR-Mergecommit `4f3a2abc0feecf93caf71140bf90c18ad2119df6`
mit Eltern main `de3d1de` und diesem Head. Sein Tree
`33a308823d592c79ad38e97754def1bc666f955d` ist identisch mit dem Produkthead.

| Build desselben Releases | Größe | SHA-256 | Gemessene Buildzeit |
| --- | --- | --- | --- |
| Lokal, Produkthead `e6b546c` | 19.616.893 Bytes | `dc74503a828532e138e578f677cfd45f78b8cc97ab33c1edee0cb219cf9f1dc9` | 78,80 Sekunden |
| Windows-CI, PR-Mergecommit `4f3a2abc` | 19.582.588 Bytes | `06993cb628925a41fde4a225c6264f15bab5852fd2c81ea6f72d51d659f1f7ff` | 36,28 Sekunden |

Dateiname jeweils `IMS-Setup-2.0.0-alpha.4-win-x64.exe`. Dies sind zwei
nachvollziehbare Builds desselben Produktstands, keine neuen Release-Nummern.
Beide sind unsigniert. Die Ressourceninventare enthalten AP4-HTML, Markdown
und alle acht AP4-Bilder.

Der [bestandene Installer-CI-Lauf](https://github.com/junker-joerg/ims/actions/runs/36975712642)
stellt [Installer und Nachweise als befristetes Testartefakt](https://github.com/junker-joerg/ims/actions/runs/36975712642/artifacts/11212818868)
bereit. Das heruntergeladene Archiv hat SHA-256
`144be9bf58ecc0378aa1e0e4794127d2e612ca2587355c7eae4878d5a46bb1aa`.
Der Lifecycle-Lauf belegt Installation, Start, Exporte, Update im laufenden
Zustand, Datenübernahme mit Sicherungen, Deinstallation, Neuinstallation und
Ergebnisdatenerhalt. Sein Vorgänger ist ausdrücklich ein **synthetischer
Installer mit demselben aktuellen App-Bundle** (`synthetic_same_bundle`), kein
historischer AP3-Build. Der Lauf ist keine unabhängige Windows-Anwenderabnahme;
Entwicklungswerkzeuge sind vorhanden, der ausführbare Prozess startet mit auf
System32 begrenztem PATH und gesperrtem Netzwerkproxy.

Der lokale Versuch eines echten AP3→AP4-Updates wurde vor der Installation
abgebrochen: Der Sicherheitscheck fand vorhandene IMS-Startmenüverknüpfungen.
Sie wurden erhalten. Der Installer ignoriert `/GROUP` bei
`DisableProgramGroupPage=yes`; ein anderer Gruppenname wäre daher keine sichere
Isolation. [Inno-Setup-Dokumentation](https://jrsoftware.org/ishelp/topic_setupcmdline.htm).
Der verfügbare echte AP3-Installer ist per SHA-256
`78a32ac25267ba72ae5cf11570c5c279a2cf62055710fe09cdea9d253415a792`
verifiziert; ein tatsächlich ausgeführtes AP3→AP4-Update wird nicht behauptet.

Die separate [Browser-CI, erster Versuch](https://github.com/junker-joerg/ims/actions/runs/36975712638/attempts/1)
bestand 39 von 40 Fällen. Der Bestandsfall „Geführter 100er 390 dark“ zeigte
Überlauf, weil Chromium die CSS-Datei mit `net::ERR_NO_BUFFER_SPACE` nicht laden
konnte. Screenshot und Networktrace belegen eine ungestaltete Seite. Lokal
und gegen den installierten CI-Build bestand derselbe Fall. Der fehlgeschlagene
CI-Job wurde ohne Änderung oder Abschwächung der Prüfung erneut ausgeführt.
Die [Wiederholung](https://github.com/junker-joerg/ims/actions/runs/36975712638/attempts/2)
bestand alle 40 Fälle. Damit sind am geprüften Produkthead `e6b546c` alle vier
erforderlichen Checks grün. Das vollständige
[Windows-Release-Gate](https://github.com/junker-joerg/ims/actions/runs/36975712703)
ist bestanden. Belege sind im
[Prüfprotokoll](ims_ap4_verification.json) nach Teststand zugeordnet.
Dieser nachfolgende Berichtskommitt verändert nur Bericht, Prüfprotokoll und
Übergabe; sein eigener aktueller CI-Stand ist separat zu prüfen.

## Offene Abnahme und nächster Schritt

AP4 bleibt im selben Draft-PR in Arbeit. Aktuelle CI-Ergebnisse prüfen; dann
den geführten Einstieg auf einem unabhängigen Windows-Rechner durchführen und
die tatsächliche Übungsdauer erfassen. Ein reales AP3→AP4-Update ist gesondert
zu belegen. Unabhängige Benutzerabnahme, Produktmerge und Veröffentlichung sind
offen. Die DORA-Benchmark-PDF blockiert diese Oberfläche nicht; G-BENCH/AP13
bleibt im Plan sichtbar.

Evernote-Ablage ist noch ausstehend, da in dieser Sitzung keine Evernote-
Schnittstelle verfügbar ist. Der ausführliche Zwischenstand ist hier und im
Draft-PR gesichert. `completion_evidence` bleibt bis zur vollständigen
Paketabnahme leer; AP5 startet erst nach übernommenem AP4-Status in main.
