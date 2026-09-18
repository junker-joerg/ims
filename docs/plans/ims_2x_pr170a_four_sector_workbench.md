# PR170a: Vier-Sparten-Bilanz in der Workbench

Stand: 2026-09-18
Status: umgesetzt; Browser-Smoke fuer breite und schmale Ansicht, Konflikte,
Entwertung und API-Fehler bestanden.

## Ziel

Der PR170-Rechner wird ohne neue Fachregel im Browser bedienbar. Die
bestehenden Editoren fuer Kfz/Sach-Haftpflicht, Leben und Kranken behalten
ihre eigenen Eingaben. Erst nach erfolgreicher Vorschau werden deren
urspruengliche Eingaben fluechtig an die Gesamtbilanzansicht uebergeben.
Diese ruft `POST /api/accounting/four-sector-balance` auf; der Server
rechnet die vier Sparten erneut und gibt nur eine vollstaendige Bilanz frei.

## Bedien- und Herkunftsgrenze

- Schaden: ein gepruefter Eingang fuer Kfz und Sach-Haftpflicht, in
  Baseline und Variante **derselbe** Stand (kein versteckter Schock).
- Leben und Kranken: die jeweils gepruefte Baseline oder Variante.
- Die vier Eingaben muessen dieselbe VU-ID und denselben Horizont haben.
  Die Krankenquelle liefert die Szenariokennung. Nichtleben und Leben
  haben noch keine gleichartigen Szenariokennungen; der Anwender bestaetigt
  ihre fachliche Zusammengehoerigkeit ausdruecklich.
- Jede Aenderung oder fehlgeschlagene Neuberechnung einer Teilrechnung
  entzieht deren Freigabe und entfernt eine alte Gesamtbilanz. Kein
  Speichern, Download, Mehrsparten-Runner oder historisches Mapping.
- Die gefuehrte Lebens-Workbench liefert derzeit zwei Perioden. PR170a
  ist deshalb als Zwei-Perioden-Bedienweg abnehmbar; der PR170-Kern
  unterstuetzt mehr, aber das ist noch kein 100-Perioden-UI-Versprechen.

## Abnahme

- Vier sichtbare Quellenzustaende, direkte Navigation zu ihren Editoren,
  Baseline/Variante und begruendete Sperre bei fehlender oder
  widerspruechlicher Quelle.
- VU-Gesamtbilanz und vier Spartenallokationen mit exakten Dezimalwerten,
  Periodentabelle, Herkunft und Digest; API-Fehler ohne Teilergebnis.
- Browserabnahme bei breitem und schmalem Viewport, einschliesslich
  erfolgreichem Fall, Horizontkonflikt, Quellenaenderung und Fehlerpfad.
  Handbuchbilder zeigen Eingaben und Ergebnis.

## Altcode und offene Punkte

`IMSDATA.C` definiert nur die beiden historischen Schadenpositionen
`LV`/`KV`; Leben und Kranken sind die dokumentierten IMS-2.x-Erweiterungen.
Die PR170a-Komponente fuehrt keine neue Aggregatformel ein. Ob die
unabhaengigen Szenarioannahmen oekonomisch gemeinsam plausibel sind,
bleibt eine fachliche Entscheidung des Anwenders. Ein gemeinsamer
Szenarioeditor und ein kontrollierter 100-Perioden-Mehrspartenlauf sind
spaetere, getrennt zu pruefende Schritte.
