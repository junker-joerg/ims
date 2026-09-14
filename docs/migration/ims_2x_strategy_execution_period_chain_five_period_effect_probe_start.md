# PR145: Kontrollierter Fuenf-Perioden-Start

Stand: 2026-09-14

## Zweck

PR145 macht die bereits in PR144 gepruefte Fuenf-Perioden-Wirkung dauerhaft
idempotent und legt ihr Ergebnis unveraenderlich ab. Die fachliche
Periodenlogik, VU-/VN-Regeln und Carryover-Reihenfolge bleiben unveraendert.

## C-zu-Python-Zuordnung

| Historische Semantik | Python-Komponente | Entsprechung und Grenze |
| --- | --- | --- |
| Periodenschleife `ESS.C:73-75` | `run_strategy_execution_five_period_effect_probe` | fuehrt weiterhin lokal die Perioden 1 bis 5 streng aufsteigend aus |
| Zustandsuebergang zwischen Perioden | vorhandene VU-/VN-Carryover-Runner | wird ausschliesslich nach den kanonischen Kettenflags ausgefuehrt |
| historischer 100-Perioden-Rahmen `IMSDATA.C:14` | Fuenf-Perioden-Startvertrag | wird noch nicht freigegeben; PR145 bleibt exakt auf fuenf Perioden begrenzt |
| historisch impliziter Laufzustand | Idempotenz- und Ergebnistabellen | macht Freigabe, Versuch, Kettenkopie und Ergebnis explizit nachvollziehbar |

Die neue Datei
`python_port/ims/api/strategy_execution_period_chain_five_period_effect_probe_start.py`
enthaelt nur Start-, Ablage- und Leselogik. Sie fuegt keine neue Fachregel ein.

## Persistenz

`strategy_execution_five_period_effect_probe_attempts` protokolliert den
atomaren Idempotenzanspruch und den Abschlussstatus. Ein fehlgeschlagener
Versuch enthaelt Aufrufzaehler und Fehlerhinweis, aber kein Teilresultat.

`strategy_execution_five_period_effect_probe_results` besitzt die Ketten-ID
als Primaerschluessel. Der Gesamtdigest deckt Ablageidentitaet und -zeitpunkt
sowie drei kanonische JSON-Bloecke ab:

1. den vollstaendigen Startrequest samt Freigabe;
2. die beim Start gepruefte Fuenf-Perioden-Kette;
3. das vollstaendige PR144-Wirkungsergebnis samt Prefixnachweis.

Beim Lesen werden Requestvertrag, Kettendigest, abgeleitete Ketten-ID,
Perioden 1-5, Uebergaenge 1-2 bis 4-5, Prefixnachweis und Ergebnisdigest erneut
geprueft. Der Nachweis haengt dabei nicht vom spaeteren Zustand der
Kandidaten- oder Prefixablage ab.

## Bewusste Grenzen

- keine Workbench-Bedienung in PR145;
- kein freier oder allgemeiner Mehrperiodenrunner;
- keine Queue, kein Worker und keine automatische Wiederholung;
- keine CSV-, JSON- oder XLSX-Ausgabedatei;
- keine neue Fachlogik oder automatische historische Regelauswahl;
- keine Aussage, dass zufallsgetriebene historische Laeufe vollstaendig
  reproduziert werden.

PR146 darf die vorhandenen Endpunkte kontrolliert in der Workbench bedienen.
PR147 entscheidet getrennt ueber die naechsten Horizonte bis 100 Perioden.
