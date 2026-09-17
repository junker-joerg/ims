# PR166: Lebens-Ergebnisablage, API und XLSX

Stand: 2026-09-17
Status: umgesetzt; PR167 Workbench und Browserabnahme folgen

## Ziel und Grenze

Die reine PR165-Lebens-Periodenkette wird ueber eine kontrollierte API
zunaechst ohne Schreibzugriff angezeigt und danach nur mit expliziter
Freigabe gespeichert. Ein gespeichertes Ergebnis ist per ID und Digest
lesbar und als XLSX mit denselben kanonischen Zahlen exportierbar.
Keine Aenderung am Nichtleben-Runner, keine Lebens-UI und keine
historische Vollgleichheitsbehauptung.

## Vertrag

- `preview`: versionierte PR165-Eingabe berechnen; Eingabe- und
  Ergebnis-Digest liefern, nichts speichern.
- `start`: PR165-Eingabe, beide erwarteten Digests, Idempotenzschluessel
  und ausdrueckliche Speicherfreigabe verlangen; serverseitig erneut
  berechnen und vor dem Schreiben vergleichen.
- SQLite-Ergebnis unter stabilem ID speichern. Wiederholung mit gleichem
  Schluessel und identischer Eingabe liest den geprueften Bestand ohne
  erneute Berechnung. Schluesselkonflikte und veraenderte/defekte
  gespeicherte Werte liefern Fehler ohne Teilergebnis.
- `result` und `result.xlsx`: nur gespeicherte, erneut digestgepruefte
  Werte lesen. XLSX verlangt `If-Match` mit Ergebnis-Digest; alle
  Betragszellen bleiben exakte Dezimalstrings als Text.
- `results`: maximal 100 juengste, erneut gepruefte Ergebnisidentitaeten
  und Horizonte rein lesend anzeigen.
- Vorschau und Start laufen ausserhalb des Event-Loops. Nach einem
  Zeitbudget von 20 Sekunden wird kooperativ abgebrochen; danach findet kein Speichern
  statt. Der PR165-Extremfall von rund 46 Sekunden darf nicht
  stillschweigend einen interaktiven Request blockieren.

## Herkunft, Nachweis, offen

`IMSDATA.C` und `IMS.E` belegen nur Perioden, zwei Schaden-Sparten und
Reservenverzinsung. Fachliche Lebenswerte kommen ausschliesslich aus
PR163-165. Tests decken Vorschau, exakte Exportzahlen, Replay,
Konflikte, Manipulation, fehlende SQLite-Freigabe, Zeitbudget und
FastAPI/Starlette ab. PR167 bleibt der gefuehrte Seminar-Bedienweg.
Die neue SQLite-Tabelle ist noch nicht Bestandteil des alten
Metadaten-Recovery-Digests; Backup-/Restore-Abnahme bleibt offen.
