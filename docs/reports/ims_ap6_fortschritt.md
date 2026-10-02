# AP6: Arbeitsstand nach tatsächlichem AP5-Merge

02.10.2026. Branch `codex/ims-german-market-top40`, Basis
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

## Datenfrage und offene Lieferung

Die vollständige nutzbare Rangbasis ist nicht vorhanden. Öffentlich geprüft sind
BaFin-Daten 2024, GDV-Aggregate und die KIVI-Studienankündigung 2025. Keine dieser
geprüften Quellen liefert bereits eine vollständige nach dieser Methode
konsolidierte Auswahl samt Rang 40/41. 2025 ist ein Datenkandidat, kein
angenommenes gemeinsames Datenjahr. Die KIVI-Studie selbst wurde nicht bestellt
oder bereitgestellt; ihre genaue Gruppen-/Deutschlandabgrenzung ist offen.

Dem Auftraggeber wurde die konkrete Datenfrage gestellt: Ist KIVI MAS 2025 oder
eine vergleichbare nutzbare Rang-/Tochtertabelle verfügbar, und wo liegt sie?
Eine Antwort bzw. der Datenzugang steht noch aus. Die Methodenprüfung muss
anschließend auch öffentliche Regionalgruppen, EWR-Geschäft, Spartenmix und
Veröffentlichungs-/Rundungsgrenzen abdecken. Weder eine Liste bekannter Namen
noch eine ungeprüfte Zusammenrechnung der BaFin-Ränge schließt dieses Tor.

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
  Frontend, Tests oder Installerquellcode; keine neue AP6-Produktprüfung behauptet.

Denselben Branch und Paket-Draft-PR fortsetzen. Zuerst eingehende vollständige
Tabelle mit Nutzbarkeit, Jahr, Maß, Deutschland, Rechtsträgern und Gruppen
prüfen; Methodenvorschlag mit realen Belegen schließen. Danach M2–M4 aus
dem Umsetzungsplan liefern und passende Tests/Anleitung im selben PR ergänzen.
Beim Fortsetzen keine nachträgliche AP6-Abnahme oder Umsetzungsfreigabe für
weitere Pakete aus diesem Recherchekommitt ableiten.
