# PR154: Strategie- und Parameterplanung je Sparte

Stand: 2026-09-16

## Ziel

Ein versioniertes, zustandslos validiertes Entwurfsformat soll fuer
einzelne VU und VN verschiedene Katalogstrategien, Zeitfenster und
Parameterwerte je geplanter Nichtleben-Sparte ausdruecken koennen.

## Historische Grenze

`IMSDATA.C` fuehrt `Vr` und `Pv` je Akteur, aber getrennte `Sp[1/2]`
beziehungsweise `Rk[1/2]`. Die vorhandenen Python-Regeln rechnen mit
Zweiervektoren und einer Strategie je Akteur. PR153 belegt nur die
Positionsabbildung C 1/2 zu Python 0/1; die modernen Ziel-IDs sind
nicht historisch gebunden.

## Umsetzung

1. Eigenes Schema `ims.sector-strategy-plan.v1`, das weder den bestehenden
   Vdefmd6-Entwurf noch vorhandene Runner-Eingaenge veraendert.
2. Eintragsschluessel: Akteur, Vdefmd6-ID, moderne `sector_id` und
   inklusives Periodenfenster 1-100. Je Akteur/Sparte duerfen Zeitfenster
   nicht ueberlappen. Luecken sind bei Teilentwuerfen erlaubt.
3. Katalogstrategie muss zum Akteur passen. Bestehende Parameterschemata
   liefern die Feldnamen und Typen; jeder Wert ist fuer *eine* Sparte
   skalar, nicht ein historischer Zweiervektor.
4. Kfz und Sach-Haftpflicht sind in diesem Entwurf nur Planungsziele.
   Leben und Kranken erhalten bis zu eigenen Regeln keine Katalogstrategie.
5. Read-only Vertrags-Endpunkt und zustandslose Validierungs-API fuer
   FastAPI und Starlette. Keine Speicherung, Materialisierung oder Ausfuehrung.

## Validierung

Positive Tests fuer verschiedene VU-/VN-Strategien, Parameter und
angrenzende Zeitfenster. Negative Tests fuer falsche Versionen, Akteur-
Regel-Mismatch, unbekannte oder noch nicht zulaessige Sparten, Parameter,
Ziel-ID und Fenster-Ueberlappung. Ungueltige Entwuerfe liefern keine
teilweise freigegebene Zuordnung.

## Offene Punkte

Die geplanten Kfz-/Sach-Zuordnungen sind keine historische
Interpretation der zwei Schadenpositionen. Ein Lauf damit benoetigt
spaeter einen ausdruecklichen, getesteten Mehrsparten-Runner; die
vorhandenen VU-/VN-Snapshots bleiben unveraendert. Es gibt keine
Gleichheits- oder regulatorische Vollstaendigkeitsaussage.
