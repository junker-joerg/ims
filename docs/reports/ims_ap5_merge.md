# AP5: tatsächlicher Merge nach Anwenderabnahme

Am 02.10.2026 um **14:39:03 Uhr Europe/Berlin** wurde
[PR #294](https://github.com/junker-joerg/ims/pull/294) gemäß dem ausdrücklich erteilten
[Abnahme-/Mergeauftrag](ims_ap5_user_acceptance.md) per Squash nach main übernommen.
Mergecommit: `03f87662e85e6081998bab79e32ee12baac52da1`. Der primäre Checkout wurde anschließend
per Fast-forward aktualisiert und war sauber. Danach begann AP6 im eigenen Branch.

Geprüfter Abnahmekommitt: `525916c5f011daa52ac6793fef7587fd9f0ca347`.
Merge- und Head-Tree: `aa3d20160678ee3ea9571e08bf54d497904c8485`, exakt gleich.
Der CI-Mergecommit `77ae508f778be5d4656151095b125752cab21aa2` hat denselben Tree und die Eltern
AP4-main `9b0d45a22be4314eda8e9ab1db61c506a44160f7` und den Abnahmekommitt.
Die Änderungen seit dem abgenommenen Produkthead 417a0ca sind Dokumentation;
kein Modell- oder Oberflächenwechsel nach der Zustimmung.

| Erforderlicher Check am Abnahmekommitt | Ergebnis | Nachweis |
| --- | --- | --- |
| browser | erfolgreich | [Lauf](https://github.com/junker-joerg/ims/actions/runs/37005747120/job/110833482259) |
| installer | erfolgreich | [Lauf](https://github.com/junker-joerg/ims/actions/runs/37005747112/job/110833477481) |
| Plan prüfen und Codex-Auftrag vorbereiten | erfolgreich | [Lauf](https://github.com/junker-joerg/ims/actions/runs/37005747170/job/110833477403) |
| release-gate | erfolgreich | [Lauf](https://github.com/junker-joerg/ims/actions/runs/37005747117/job/110833477280) |

Der tatsächlich heruntergeladene [CI-Installer](https://github.com/junker-joerg/ims/actions/runs/37005747112/artifacts/11225699767)
trägt **2.0.0-alpha.5** / Windows **2.0.0.5**,
19.914.327 Bytes und SHA-256 `48124d3863528aa9726c78e32642b50c71830bf3a87dbe12da72a424705793a5`.
Archivgröße und SHA-256 stimmen mit dem GitHub-Artefakt überein.
14 Lifecyclefälle sowie 50 installierte Browserfälle bestanden; Browser:
keine unerwarteten, übersprungenen oder flakigen Fälle. Exakte Metadaten,
Laufzeiten und Checks: [Prüfprotokoll](ims_ap5_verification.json), `main_merge`.

Der Lifecycle-Vorgänger ist ein synthetisches Binary desselben Bundles.
Ein echter alpha.4→alpha.5-Updateversuch oder unabhängig gemessene
Clean-Windows-Anwendertestdetails sind weiterhin nicht nachgewiesen.
Die allgemeine menschliche Produktabnahme bleibt davon getrennt bestätigt.
Die offene Ursache sporadischer lokaler HTTP-Verbindungsresets bleibt im
Abschlussbericht dokumentiert. Es wurde kein öffentliches Release erzeugt.

Der Fortsetzungsauftrag autorisiert nach diesem tatsächlichen Merge AP6.
[AP6-Auftrag](../plans/ims_ap6_work_order.md) und
[Umsetzungsplan](../plans/ims_ap6_implementation.md) benennen seine weiterhin
verbindlichen Daten-/Methodentore. Keine Freigabe für AP6-Merge oder AP7–AP14.
