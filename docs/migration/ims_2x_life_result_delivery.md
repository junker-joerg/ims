# PR166: Lebens-Ergebnisdienst und XLSX

Stand: 2026-09-17
Vertrag: `ims.life-result-delivery.v1`

## Herkunft und fachliche Grenze

| Ursprung | Umsetzung | Grenze |
| --- | --- | --- |
| `IMSDATA.C` (`MAXSPARTEN 2`, `BAV.Zs`), `IMS.E` (Perioden- und Reserveverzinsung) | Keine Aenderung am Alt- oder Nichtleben-Pfad | Der Altcode belegt kein Lebensmodell. |
| PR163-165 | `life_period_chain.run_life_policy_period_chain` bleibt die einzige Lebensrechnung | Keine zweite Bilanz-, Anlage- oder Mortalitaetslogik in API oder Export. |
| IMS-2.x-Ablage | `life_result_delivery.py`, `life_result_workbook.py` | Modellrechnung, keine gesetzliche Bilanz, Solvency-II-Meldung oder historische Vollgleichheit. |

## Bedienbarer API-Vertrag

`POST /api/accounting/life-period-chain/preview` nimmt die vollstaendige
PR165-Eingabe entgegen und liefert unveraendertes Rechenergebnis sowie
kanonische SHA-256-Digests fuer Eingabe und Ergebnis. Es wird nichts
geschrieben. Ein ungueltiger Fall liefert HTTP 422, null Zeilen und
null Quellenwerte.

`POST /api/accounting/life-period-chain/start` verlangt
`ims.life-result-start.v1`, die vollstaendige Eingabe, beide erwarteten
Digests, einen Idempotenzschluessel und
`explicit_storage_release = true`. Nur eine explizit konfigurierte
SQLite-Metadatenquelle ist zulaessig. Der Server rechnet selbst erneut;
ein abweichender Digest verhindert das Speichern. Derselbe Schluessel
mit denselben Digests liest das vorhandene, gepruefte Ergebnis ohne
erneute Berechnung. Ein Schluessel fuer andere Inhalte wird abgewiesen.
Gleichzeitige identische Schreibversuche erzeugen genau einen Datensatz.

`GET /api/accounting/life-period-chain/results` zeigt maximal die 100
juengsten geprueften Ergebnisse. `GET .../result/{result_id}` liest
ein einzelnes gespeichertes Ergebnis samt vollstaendiger Eingabe. Beide Wege pruefen Eingabe-,
Ergebnis-, ID- und Datensatz-Digest (einschliesslich Speicherzeit) erneut
und schreiben nichts.
`GET .../result/{result_id}.xlsx` exportiert ausschliesslich dieses
gepruefte Ergebnis und verlangt `If-Match` mit dem Ergebnis-ETag.
Die Datei enthaelt Perioden, Quellen, Todesfaelle je Kohorte,
Policen- und Kohortenbestaende/-bewegungen, Neugeschaeft und Herkunft.
Alle Geld- und Zinssaetze bleiben exakt als Dezimaltextzellen erhalten;
es gibt keine Excel-Fliesskomma-Neuberechnung. Das vollstaendige
kanonische Ergebnis bleibt im JSON-Abruf verfuegbar.

## Laufzeit, Fehler und offene Punkte

Vorschau und Start nutzen einen einzelnen Hintergrund-Worker pro App.
Nach 20 Sekunden wird kooperativ abgebrochen; ein verspaetetes
Teilergebnis wird weder ausgeliefert noch gespeichert. Solange der
Worker noch beendet, werden weitere Berechnungen mit HTTP 429
abgewiesen. Die reine PR165-Funktion bleibt auch fuer den lokal
gemessenen 100x100-Extremfall (rund 46 Sekunden) verfuegbar;
dieser Fall ist **nicht** fuer den interaktiven API-Start freigegeben.
Das HTTP-Bodylimit betraegt 8 MB. Die 20-Sekunden-Grenze ist eine
konservative Serverfreigabe, keine fachliche 100-Perioden-Garantie
fuer jeden Policenbestand.

Die SQLite-Datei muss fuer dauerhafte Ergebnisse vom Betreiber
gesichert werden. Die bestehende Metadaten-Recovery prueft diese
neue Tabelle nicht in ihrem alten kritischen Tabellendigest; eine
separate Backup-/Restore-Abnahme fuer Lebensresultate ist offen.
PR167 liefert erst den nichttechnischen Workbench-Bedienweg und
Browserabnahme. Keine historische RNG-Reproduktion und keine
historische Vollgleichheitsbehauptung.
