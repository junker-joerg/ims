# IMS 2.x: Snapshot-Kontext in der Workbench

Stand: PR113, 2026-09-07

## Ziel

PR113 bindet den PR112-Kontextvertrag an die vorhandene Strategie-Workbench.
Der neue Tab `Kontext` schliesst die sichtbare Kette vom lokalen
Strategieentwurf ueber partielle Snapshot-Bauplaene bis zur formalen Pruefung
der noch fehlenden Werte fuer genau eine Periode.

Der Kontext bleibt ein fluechtiger React-Zustand. Die Workbench sendet ihn
gemeinsam mit dem unveraenderten Strategieentwurf an die bestehende
Validierungs-API. Der Server verwendet keinen Kontextwert weiter.

## Bezug zum Altmodell

| Grundlage | Sichtbare Entsprechung | Grenze |
| --- | --- | --- |
| `IMSDATA.C`, `ACTION.st` | VU-/VN-Ziel und Strategiebindung | keine neue Regelwahl |
| `IMS.E`, periodischer Regelaufruf | genau eine positive Kontextperiode | keine Umdeutung von Logtime oder Laufgrenze |
| VU-Regelaufrufe | Ziehungen, Zinssatz, Schockstatus und Schwellen | keine Zufallserzeugung oder Defaults |
| VN-Regelaufrufe | Ziehungen, Marktinput, Historie und Informationskosten | verschachtelte Fachsemantik bleibt offen |
| PR110-Bauplan | exakte `unresolved_snapshot_fields` je Ziel | keine parallele Feldliste in der UI |

## Zustandsfolge

Der Kontext-Tab besitzt zwei Voraussetzungen: Der aktuelle Entwurf muss
serverseitig gueltig sein und die PR110-Uebersetzung muss vollstaendig
vorliegen. Erst `Kontext anlegen` kopiert Akteur, Ziel, Strategie und offene
Feldnamen in einen leeren lokalen Editorzustand.

Es werden keine Werte aus Fixtures, Szenarien oder vorherigen Laeufen
vorbelegt. Eine Entwurfsaenderung verwirft Entwurfspruefung,
Bauplanvorschau und Kontext. Eine erneute Bauplananforderung verwirft den
Kontext ebenfalls. Damit kann kein formal passender, aber zu einem aelteren
Entwurfsstand gehoerender Kontext weiterverwendet werden.

## Eingabe und Transport

Jede Kontexteingabe bleibt zunaechst Text im Browserzustand:

- `boolean` wird als ausdrueckliche Ja-/Nein-Auswahl erfasst;
- `finite_number` und `integer` verwenden numerische Eingaben;
- `number_array`, `positive_integer_array`, `array` und `object` verwenden
  sichtbare JSON-Eingaben;
- ein nullable Feld kann unabhaengig vom Text bewusst als `null` markiert
  werden.

Erst unmittelbar vor dem POST werden Zahlen und syntaktisch gueltiges JSON
in JSON-Werte ueberfuehrt. Leere Felder werden ausgelassen, sodass der
PR112-Validator `context_value_missing` meldet. Nicht parsebares JSON bleibt
als Zeichenkette erhalten und erzeugt `context_value_shape_invalid`. Diese
Transportumwandlung normalisiert keine Fachwerte und ersetzt keinen Default.

## API und Fehlerbezug

`GET /api/strategies/assignment-snapshot-context-contract` liefert Version,
Feldformen, Nullable-Markierungen und Herkunftsgruppen. `POST
/api/strategies/assignment-snapshot-context-validation` prueft das Paar aus
Entwurf und Kontext atomar.

Der Serverpfad eines Feldfehlers, zum Beispiel
`$.context.entries[0].values.interest_rate`, wird direkt dem entsprechenden
Editorfeld zugeordnet. Der Gesamtbericht bleibt darunter vollstaendig
sichtbar. Ein gueltiger Bericht zeigt trotzdem:

- `defaults_applied = false`;
- `context_values_consumed = false`;
- `snapshot_loader_invocation_performed = false`;
- `snapshots_created = false`;
- `execution_performed = false`;
- `simulation_performed = false`.

## Aussagegrenzen

Die Workbench prueft nur die in PR112 festgelegten eindeutigen Wertformen.
Sie kennt weiterhin keine Fachsemantik der regelabhaengigen VN-Ziehungs-,
Markt- und Historienstrukturen. Ein formal gueltiger Kontext ist deshalb noch
kein materialisierbarer Snapshot und keine fachliche Lauffreigabe.

Es erfolgen keine Speicherung, keine Materialisierung, keine Ausfuehrung und
keine Simulation. Historische RNG- oder Vollgleichheit wird nicht behauptet.

## Naechster Schritt

PR114 soll zunaechst den Materialisierungsvertrag und die noch zu belegenden
verschachtelten VN-Wertformen dokumentieren und testen. Erst ein danach
ausdruecklich freigegebener Schritt darf gueltige Kontextwerte in vorhandene
Snapshot-Dataclasses uebernehmen. Eine Runner-Kopplung bleibt separat.
