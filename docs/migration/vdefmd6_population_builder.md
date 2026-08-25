# Vdefmd6-Populationsbuilder

## Ziel

PR 74 bildet die vollstaendige Ausgangspopulation des historischen Modells
`Vdefmd6` als typisierte Python-Struktur ab. Der Builder erzeugt 25
`Insurer`- und 200 `Policyholder`-Entitaeten sowie separate, unverkuerzte
Initialisierungsdefinitionen.

Der Schnitt fuehrt keine Aktion aus, zieht keine Zufallszahl und startet keine
Simulation.

## C-zu-Python-Zuordnung

| Historischer Ursprung | Python-Ziel | Bedeutung |
| --- | --- | --- |
| `IMS.E:4137-4184`, `Vuauini` | `Vdefmd6InsurerDefinition` | VU-Aktivierung, Regel, Aktionszeit, Anspruchsniveaus, Startwerte und Parameter |
| `IMS.E:4191-4233`, `Vnauini` | `Vdefmd6PolicyholderDefinition` | VN-Aktivierung, Regel, Aktionszeit, Anfangsstatus, Vermoegen und Parameter |
| `IMS.E:4566-4628`, `Vdefmd6` | `_INSURER_GROUPS` | neun Regeln in zehn konkreten VU-Gruppen inklusive Allianz-Sonderbelegung |
| `IMS.E:4630-4669`, `Vdefmd6` | `_POLICYHOLDER_GROUPS` | sechs Grundgruppen und zwei ab Periode 50 aktivierte VN-Gruppen |
| `IMSDATA.C:77-78` | `_VU_RULE_CLASSES`, `_VN_RULE_CLASSES` | Regel-zu-Klassen-Zuordnung |

## Ergebnis

Der read-only Bericht `python -m ims.api.vdefmd6_population_report --repo-root .`
prueft folgende Invarianten:

- fortlaufende IDs `1-25` und `1-200`;
- 25 aktive VU und 150 in Periode 1 aktive VN;
- 50 weitere VN mit Aktivierungsperiode 50;
- logische Aktionszeit 1 und Aktivierungslaeufe bis 100;
- 16 Parameter je VU- und VN-Definition;
- Regel- und Regelklassenverteilungen;
- 13 konkrete Anker im historischen Quelltext;
- VU14 als Allianz, Regel 6, Klasse 2, Startpraemien 40/40 und Werbung 10/10.

Die generischen Entitaetsfelder `active` und `active_prev` beschreiben nur den
Startzustand fuer Periode 1. Die historischen Aktivierungsperioden und
Aktivierungslaeufe bleiben davon getrennt und vollstaendig in den typisierten
Definitionen erhalten.

## Quellenkonflikt

Die ausfuehrbaren Schleifen in `IMS.E:4660-4669` initialisieren VN `151-190`
mit Regel 3 und VN `191-200` mit Regel 2. Der spaetere Bildschirmtext nennt
abweichend `151-180` und `181-200`. Der Builder folgt konservativ den
ausgefuehrten Schleifen und dokumentiert den Widerspruch im Vertrag
`vdefmd6_population_contract.json`.

## Grenzen

- Der Builder ist noch nicht an einen vollstaendigen Schedulerlauf angebunden.
- PR 75 beschreibt die Aktionsslots und moderne Seed-Policy; die historische
  Ziehungsreihenfolge bleibt offen.
- VN-Entscheidungen, Schadenentstehung und Zustandsfortschreibung werden nicht
  ausgefuehrt.
- Legacy-Ausgabezeilen werden nicht als Eingabe verwendet.
- Es gibt keine historische Vollgleichheits- oder Produktionsfreigabe.

## Danach

PR 75 hat die Aktionsslots und eine explizite, reproduzierbare moderne
Seed-Policy lesend gebunden. PR 76 hat danach die VU14-Regelprojektion fuer
Perioden 1-49 klassifiziert. PR 77 hat den offenen VN-/Schaden-/Settlement-
Pfad kartiert; PR 78 leitet als naechstes die expliziten Vorschock-Snapshots
und eine moderne Drawfolge ab.
