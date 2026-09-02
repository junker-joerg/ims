# IMS 2.x: Strategieentwurf in der Workbench

Stand: 2026-09-02

## Einordnung

PR109 ergaenzt den read-only Strategiearbeitsbereich um einen lokalen
Entwurfsmodus. Er macht die in PR108 definierte JSON-Form bedienbar, ohne die
fachliche oder technische Systemgrenze zu verschieben: Der Browser haelt den
Entwurf nur im aktuellen React-Zustand und sendet ihn ausschliesslich an die
zustandslose Validierungs-API.

## C-zu-Workbench-Mapping

| Historischer Ursprung | Workbench-Feld | Bedeutung |
| --- | --- | --- |
| `IMSDATA.C`, `ACTION.st` | Strategie und Zeitangaben | Regelbindung eines einzelnen Akteurs |
| `IMSDATA.C`, `vkrvu` / `vkrvn` | VU/VN und Ziel-ID | Auswahl innerhalb der bekannten Population |
| `IMS.E`, `Vuauini` / `Vnauini` | Aktivierung, Laufgrenze, logische Zeit | explizite technische Laufangaben ohne neue Defaults |
| historische Zweiervektoren | Position 1 und Position 2 | vorhandene, noch nicht modern benannte Parameterform |
| vorhandene Parameterloader | dynamische Formularfelder | technisch belegte Felder und Zahltypen |

## Bedienung

Der Tab `Entwurf` bietet Kopffelder fuer ID und Bezeichnung sowie einen Editor
fuer genau eine Akteurszuordnung. Die Strategieliste wird nach VU oder VN
gefiltert. Bei einem Strategiewechsel erzeugt die Workbench nur die zum
vorhandenen Schema gehoerenden leeren Eingabefelder. Sie setzt keine
fachlichen Standardwerte.

Eine vollstaendige Zuordnung kann der lokalen Liste hinzugefuegt, daraus
erneut zur Bearbeitung geladen oder entfernt werden. Jede Aenderung am
Entwurfsinhalt verwirft einen zuvor angezeigten Pruefbericht. `Entwurf pruefen`
sendet das gesamte Dokument an
`POST /api/strategies/assignment-draft-validation`.

Der Bericht zeigt Gueltigkeit, gepruefte Zuordnungen und einzelne Fehlerpfade.
Er bestaetigt zugleich, dass weder Schreiben noch Snapshot-Erzeugung,
Ausfuehrung oder Simulation stattgefunden haben.

## Bewusste Grenzen

- Browser-Neuladen verwirft den Entwurf.
- Es gibt keinen Import, Export und keine persistente Ablage.
- Zuordnungen gelten fuer einzelne Akteure; Gruppen und geplante Wechsel sind
  nicht enthalten.
- Die zwei historischen Parameterpositionen bleiben unbenannt und teilen sich
  eine Strategie.
- Die Workbench uebersetzt den Entwurf nicht in Kernmodell-Snapshots.
- Der Entwurf ist keine Simulation und kein historischer
  Vollgleichheitsnachweis.

## Anschluss

PR110 definiert als naechste fachliche Grenze die deterministische Abbildung
eines bereits gueltigen Entwurfs auf vorhandene VU-/VN-Regel-Snapshots. Ein
Speicher- oder Ausfuehrungspfad ist damit noch nicht verbunden.
