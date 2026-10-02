# AP6: Arbeitsstand nach tatsächlichem AP5-Merge

**Aktuelle Umfangsentscheidung:** Der Auftraggeber hat den gekennzeichneten
BaFin-Referenzfall für AP6 ausdrücklich angenommen; [Beleg](ims_ap6_scope_acceptance.md).
Die nachstehende ursprüngliche Deutschlandprüfung bleibt als Herkunft erhalten.
Die Umsetzung wird mit diesem beschränkten Quellenumfang und sichtbar
bearbeitbaren Workshop-Annahmen im selben PR fortgesetzt.

**Aktuelle Lieferung:** M2/M3 des angenommenen Referenzumfangs sind implementiert:
Offline-Katalog, 40 stabile Modellidentitäten, begründete Overrides, vollständige
Neusortierung, Gewichte und disjunkte Reste; API, schreibfreies Demooriginal,
eigene Sitzung und frischer quellengebundener Einzel-VU-Export. Der
[Modellvertrag](../plans/ims_ap6_reference_mapping.md) und die
[Produktprüfung](ims_ap6_produktpruefung.md) erklären Handfälle und Grenzen.
10 Audit-, 10 Referenz-, 16 AP5- und 35 Plantests bestanden; neun verschiedene
Browserfälle einschließlich tatsächlichem 40×100-Lauf und korrigierter
Hell-/Dunkelmatrix bestanden. Frontend und Release-Metadaten alpha.6 geprüft.
M4 bleibt bis aktueller CI-/Installer-/installierter Prüfung offen. Danach
Anwenderabnahme anbieten; keine AP6-Merge-/Releasefreigabe. Die nachstehenden
ursprünglichen Deutschland-/Zugangsstände sind historische Meilensteine.


02.10.2026. [Paket-Draft-PR #295](https://github.com/junker-joerg/ims/pull/295),
Branch `codex/ims-german-market-top40`, Basis
`03f87662e85e6081998bab79e32ee12baac52da1` nach
[AP5-Merge #294](ims_ap5_merge.md). Eigene vorhandene editable Umgebung im
primären Checkout geprüft. [Authorized-Auftrag](../plans/ims_ap6_work_order.md)
vor AP6-Manifeständerung erfolgreich erzeugt; keine erfundene Freigabe.
Die übrigen Planannahmen und fachlichen Entscheidungstore bleiben erhalten.

## Fortschritt

- AP5-Abnahme, alle vier Checks des Abnahmekommitts und tatsächlicher main-Tree
  nachgewiesen. Aktuellen CI-Installer heruntergeladen; Größe und Hash geprüft.
- [Umsetzungsplan](../plans/ims_ap6_implementation.md) mit vier Meilensteinen
  im selben Paket-PR angelegt.
- [Methodenvorschlag](../plans/ims_ap6_data_method.md): gemeinsame Kennzahl/Jahr,
  Tochterkonsolidierung, Deutschland-/Direktgeschäft, vollständige Kandidaten,
  Rundung/Grenze 40/41, Spartenmix, Nenner und Rest erklärt. Vier fiktive Handfälle.
- [Quellenregister](../research/ims_ap6_sources_2026_10.json) mit sieben wirklich
  heruntergeladenen PDF-/Exceldateien einschließlich SHA-256, zwei ergänzenden
  Register-/Gruppenquellen und ausdrücklichen Evidenzgrenzen.
- Aktuelles BaFin-Portal direkt erreichbar; historische 403/404 sind kein
  pauschaler aktueller Zugangsblocker. Die Tabellen selbst haben fachlich einen
  anderen Umfang als die verlangte direkte deutsche Gruppenrangfolge.
- [Anleitung zu Fakten und Modellannahmen](../handbook/market_data_ap6.md)
  als Arbeitsfassung ergänzt; noch kein neu ausgeliefertes Produkt.
- Bereitgestellte Top-40-Arbeitsmappe vollständig gegen die drei BaFin-Originale
  geprüft: 326 Quellzeilen, 145 redaktionelle Gruppen, 663 Formeln ohne Fehler.
  [Prüfbericht](ims_ap6_top40_workbook_review.md), [versionierter Katalog](../research/ims_ap6_top40_2024_audit.json)
  und reproduzierbarer Prüfer mit zehn Tests ergänzt. Quellstriche als belegte
  Nullwerte aufgelöst; Originalmappe unverändert.

## Datenfrage und offene Lieferung

Auf die bisherige Datenfrage stellte der Auftraggeber
`Versicherungsgruppen_Top40_2024.xlsx` bereit und beauftragte „weiter gehts“.
Der Zugangsstand ist damit fortgeschritten: Für diese BaFin-Auswertung sind
vollständige Quellzeilen und Nichtauswahl vorhanden. Ihre Grenze 40/41
(Münchener Verein 877,204 / Itzehoer 843 Mio. Euro) ist unter der eingetragenen
Gruppierung präzisionsfest. Das ist kein Nachweis für den deutschen Direktmarkt:
Die Mappe benennt Ausland und übernommene Rückversicherung, verdiente Beiträge
und fehlende konzerninterne Eliminierung ausdrücklich. EWR-Kandidaten und
beobachtete Kfz-/Sach-/übrige Zweige fehlen weiterhin. Die historische Kontrolle
aller redaktionellen Gruppen ist nicht unabhängig fertig geprüft.

2024 ist das geprüfte Quellenjahr dieser Referenz, noch kein angenommenes
AP6-Rankingjahr. 2025 bleibt ein Datenkandidat; die KIVI-Studie wurde nicht
bereitgestellt oder bestellt. Ein konkreter
[vorläufiger BaFin-Referenzfall](../plans/ims_ap6_bafin_reference_proposal.md)
liegt zur Entscheidung vor. Die fachliche Rückfrage betrifft seinen anderen
Umfang, keine erneute AP6-Umsetzungsfreigabe. Ohne diese Entscheidung bleibt
die angenommene Deutschland-/Direktgeschäftsanforderung bestehen.

M1 ist begonnen, nicht vollständig abgenommen. M2–M4 sind offen: keine
belegte Auswahl, keine Top-40-DEMO, keine neue API/UI-Datenquelle oder Excel-
Abbildepipeline, keine AP6-Produktprüfung/Installerlieferung. AP6 ist
`in_progress`, technisch unvollständig; `selection_verified=false`.
Aktuelle Produktkennung bleibt alpha.5. Keine AP6-Merge-/Releasefreigabe und
keine AP7–AP14-Umsetzung.

## Prüfung und Fortsetzung

Die sieben Quelldateien wurden nur gelesen. Excel-Header/Fußnoten und PDF-Text
sowie gerenderte relevante Seiten wurden geprüft; Beträge und Studie nicht
als nachgewiesener Modelllauf ausgegeben. Aktuelle Prüfungen dieses Meilensteins:

- 35 Plan-/Freigabe-/Abhängigkeitstests bestanden (5,133 Sekunden).
- Sieben Quelldateigrößen und SHA-256 gegen die Downloads sowie neun eindeutige
  Quellen-IDs und 44 lokale Dokumentlinks geprüft.
- Tatsächlicher origin/main-Mergecommit und Tree nochmals abgeglichen.
- Gemeinsame Release-Metadaten alpha.5 / Windows 2.0.0.5 stimmen überein.
- `git diff --check` erfolgreich. Keine Änderungen am Simulationskern, API,
  Frontend oder Installerquellcode; der neue Rechercheprüfer hat eigene Tests,
  keine neue AP6-Produktprüfung behauptet.

Fortsetzung mit der gelieferten Mappe: zehn neue Audit-Tests bestanden; alle
326 Eingänge und 663 Formeln unabhängig geprüft. Aktuelle Nachweise stehen im
[Arbeitsmappenbericht](ims_ap6_top40_workbook_review.md); die obigen Zahlen
beschreiben den vorausgehenden Recherchemeilenstein.

Denselben Branch und Paket-Draft-PR fortsetzen. Die eingehende Tabelle ist
arithmetisch geprüft; zuerst Quellenumfang entscheiden und historische
Gruppen-/Spartenbelege vervollständigen. Methodenvorschlag mit realen Belegen
schließen. Danach M2–M4 aus
dem Umsetzungsplan liefern und passende Tests/Anleitung im selben PR ergänzen.
Beim Fortsetzen keine nachträgliche AP6-Abnahme oder Umsetzungsfreigabe für
weitere Pakete aus diesem Recherchekommitt ableiten.
