# PR169d: Kranken-Workbench bis 100 Perioden

Stand: 2026-09-17

## Ursprung und Entsprechung

| Ursprung | IMS 2.x | Grenze |
| --- | --- | --- |
| `IMSDATA.C`: historische periodische VU-/VN-Zustaende fuer zwei Schadenpositionen | `frontend/src/healthScenario.ts` fuellt den geprueften PR169b-Krankeneingang | keine belegte Gleichsetzung einer Altposition mit moderner Krankenversicherung. |
| `IMS.E`: historische Aggregatausgaben | `frontend/src/HealthWorkbench.tsx` zeigt getrennte IMS-2.x-Krankenzeitreihen | keine Feld- oder RNG-Vollgleichheit mit historischen DAT-Dateien. |
| PR169c: `ims.api.health_result_delivery` | Vorschau, ausdruecklicher Start, Verlauf und drei Downloads | keine neue Fachregel oder zweite Bilanzrechnung im Browser. |

Der Seminarfall hat einen gemeinsamen Anfangsbestand und einen Horizont
von 1, 2, 5, 10, 25, 50 oder 100 Perioden. Baseline-Werte gelten
konstant. Die Variante aendert ab einer expliziten Periode Preis,
exogenen Leistungsanfall und Auszahlung; Neugeschaeft, Abgang, Anlage,
Aufwand und Kapital bleiben gemeinsam. Liegt die Aenderung hinter dem
Horizont, sind beide Prefixe gleich. Die Ausgabe kann nicht als
Versichererstrategie fuer den exogenen Leistungsanfall gelesen werden.

Der Browser sendet zwei vollstaendige PR169b-Eingaenge nacheinander an
die fluechtige Vorschau. Der Server allein validiert und rechnet. Erst
nach separater Auswahl und Bestaetigung sendet die Workbench den
geprueften Eingabe- und Ergebnis-Digest sowie einen Idempotenzschluessel
an PR169c. Verlaufsabruf und CSV/JSON/XLSX-Download stammen aus der
verifizierten Ablage; jeder Download verlangt `If-Match`. Ohne
konfigurierte SQLite-Ablage bleiben Vorschau und Vergleich verfuegbar,
nicht aber Speichern oder Verlauf.

Die Tabelle zeigt unveraenderte Dezimalstrings. Nur die Kurve nutzt
Browser-Zahlen fuer Pixelkoordinaten. Die Beispielfelder sind bewusst
einfach und keine empirischen Krankenmarktdaten. Eine gesetzliche
Krankenbilanz, Solvency II, DORA-Kausalkette und die Vier-Sparten-Summe
bleiben ausserhalb dieses PRs.

## Abnahme

`tests/test_health_workbench_scenario.py` prueft die echte
TypeScript-Uebersetzung gegen den Python-Kern fuer alle sieben Horizonte
und deren exakte Prefixe. `tests/browser/health_workbench_pr169d.mjs`
prueft in Edge 100 Perioden, breite und schmale Ansicht, Start,
Verlauf, alle drei Downloads und einen atomaren Bilanzfehler. Vier
gepruefte Browserbilder liegen im Handbuch. Die PR169c-API-Tests decken
zusaetzlich Speicher- und Digestfehler ab.
