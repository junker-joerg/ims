# Arbeitsaufträge AP1–AP14

Der Generator bereitet Dateien vor und startet keine Codex-Ausführung. Origin
vorher aktualisieren. Unter Windows im jeweiligen Checkout die eigene editable
Umgebung verwenden. AP1–AP3 bleiben im historischen Modus kompatibel; Folgepläne
werden ohne weiteren Schalter als **Vorschau** behandelt.

## Geprüfte Aufrufe

```powershell
git -c http.sslBackend=schannel fetch origin --prune
.\.venv\Scripts\python.exe scripts\planning\ims_sprint_plan.py --out .tmp-pr-board-plan\legacy
.\.venv\Scripts\python.exe scripts\planning\ims_sprint_plan.py --plan docs\plans\ims_explainable_market_plan.json --package AP4 --mode preview --out .tmp-pr-board-plan\ap4-preview
.\.venv\Scripts\python.exe scripts\planning\ims_sprint_plan.py --plan docs\plans\ims_board_strategy_plan.json --package AP10 --mode preview --out .tmp-pr-board-plan\ap10-preview
.\.venv\Scripts\python.exe scripts\planning\ims_sprint_plan.py --plan docs\plans\ims_board_strategy_plan.json --package auto --out .tmp-pr-board-plan\next-preview
```

Der alte Auto-Aufruf meldet aktuell kein Paket, weil AP1–AP3 fertig sind. Der
Board-Auto-Aufruf zeigt AP4 als nächstes angenommenes, noch nicht abgeschlossenes
Paket. Eine AP10-Vorschau benennt offene AP4–AP7-Abhängigkeiten. `deferred` und
`done` erzeugen auch bei expliziter Auswahl keinen Auftrag. Vorschlagsstatus
erzeugt keinen freigegebenen Auftrag. Fehler löschen ältere Ausgabedateien im
angegebenen Zielordner, damit kein veralteter Auftrag übrig bleibt.

## Freigegebener Auftrag nach tatsächlicher menschlicher Freigabe

Der Modus `authorized` benötigt einen angenommenen Paketumfang im aktuellen
`origin/main`, dort erledigte transitive Abhängigkeiten mit Abschlussbelegen und
eine Datei mit dem **bereits erteilten tatsächlichen** Umsetzungsauftrag. Ein
Planungsmerge allein reicht nicht. Der Auftrag enthält die getrennten Zustände;
technisch done in einem Branch erfüllt keine main-Abhängigkeit.

Dateiformat `ims.execution-authorization.v1`, zum Beispiel für AP4:

```json
{
  "schema_version": "ims.execution-authorization.v1",
  "package": "AP4",
  "scope": "implementation",
  "plan_commit": "VOLLSTAENDIGER_AKTUELLER_ORIGIN_MAIN_SHA",
  "authorized_by": "TATSAECHLICHER_AUFTRAGGEBER",
  "authorized_at": "2026-10-02T12:00:00+02:00",
  "user_request": "HIER_DEN_TATSAECHLICH_ERTEILTEN_AP4_AUFTRAG_DOKUMENTIEREN"
}
```

Das Beispiel ist ausdrücklich **keine erteilte Freigabe**. Datum, Wortlaut und
SHA durch echte Werte ersetzen; Datei lokal außerhalb der versionierten Planung
ablegen, etwa `.tmp-pr-board-plan/ap4-authorization.json`. Der Prüfer validiert
den Beleg und Umfang, authentifiziert aber keinen Menschen. Agenten/Operatoren
dürfen keine Freigabe erfinden oder einen Planungsauftrag als Umsetzung auslegen.

Nach realer Freigabe und Vorliegen dieser Datei:

```powershell
.\.venv\Scripts\python.exe scripts\planning\ims_sprint_plan.py --plan docs\plans\ims_explainable_market_plan.json --package AP4 --mode authorized --authorization-file .tmp-pr-board-plan\ap4-authorization.json --out .tmp-pr-board-plan\ap4-authorized
```

Später gilt derselbe Aufruf mit `ims_board_strategy_plan.json`, `AP10` und dem
entsprechenden tatsächlichen AP10-Freigabebeleg. Zuvor muss der Boardplan mit
Planannahmebeleg und angenommenen Paketstatus in main übernommen und AP7 dort
abgenommen sein. Heute muss ein authorized-Aufruf für AP10 scheitern.

Proposed-Ergänzungen zu AP5/AP7/AP8 stehen separat im Vorschauauftrag. Ein
freigegebener Auftrag aus dem angenommenen Marktplan erweitert seinen Umfang
nicht um diese Vorschläge. Nach Annahme werden die betroffenen Paketumfänge mit
Herkunft/Abnahmen in main eingearbeitet oder fehlende Voraussetzungen in AP10
zugeordnet. `implementation_authorized` im Manifest ist ein gespeicherter
Status, keine pauschale Erlaubnis für den Generator; der konkrete Auftrag ist
zusätzlich mit einem Beleg an den aktuellen Plancommit gebunden.

## Struktur- und Statusprüfung

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_ai_sprint_plan*.py -v
.\.venv\Scripts\python.exe -m pytest tests\test_ict_workshop.py tests\test_api_ict_workshop.py tests\test_api_seminar.py -q
```

Geprüft werden alte ID-Abdeckung, 65 neue IDs/Dispositionen, eindeutige Paket-
und Quellen-IDs, vorhandene Quellenpfade, vollständige Evidenzmatrix,
Abhängigkeitszyklen, vorgeschlagen/zurückgestellt/angenommen, Abschluss-/Merge-
Trennung, Erzeugung und fehlende/stale Freigaben. CI veröffentlicht Vorschauen;
sie stellt keine Umsetzungsfreigabe aus. Produktprüfungen und Benutzerabnahmen
bleiben getrennt. Bei späterer Änderung der Anforderungsversion Abdeckungs-
katalog und Tests gemeinsam nachvollziehbar ändern.
