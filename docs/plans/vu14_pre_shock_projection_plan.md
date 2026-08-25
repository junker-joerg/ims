# Plan: VU14-Vorschockprojektion fuer PR 76

## Ziel

PR 76 erzeugt fuer VU14 die Perioden 1-49 unabhaengig aus der
`Vdefmd6`-Initialisierung und dem bereits portierten `Vrvu06`-Regelkern. Die
Perioden 2-49 bilden den geplanten Folgezustands-Slice. Erst nach vollstaendiger
Erzeugung wird die historische VU14-Reihe gelesen und die Abweichung nach
Feldgruppen und Periodengrenzen klassifiziert.

## Historische Belege

- `IMS.E:1578-1688`: `Vrvu06` liest Praemie, Werbung, Reserven,
  Schadenanzahl und Schadensumme aus der Vorperiode;
- `IMS.E:1625-1632`: erwarteter Schaden ist `Sh / Sa` mit Nullschutz;
- `IMS.E:1633-1640`: Praemie und Werbung waehlen ihre Multiplikatoren anhand
  dieses Vorperiodenwerts;
- `IMS.E:2269-2276` und die entsprechenden VN-Regelbloecke: VN-Aktionen
  schreiben Reserven, Schadensumme und Schadenanzahl des Versicherers;
- `IMS.E:4602-4605`: VU14 verwendet Regel 6 und die in `Vdefmd6` belegten
  16 Parameter;
- `IMS.E:4669`: der Aenderungsschock beginnt erst ab Periode 50.

## Konservative Umsetzung

1. Die Projektion beginnt bei der typisierten `Vdefmd6`-Population.
2. Fuer Perioden 1-49 wird nur `Vrvu06` mit dem belegten Zinssatz und ohne
   Aenderungsschock angewendet.
3. Nicht gebundene VN-/Schaden-/Settlement-Werte werden nicht erfunden und
   nicht aus der historischen Ausgabedatei uebernommen. Ihr initialer
   Nullzustand bleibt deshalb unveraendert.
4. Alle 49 Exportzeilen werden im Speicher erzeugt, bevor die Legacy-Referenz
   fuer die Diagnose gelesen wird.
5. Treffer in nicht gebundenen Downstream-Feldern gelten ausdruecklich nicht
   als Herkunftsnachweis.

## Erwartete Klassifikation

- Header und Periodenidentitaet stimmen fuer 49/49 Zeilen.
- Die vier direkten VU-Regelausgaben `Pr1`, `Wa1`, `Pr2`, `Wa2` stimmen fuer
  Perioden 1-16; die erste entscheidungsrelevante Luecke wird in Periode 17
  sichtbar.
- Nur Periode 1 ist als ganze Zeile identisch.
- Reserven, Versicherte und Schadenfelder bleiben ab Periode 2 durch den
  fehlenden VN-/Schaden-/Settlement-Pfad blockiert.

## Grenzen

- keine Legacy-Zeile als Erzeugungsinput;
- keine neue Fachlogik;
- keine RNG-Ziehung;
- kein Scheduler- oder Simulationsstart;
- keine historische Vollgleichheitsbehauptung;
- keine Freigabe der Perioden 2-49 als vollstaendiger Modellzustand.

## Folgeplanung

Der Befund teilt den bisherigen Folgeschritt konservativ. PR 77 kartiert die
VN-/Schaden-/Settlement-Eingaben und ihre Draw-Reihenfolge fuer die
Vorschockperiode. PR 78 hat daraus die VN-Snapshots einer einzelnen Periode
materialisiert. PR 79 hat alle VU- und BAV-Eingaben vorbereitet; PR 80 bindet
die Informationskosten an und schliesst danach VU14/2-49. Der Schock- und
Nachschockpfad folgt erst danach.
