# AP6: tatsächlicher Merge nach Anwenderabnahme

Am 03.10.2026 um **08:28:46 Uhr Europe/Berlin** (06:28:46 UTC) wurde
[PR #295](https://github.com/junker-joerg/ims/pull/295) gemäß dem ausdrücklich
erteilten [Abnahme-/Mergeauftrag](ims_ap6_user_acceptance.md) per Squash nach main
übernommen. Mergecommit: `88841290113a37faa6bf117d4cd67dcd9ff0867c`.
Der gefetchte Stand `origin/main` und der anschließend per Fast-forward
aktualisierte lokale main stimmen damit überein; der Checkout war sauber.
Danach wurde `codex/ims-market-shock-demos` von diesem Stand angelegt.

Geprüfter Abnahmekommitt: `a2787a9592af858bd00b7ae733cfd99d8c8d9e87`.
Merge- und Head-Tree: `82ea185836c4636bd9ccdb8679c78b7cf35965f7`, exakt gleich.
Der CI-Mergekommitt `3576f211726b6ee8f79fbbdafd80044ea5bbaf1d` hat denselben Tree
und die Eltern AP5-main `03f87662e85e6081998bab79e32ee12baac52da1` und den
Abnahmekommitt. Tatsächlicher Squash-Merge hat den genannten AP5-main als Eltern.
Seit dem abgenommenen Produkthead 70c0431 wurde nur dessen Abnahme dokumentiert.
Alle 357 Installerressourcen stimmen in ihren Rohdatei-Hashes mit dem
abgenommenen CI-Produkt überein.

| Erforderlicher Check am Abnahmekommitt | Ergebnis | Nachweis |
| --- | --- | --- |
| installer | erfolgreich | [Lauf](https://github.com/junker-joerg/ims/actions/runs/37101841560/job/111142752606) |
| release-gate | erfolgreich | [Lauf](https://github.com/junker-joerg/ims/actions/runs/37101841558/job/111142752478) |
| browser | erfolgreich | [Lauf](https://github.com/junker-joerg/ims/actions/runs/37101841548/job/111142752378) |
| Plan prüfen und Codex-Auftrag vorbereiten | erfolgreich | [Lauf](https://github.com/junker-joerg/ims/actions/runs/37101841552/job/111142752326) |

Der tatsächlich heruntergeladene [CI-Installer](https://github.com/junker-joerg/ims/actions/runs/37101841560/artifacts/11266503098)
trägt **2.0.0-alpha.6** / Windows **2.0.0.6**, 20.348.136 Bytes und SHA-256
`487908e6271497d492fbe6f2a6066160deebb954f0b526332152af63dfb45296`.
14 Lifecycle- und 59 installierte Browserfälle bestanden; keine unerwarteten,
übersprungenen oder flakigen Browserfälle. Release-Gate: 2.735 Python-Tests und
14 Subtests bestanden; separater Browsercheck: 59 Fälle. Archivgröße und SHA-256,
Build-, Laufzeit- und Commitbezug: [Prüfprotokoll](ims_ap6_verification.json),
`main_merge`. Der CI-Kommitt ist vor dem Merge erzeugt; sein identischer Tree
belegt den Bezug zum übernommenen Inhalt.

Die Abnahme gilt weiterhin für **„BaFin-Gruppenauswertung 2024 – Workshop“**,
keine vollständige deutsche Direktmarktrangfolge oder verifizierte Konzern-
eliminierung. Ursprüngliche Daten-/Methodentore bleiben sichtbar offen.
Der Lifecycle-Vorgänger ist ein synthetisches Binary desselben Bundles; daraus
folgt kein echter alpha.5→alpha.6-Updateversuch oder unabhängig gemessener
Clean-Windows-Anwendertest. Allgemeine menschliche Produktabnahme ist bestätigt;
konkrete Anwender-Testdetails bleiben unbekannt. Kein öffentliches Release erzeugt.

Der Fortsetzungsauftrag autorisiert jetzt AP7.
[Arbeitsauftrag](../plans/ims_ap7_work_order.md) wurde erst nach diesem tatsächlichen
Merge gegen gefetchtes main erzeugt. Die Lebens-Nachfrage- und ICT-Zeit-/
Buchungsverträge benötigen die im angenommenen Plan vorgeschriebene konkrete
fachliche Annahme. Keine AP7-Merge-/Veröffentlichungsfreigabe oder AP8–AP14-Arbeit.
