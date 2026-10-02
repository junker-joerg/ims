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

## Verbleibende Lieferprüfung

Aktuelle CI-, Installer-/Lifecycle- und installierte Browserprüfungen stehen
für den Produktkommitt noch aus. Die frühere AP5-Installerprüfung zählt nicht
als Prüfung von alpha.6. Technische Fertigstellung, Anwenderabnahme und Merge
werden nach diesen tatsächlichen Ergebnissen getrennt dokumentiert.
Keine AP6-Mergefreigabe; AP7–AP14 bleiben unbeauftragt.
