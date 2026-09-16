# PR146: Fuenf-Perioden-Bedienpfad im Browser abnehmen

Stand: 2026-09-16

## Einordnung

PR146 schliesst die in PR145 geoeffnete Fuenf-Perioden-Startgrenze mit einer
reproduzierbaren Browserabnahme. Kandidatenbau, Kettenbau, Runner, Carryover,
Prefixvergleich, Idempotenz und Ergebnisablage bleiben fachlich unveraendert.

## C-zu-Python-Mapping

| Historischer Bezug | Python-/UI-Ziel | Bedeutung |
| --- | --- | --- |
| Periodenschleife in `ESS.C:71-75` | vorhandener PR144/PR145-Pfad | kontrollierter Ausschnitt aus Periode 1 bis 5 mit vier Uebergaengen |
| VU-/VN-Vorperiodenzustand | sichtbare Uebergangszeilen | die gespeicherten Carryover-Flags werden unveraendert angewandt |
| `SIMLAENGE = 100` in `IMSDATA.C:14` | gesperrte Folgegrenze | Browserabnahme fuer fuenf Perioden belegt noch keinen 100-Perioden-Lauf |
| historischer manueller Programmstart | Workbench-Freigabeformular | Person, Begruendung, Prefixreferenz und ausdrueckliche Bestaetigung sind sichtbar |

PR146 portiert keine C-Regel und behauptet keine historische
Vollgleichheit.

## Read-only Ketteneingang

`strategy_execution_period_chain_input_from_payload` projiziert einen beim
Lesen bereits vollstaendig verifizierten kanonischen Kettensatz auf den
versionierten Eingang `ims.strategy-execution-period-chain-input.v1`. Die
Projektion besteht ausschliesslich aus Basismodell, Lauf- und Horizontwerten,
unveraenderlichen Kandidatenreferenzen sowie den gespeicherten
Uebergangsflags. Sie schreibt nicht und startet nichts.

Damit sendet die Workbench denselben Eingang erneut an die serverseitige
PR145-Pruefung. Ein frei editierbares JSON, ein Browser-Dateipfad oder eine
Umgehung des Neubaus wird nicht eingefuehrt.

## Reproduzierbarer Smoke-Aufbau

Der PR146-Smoke erstellt eine frische lokale Datenbank, den erfolgreichen
Zwei-Perioden-Prefixnachweis und eine getrennte Fuenf-Perioden-Kette. Der
regulaere Webserver liefert Produktionsfrontend und API nur ueber Loopback.
Die Metadatenleser werden fuer den nebenlaeufigen Browser-Smoke serialisiert;
dies aendert weder Produktpersistenz noch Fachlogik.

## Sichtbare Abnahme

- `1440 x 1000`: alle fuenf Perioden, vier Uebergaenge, Prefixnachweis,
  Ergebnisdigest, Verlauf und Folgegrenze sind lesbar;
- `390 x 844`: Zeitlinie, Nachweise und Bedienfelder stehen einspaltig ohne
  horizontale Ueberbreite oder Ueberlagerung;
- vor der ausdruecklichen Checkbox ist `Fuenf Perioden starten` deaktiviert;
- nach erfolgreichem Start ist der Startknopf entfernt und der unveraenderlich
  gespeicherte Nachweis sichtbar;
- ein Browser-Neuladen liest dasselbe Ergebnis und denselben Verlauf;
- die Browserkonsole bleibt ohne Warnung oder Fehler.

## Automatisierte Abnahme

Die Tests pruefen:

- frische Datenbank, frische Profile, vorhandenen Frontend-Build und
  Loopback-Bindung;
- den verlustfrei rueckprojizierten Ketteneingang;
- einen erfolgreichen Start mit fuenf Runner- und acht Carryover-Aufrufen;
- fuenf Periodenwirkungen, vier Uebergaenge und exakten Prefix 1-2;
- idempotenten Replay ohne weitere Aufrufe oder Schreibvorgaenge;
- fehlende Freigabe und falschen Digest vor einem Runner;
- einen Fehler in Periode 4 ohne Teilresultat;
- Browseranker sowie Format und Abmessungen beider Handbuch-PNGs.

## Grenzen und naechster Schritt

Die Abnahme belegt genau den vorbereiteten Lauf fuer Periode 1 bis 5. Sie
belegt keinen freien Mehrperiodenlauf, keinen 100-Periodenlauf, keine
Regulierungssimulation und keine Reproduktion eines historischen RNG-Laufs.
Es entstehen keine fachlichen Ausgabedateien; `incomming/` wird nicht gelesen
und bleibt unversioniert.

PR147 definiert als naechstes die kontrollierten Horizonte 10, 25, 50 und
100 samt Laufzeit-, Ressourcen-, Abbruch- und Fehlergrenzen, noch bevor ein
laengerer Runner freigegeben wird.
