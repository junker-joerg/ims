# AP8 alpha.11 · Produktprüfung von Modellwelt und Dokumentation

Erfasst 2026-10-06T07:47:16.480702+00:00. Technisch fertig im selben [Paket-PR #297](https://github.com/junker-joerg/ims/pull/297). Produkt 2.0.0-alpha.11, Windows 2.0.0.11. Anwenderabnahme und Merge bleiben offen. Kein öffentliches Release oder AP9–AP14-Auftrag.

## Ergebnis und Herkunft

Vier weitere Designreferenzen sind in die gemeinsame Oberfläche eingeflossen: auswählbare Modellwelt mit Quellen-/Grenzeninspektor, Unternehmensportfolio mit Suche/Seiten/Anzeigevergleich und Fokus im selben Vorstandseditor, Wiedergabe vollständig berechneter Perioden und aktuelle Szenario-/Entscheidungsführung. Bestehende vier Schritte, sechs Auswertungen und E08-01 bleiben erhalten. Vorstandsstrategien sind endogen; Kunden folgen eigenen Regeln; äußere Ereignisse sind exogene Annahmen.

37 fachliche Eingabegruppen und alle 191 input/select/textarea-Deklarationen in 19 TSX-Komponenten dokumentiert. Drei skalierbare SVGs erklären Architektur, tatsächliche AP7-Periodenplanung/Buchung sowie fachliche Abweichungen zum ursprünglichen IMS. C-Herkunft: IMS.E/Vrvu01/Vrvn06/aktive Anbieter, IMSDATA.C-Zustände/Aggregate, ESS.C-Aktionszeit. Der aktuelle gemeinsame Markt rechnet weiterhin moderne Kohorten, deklarierte Risikoflüsse, gebundene VU-Zufallszüge und die angenommenen AP7-Erweiterungen. Keine vollständige C/Python-Identität behauptet.

Aktuelle Einstiegstexte und Menüwege aktualisiert, historische Abnahmen/Pläne/Produktbelege erhalten. Neue Handbuch-/Inventar-HTMLs, JSON-Inventare, drei SVGs und sechs neue Browserbilder sind kontrolliert im authentischen Installer enthalten. [Eingaben](../handbook/eingabeinventar.md), [Rechenkern](../handbook/rechenkern.md), [Dokumentationsaudit](ims_ap8_documentation_audit.md).

## Korrigierte Vorprüfung

Der erste Release-Gate-Lauf an f9e6b05 meldete 2.763 bestandene Tests/14 Subtests und eine veraltete Dokumentationserwartung: Der aktuelle Handbuchindex sollte noch „Handbuchstand: PR178a“ enthalten. Die bestehende Prüfung kontrolliert jetzt heutige Menüwege und vorhandene Eingabe-/Rechenkernziele; der historische Seminarlink bleibt geprüft. [Ursprünglicher Fehlerlauf](https://github.com/junker-joerg/ims/actions/runs/37422825328/job/112135769482). Die folgenden vier Prüfungen gehören zum korrigierten Produktpunkt.

## Vier tatsächliche Produktchecks

Produktkommitt `6117b72eb48a05d93b73e354099e5528a8b0ba6b`, Tree `4b8c247ad42064145a8bee6053b1027bec373ccc`. CI-Prüfmerge `f3ecba92ece38f6a2a37afb4167d5fbea1ee016d` hat denselben Tree und Eltern AP7-main `32ba3112d994f57f33e64e1bc318e7d095223cd0` sowie Produktkommitt. Dies ist kein AP8-Merge nach main.

- [Planprüfung](https://github.com/junker-joerg/ims/actions/runs/37426574847/job/112147468593): erfolgreich.
- [Release-Gate](https://github.com/junker-joerg/ims/actions/runs/37426574862/job/112147594111): 2.764 Python-Tests, 14 Subtests, 1 bekannte Warnung; 1182.56 s.
- [Checkout-Browser](https://github.com/junker-joerg/ims/actions/runs/37426574864/job/112147756300): 99 Fälle, 0 übersprungen/fehlgeschlagen/flaky; 2512.993 s.
- [Installer](https://github.com/junker-joerg/ims/actions/runs/37426574893/job/112147638391): echter Build; 14 Lifecycle-Prüfungen und 99 installierte Browserfälle, alle bestanden. Updategegenstück `synthetic_same_bundle`, keine externe Altinstallation behauptet.

99 Browserfälle umfassen die bisherigen 91 sowie acht neue Fälle: gemeinsame Quelle/Fokus/Anzeige in Hell/Dunkel bei 1440/1024/390 Pixeln, Offline-HTML/SVG und BaFin-Paginierung/Suche. Tastatur, AXE und Seitenbreite geprüft; Filter/Wiedergabe behalten den Modelldigest ohne zusätzliche Rechnung. Gemessener Mindestkontrast der sechs bestehenden Kontrastproben: 5.300:1. Das ist kein pauschaler Nachweis menschlicher Verständlichkeit.

## Unveränderte Modellnachweise

| Fall, 100 Perioden | Checkout | Installiert | Wire-Bytes | Modelldigest |
| --- | --- | --- | --- | --- |
| `us_hyperscaler_outage` | 149.239 s | 115.186 s | 27.994.700 | `7ee786bf1266f74c4e95aaca4f01bd50e60c1a9c708cea6169d1be32b8b10c66` |
| `google_motor_entry` | 150.894 s | 108.903 s | 27.920.690 | `8d5e165ab934891c5abedf1d10dce231d06e0bcbc5b69844b98dc7514611225f` |
| `life_demand_shock` | 158.341 s | 113.396 s | 27.561.354 | `b5e4dcc1f876e5f76ec6ebf6abdef705eec1a975a1d750a36205dbfb191ae96a` |
| `dora_2_workshop` | 153.818 s | 109.629 s | 28.024.102 | `f2a21bdc95f946eb77b479f489dd81b7ec0308ccbde9fabe8e1f48fc2c3c2a38` |

Alle vier AP7-Digests bleiben erhalten. Checkout und installiertes Produkt stimmen bei Modell-/Ansichtsdigest, vollständiger Übertragung und 25er-Prefixen überein. Dateien unter python_port/ims/market gegenüber alpha.10 unverändert. Keine Erweiterung der Kernverträge durch die UI.

## Installer und Ressourcen

`IMS-Setup-2.0.0-alpha.11-win-x64.exe` · 29.277.186 Bytes · SHA-256 `376a3c1d3d5d67eea8949170747c976fa0128951f71d2345ab0c0e961dd3ebef`.
[Authentisches Actions-Artefakt](https://github.com/junker-joerg/ims/actions/runs/37426574893/artifacts/11397180032); lokal `dist/installer/IMS-Setup-2.0.0-alpha.11-win-x64.exe`. Archivgröße und GitHub-SHA sowie EXE-Größe/SHA gegen Build-/Lifecyclebelege geprüft. Kein öffentliches Release.

424 versionierte Ressourcen gegen den eingefrorenen Git-Tree geprüft: 86 roh identisch; 338 ausschließlich Windows-CRLF-Konversion. 40 AP8-PNGs, drei neue SVGs, 28 Bildreferenzen in der aktuellen AP8-Anleitung. Neue HTML-/SVG-Ziele wurden im installierten Browser erreichbar geprüft; beide JSON-Inventare sind durch den Ressourcenvergleich gegen ihre versionierten Quellen gebunden.

## Offene fachliche und menschliche Grenzen

Pause und Einzelschritt betreffen nur die Anzeige, keinen gespeicherten Kerncheckpoint. Neue Entscheidungen benötigen eine vollständige neue Rechnung. BaFin einschließlich Ausland/Rückversicherung und redaktioneller Gruppen bleibt Workshop-Referenz, kein belegter deutscher Direktmarkt. SCR/MCR/Solvenz, dynamische Insolvenz, Konzerneliminierung, spartenübergreifende Finanzierung und Claims-Queue-abhängige Auszahlung bleiben außerhalb des Vertrags. Installer unsigniert; Lifecycle-Update nur am synthetischen gleichen Bündel. Wissenschaftlicher Produktionskorpus und historische Vollgleichheit behalten ihre eigenen offenen Grenzen.

Anwenderabnahme, externe saubere Windows-Abnahme und AP8-Merge sind nicht erteilt. [Maschinenlesbare Verifikation](ims_ap8_modelworld_verification.json). Frühere [alpha.10-Prüfung](ims_ap8_cockpit_produktpruefung.md) bleibt unverändert historisch.
