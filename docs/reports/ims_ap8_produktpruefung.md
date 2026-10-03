# AP8: Produktprüfung der sechs verknüpften Marktansichten

Erfasst 2026-10-03 17:18:19 +02:00 (Europe/Berlin). **AP8 technisch fertig**, Produkt **2.0.0-alpha.8**, Windows
**2.0.0.8**, ein [Paket-PR #297](https://github.com/junker-joerg/ims/pull/297).
[Maschinenlesbare Verifikation](ims_ap8_verification.json),
[Abschluss](ims_ap8_abschlussbericht.md),
[Offline-Anleitung mit zwölf echten Bildern](../handbook/market_ap8.html).
Anwenderabnahme und Merge für AP8 bleiben offen; kein öffentlicher Release.

## Anwendernutzen und nachvollziehbare Auswertung

Markt-/Spartenverlauf, Modellanteile/HHI, aktuelle Strategiefamilien mit Gewichten
und Streuung, tatsächlich wirksame Kundenwechsel, Ereignis-/Entscheidungszeitlinie
und Provider-/Prozess-/Wiederanlaufansicht lesen dieselbe frische Rechnung.
Periode, Sparte, Gruppe und Vergleichsseite gelten gemeinsam; Rollen und Fokus
erhalten den Lauf. E08-01 aus dem separat angenommenen Boardplan/PR #292 ist
mit eigener Herkunft umgesetzt: absolute Ergebnisse und relative Position von
Fokus, Rivalen und Modellmarkt mit sichtbarem vollständigem Nenner.

ICT wird durch rote Ausfallstunden, konkrete transitive Abhängigkeiten,
tatsächlich wirksame Ersatzpfade, gemeinsame Arbeitseinheiten, ausgewählte
Warteschlangen und Erholung sichtbar. Ereignis, verfügbare Kapazität, erledigter
Vorgang und Buchung bleiben unterscheidbar. Gemeinsame Ressourcen werden nicht
je VU addiert; Vorgangszahl ist keine Arbeitseinheit. Retrospektive Pläne bedeuten
kein damals verfügbares Wissen. AP7 verwendet 24 Prozessstunden, keinen Kalender.

Diagramme bieten die zugängliche Datentabelle und den konkreten VU-/Sparten-
Beitrag. Geld-/Anteilswerte verwenden exakte Dezimalarithmetik; Fließkommazahlen
positionieren nur SVG. Die Buchungsbrücke erfüllt Ergebnis und Eigenkapital ohne
Rest und ohne doppelte Kosten-/Leistungsbuchung. Exakte Addition, belegter Kanal,
gemeinsame Wirkung und beobachtete Korrelation sind ausdrücklich erklärt.

Ein unabhängiger Handfall mit ab P6 erschöpften VU-Kapazitäten erzeugt 40 Schaden
ohne Vertragsträger: **0 VU-Risikoaufwand und 40 unversicherter Schaden**. Die
Oberfläche zeigt beide getrennt; die Klassifikation ist kein zusätzlicher Verlust.
Der ursprüngliche Kern hatte korrekt gebucht; korrigiert wurde die Anzeige.

Reine Projektion `ims.market-explorer-result.v1`, API `/api/market/explore`
unter der vorhandenen Rechensperre, unveränderter Modell-Digest und eigener
Ansichtsdigest. Filter ändern keine Rechnung. Original-JSON und Einzel-VU-Excel
werden frisch an den Modellnachweis gebunden. Ungültige Quellen/Budgetüberschreitung
liefern keine halbe Ansicht. [C-/Python-Herkunft](../migration/ap8_market_explorer.md)
benennt vorhandene BAV-/VU-/VN-Aggregate und moderne Auswertung. Finanz-, Risiko-,
Nachfrage-, Garantie-, FIFO- und RNG-Kerne blieben unverändert.

## Tatsächliche CI-Prüfungen am festgehaltenen Produkt

Produktkommitt `17cbf5e631233ff5e5f5153a673a2eb6adaa7375`, Tree
`c901285842f2d6a999f6dbd3b4ddc0f498a59816`. GitHub-Prüfmerge
`33ea51d7737333b355e3661d66783f4f0b59192f` hat denselben Tree und die Eltern tatsächliches
AP7-main `32ba3112d994f57f33e64e1bc318e7d095223cd0` und Produktkommitt.
Dies ist kein AP8-Merge nach main. Alle vier erforderlichen Checks erfolgreich:

- [Planprüfung](https://github.com/junker-joerg/ims/actions/runs/37130011519/job/111223078144).
- [Windows-Release-Gate](https://github.com/junker-joerg/ims/actions/runs/37130011518/job/111223078352): **2.764 Python-Tests + 14 Subtests**,
  1 bestehende Warnung, 761.63 s; Frontend-/Paket-/Portable-Prüfungen bestanden.
- [Browser-CI](https://github.com/junker-joerg/ims/actions/runs/37130011512/job/111223078170): **83 echte Fälle**, darunter 13 AP8-Fälle,
  2352.401 s.
- [Installer-CI](https://github.com/junker-joerg/ims/actions/runs/37130011564/job/111223078338): **14 Lifecycle-Prüfungen**,
  2193.677 s; **83 Browserfälle am tatsächlich installierten Produkt**,
  2165.621 s.

Kein übersprungener, fehlgeschlagener oder instabiler Browserfall; Test-Retry 0.
Vier frische 100er-AP8-Rechnungen prüfen alle sechs Ansichten, Originalbuchungen,
vollständige Anteilsnenner, Gewichte/Familien, lokale Filter, exakte 25er-Prefixe
und erhalten die übernommenen AP7-Modell-Digests. Checkout und installierte
Anwendung liefern dieselben Modell-/Ansichtsdigests und vollständigen Antwortbytes.
Der Prefixvergleich umfasst alle periodischen Tabellen bis P25; die ausdrücklich
horizontabhängigen `terminal_process_rows` werden nicht als identisch behauptet.

| Fall | Checkout-Rechnung/Anzeige | Installierte Rechnung/Anzeige | AP8-Antwortbytes | Erhaltener AP7-Modell-Digest |
| --- | --- | --- | --- | --- |
| `us_hyperscaler_outage` | 155.234 s | 137.064 s | 27.994.700 | `7ee786bf1266f74c4e95aaca4f01bd50e60c1a9c708cea6169d1be32b8b10c66` |
| `google_motor_entry` | 155.319 s | 137.611 s | 27.920.690 | `8d5e165ab934891c5abedf1d10dce231d06e0bcbc5b69844b98dc7514611225f` |
| `life_demand_shock` | 166.495 s | 141.080 s | 27.561.354 | `b5e4dcc1f876e5f76ec6ebf6abdef705eec1a975a1d750a36205dbfb191ae96a` |
| `dora_2_workshop` | 158.037 s | 137.164 s | 28.024.102 | `f2a21bdc95f946eb77b479f489dd81b7ec0308ccbde9fabe8e1f48fc2c3c2a38` |

Alle AP8-Antworten unter 40 MiB. Zeiten sind Einzelmessungen dieser CI-Maschinen,
keine allgemeine Laufzeitgarantie. Die Tabellenzeit umfasst jeweils frische
100er-Rechnung, Ansichtsprüfungen und 25er-Prefixvergleich. Neun kleine AP8-Tests prüfen unabhängig
90/10-Gewichte, HHI 8.200, Quote 12 %, Rundung, Null-/negative Nenner, mehrere
Sparten, wirksame Wechsel, unversicherte Verluste, dynamische Mitgliedschaft,
Reinheit, einmalige Kosten, Exportbindung und geteilten Rechenausschluss.

Hell/Dunkel × 1440×900, 1024×768, 390×844: Tastatur/Rollen/Slider,
keine Axe-Verstöße und kein Seitenüberlauf; kleinster gemessener Textkontrast
5.32:1 im Checkout und 5.32:1 installiert.
Leere/undefinierte Daten erhalten keine erfundenen Nullbalken. Quellenreste und
angenommener Mix sind getrennt von Modellwährung sichtbar. Eigene JSON-Sitzung,
ungültiger Import, Entwertung alter Ergebnisse, frisches JSON/Excel und alle
zwölf tatsächlich erreichbaren Anleitungsbilder sind geprüft.

## Installer und Ressourcenbindung

[Authentisches CI-Artefakt](https://github.com/junker-joerg/ims/actions/runs/37130011564/artifacts/11277137832), EXE **21.933.992 Bytes**,
SHA-256 **`9ddb429db03bd11a06a8ec0750f2e9d11c11393f7eddc379035765fbdb858f38`**. Archiv- und EXE-Größe/-Hash stimmen unabhängig
mit GitHub, Build und Lifecycle überein. Sauberer Buildkommitt, Version und
Windows-Dateiversion sind geprüft. **387 Ressourcen** entsprechen
dem festgehaltenen Git-Tree (58 unveränderte Git-Blobs, 329 ausschließlich
Zeilenendenkonvertierungen), darunter Offline-Anleitung und zwölf AP8-Bilder.
Der ausgelieferte lokale Download unter `dist/installer` ist diese geprüfte CI-EXE.

Installation, API-/Modellausführung, Export, Update, Datenerhalt und Deinstallation
wurden tatsächlich automatisiert geprüft. Die vorhergehende Fassung ist ausdrücklich
ein synthetischer Vorgänger desselben aktuellen Bundles; dies belegt keinen echten
historischen alpha.7→alpha.8-Upgradepfad. CI-Windows besitzt Entwicklerwerkzeuge;
der ausführbare PATH war auf System32 beschränkt. Eine zusätzliche externe
Clean-Windows-Anwenderabnahme wurde nicht durchgeführt. Installer unsigniert.

Korrigierter lokaler Build am Vorpunkt 23e493b: SHA `c0351feed699c67ccb94c6f76da8d97ad587a31219a546a5f41911b517398adf`,
76.71 s;
drei gezielte Browserfälle an der direkt ausgeführten Frozen-App bestanden.
Dies ist keine Installation. Der lokale Lifecycle-Schutz bei vorhandenen
Benutzer-Startmenülinks wurde nicht umgangen. Frühere lokale Iterationen,
Bild-404/Labelkorrektur und Transportabbruch sind getrennt dokumentiert,
nicht als grüne Gesamtabnahme gezählt.
Am Vorpunkt 23e493b bestanden in beiden CI-Umgebungen alle 13 neuen AP8-Fälle;
sechs ältere Versionsprüfungen verlangten irrtümlich alpha.7 statt alpha.8.
Dadurch brach der damalige Lifecycle ab. Die genaue Release-Erwartung wird jetzt
aus den gemeinsamen Metadaten gelesen; erst der neue vollständige grüne Lauf
zählt als technische Fertigstellung. Die Korrektur änderte keine Produktressource.

## Umfang, Übergabe und offene Freigaben

AP7 wurde nach ausdrücklicher Anwenderabnahme tatsächlich nach main übernommen;
AP8-Auftrag wurde danach und vor Änderung seines Status gegen dieses frisch
gefetchte main autorisiert. M1–M4
sind im selben Paket geliefert. Keine zusätzliche menschliche Vertragsannahme
erfunden, keine historische Abnahme rückwirkend erweitert. AP8 done bedeutet
technisch fertig; **Anwenderabnahme pending, Merge nicht freigegeben, main unverändert**.
Der finale Dokumentationshead ist vom hier geprüften Produktkommitt zu unterscheiden.

BaFin-Referenz bleibt verdiente Beiträge einschließlich Ausland/Rückversicherung,
redaktionelle Gruppen ohne konzerninterne Eliminierung; deutscher Direktmarkt,
vollständige Spartenkalibrierung und reale Providerprofile bleiben offen.
Claims/Service koppeln nur administrative Arbeit/Kosten, keine verzögerten
Versicherungszahlungen. Hypothetische DORA-Annahmen sind keine Konformitätsprüfung.
Das technische Release-Gate bleibt von der gesperrten wissenschaftlichen
Produktionsfreigabe und unbelegten historischen Vollgleichheit getrennt.

AP9 benötigt AP8 tatsächlich in main und einen neuen menschlichen Folgeauftrag.
Kein AP9–AP14-Auftrag und kein öffentlicher Release. Evernote-Ablage ausstehend:
keine verfügbare Werkzeugverbindung in dieser Sitzung; vollständige Berichte im PR.
