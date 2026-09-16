# PR150: Ergebnisbuendel fuer den technischen 100-Perioden-Lauf

Stand: 2026-09-16

## Herkunft und Umsetzung

| Ursprung | Umsetzung | Grenze |
| --- | --- | --- |
| `ESS.C:71-75`, `IMSDATA.C:14` | vorhandene PR149-Periodenfolge | keine neue historische Regel oder Aggregatberechnung |
| `strategy_execution_period_chain_extended_probe.py` | `strategy_execution_result_bundle.py` | nur nach explizitem, erfolgreich abgeschlossenem v2-100er-Lauf |
| `strategy_execution_candidate_effect_probe.py` | `kennzahlen.csv`, `kennzahlen.xlsx`, `ergebnis.json` | vorhandene Regelanwendungszahlen und projizierte VU-/VN-Zustaende vor/nach der Periode |
| `strategy_execution_period_chain_five_period_effect_probe.py` | vollstaendiges `source_result` in `ergebnis.json` | Uebergaenge und Prefixbeleg, nicht als neue Tabellenkennzahl umgedeutet |

## Downloadvertrag

`POST /api/run-control/strategy-period-chain-extended-result-bundle` nimmt
denselben ausdruecklich freigegebenen v2-Eingang wie die PR149-Probe an.
Nur genau 100 Perioden sind fuer den Export zulaessig. Der Server prueft
erneut Kette, Kandidaten, gespeicherten Fuenf-Perioden-Prefix und
Ressourcenbudgets, startet den isolierten Lauf und liefert danach ein
ZIP (`ims-100-perioden.zip`) im Response. Fehler liefern JSON mit
`partial_result_returned: false` nach dem Lauf, niemals ein Teilarchiv.

Das ZIP enthaelt:

| Datei | Inhalt |
| --- | --- |
| `manifest.json` | Bundle-Version v1, 100 Perioden, Zeilen/Spalten, Ketten-ID, Ketten-/Wirkungsdigest und Datei-Hashes |
| `ergebnis.json` | dieselbe Kennzahlentabelle plus vollstaendiges PR149-Ergebnis einschliesslich Uebergaengen und Prefixnachweis |
| `kennzahlen.csv` | normalisierte Kennzahlentabelle, UTF-8 |
| `kennzahlen.xlsx` | dieselbe Tabelle auf Blatt `Kennzahlen`; alle Zellen als Text, keine Formeln |

Jede Zeile hat Herkunft (`chain_id`, `content_digest`, `effect_digest`),
Periode/Globalperiode, Stufe (`applications`, `state_before`, `state_after`),
Akteursart/-ID, nullbasierten Sektorindex, bestehenden Feldnamen und
Typ/Wert. CSV, JSON und XLSX enthalten dieselben Zeilen und Texte ohne
Rundung oder abgeleitete Kennzahl. `-` bezeichnet in einer leeren
Akteurs-/Sektorspalte `nicht zutreffend`, bei Typ `null` einen fehlenden
Wert. Es ist weder ein vollstaendiger historischer AGRSICH-Export noch
eine Bilanz, Solvency-II- oder DORA-Auswertung.

## Validierung und offen

Der Export prueft Ergebnisdigest, Vollstaendigkeit, Prefix, Periodenfolge,
Typen, Groessen- und Zeilenbudget vor der ZIP-Auslieferung. Tests lesen
alle drei Formate wieder ein, vergleichen Zeilen und Hashes, testen den
echten 100er-Lauf sowie beide Serverpfade und beschaedigte Eingaben.
`openpyxl` ist ab jetzt eine deklarierte Web-/Paketabhaengigkeit.

Der 100er-Lauf und das ZIP bleiben fluechtig, ohne Idempotenz oder
Ergebnisablage. Ein Download ist keine Betriebs- oder Forschungsfreigabe.
PR151 plant den Ergebnisarbeitsplatz und einen verstaendlichen Bedienweg;
ein persistierter 100er-Start braucht zuerst einen eigenen Vertrag.
Weder historische RNG- noch Vollgleichheit wird behauptet. `incomming/`
bleibt unversioniert.
