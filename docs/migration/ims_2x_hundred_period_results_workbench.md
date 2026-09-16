# PR151: 100-Perioden-Ergebnisarbeitsplatz

Stand: 2026-09-16

## Ziel, Ursprung und Grenze

| Historischer Bezug | Heutiger Anschluss | Aussage |
| --- | --- | --- |
| Periodenschleife `ESS.C:71-75`, `SIMLAENGE = 100` in `IMSDATA.C:14` | unveraenderter PR149-Lauf | genau 100 vorbereitete Perioden, keine neue Fachregel |
| VU-/VN-Vorperiodenzustand | gespeicherter PR145-Prefix und PR149-Uebergaenge | stabile Perioden 1-5 vor der laengeren Kette |
| historische Aggregatdateien | PR150-ZIP | heutige projizierte Zustandsfelder, kein AGRSICH-Vollersatz |

Die neue Workbench-Registerkarte `Ergebnisse` zeigt gepruefte,
gespeicherte 100-Perioden-Ketten und passende gespeicherte
Fuenf-Perioden-Nachweise. Freigabeperson, Begruendung und Checkbox
sperren den Start bis zur ausdruecklichen Zustimmung. Der Server baut
die Kette erneut und fuehrt den bestehenden isolierten Lauf aus.
Ein Fehler liefert kein Teilergebnis.

## Ausgabe und Vergleich

Nach Erfolg zeigt der Browser den Prefixnachweis, die 100-Perioden-Reihe,
VU-/VN-Akteure, vorhandene Zustandsfelder und gegebenenfalls die
nullbasierte Vektorposition. Die Tabelle gibt die Originalzahlen der
einzelnen Perioden wieder; das Diagramm ist nur deren Darstellung.
Es wird weder summiert noch gerundet oder eine neue Modellkennzahl erzeugt.
Zwei bereits gelaufene Ketten sind nur dann vergleichbar, wenn derselbe
gespeicherte Fuenf-Perioden-Nachweis als Prefix verwendet wurde.
Das ist keine automatische Kausalinterpretation.

`ZIP herunterladen` wiederholt wegen der fluechtigen PR149/150-Grenze den
100er-Lauf. Die Workbench sendet den sichtbaren Wirkungsdigest als
`If-Match`; der Server liefert nur bei genau diesem Digest ein ZIP mit
`ETag`. Sonst kommt ein 409-Fehler ohne Teilarchiv. Ein Neuladen des
Browsers verliert die Ergebnisansicht. Es gibt keine dauerhafte
100er-Ergebnisablage oder Idempotenz fuer diesen Horizont.

## Abnahme

- Frischer Datenstand mit gespeicherter Zwei-, Fuenf- und zwei getrennten
  100-Perioden-Ketten; nur die beiden 100er sind startbar.
- Beide Starts im Browser erfolgreich; je 100 Tabellenzeilen und zwei
  Vergleichslinien. Start ohne Checkbox gesperrt.
- Absichtlich falscher Download-Digest: 409, kein ZIP. Richtiger Digest:
  `ims-100-perioden.zip`, Manifest passend zum sichtbaren Ergebnis.
- Breite Browseransicht 1440 x 1000 und schmale 390 x 844 ohne
  horizontales Ueberlaufen oder Browserfehler. Datierte Handbuchbilder:
  `windows_hundred_period_results_pr151_wide_2026-09-16.png` und
  `windows_hundred_period_results_pr151_narrow_2026-09-16.png`.

Offen bleiben das bedienbare Erzeugen der 100 Einzelkandidaten, eine
dauerhafte 100er-Ablage und fachlich benannte Sparten/Bilanzen.
Es gibt keine historische RNG-/Vollgleichheits- oder regulatorische
Produktionsbehauptung. `incomming/` bleibt unversioniert.
