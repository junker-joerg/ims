# AP5: gemeinsamer moderner Markt

Aktuelle Einordnung 06.10.2026: Dieser Text beschreibt den AP5-Vertrag. Spätere AP6-/AP7-Erweiterungen liefern den gekennzeichneten BaFin-Referenzfall, Lebens-Neugeschäft und begrenzte Markt-/ICT-Kopplung. Der [heutige Rechenkernüberblick](../handbook/rechenkern.md) unterscheidet diese Ergänzungen von AP5-Grenzen.

Der am 02.10.2026 angenommene [Marktvertrag](../plans/ims_ap5_market_contract.md)
ist eine eigene deklarierte Modellrechnung. AP3-Verträge und historische
25er-Validatoren bleiben erhalten. Keine vollständige historische Gleichheit.

| Herkunft | Moderne Komponente | Entsprechung / erklärte Abweichung |
| --- | --- | --- |
| `IMS.E`, Vrvu01; vorhandener `ims.model.vu_rules` | `ims.market.runner.actor_draws`, `side_result` | Vorhandener Angebots-/Werbekern. Neue, versionierte Zufallsbindung an Seed/VU/Periode/Kanal; keine myrndf-Gleichheitsbehauptung. |
| `IMS.E`, Vrvn06; vorhandener `ims.model.vn_insurance_rules` | `side_result` | Schwelle und günstigstes zulässiges Angebot. Angenommene moderne ganze Kohortenaufnahme, ID-Reihenfolge, Restnachfrage unversichert. |
| `ESS.C`, `IMSDATA.C`, Zustände/Perioden/Aggregate | `ims.market.contract`, `Balance`, `aggregate` | Explizite moderne Kohorten-/Risiko-/Cash-/Reservebuchung; alle aktiven VUs, A=L+E und Carryover. Neue Prospektiv-/Altreservezuordnung ist ein angenommener Vertrag, keine behauptete Altcode-Portierung. |
| Bestehende Python-Lebens-/Krankenketten | `actuarial` | Pro moderner VU isolierter vorhandener Vertrag mit lokaler ID1. Originalquelle und stabile moderne ID bleiben im Nachweis; geschlossene Lebensbestände, erklärte Krankenprofile. |
| E05-01/E05-02 aus Boardplan #292 | `profile`, Informationssnapshots | Kosten einmal in Entscheidungsperiode, Vorlauf und begrenztes Wirkfenster; keine überlappenden Parameter. VU-Information höchstens P−1; Kunden kennen aktuelle öffentliche Angebote vor Risikobuchung. |

`contract.py` prüft Daten, Gruppen, Zuordnungen und Grenzen; `presets.py` stellt
drei vollständige synthetische Fälle bereit. Der Runner hat keine I/O,
UI-Abhängigkeit oder versteckte RNG-Zustände. Sein lokaler actuarial-Cache
verwendet den vollständigen isolierten Eingangsvertrag als Schlüssel; verschiedene
VU-Bestände, Kosten oder Parameter teilen keine abweichende Rechnung. Dies
spart Wiederholungen identischer erklärter Bestände im 40er-Muster.

## Transport und Exporte

Das semantische Ergebnis `ims.modern-market-result.v1` enthält benannte Zeilen.
Die API kennzeichnet ihre verlustlose Tabellendarstellung mit
`transport: ims.market-row-table.v1`: Jede Sammlung enthält `columns`,
`rows` und bei unterschiedlichen Zeilentypen `missing` (Zeilenindex → fehlende
Spalten). `null` bleibt ein vorhandener undefinierter Wert; eine in der
ursprünglichen Zeile nicht vorhandene Spalte wird beim Entpacken entfernt.
Das Inhaltsdigest bezieht sich auf den semantischen Vertrag und alle Quellen,
nicht auf die bloße Transportanordnung. Frontend und Transporttest entpacken
dieselben Zeilen; Filter führen keine neue Rechnung aus.

`ims.api.market` ist in beiden vorhandenen API-Backends angeschlossen.
Input maximal 16 MiB, ein gleichzeitiger Marktauftrag, bis 41 VUs, 200
Kfz-/Sach-Kohorten und 100 Perioden; weitere Listen/Policen bleiben begrenzt.
Die gemessene vollständige 41er-Antwort umfasst 36.239.738 UTF-8-Bytes. Ein
48-MiB-Ergebnisbudget lässt dieses Muster zu; größere erklärte Eingaben
können atomar scheitern. Die Grenze wurde nicht pauschal entfernt.

JSON und Einzel-VU-Excel rechnen frisch und benötigen denselben `If-Match`-
Nachweis. Excel enthält die ausgewählte VU, zugehörige Kundenbuchungen und
vollständige Quellherkunft. Werte sind Textzellen, vier Dezimalstellen bleiben
erhalten und Formelinjektion wird nicht ausgeführt. Markt-/Familien-/Peer-
Ergebnisse werden in IMS dargestellt. Größere Prozessvisualisierungen sind AP8.

## Nachweis und Grenzen

`tests/test_modern_market.py` prüft Handrechnungen, Familienpartition,
Risikoerhaltung, Altreserven, Rundung, Carryover, Prefixe, Information,
Maßnahmen, Akteurbindung, 40/41×100, API, verlustlosen Transport, Export und
unveränderte AP3-Rechnung. Browserprüfungen verwenden reale API-Ergebnisse,
keine eingeblendeten Modellwerte. Noch keine Top-40-Namen, Lebens-Nachfrage,
Markt-/ICT-Kopplung, dynamische Insolvenz oder regulatorische Kapitalrechnung.
