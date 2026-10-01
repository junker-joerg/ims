# AP3 M1: deklarierte ICT-Wirkungskette

Stand 01.10.2026. Neue Workshop-Erweiterung; keine historische ICT-Portierung.

| Quelle / Grenze | Neue Komponente | Entsprechung und Abweichung |
| --- | --- | --- |
| `ESS.C:main/sy_simltp/sy_xaktion` | `ims.ict.contract`, `simulation` | Diskrete Perioden, Ereignisse vor Prozessarbeit; reale Stunden werden ausdrücklich zusätzlich deklariert. |
| `IMSDATA.C:SIMLAENGE`, `gperiod/glogtime` | Quellenvertrag | Höchstens 100 Perioden. Ein Tag hat 24 Stunden; die historische Periode bestimmt keine physische Dauer. |
| `IMSDATA.C:classBAV.As/Ar` | ICT-Ereignisse | Historische exogene Schocks begründen keine ICT-Kalibrierung. Ausfall, Teilkapazität, Datenintegrität und gemeinsamer Anbieterausfall sind neue deklarierte Typen. |
| Szenariobasierte moderne Modellbilanz / Eigenmittel-Proxies | ICT-Bilanzoverlay | Explizite Anfangsbilanz und Baseline-Ergebnis; keine gesetzliche Bilanz und derzeit keine automatische Vier-Sparten-/Marktkopplung. |

## Quellen- und Zeitvertrag

`ims.ict-workshop-input.v1` verlangt alle Felder ausdrücklich: Szenario/Variante,
Zeitskala, Quellenhinweis, Anbieter, Assets, gerichtete Asset-Abhängigkeiten,
VU-verantwortliche Services, Nachfrage/Kapazität/Kosten, Bilanzannahmen,
Ereignisse und Gegenmaßnahmen. Unbekannte IDs, Kreisabhängigkeiten, doppelte
Einträge und ungültige Zahlen sperren den ganzen Auftrag. Dezimalwerte sind
begrenzte Zeichenketten, keine binären Gleitkommazahlen.

Intervalle sind halboffen `[Beginn, Ende)`. Innerhalb einer Periode wird an
allen Ereignis- und Maßnahmenzeiten unterteilt. Gemeinsame Anbieterausfälle
wirken auf alle transitiv abhängigen Assets; überlappende identische Ausfälle
werden nicht addiert. Die schlechteste Kapazität bestimmt den Engpass.

## Wirkung und Bilanz

Originalvorgänge und Nacharbeit bilden getrennte Warteschlangen. Verfügbare
Kapazität erledigt zuerst Originale, danach Nacharbeit. Unbearbeitete Vorgänge
bleiben als Rückstand erhalten. Nur erledigte Originale verdienen die
deklarierte Marge. Bei Aufholung kann die Margenwirkung einer Folgeperiode
negativ werden. Nacharbeit verdient keine zweite Marge.

Die periodische ICT-Wirkung ist entgangene Originalmarge gegenüber der
Baseline plus zusätzliche deklarierte Rückstandshaltekosten und Kosten neu
erzeugter Nacharbeit. Haltekosten werden aus den Segment-Endrückständen und
Segmentlängen berechnet; das ist eine explizite diskrete Workshop-Näherung.
Rückstand erzeugt keine ungeprüfte Schadenverpflichtung. Gegenmaßnahmenkosten
werden einmal auf die eindeutig betroffenen VUs verteilt. Periodenergebnis
= Baseline-Ergebnis minus ICT-Wirkung minus Maßnahmenkosten; Eigenmittel
werden damit fortgeschrieben. In jeder Zeile gilt Aktiva = Passiva + Eigenmittel.

Prävention reduziert die Ereignisschwere nur bei rechtzeitiger Aktivierung.
Fallback stellt lokale Kapazität bereit; er repariert weder Daten noch den
gemeinsamen Anbieter für andere Assets. Wiederanlauf verkürzt die lokale
verbleibende Ausfalldauer. Wirksamkeit und Kosten sind unkalibrierte Eingaben.

## Anschluss und Nachweise

`/api/ict` ist dieselbe Starlette-Unteranwendung in beiden vorhandenen API-
Varianten. Validierung und Rechnung schreiben weder Datenbank noch Dateien
und starten keinen historischen Runner. Quellenlimit 256 kB, eine parallele
Rechnung; Exporte verlangen `If-Match` auf den erneut berechneten Ergebnis-
Digest. JSON, CSV und XLSX tragen denselben Digest und genaue Dezimalwerte.

Die Workbench bietet Eingaben, atomar geprüften Expertenvertrag, Baseline/
Variante, Periodenauswahl, Prozessrückstand, Zeitlinie, Anbieterkonzentration
und echte Downloads. Änderungen entwerten Ergebnis und Exportfreigabe.

22 neue Kern-/API-Prüfungen bestanden (zuletzt 2,97 s), zusätzlich 70 vorhandene
Bilanz-/Solvenz-/API-Prüfungen (6,48 s). Sechs reale Browserfälle bestanden
(zuletzt 34,7 s), in Hell/Dunkel bei 1440, 1024 und 390 Pixeln: 100 Perioden,
Fehlerkorrektur, Zustandserhalt, drei echte Downloads, kein Seitenüberlauf
und keine von axe gemeldeten Barrierefreiheitsverletzungen. Eine kleine
Referenzrechnung prüft Rückstände 96/48/0 und kumulierte Wirkung 2,88 exakt.
Der Standardfall endet bei Eigenmittel-Proxy 16769,6000 je VU.

SCR, MCR, regulatorische Quoten, DORA-Konformität und historische Vollgleichheit
bleiben gesperrt. M1 ersetzt nicht die noch offenen M2–M5-Abnahmen des AP3.
