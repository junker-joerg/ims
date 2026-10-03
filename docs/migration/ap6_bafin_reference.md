# AP6: BaFin-Fakten und moderne Workshop-Abbildung

Der gekennzeichnete Umfang wurde separat [angenommen](../reports/ims_ap6_scope_acceptance.md).
AP6 liefert eine moderne Szenarioquelle; historische IMS-Dateien enthalten
keinen entsprechenden deutschen Top-40-Beitragskatalog.

| Herkunft | Neue Komponente | Fachliche Entsprechung / Abweichung |
| --- | --- | --- |
| BaFin 160/460/560, bereitgestellte Gruppierungsmappe 2024 | `seminar_cases/bafin_2024_catalog.json` | Gepinntes Original, 326 Zeilen, 145 redaktionelle Gruppen; verdientes Gesamtgeschäft, keine konzerninterne Eliminierung und kein vollständiger deutscher Direktmarkt. |
| Neu angenommene moderne Quellen-/Workshop-Abbildung | `ims.market.reference` | Stabile Identitäten, vollständige Neusortierung, getrennte Overrides, Gewichte, disjunkte Reste und explizite Skalierung. Kein historischer Kalibrierungskanal. |
| `IMSDATA.C` classBAV/Vuag/Vnag, `IMS.E` Aggregation; AP5-Mapping | unveränderter `ims.market.runner` | Gemeinsame VU-Bilanzen, Kunden-/Risiko-Zuordnung und echte Summen weiterhin aus AP5. Moderne Quellenobjekte sind keine historischen Pointer-/Aktivitätsstrukturen. |
| Bestehende begrenzte Lebens-/Krankenverträge | Quellenaufbau in `ims.market.reference` | Eine Modellpolice Leben, 100 Krankenpolicen je aktivierter Gruppe; deklarierte Mengen und Bilanzen, keine neue Nachfrage oder ICT-Kopplung. |
| API/UI/Einzel-VU-Export aus AP5 | `ims.api.market`, `MarketWorkbench`, `ims.market.export` | Referenzbündel mit frischer Rechnung und digestgebundenem Export; Original, Overrides und Modellwerte bleiben getrennt. |

Annahmen: Kfz/Sach/Rest zunächst 40/40/20 des breiten Nichtleben-Betrags;
0,01 Modellwährung je Mio. Euro Beitragsbasis, Preis 3, Schadenquote 0,6,
Anfangsaktiva 100 × Beitragsziel. Vierstellige Modellrundung ist sichtbar; das
Quellen-/Restledger behält exakte Dezimalwerte. Fehlende Beobachtungen werden
nicht als tatsächliche Nullwerte oder Unternehmensstrategien ausgegeben.

Risiken bleiben explizit: redaktionelle, nicht vollständig unabhängig historisch
geprüfte Gruppierung; fehlende EWR-/übrige Deutschlandabdeckung; keine beobachtete
Nichtleben-Zweigaufteilung; mögliche konzerninterne Rückversicherungsdoppelzählung.
Die Scope-Annahme beseitigt diese Grenzen nicht, sondern beschriftet sie am Fall.
