# PR163: Begrenzte Einzelpolicen und variable Ablaufleistung

Stand: 2026-09-17
Status: umgesetzt als eigener vollstaendig enumerierter Policenmodus

## Ziel und Grenze

Ein kleiner Lebensfall weist jede aktive Police mit stabiler ID, Kohorte,
Laufzeit, Garantiesatz und Buchverpflichtung aus. Praemie, Zuweisung,
Todesfall und Ablaufleistung werden je Police explizit erfasst. Die
Policenwerte muessen zu Kohorten und Segmentbilanz stimmen. Der
aggregierte PR162-Modus bleibt unveraendert; es gibt keinen impliziten
Moduswechsel, Runner, API, UI, Speicherung oder Export.

## Festgelegte Semantik

- `mode = "fully_enumerated_policies"` und eigene Ein-/Ergebnisversion.
  Zu Periodenbeginn und -ende sind hoechstens 100 aktive Policen erlaubt.
  Alle aktiven Policen sind aufgefuehrt, keine Stichprobe. IDs werden auch
  nach Tod/Ablauf nicht wiederverwendet. Neue Kohorten enthalten ihre
  vollstaendig aufgelisteten neuen Policen.
- Eine Kohorte hat weiterhin homogene Ausgabeperiode, Laufzeit,
  Restlaufzeit und Garantiesatz. Individuelle Buchwerte und Leistungen
  duerfen abweichen. Anfangs- und Schluss-Stueckzahlen sowie
  Garantieverpflichtungen stimmen auf Policen-, Kohorten- und
  Segmentebene exakt ueberein. Praemien und Zuweisungen neuer Policen
  stimmen zu den Ausgabesummen ihrer Kohorte.
- Garantie wird auf den **Anfangsbuchwert jeder Police** mit
  `ROUND_HALF_EVEN` auf `0.0001` berechnet. Laufende Zuweisung folgt,
  dann Tod, dann Ablauf bei Restlaufzeit 1. Bei Tod wird der ganze
  Policenbuchwert freigesetzt; Todesfallleistung bleibt explizit.
  Neupolicen werden erst nach Abgaengen ausgegeben und koennen in der
  Ausgabeperiode weder sterben noch ablaufen; erste Garantie folgt in
  der naechsten Periode.
- Die Ablaufleistung ist je faelliger, ueberlebender Police ein
  **expliziter Szenariobetrag** und muss mindestens deren freigesetzten
  Buchwert decken. Nicht faellige oder verstorbene Policen haben null
  Ablaufleistung. Auszahlung, Freisetzung und Ergebniseffekt werden
  getrennt gezeigt. Eine unveraenderliche Ablaufleistung als
  Vertragsausgabeterm bleibt optionaler spaeterer Quellenmodus; sie
  wird hier nicht stillschweigend eingefuehrt.
- Die vorhandene PR162-Berechnung kann eine Police intern als
  Ein-Stueck-Kohorte fortschreiben. Fuer den Policenmodus wird nur eine
  kontrollierte, interne Ablaufleistungsquelle ergaenzt; PR162s
  oeffentliche Eingabe und Null-Mehrleistungsfall bleiben wertgleich.
  Ausgabe gruppiert Policen wieder unter ihren fachlichen Kohorten.
- Alle Eingaben werden atomar validiert. Ungueltige Zuordnung, fehlender
  Policenfluss, Doppel-ID, nicht faellige Auszahlung, Verletzung der
  Garantieuntergrenze, negative Schlussaktiva oder Summenfehler liefern
  null Ergebniszeilen.

## Herkunft, Tests und offen

`IMSDATA.C` (`MAXSPARTEN 2`, `classVU.Sp`, `classVN.Rk`) und `IMS.E`
belegen Schaden-Sparten und Reserveoperationen, aber keine historische
Lebenspolice. Die neue Semantik ist eine versionierte IMS-2.x-Annahme
aus dem PR160-v3-Zielvertrag. Feste Positiv-/Negativfaelle pruefen
je-Police-Rundung gegen Kohortenrundung, Tod vor Ablauf, abweichende
Leistung und Ergebnis, Summenidentitaeten, spaete Fehler ohne Teilzeilen,
stabile Prefixe sowie unveraenderte PR161/PR162-Ergebnisse. Keine
historische Vollgleichheit, gesetzliche Bilanz oder Solvency-II-Aussage.
Automatische Anlage/Mortalitaet folgen PR164; Runner und Bedienweg
folgen PR165-167.
