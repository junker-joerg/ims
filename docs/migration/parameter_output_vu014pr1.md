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

## Naechster Schritt

Vor einer Referenzuebernahme braucht es einen separaten kleinen Schnitt:

1. Historische Schreibstelle oder belastbares Feldmapping fuer `Pr1L1` bis
   `Pr1L5` identifizieren.
2. Entscheiden, ob ein eigener Parameterausgabe-Parser noetig ist.
3. Erst danach eine gezielte Referenzuebernahme und Tests planen.
