# IMS 2.x: Restplan ab PR179

Stand: 2026-09-18. Planungsstand nach PR178a; naechster Umsetzungsschritt PR179.
Die [aktive Roadmap](ims_2x_all_lines_management_lab_roadmap.md) bleibt die
nummerierte Quelle. Dieses Dokument erklaert Anforderungen, Abhaengigkeiten
und Abnahmegrenzen aus Sicht eines Anwenders im Managementseminar.

## Ausgangspunkt

- Der portierte 100-Perioden-Kern, die Einzelspartenmodelle, eine
  Vier-Sparten-Modellbilanz fuer zwei Perioden, eine vereinfachte
  Kapitalansicht und das Benutzer-/Installationshandbuch v1 sind vorhanden.
- Die 100-Perioden-Kette ist nicht durchgaengig gefuehrt aufbaubar.
  Die gemeinsame Vier-Sparten-Rechnung und -Ansicht reichen noch nicht bis
  Periode 100. PR154 validiert Strategieplaene je Nichtleben-Sparte, fuehrt
  sie aber nicht aus. Leben und Kranken haben noch keine solche
  Katalogstrategie je Sparte.
- Kfz und Sach-Haftpflicht sind moderne Zielsparten. Die zwei anonymen
  historischen Schadenpositionen belegen keine fachliche Kfz-/Sach-Zuordnung.
- Der Legacy-Korpus ist ein diagnostischer Vergleich, kein Nachweis
  historischer Vollgleichheit. `incomming/` bleibt unversioniert.

## Anforderungen und Zuordnung

| Anforderung | Belegter Stand | Verbleibende Abnahme |
| --- | --- | --- |
| 100 Perioden selbst aufbauen, starten, vergleichen | Vorbereitete Kette laeuft; gefuehrter Bau fehlt | PR187a-c: vollstaendige Kontexte, neue Kandidaten, explizite Freigabe, Start und Fehlerpfade |
| Vier Sparten, Versichererbilanz und Downloads | Vier-Sparten-Bilanz fuer zwei Perioden; getrennte 100er-Quellen | PR187d-f: gemeinsamer Quellenvertrag, 100er-Rechnung und lesbare Ansicht; anfangs nur explizit zusammengefuehrte Teilmodelle |
| VU/VN-Strategie, Parameter, Gruppe und Aktivierungszeit je Sparte | PR154 ist nur ein gepruefter Nichtleben-Entwurf; Leben/Kranken getrennte Annahmen | PR187g-k: Quellen-/Zeitvertrag, begrenzte Ausfuehrung, gefuehrte Eingabe und mindestens eine belegte Wechselwirkung |
| Kapital unter Schocks erklaeren | Modell-Eigenmittel-Proxy und Managementschwellen sichtbar | PR185: DORA-Folgen auf Modellwerte; keine regulatorische Bedeckungsquote oder SCR/MCR |
| ICT-/DORA-Wirkungskette verstehen | Noch keine durchgehende Kette | PR179-186: Service, Asset, Anbieter, Ereignis, Zeitmass, Betriebswirkung, Gegenmassnahme und Dossier |
| Seminar ohne Quellcode durchfuehren | Handbuch v1 und Teilansichten | PR187, PR188-190: gefuehrter Pfad, reproduzierbare Faelle, Moderation und End-to-End-Abnahme |
| Einfache Windows-Verteilung | Testpaket benoetigt Python auf dem Zielrechner | PR191-192: offline testbares One-folder-ZIP mit Doppelklick-Start; erst nach PR190 |

## Reihenfolge und Entscheidungstore

1. **PR179-186: DORA-Wirkungsketten.** Ein begrenzter, klar markierter
   Workshopfall muss vom ICT-Ereignis bis zu operativen Fluesseffekten und
   dem Modell-Ergebnis nachvollziehbar sein. PR179 liefert zuerst einen
   read-only Herkunfts- und Abhaengigkeitsvertrag. Keine Compliance-Pruefung.
2. **PR187 und PR187a-c: gefuehrte 100er-Kette.** PR187 legt den
   gefuehrten Szenarioassistenten an; danach ist jeder Kandidat neu geprueft.
   Perioden, Seeds, Digests und Prefixe sind stabil. Ein fehlerhafter
   Kontext erzeugt weder Lauf noch Teilresultat.
3. **PR187d-f: gemeinsamer 100er-Vier-Sparten-Fall.** Quellen und Varianten
   werden erklaert statt still gleichgesetzt. Die Bilanz geht je VU und
   Periode auf; Ansicht und CSV/JSON/XLSX stammen aus demselben Lauf.
   Das ist noch keine endogen gekoppelte All-Sparten-Marktreaktion.
4. **PR187g-k: Strategien wirksam machen.** PR187g klaert fuer VU und VN
   je Sparte, Gruppe und inklusivem Periodenfenster die Regelquelle, die
   Parameter, exogene Groessen und zulaessige Uebergaenge. Ohne belegtes
   Mapping gibt es keinen Ausfuehrungsadapter. PR187h schliesst nur die
   gedeckten Kfz-/Sach-Haftpflicht-Strategien an. PR187i bindet begrenzte
   Lebens-/Kranken-Entscheidungen an vorhandene Fluesse an; Schaden- und
   Todesfallannahmen bleiben als exogen erkennbar. PR187j macht Auswahl,
   Gruppen und Zeitfenster in der Workbench pruef- und bedienbar. PR187k
   belegt in einem kontrollierten 100er-Fall mindestens eine durchgaengige
   Reaktion von Strategieentscheidung ueber Spartenfluss zur Modellbilanz;
   Umfang und nicht gekoppelte Kanaele werden sichtbar benannt.
5. **PR188-190: Seminarfreigabe.** Kuratierte Baseline/Variante-Faelle,
   Moderationsmaterial und ein browserabgenommener Durchlauf mit Bilanz,
   Modellkapital, DORA-Kette und Export. Die jeweils aktuellen
   Handbuch-Screenshots zeigen nicht nur Menues, sondern Schock, Output
   und fachliche Deutung. PR190 ist Demo-/Seminarreife, keine fachliche
   Produktionsfreigabe fuer Unternehmens- oder Aufsichtsentscheidungen.
6. **PR191-192: Windows-ZIP.** Erst nach fachlicher Seminarabnahme:
   entpacken, doppelklicken, offline auf frischem Windows x64 ohne
   installiertes Python/Node starten. Unsigned-EXE-/SmartScreen-Grenzen
   und Nutzerdatenpfad stehen in der Kurzanleitung.

PR187g ist ein fachliches Entscheidungstor. Zeigen die Quellen keine
saubere sektorbezogene Uebersetzung oder ist die geforderte Kopplung
groesser als ein reviewbarer PR, wird der betroffene Schritt vor
Implementierung weiter aufgeteilt und die PR-Zahl offen korrigiert.
Keine erfundene historische Zuordnung und kein Ersatz durch bloss
addierte Spartenwerte.

## Restzahl und grober Aufwand

| Ziel | Zusaetzliche PRs ab PR178a |
| --- | ---: |
| DORA-Dossier nach PR186 | 8 |
| Gefuehrter 100er-Kettenstart nach PR187c | 12 |
| Additive 100er-Vier-Sparten-Ansicht nach PR187f | 15 |
| Erste kontrollierte Strategie-/Sparten-Wirkung nach PR187k | 20 |
| Managementseminar-Abnahme nach PR190 | 23 |
| Windows-ZIP nach PR192 | 25 |

Das sind **geplante reviewbare Schnitte, keine Terminzusage**. Als grobe
Restannahme fuer Code, Tests und Dokumentation gelten 8.000-16.000 LoC
bis PR192: DORA 3.000-5.000, 100er-/Strategie-/Seminaranschluss
4.000-9.000, Windows-Paket 1.000-2.000. Diese Zahlen sind keine Messung
des bestehenden Repos; nach PR186 und PR187g werden sie neu geschaetzt.

## Nicht still enthalten

- Historische 1:1-Zufallsfolgen oder eine Vollgleichheit aller Altdaten;
  Referenzlaeufe mit anderer Parametrisierung bleiben getrennt.
- Regulatorisch berechnetes Solvency-II-SCR/MCR, Eigenmittel oder echte
  Bedeckungsquote; PR176 hat diese Werte bewusst gesperrt.
- Ein automatisches DORA-Konformitaetsurteil oder eine Rechtsauslegung.
- Nachweis eines vollstaendig endogen gekoppelten deutschen All-Sparten-
  Versicherungsmarkts. PR187k belegt nur die konkret implementierten
  Reaktionskanaele. Ein groesserer Markt-/Regulierungs-Simulator braucht
  danach einen eigenen fachlichen Scope und Datensatz.
- Kalibrierung an aktuellen realen Marktzahlen, Linux-/iOS-Juno-Support,
  grafischer Installer und Code-Signierung. Diese Optionen sind
  Entscheidungen nach separater Quellen-, Machbarkeits- und
  Nutzenpruefung, keine bereits zugesagten PRs.
- Eine Rueckverdichtung auf die sechs oder sieben C-Dateien. Ein
  gezieltes Modulaudit liegt vor; Konsolidierung folgt nur belegter
  Komplexitaetsreduktion und darf die Fachphasen nicht blockieren.

Jeder neue Fachschritt benoetigt nachvollziehbare Quellen, deterministische
Positiv-/Negativfaelle, stabile Prefixe, atomare Fehlerpfade und klare
Kennzeichnung von Modellannahmen. UI- und Export-Schritte benoetigen
zusaetzlich Browserabnahme auf breitem und schmalem Viewport und
inhaltlich gleiche Ausgabeformate. Der naechste konkrete Schnitt bleibt
PR179: read-only Vertrag fuer Service-, ICT-, Anbieter- und
Abhaengigkeitsbeziehungen.
