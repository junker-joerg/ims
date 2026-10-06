# AP7: tatsächliche Übernahme nach main

[PR #296](https://github.com/junker-joerg/ims/pull/296) wurde am **03.10.2026,
11:39:38 UTC** nach main übernommen. Mergekommitt
`32ba3112d994f57f33e64e1bc318e7d095223cd0`, Elternkommitt AP6-main
`88841290113a37faa6bf117d4cd67dcd9ff0867c`. Der ausdrücklich erteilte
[Anwenderabnahme-/Mergeauftrag](ims_ap7_user_acceptance.md) war Voraussetzung.

Der nach main übernommene Tree `236102cec1386f096b3d95417c962d95953764f2` ist
identisch zum vollständig geprüften Abnahmekommitt
`f440f4c7823eb029cb42c4c7219f6304d4205d37`. CI verwendete den Merge-Testkommitt
`a9d6cdedd2102622240219daf3302a3166570eef` mit demselben Tree und den beiden
Eltern AP6-main/Abnahmekommitt. Origin wurde nach Merge gefetcht und der lokale
main-Checkout ausschließlich per Fast-forward aktualisiert.

Alle vier Checks des exakt übergebenen Heads bestanden:

- [Planprüfung](https://github.com/junker-joerg/ims/actions/runs/37118688647/job/111190371358).
- [Release-Gate](https://github.com/junker-joerg/ims/actions/runs/37118688644/job/111190371224):
  2.755 Python-Tests, 14 Subtests, eine bestehende Warnung; 791,56 s.
- [Browser](https://github.com/junker-joerg/ims/actions/runs/37118688670/job/111190371103):
  70 bestanden, keine ausgelassenen/instabilen Fälle; 1.607,581 s.
- [Installer](https://github.com/junker-joerg/ims/actions/runs/37118688646/job/111190371264):
  14 Lifecycle-Prüfungen bestanden (1.230,198 s), alle 70 Browserfälle am
  tatsächlich installierten aktuellen Produkt bestanden (1.208,205 s).

Das tatsächlich heruntergeladene [Installer-Artefakt](https://github.com/junker-joerg/ims/actions/runs/37118688646/artifacts/11272882148)
enthält alpha.7, Windows-Dateiversion 2.0.0.7: **21.199.107 Bytes**, SHA-256
`321b22de571cee82bd8f3b12b40cac6305bd02dfba6a676b86d48dddade1d7de`.
Archiv-/Binärgröße und -Hash wurden unabhängig gegen GitHub/Buildnachweis
geprüft. Alle 372 Ressourcen sind identisch zur ursprünglichen Produktprüfung.
Alle vier vollständigen 100er-Ergebnisdigests sind im aktuellen Checkout und
installierten Produkt gleich und entsprechen auch der ursprünglichen Lieferung.
Der wiederholte Build derselben Produktfassung hat eigenen Kommitt-/Hashbezug;
historische Installerwerte werden nicht ersetzt.

Der CI-Vorgänger bleibt ein synthetischer Installer desselben Bundles.
Kein daraus abgeleitetes echtes alpha.6→alpha.7-Upgrade, unabhängiger
Clean-Windows-Test oder öffentliches Release. Allgemeine Anwenderabnahme bleibt
von gemessenen Testdetails getrennt. Die [Verifikation](ims_ap7_verification.json)
enthält Originalprodukt und spätere Abnahme-/Mergebelege separat.

Damit ist die AP7-main-Abhängigkeit erfüllt. „Fahre fort“ beauftragt das nächste
angenommene Paket AP8; sein authorized-Auftrag wird erst gegen dieses tatsächliche
main erzeugt. Der begrenzte Lebens-/ICT-Vertrag und die BaFin-/Workshop-Grenzen
bleiben erhalten. Kein AP8-Merge, öffentliches Release oder AP9–AP14-Auftrag.
