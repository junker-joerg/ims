# PR165: Kontrollierter Lebensanschluss an die Periodenkette

Stand: 2026-09-17
Status: umgesetzt als fluechtiger, atomarer Lebensketten-Schnitt

## Ziel und Grenze

Die PR164-Quellen werden periodengenau aus dem jeweils geprueften
Anfangsbestand aufgeloest und an die bestehende PR163-Policenrechnung
uebergeben. Es gibt bis zu 100 geordnete Modellperioden mit exakt
stabilem Prefix und geprueftem Carryover. Kein Eingriff in den
historischen Nichtleben-Runner, keine API, Ablage, XLSX oder UI.

## Eingabe und Wertuebergabe

- Eigene versionierte Huelle mit VU-ID, `opening`, `periods` und
  vollstaendigem PR164-Annahmeplan. VU-ID und Horizont stimmen genau
  ueberein. PR163-Anfangsbestand und Neugeschaeft bleiben vollstaendig
  enumeriert; hoechstens 100 aktive Policen zu jedem Periodenrand.
- Periodenfluesse nennen `death_benefit_if_death` und
  `maturity_benefit_if_due` je aktiver Anfangspolice. Es gibt darin
  weder ein zweites `investment_result` noch explizite `death`-Flags:
  diese stammen ausschliesslich aus dem PR164-Plan. Eine ausgewaehlte
  tote Police erhaelt die explizit gelieferte Todesfallleistung und
  null Ablaufleistung. Bei ueberlebender, faelliger Police greift die
  PR163-Garantieuntergrenze auf die Ablaufzahlung. Keine Leistung wird
  aus dem Kurvensatz erfunden.
- Die Quellenbasis fuer Periode 1 kommt aus `opening`; danach werden
  Anfangsaktiva und aktive Policen **nur** aus dem geprueften Schluss
  der Vorperiode uebernommen. Neugeschaeft erhaelt erstmals in der
  Folgeperiode Garantie, Anlage auf Anfangsaktiva keinen
  rueckwirkenden Ertrag aus aktueller Praemie oder Kapital.
- Nach jeder Periode wird der gesamte Prefix mit der bestehenden
  PR163-Funktion validiert. Ein spaeter Fehler oder expliziter Abbruch
  liefert atomar keine Zeilen/Quellenwerte. Diese konservative
  Wiederpruefung vermeidet einen neuen Zustandsrechner; ihre
  Laufzeit wird fuer den 100er-Horizont gemessen und budgetiert.

## Abnahme, Herkunft und Risiken

`IMSDATA.C`/`IMS.E` belegen historische Perioden und Verzinsung der
zwei Schadenreserven, aber weder Lebens-Policen noch Sterblichkeit.
PR165 ist ein separater IMS-2.x-Anschluss, keine Gleichheitsbehauptung.
Tests pruefen exakte PR163-Werte im expliziten Spezialfall,
kurvenbasierte Zwei-Perioden-Wirkung, 100-Perioden-Prefix,
Carryover, VU-/Horizont-Mismatch, doppelte Quellen, spaete
Fehler und Abbruch ohne Teilresultat. Vorhandene PR162/163- und
Nichtleben-Tests bleiben gruen.

PR166 verantwortet erst gespeicherte Ergebnisse, Digest, Idempotenz,
API und XLSX; PR167 die gefuehrte Workbench. Rueckkauf, Bonus,
individuelle Ausgabeterm-Ablaufleistung und historische RNG-
Reproduktion bleiben offen.
