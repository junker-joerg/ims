# PR167: Gefuehrte Lebens-Workbench

Stand: 2026-09-17

## Herkunft und Grenze

| Ursprung | IMS-2.x-Umsetzung | Grenze |
| --- | --- | --- |
| `IMSDATA.C:14-17` (`SIMLAENGE 100`, `MAXSPARTEN 2`) und `ESS.C:71-75` (Periodenablauf) | Keine Aenderung an C-Quellen oder Nichtleben-Runner | Die zwei C-Sparten belegen kein historisches Lebensmodell. |
| `IMS.E:4103-4129` (`Bavauin`, Reserve-Zinssatz je Periode) | Explizite Seminarannahmen in `life_workshop_presets.py` | Keine Uebernahme dieses Zinssatzes als Lebens-Garantiezins. |
| PR163-166: Policen, Annahmen, Periodenkette, Ergebnisdienst | `LifeWorkbench.tsx` nutzt ausschliesslich die vorhandene Vorschau, Digest-Freigabe, Ablage und XLSX | Keine zweite Lebensrechnung in React oder in den Presets. |

## Bedienweg

`GET /api/accounting/life-period-chain/presets` liefert drei versionierte,
schreibfreie Zwei-Perioden-Faelle: Tod, Neugeschaeft sowie Anlage/Kapital.
Alle haben denselben Anfangsbestand und dieselbe Baseline. Die Variante
aendert jeweils einen benannten Hebel. Die Workbench zeigt Anfangsbestand
und Policen, erlaubt Versichererwahl, Tod und Neugeschaeft als atomare
Schalter sowie Anlage-, Kapital- und Policenfluesse als beschriftete Werte.
Anfangsbestand, Garantiesaetze und Laufzeiten der kuratierten Faelle
bleiben in PR167 fest; freie Bestandsgestaltung ist nicht freigegeben.

Baseline und Variante werden einzeln gegen die PR166-Vorschau geprueft.
Fehler der Eingabe erscheinen vor jeder Speicherung. Das Diagramm und die
Tabelle lesen dieselben periodischen Ergebnisfelder; die Quellenanzeige
zeigt explizite Anlage- und Todesfallannahmen. Nach ausdruecklicher
Speicherfreigabe schickt die UI beide erwarteten Digests an PR166. Der
Server rechnet erneut und verweigert abweichende Staende. Verlauf und
XLSX lesen nur das gepruefte gespeicherte Ergebnis. Ohne konfiguriertes
SQLite bleibt die Vorschau nutzbar, die Speicherfreigabe aber gesperrt.

## Nachweis und offene Punkte

Alle sechs Preset-Eingaben sind deterministisch mit PR165 geprueft;
Positiv- und API-Negativtests decken Quelle, Schema und Schreibfreiheit.
Der Frontend-Build und die Browserpfade fuer Vorschau, ungueltigen Wert,
Speichern, Verlauf sowie breite und schmale Ansicht wurden geprueft.
Der Browser-Download als Datei und neue statische Handbuch-Screenshots
konnten in dieser Umgebung nicht nachgewiesen beziehungsweise abgelegt
werden; API-/XLSX-Tests aus PR166 bleiben der maschinelle Exportnachweis.
Das ist eine explizite PR167-Testluecke fuer die naechste UI-Abnahme.

Die UI ist ein Zwei-Perioden-Seminarpfad, nicht ein freier
100-Perioden-Lebenseditor oder eine Vier-Sparten-Gesamtbilanz. Kein
Rueckkauf, Bonus, historisches Lebensmodell oder gesetzlicher
Bilanz-/Solvency-II-Nachweis. Der PR166-Backup-/Restore-Nachweis fuer die
Lebensresultat-Tabelle bleibt offen.
