# PR150: fluechtiges Ergebnisbuendel fuer 100 Perioden

## Ziel und Grenze

Ein explizit freigegebener PR149-Lauf liefert optional ein ZIP im HTTP-Response.
Es enthaelt einen vollstaendigen JSON-Nachweis sowie dieselbe normalisierte
Kennzahlentabelle als JSON, CSV und XLSX. Es gibt weder eine neue
Berechnung noch eine dauerhafte Ablage; ohne Download muss ein Lauf erneut
ausgefuehrt werden. PR151 macht Ergebnisse erst im Browser auswertbar.

## Ursprung und Abbildung

| Vorhandener Ursprung | PR150-Abbildung |
| --- | --- |
| Historische ESS-Periodenfolge und IMSDATA-Aggregatausgaben | Keine Neuberechnung historischer Aggregate; Referenz fuer die fachliche Grenze |
| `strategy_execution_period_chain_extended_probe.py` | Nur erfolgreich geprueftes 100-Perioden-Ergebnis als Quelle |
| `strategy_execution_candidate_effect_probe.py` | Bestehende Vor-/Nachzustaende und Regelanwendungszahlen als Tabellenzeilen |
| `strategy_execution_period_chain_five_period_effect_probe.py` | Uebergangsnachweise verbleiben unverkuerzt im JSON |

## Vertrag

- Neuer, versionierter Export nur fuer Resultat v2 mit 100 Perioden und
  nachgewiesenem Prefix. Gleicher Freigabeeingang wie PR149; getrennte
  Download-Route. Fehler liefern nie ein Teil-ZIP.
- JSON enthaelt das unverkuerzte PR149-Ergebnis, Herkunft, Tabellen-Spalten
  und alle normalisierten Zeilen. CSV und XLSX enthalten exakt dieselben
  Spalten und Werte. Ein Manifest nennt Version, Herkunft, Zeilenzahl und
  Hashes der drei Dateien. Keine neue Kennzahl oder Rundung.
- Eine Tabellenzeile beschreibt einen bereits vorhandenen skalaren Wert:
  Regelanwendungen, VU-/VN-Zustand vor/nach der Periode. Vektorwerte
  behalten ihren nullbasierten Sektorindex. Bool, Ganzzahl, Gleitkommazahl
  und fehlender Wert werden als Typ und kanonischer Text kodiert. Nicht
  belegte Akteurs-/Sektorindizes und `null` nutzen den Text `-`, damit CSV
  und XLSX beim Wiedereinlesen identische Zellen liefern.
- Groessen- und Zeilengrenzen sowie valide Feldtypen und Formelschutze
  sperren fehlerhafte Eingaben vor Auslieferung. ZIP entsteht nur im Speicher.
- Dauerhafte Speicherung/Idempotenz eines 100-Perioden-Ergebnisses sind nicht
  durch das vorhandene fluechtige PR149-Protokoll gedeckt. Entscheidung fuer
  einen gespeicherten Start braucht einen gesonderten Vertrag und PR.

## Nachweise und Restfragen

Vergleiche JSON/CSV/XLSX zeilenweise, pruefe Digests und Herkunft,
100-Perioden-API sowie FastAPI-/Fallback-Fehlerpfade. Die projizierten
Zustaende sind keine vollstaendigen historischen Aggregattabellen oder
Bilanz-/Solvency-II-Kennzahlen. Die historische Zufallsfolge wird nicht
als identisch behauptet.
