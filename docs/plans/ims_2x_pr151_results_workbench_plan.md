# PR151: 100-Perioden-Ergebnisarbeitsplatz

## Ziel

Eine bereits gespeicherte, vollstaendige 100-Perioden-Kette wird in der
Workbench ausdruecklich freigegeben, fluechtig ausgefuehrt und sofort als
Zeitreihe gelesen. Ein zweiter, gleich praefixierter Lauf kann als
Vergleichslauf angezeigt werden. Das PR150-ZIP ist aus genau dem sichtbaren
Ergebnisdigest heraus erneut erzeugbar und wird bei Abweichung gesperrt.

## Historischer Bezug und technische Grenze

| Ursprung | PR151-Nutzung |
| --- | --- |
| `ESS.C:71-75`, `IMSDATA.C:14` | vorhandener PR149-Lauf ueber Perioden 1-100; kein neuer Scheduler |
| VU-/VN-Vorperiodenzustaende | bestehender Prefixnachweis und vorhandene `state_after`-Felder; keine neue Regel |
| PR145-Fuenfperiodennachweis | gespeicherte Prefixreferenz vor einem 100er-Start |
| PR150-Buendel | Digest-gebundener Download, keine Ergebnisablage |

## Bedienvertrag

- Neue Ergebnisansicht nutzt nur erneut verifizierte gespeicherte Ketten
  mit exakt 100 Perioden und einen verfuegbaren Fuenf-Perioden-Nachweis.
  Freigabeperson, Grund und ausdrueckliche Bestaetigung sind Pflicht.
- Ein Start laesst die vorhandene isolierte Wirkungsprobe einmal laufen.
  Ergebnis bleibt nur im aktuellen Browserzustand. Reload verliert es;
  fehlende Kette, Prefix, Freigabe und Laufzeitfehler werden sichtbar.
- Zeitreihe: Akteursart, Akteur, vorhandenes Zustandsfeld, ggf. nullbasierter
  Sektorindex. Keine Aggregation oder Neuberechnung. Vergleiche sind nur
  zwischen Ergebnissen mit derselben gespeicherten Prefixreferenz moeglich.
  Zwei Linien und eine tabellarische Periodenansicht ohne Kausalaussage.
- Download startet den PR150-Lauf erneut. Ein `If-Match`-Digest und
  Antwort-Header pruefen die Gleichheit zur sichtbaren Wirkung; bei
  Abweichung gibt es kein ZIP. Kein stilles Replay/Idempotenzversprechen.
- Breiter und schmaler Viewport, Tastaturpfad, Lade-/Fehler-/Leerstaaten,
  100 Perioden, falscher Digest und Download werden abgenommen.

## Offen

Der Aufbau von 100 Einzelkandidaten und einer gespeicherten 100er-Kette
ist eine getrennte vorbereitende Aufgabe. PR151 macht vorhandene Ketten
bedienbar, erzeugt sie aber nicht automatisch. Eine dauerhafte
100-Perioden-Ergebnisablage benoetigt einen eigenen Vertrag. Keine
historische Vollgleichheits- oder regulatorische Aussage.
