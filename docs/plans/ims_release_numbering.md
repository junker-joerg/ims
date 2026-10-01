# Eindeutige Release-Nummern und sichtbarer Versionsstand

Auftrag vom 01.10.2026: „Ab jetzt eindeutige Releasenummern vergeben und auf
dem Startbildschirm unten links anzeigen“. AP1/AP2 und der frühe AP3-Installer
trugen 2.0.0-alpha.1; allein dieser Name unterschied die Funktionen nicht.
Der neue AP3-Stand erhält 2.0.0-alpha.3. Alte Abnahmeberichte/SHA-Belege bleiben
historisch erhalten. Dies ändert keine Modellsemantik und portiert keine C-Regel.

Gemeinsame Quelle: `python_port/ims/release.py`. Python- und npm-Paketmetadaten
werden beim Versionswechsel gemeinsam aktualisiert und vor dem Installerbau
geprüft. Höhere neue Nummern sind Pflicht; gleiche oder kleinere Nummern werden
vom Versionswechselwerkzeug abgewiesen. Wiederholungsbuilds desselben Releases
werden zusätzlich über Commit/SHA ausgewiesen. Ein neuer ausgelieferter
Produktstand darf eine bereits ausgelieferte Nummer nicht wiederverwenden.

Installer und CI verwenden den daraus abgeleiteten Dateinamen und die vierteilige
Windows-Version. Inno Setup hat keine stille alte Standardversion mehr.
Der sichtbare Release-Stand kommt aus der gebauten Oberfläche, wird unabhängig
von den übrigen Metadaten mit `/api/version` abgeglichen und bleibt auch bei
API-Fehlern lesbar. Unterschiedliche Oberflächen-/Anwendungsversionen zeigen
einen verständlichen Hinweis zum Neustart/Neuladen.

Die Anzeige steht auf Desktop unten links in der Sidebar, auf kleinen Geräten
unter der unteren Navigation. Navigation, Eingaben und Modellfreigaben behalten
ihre bisherigen Verträge. Prüfung: konsistente Versionen/monotoner Wechsel,
Backend-Endpunkte, echte Browser in drei Breiten und beiden Farbmodi samt
Fehler/Versionskonflikt; neu gebauter tatsächlicher Installer inklusive
installierter Browserabnahme. Die Änderung bleibt im bestehenden AP3-PR #290;
Merge und öffentliche Veröffentlichung bleiben einer Freigabe vorbehalten.
