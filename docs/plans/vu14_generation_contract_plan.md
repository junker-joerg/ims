# Plan: VU14-Erzeugungsvertrag fuer PR 72

## Ziel

PR 72 bereitet den vollstaendigen Abnahmevertrag fuer eine spaetere,
unabhaengige Erzeugung von `imsvu014.dat` in den Perioden `1-100` vor. Der
Schritt erzeugt noch keine Periodenzustaende, startet keinen Runner und fuegt
keine Fachlogik hinzu.

## Historischer Ursprung

- `IMSDATA.C:94-103` ordnet Versicherer 14 der Stufe-I-Datei
  `imsvu014.dat` zu.
- `IMS.E:1045-1063`, `act PlanVU`, dispatcht die dem Versicherer und
  logischen Zeitpunkt zugeordneten VU-Aktionen.
- `IMS.E:402-446`, `act Agrsich`, schreibt danach je Periode die aktuellen
  Praemien-, Werbe-, Reserven-, VN-, Schadenanzahl- und Schadensummenwerte
  beider Sparten.

Der historische Code belegt damit Ausgabeform und Dispatchgrenze. Er belegt
nicht die konkrete Population, Parameterbelegung, Aktionsfolge oder den
Zufallsstrom des versionierten `VU14L1.DAT`-Laufs.

## Konservative Annahme

Der vorhandene Vier-Perioden-Plan `replay_vu14_period_plan.json` bleibt nur
ein Aggregat-, Writer- und Vergleichsnachweis. Er setzt die spaeter
exportierten Zustandsfelder periodengenau direkt und darf deshalb nicht als
unabhaengige Erzeugungsquelle fuer `1-100` hochskaliert werden.

## Vertragsumfang

Ein read-only Bericht soll pruefbar festlegen:

1. genau `insurer / I / entity = 14 / imsvu014.dat`;
2. genau die lueckenlosen globalen Perioden `1-100`;
3. belegte Startpopulation fuer VU, VN und BAV;
4. belegte VU14-Regelzuordnung, Regelparameter und Aktionszeitpunkte;
5. explizite RNG-Quelle, Seed- und Ziehungsreihenfolge fuer stochastische
   Pfade;
6. durchgaengige Zustandsfortschreibung statt periodengenauem Output-Echo;
7. Herkunft der beiden Spartenwerte fuer Praemie, Werbung, Reserven,
   Versicherte, Schadenanzahl und Schadensumme;
8. strikte Trennung zwischen berechnetem Output und erst danach gelesener
   Legacy-Referenz.

## Negativgrenzen

Der Vertrag verwirft insbesondere:

- fehlende, doppelte, unsortierte oder nicht bei `1` beginnende Perioden;
- eine andere Exportidentitaet oder Aggregatstufe;
- Legacy-Zeilen als Zustands- oder Regelinput;
- direkte periodische Vorgabe aller spaeter exportierten VU14-Felder;
- unbelegte Population, Regelparameter, Aktionsfolge oder RNG-Herkunft;
- eine Freigabe- oder Vollgleichheitsbehauptung allein aus dem Vertrag.

## Validierung

- stabiler Berichtsvertrag `pr72-v1`;
- Zielidentitaet und 100 Perioden aus dem Kernbundle abgeleitet;
- vorhandener Vier-Perioden-Slice als nicht unabhaengig klassifiziert;
- Quellanker und erforderliche Eingangsgruppen vollstaendig vorhanden;
- Negativtests fuer Periodendrift und fehlende Herkunft;
- alle Ausfuehrungs-, Schreib-, Simulations- und Gleichheitsflags bleiben
  `false`.

## Danach

PR 73 darf auf diesem Vertrag einen unabhaengigen VU14-Zustandsweg fuer
`1-100` umsetzen. Erst dessen berechneter Export darf gegen `VU14L1.DAT`
verglichen werden. Population, Scheduler, RNG oder Fachlogik werden dabei nur
in getrennten, belegten Slices ergaenzt.

