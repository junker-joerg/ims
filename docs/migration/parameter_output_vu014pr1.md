# Parameterausgabe VU014PR1

## Ziel

Dieser Schnitt klaert `VU014PR1.DAT` nur als historischen Kandidaten fuer eine
spaetere Parameterausgabe-Validierung. Die Datei wird nicht in
`tests/references/legacy_agrsich/` uebernommen und nicht in das
Legacy-Validierungsbundle eingetragen. Es gibt keine Simulation, keine neue Fachlogik
und keine historische Vollgleichheitsbehauptung.

## Quelle

Lokale, nicht versionierte Quelle:

```text
incomming/IMS.DAT/VU014PR1.DAT
```

`incomming/` bleibt lokaler Kandidatenbestand und wird nicht versioniert.

## Beobachtetes Format

| Eigenschaft | Wert |
| --- | --- |
| Dateigroesse | `3737` Bytes |
| SHA-256 | `af8e58e6548582fde3d02c0f037bb1c89c71402649b1ab1f342a11dc9d78fecd` |
| Nichtleere Zeilen | `101` |
| Datenzeilen | `100` |
| Periodenfenster | `1-100` |
| Spalten je Zeile | `6` |

Beobachteter Header:

```text
#t   Pr1L1  Pr1l2 Pr1L3 Pr1L4 Pr1L5
```

Die Datenzeilen beginnen mit einer vierstelligen Periode und enthalten danach
fuenf numerische Werte. Der Header deutet auf eine Praemien-Parameterreihe fuer
VU `014`, Sparte oder Parameter `Pr1` und fuenf `L*`-Spalten hin. Die genaue
fachliche Bedeutung der fuenf Spalten ist in diesem Schnitt nicht belegt.

## Altcode-Spur

Eine reine Textsuche im versionierten Altcode nach `VU014PR1`, `014PR1` und
nahen Dateinamensmustern liefert keinen direkten Treffer. Damit ist die
historische Schreibstelle fuer diese konkrete Datei im aktuellen Repo-Kontext
noch nicht identifiziert.

Die naechsten belegbaren Spuren in den versionierten Altquellen sind:

- `IMSDATA.C` definiert fuer Versicherer je Sparte `Pr[SIMLAENGE+1]` als
  Zielvektor "Praemie in Periode t".
- `IMSDATA.C` definiert ausserdem `Pv[16]` als IMS-Parametervektor der
  Versicherungen.
- `IMS.E` schreibt in `Agrsich` die normalen Versicherer-Aggregatdateien mit
  Header `#t Pr1 Wa1 Rs1 Vn1 Sa1 Sh1 Pr2 Wa2 Rs2 Vn2 Sa2 Sh2`; diese Werte
  kommen direkt aus `VU[i].DatenVU->Sp[1].l.Pr[period]`,
  `VU[i].DatenVU->Sp[1].l.Wa[period]` und den weiteren Spartenfeldern.
- `IMS.E` liest in `Erstvu` den Startwert `pr1t1` aus
  `VU[j].DatenVU->Sp[1].l.Pr[1]` und die Parameterwerte aus `Pv[0]` bis
  `Pv[15]`, bevor `Vuauini(...)` mit Praemien- und Werbereaktionsparametern
  aufgerufen wird.

Damit ist `Pr1` als Versicherer-Praemienbezug fuer Sparte 1 plausibel, aber die
fuenf `L*`-Spalten von `VU014PR1.DAT` sind nicht aus der identifizierten
Schreiblogik ableitbar. Insbesondere ist nicht belegt, ob `L1` bis `L5`
Parameterlaeufe, Sensitivitaetsvarianten, lokale Auswertungslaeufe oder eine
andere historische Gruppierung bezeichnen.

## Verwandte lokale Kandidaten

Im lokalen, nicht versionierten Kandidatenbestand wurden naheliegende Dateien
geprueft:

| Datei | Befund |
| --- | --- |
| `VU14P1.DAT` | 13-spaltiges Versicherer-Agrsich-Format, Periodenfenster `51-100` |
| `VU14P2.DAT` | 13-spaltiges Versicherer-Agrsich-Format, Periodenfenster `1-50` |
| `IMSVU014.DAT` | In mehreren ZIP-Archiven vorhanden, normales Versicherer-Agrsich-Format |

Diese Dateien belegen die normale Agrsich-Ausgabe fuer Versicherer `014`, aber
nicht das 6-spaltige Parameterausgabe-Format von `VU014PR1.DAT`. In den
geprueften ZIP-Archiven wurde keine zweite `VU014PR1.DAT`-Variante gefunden.

## Vorlaeufige Einordnung

`VU014PR1.DAT` bleibt im Coverage-Backlog als `parameter_output` eingeordnet.
Die Datei passt nicht zum bestehenden Versicherer-Agrsich-Parser fuer
`#t Pr1 Wa1 Rs1 ...`, weil sie nur fuenf Werte je Periode nach `#t` enthaelt
und offenbar eine Parameterausgabe statt eines Agrsich-Aggregats beschreibt.

## Grenzen

- Keine Uebernahme in `tests/references/legacy_agrsich/`.
- Keine Erweiterung von `tests/fixtures/legacy_validation_bundle.json`.
- Kein Parser fuer fachliche Werte, solange das Feldmapping nicht geklaert ist.
- Keine Gleichsetzung mit den bestehenden `imsvu014.dat`-Agrsich-Ausgaben.
- Keine Aussage, dass die fuenf `L*`-Spalten Aggregatstufen, Zeitfenster oder
  Klassen bedeuten.
- Feldmapping bleibt offen; der Schnitt dokumentiert eine Grenze, keine neue
  Validierungsabdeckung.

## Naechster Schritt

Vor einer Referenzuebernahme braucht es externe oder noch nicht erschlossene
historische Evidenz:

1. Historische Schreibstelle oder belastbares Feldmapping fuer `Pr1L1` bis
   `Pr1L5` identifizieren.
2. Entscheiden, ob ein eigener Parameterausgabe-Parser noetig ist.
3. Erst danach eine gezielte Referenzuebernahme und Tests planen.
