# Plan: Produktions-Altdatenkorpus fuer die erste Freigabe

## Ziel

PR 56 fixiert den historischen Referenzkorpus, gegen den die erste
konservative Produktionsfreigabe vorbereitet wird. Der Plan trennt einen
verpflichtenden Kernkorpus von spaeteren, einzeln zuzulassenden Ergaenzungen.

Dieser PR importiert keine Datei aus `incomming/`, startet keine Simulation,
aendert keine Fachlogik und behauptet keine historische Vollgleichheit.

## Verbindlicher Kernkorpus v1

Quelle der maschinenlesbaren Zielgrenzen bleibt
`tests/fixtures/legacy_validation_bundle.json`. Der Kernkorpus besteht aus den
19 bereits versionierten Dateien unter `tests/references/legacy_agrsich/` und
6.300 konkret eingetragenen Vergleichsperioden.

| Familie | Dateien | Subjekt / Stufe / Selektor | Fenster | Vergleichszeilen |
| --- | --- | --- | --- | ---: |
| Versicherer einzeln | `VU14L1.DAT` | insurer / I / `entity = 14` | `1-100` | 100 |
| Versicherer SK1 | `VUSK1L5.DAT`, `VUSK1L4.DAT`, `VUSK1L3.DAT`, `VUSK1L2.DAT`, `VUSK1L1.DAT` | insurer / IV / `all = SK1` | `1-100`, `101-200`, `201-300`, `301-400`, `401-500` | 500 |
| VN SK1 | `IMSVNSK1.DAT` | policyholder / IV / `all = SK1` | `1-100` | 100 |
| VN-Regeln | `IMSVNR01.DAT` bis `IMSVNR06.DAT` | policyholder / II / `rule = 1` bis `6` | `1-300`, `1-300`, danach viermal `1-500` | 2.600 |
| VN-Klassen | `IMSVNVK1.DAT` bis `IMSVNVK3.DAT` | policyholder / III / `rule_class = 1` bis `3` | jeweils `1-500` | 1.500 |
| VU-Klassen | `IMSVUVK1.DAT` bis `IMSVUVK3.DAT` | insurer / III / `rule_class = 1` bis `3` | jeweils `1-500` | 1.500 |

Die fuenf `VUSK1L*`-Dateien sind Zeitfenster desselben `SK1`-/`all`-Aggregats
auf der unterstuetzten Aggregatstufe IV. Sie sind keine unterschiedlichen
Aggregatebenen.

Die 19 Dateien enthalten physisch 6.700 Datenzeilen. Der Freigabekorpus zaehlt
nur die 6.300 im Bundle eingetragenen Perioden. Insbesondere enthaelt die
versionierte `IMSVNSK1.DAT` 500 Zeilen, waehrend der Kernkorpus bewusst nur das
belegte Fenster `1-100` verwendet. Physisch vorhandene Restzeilen werden nicht
stillschweigend als validiert behandelt.

## Parser- und Formatgrenzen

Versichererdateien muessen durch `parse_legacy_insurer_dat` mit folgendem
13-spaltigen Agrsich-Header lesbar sein:

```text
#t Pr1 Wa1 Rs1 Vn1 Sa1 Sh1 Pr2 Wa2 Rs2 Vn2 Sa2 Sh2
```

VN-Dateien muessen durch `parse_legacy_policyholder_dat` mit folgendem
VN-Agrsich-Header lesbar sein:

```text
#t Vu1 Vs1 Vp1 Ev1 Sh1 Vu2 Vs2 Vp2 Ev2 Sh2 Vm
```

Whitespace-Varianten im Header duerfen nur nach den vorhandenen Parserregeln
akzeptiert werden. Jede Zielperiode muss eindeutig, sortiert, lueckenlos und in
der Referenz vorhanden sein. Writer-Referenzen unter
`tests/references/agrsich/` sind keine historischen Quellen.

## Herkunft und Nachvollziehbarkeit

Die vorhandenen Familiennotizen bleiben Bestandteil des Herkunftsnachweises:

- `docs/migration/vn_rule_family_imsvnr.md` fuer `IMSVNR01` bis `IMSVNR06`;
- `docs/migration/vn_class_family_imsvnvk.md` fuer `IMSVNVK1` bis `IMSVNVK3`;
- `docs/migration/insurer_class_family_imsvuvk.md` fuer `IMSVUVK1` bis
  `IMSVUVK3`;
- `docs/migration/agrsich_validation_report.md` fuer Bundle, Fenster und
  Reportgrenzen;
- `docs/plans/historical_testdata_inventory.md` fuer den lokalen
  Kandidatenbestand.

Wo eine Referenz schon vor dem lokalen Kandidateninventar versioniert war,
bleibt dieser geerbte Herkunftsstand im Abschlussbericht sichtbar. PR 56
erfindet keine nachtraegliche Archivzuordnung. Der Git-Stand und die bereits
dokumentierten SHA-256-Werte fixieren den verwendeten Inhalt.

## Aktueller Nachweis und seine Grenze

Die Coverage-Matrix meldet fuer den Kernkorpus 19 vorhandene und 19 abgedeckte
Referenzen ohne Dateiluecke. Der fixturegetriebene Validierungsreport meldet
6.300 von 6.300 ausgerichteten Referenzzeilen als Treffer.

Dieser Befund prueft Referenzpfade, Parser, Header, Periodenfenster,
Target-Metadaten und Reportbildung. Der Validierungslauf baut seine
Vergleichstabellen aus den gelesenen Referenzzeilen auf. Er ist deshalb noch
kein unabhaengiger Neu-/Alt-Vergleich eines berechneten historischen Modells.
PR 58 hat dafuer den strikten Eingangsvertrag fuer von aussen gelieferte
berechnete Exporttabellen umgesetzt. PR 59 hat die read-only
Abweichungsdiagnose ergaenzt; fuer den Kernkorpus bleibt sie mit 15 fehlenden
berechneten Exporttabellen blockiert. Ein berechneter Kernkorpus-Lauf ist damit
weiterhin nicht belegt.

## Bewusst ausgeschlossene Kandidaten

| Kandidat | Entscheidung fuer Kernkorpus v1 | Begruendung |
| --- | --- | --- |
| gesamtes `incomming/` | ausgeschlossen | lokaler Kandidatenbestand, kein Sammelimport |
| `VU014PR1.DAT` | blockiert | sechs Spalten und ungeklärte Bedeutung von `Pr1L1` bis `Pr1L5`; eigener Parserentscheid erforderlich |
| `IMSVU001.DAT` bis `IMSVU025.DAT` | ausgeschlossen | individuelle VU-Ausgaben ohne festgelegte Freigabe-Subjektmenge und mit mehreren Quellenvarianten |
| `IMSVUR01.DAT` bis `IMSVUR09.DAT` | geparkt | VU-Regelfamilie braucht zuerst eigene Quellen-, Header- und Selektorkartierung |
| alternative ZIP-Varianten | ausgeschlossen | abweichende Laengen und Hashes duerfen nicht zwischen historischen Laeufen vermischt werden |
| Parameterausgaben und unbekannte Formate | ausgeschlossen | keine Aufnahme ohne belegtes Feldmapping und passenden Parser |

Ein Ausschluss bedeutet nicht, dass die Datei fachlich wertlos ist. Er bedeutet
nur, dass sie fuer die erste Freigabe noch keine belastbare Vergleichsgrenze
besitzt.

## Ergebnis des Aufnahmeentscheids aus PR 57

PR 57 hat gezielt das zusammengehoerige ZINS000-Paar geprueft und unter
`tests/references/legacy_agrsich/zins000/` versioniert:

| Datei | Lokale Quelle | Headerfamilie | Zeilen / Fenster | SHA-256 |
| --- | --- | --- | --- | --- |
| `IMSVU014.DAT` | `incomming/ZINS000/IMSVU014.DAT` | Versicherer-Agrsich | 300 / `1-300` | `0276eab7b1f80dfc39773eb0e5a4a5df02b69b140792be9f810baa222e8ce828` |
| `IMSVUSK1.DAT` | `incomming/ZINS000/IMSVUSK1.DAT` | Versicherer-Agrsich | 300 / `1-300` | `dc066d624c443fc165b0fb83481083dae33d823bd8a3a20d934adb4bf5426b2a` |

Beide Kandidaten sind mit dem Versichererformat plausibel, repraesentieren aber
nicht einfach laengere Fassungen der heutigen Baseline. Ein numerischer
Zeilenvergleich ergab im Ueberlapp:

- `IMSVU014.DAT` gegen `VU14L1.DAT`: `0/100` gleiche Periodenzeilen;
- `IMSVUSK1.DAT` gegen `VUSK1L5`, `VUSK1L4` und `VUSK1L3`: `0/300` gleiche
  Periodenzeilen.

Das Paar ist daher nur als getrennte ZINS000-Referenzschicht aufgenommen,
niemals als Ersatz oder Fortsetzung der 19 Kernreferenzen. Header,
Periodenfolge, Zeilenzahl, Hashes und die gemeinsame Quelleneinordnung sind in
`tests/fixtures/legacy_zins000_reference_layer.json` fixiert und getestet. Der
Kernkorpus bleibt bei 19 Dateien und 6.300 Vergleichszeilen.

`incomming/` selbst bleibt unversioniert. Es wurden nur die beiden einzeln
geprueften Dateien gezielt in den historischen Referenzbestand uebernommen.
Die Herkunfts- und Vergleichsgrenzen stehen in
`docs/migration/zins000_reference_layer.md`.

## Freigabegates ab PR 60

Vor dem Mehrperiodenvergleich muessen folgende Punkte gruen sein:

1. alle Korpusdateien sind versioniert und anhand ihres Hashes identifizierbar;
2. Header, Parserfamilie, Subjekttyp, Aggregatstufe und Selektor sind belegt;
3. Periodenfenster sind eindeutig, sortiert und lueckenlos;
4. Coverage meldet keine vorhandene, aber ungedeckte Referenz;
5. ZINS000 wird, falls aufgenommen, als eigene historische Schicht behandelt;
6. `VU014PR1.DAT` bleibt ohne Feldmapping ausserhalb aller Agrsich-Bundles;
7. der PR-58-Vertrag akzeptiert nur extern gelieferte, vollstaendige
   Exporttabellen und baut keine Neu-Zeilen aus Referenzzeilen;
8. PR 59 klassifiziert vollstaendige Vergleiche technisch und weist fehlende
   Inputs blockierend aus, ohne aus Teiltreffern Vollgleichheit abzuleiten;
9. PR 60 liefert einen ersten tatsaechlich berechneten schmalen Output oder
   dokumentiert die konkrete verbleibende Adapterluecke (erledigt fuer VU14,
   Perioden `1-4`, nur Aggregation/Export aus expliziten Snapshots);
10. PR 61 klaert `selector_value = "all"` gegen den historischen Level-IV-
    Selektor `SK1`, ohne VUSK1-Zeitfenster als Aggregatebenen umzudeuten
    (erledigt durch enge technische Kanonisierung und Negativtests);
11. PR 62 bereitet den kontrollierten Run-Control-Freigabepfad vor, ohne die
    Korpusgrenzen oder historischen Gleichheitsaussagen zu erweitern
    (read-only Freigabecheck erledigt);
12. PR 63 schafft vor einem echten Adapterstart die atomare Status- und
    Ergebnisgrenze gegen Doppelstarts (erledigt; ohne Erweiterung des
    historischen Korpus oder der Gleichheitsaussage).
13. PR 64 darf nur den kontrollierten UI-Pfad an diese Backend-Grenze anbinden;
    der historische Korpus, automatische Regelwahl und freie Browserpfade
    bleiben unveraendert gesperrt (erledigt).
14. PR 65 darf Ergebnisverlauf und Fehleranzeige haerten, aber weder den
    Korpus erweitern noch aus persistierten Teilergebnissen historische
    Vollgleichheit ableiten.

## Offene Risiken

- Der genaue historische Laufkontext einzelner geerbter Referenzen ist nicht
  fuer jede Datei gleich stark belegt.
- ZINS000-Zeitstempel aus 2026 sind lokale Entpack-/Bereitstellungszeitpunkte
  und kein Beleg fuer den historischen Erzeugungszeitpunkt.
- Historischer RNG, Scheduler und automatische Regelwahl sind durch den
  Dateikorpus nicht rekonstruiert.
- Weitere Modellkorrekturen sind erst nach belegten Abweichungen aus PR 59
  zulaessig.
