# AP6: Produktprüfung des gekennzeichneten BaFin-Referenzfalls

Produktkennung **2.0.0-alpha.6**, Windows 2.0.0.6.
[Draft-PR #295](https://github.com/junker-joerg/ims/pull/295).
Der [angenommene Umfang](ims_ap6_scope_acceptance.md) und
[erklärte Modellvertrag](../plans/ims_ap6_reference_mapping.md) gelten.
Maschinenlesbare Nachweise: [Verifikation](ims_ap6_verification.json).

## Vorhandene Lieferung

40 redaktionelle BaFin-Gruppen sind offline ladbar, mit stabilem Namen-/ID-/
Rangbezug. Der gepinnte Katalog enthält alle 326 Gesellschaftszeilen und 145
Kandidaten. Schreibfreies Demooriginal, eigene bearbeitbare Sitzung, Mix-/Override-
Bedienung und portable JSON-Wiederaufnahme sind an die wirkliche API angeschlossen.
Gewichte und zwei disjunkte Restkomponenten werden frisch abgeleitet; tatsächliche
Kfz-/Sach-/Rest-Aufteilung bleibt unbekannt und der verwendete Mix angenommen.

Der vorhandene AP5-Kern rechnet alle aktiven VUs/Sparten gemeinsam. Die
Referenz ergänzt keine Lebens-Nachfrage oder ICT-Kopplung. Einzel-VU-Excel
enthält dieselben Laufwerte sowie Originalwerte, URLs/Zellbezüge/Hashes,
Workshop-Annahmen und vollständiges Referenzbündel. Alte Exportnachweise werden
nach Quellenänderungen abgelehnt. Originalkataloge können nicht still geändert
und als recherchierte Fakten importiert werden.

Aktuelle Offline-Anleitung: [HTML](../handbook/market_ap6.html), aus IMS verlinkt,
mit Handrechnungen, vier Rollenwegen, Null-/Fehlend-Erklärung und echten Bildern.
Die Installer-Ressourcenliste enthält Katalog und Anleitung; die neue Paketnummer
wurde über die gemeinsame Release-Metadatenroutine gesetzt.

## Lokale Prüfungen

- 10 Audit- und 10 Referenztests bestanden, einschließlich Quellzeichen,
  exakter Quellen-/Restkonservation, Auswahländerung mit stabilen IDs,
  unverändertem Original, Override-Begründung, ungültigen Eingaben und Export.
- Allianz-Handfall unabhängig geprüft: Kfz-Ziel 79,66, Exposition 26,5533,
  Prämie 79,6599, Schaden 47,7959, Schlussaktiva 7.997,8640.
- 40 Gruppen über 100 Perioden; identische Prefixe gegenüber kurzem Lauf,
  Marktsumme = VU-Summe und Bilanzidentität in P1/P6/P100 beider Seiten geprüft.
  Browser zeigt die API-Schlusssumme aus demselben vollständigen 100er-Lauf.
- 16 AP5-Regressionsfälle bestanden, einschließlich ursprünglicher Handfälle,
  41×100, RNG-Bindung, Quellen-/Exportidentität und unveränderter AP3-Verträge.
- 35 Plan-/Freigabe-/Abhängigkeitstests bestanden; Frontend baut erfolgreich.
- Zwei echte Browser-Bedienwege bestanden: Original, Rechnung, Excel und
  JSON-Wiederaufnahme ohne externe Netzwerkaufrufe; eigene Sitzung, Mix,
  Rechtsträger-Override, neue Auswahl und entwertete Ergebnisse.
- Sechs aktuelle Browseransichten mit Hell/Dunkel und 1440×900, 1024×768,
  390×844 bestanden; aktiver Farbmodus explizit geprüft, keine Axe-Verletzung,
  Textkontrast mindestens 4,5:1, Tastaturweg und kein seitlicher Seitenüberlauf.
  Der zunächst falsch benannte Dunkel-Einstellungsschlüssel wurde bei der
  Bildkontrolle erkannt, korrigiert und die Matrix vollständig wiederholt.

Der ursprüngliche vollständige 100er-Quellenlauf dauerte lokal 69,517 Sekunden;
dies ist eine einzelne Messung, keine allgemeine Laufzeitgarantie. Keine neue
Behauptung historischer oder regulatorischer Gleichwertigkeit.

## Geprüfte Produktlieferung

AP6 ist im ausdrücklich angenommenen BaFin-Referenzumfang technisch fertig.
Produktkommitt `18748357a2c71b2b159b4b2f11b01b1d60072982`, Tree
`55e804b3b2865583a7a480a681fe278f96bbbec2`. Alle vier erforderlichen Checks
(Plan, Browser, Installer, Windows-Release-Gate) bestanden. GitHub prüfte den
PR-Mergekommitt `81febe295116a7c4e716a9425f9d64e77bdcff65`; dessen Eltern
sind das tatsächliche AP5-main und der Produktkommitt, sein Tree ist identisch.

- [Windows-Release-Gate](https://github.com/junker-joerg/ims/actions/runs/37024113216):
  2.735 Python-Tests, 14 Subtests, eine bestehende Warnung; 976,88 Sekunden.
  Frontend, Paket-/Portable-Smokes und der bisherige historische Corpusvertrag
  bestanden. Historische Vollgleichheit oder Produktionskalibrierung bleibt
  damit weiterhin nicht behauptet.
- [Browser-CI](https://github.com/junker-joerg/ims/actions/runs/37024113090):
  alle 59 Fälle bestanden, davon neun AP6-Fälle; keine übersprungenen,
  fehlgeschlagenen oder instabilen Fälle. Dauer 596,212 Sekunden.
- [Installer-CI](https://github.com/junker-joerg/ims/actions/runs/37024113101):
  echter alpha.6-Installer, 14 Lifecycle-Prüfungen bestanden, darunter Update
  im laufenden Betrieb, Datenübernahme, Deinstallation, Wiederinstallation und
  Datenerhalt. Alle 59 Browserfälle am installierten aktuellen Produkt bestanden
  (812,390 Sekunden); gesamter Lifecycle 839,464 Sekunden.

Der [heruntergeladene CI-Nachweis](https://github.com/junker-joerg/ims/actions/runs/37024113101/artifacts/11234474195)
enthält den geprüften Installer: **20.348.521 Bytes**, SHA-256
`8bcf7fc144c68026809988331c404cdc78d9deb86040f97a23313f4f804e4556`.
Archivgröße/-Hash, Binärgröße/-Hash, Produktversion alpha.6 und Windows-Dateiversion
2.0.0.6 wurden unabhängig abgeglichen. 357 Ressourcen sind nachvollziehbar;
354 Rohdateihashes stimmen mit diesem Checkout überein, drei Textdateien haben
im Windows-CI lediglich CRLF statt LF. Alle Inhalte entsprechen dem Produktkommitt.
Lokale Kopie: `dist/installer/verified-1874835/IMS-Setup-2.0.0-alpha.6-win-x64.exe`.

Der zusätzliche lokale Build vom sauberen Produktkommitt und isolierte Start
mit ausschließlich System32 im Kindprozess-PATH bestanden ebenfalls. Quellen-
JSON und Einzel-VU-Excel enthielten dasselbe vollständige Referenzbündel;
Offline-Anleitung und Bilder waren erreichbar. Die vorhandenen fünf
Startmenü-Verknüpfungen wurden unangetastet gelassen; der vollständige
Installer-Lifecycle wurde im separaten CI-Testkonto ausgeführt.

Der CI-Vorgängerinstaller alpha.0 enthält dasselbe alpha.6-Bundle. Damit ist
der Update-Lifecycle geprüft, kein echtes alpha.5→alpha.6-Anwendungsupgrade.
Eine unabhängige Anwenderprüfung auf einem Windows-Gerät ohne Entwicklerwerkzeuge
steht aus. Die Installer sind unsigniert; kein öffentliches Release wurde erstellt.

Die Abschlussdokumentation folgt diesem festgehaltenen Produktkommitt; aktuelle
Checks des abschließenden Dokumentationsstands sind im selben PR separat sichtbar.
Am 03.10.2026 wurden Anwenderabnahme und Mergeauftrag ausdrücklich erteilt;
[Beleg](ims_ap6_user_acceptance.md). Danach ist AP7 mit erhaltenen fachlichen
Toren beauftragt. Die ursprüngliche Deutschland-Abnahme bleibt unerfüllt;
AP7-Merge, öffentliches Release und AP8–AP14 sind nicht beauftragt.
