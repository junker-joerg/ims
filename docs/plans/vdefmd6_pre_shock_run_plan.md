# Plan: kontrollierter Vdefmd6-Vorschockpfad fuer PR 80

## Ziel

PR 80 bindet die in `Vrvn05` und `Vrvn06` berechneten Informationskosten an
den bestehenden VN-Settlement-Kern und fuehrt danach den modernen
`Vdefmd6`-Zustandspfad fuer Perioden 2-49 kontrolliert aus. Der VU14-Export
entsteht vollstaendig im Speicher, bevor die historische Reihe gelesen wird.

## Quellen und Mapping

- `IMS.E:3229-3514`, `Vrvn05`: Stichprobenkosten und Abzug von `Vm`;
- `IMS.E:3521-3786`, `Vrvn06`: Vollinformationskosten und Abzug von `Vm`;
- `IMS.E`, `Frmdinf`: Vorperiodeninformationen vor den VU-Regeln;
- vorhandene VU-/VN-Snapshotbuilder aus PR 78 und PR 79;
- vorhandene VU-, VN-, Schaden-, Settlement- und Agrsich-Kerne.

Mangels historischer Aufteilungsregel werden Informationskosten genau einmal
vom kumulierten VN-Vermoegen abgezogen. Die sektoralen Hilfswerte werden nicht
veraendert.

## Kontrollierte Reihenfolge

Der Vertrag `vdefmd6-modern-pre-shock-state-v1` verwendet reproduzierbar:

1. BAV-Fremdinformation aus `t-1`;
2. VU-Regeln nach aufsteigender VU-ID;
3. VN-Regeln, Schaden und Settlement nach aufsteigender VN-ID;
4. Agrsich-Export im Speicher.

Vor jeder Periode werden `t-1` und `t-2` explizit getrennt. VU-Aggregatfelder
fuer Versicherte und Schaeden werden erst nach den VU-Regeln fuer die neue
VN-Abrechnung geleert. Die Vrvn04-Suchhistorie wird periodisch fortgeschrieben.

Diese moderne Reihenfolge ist ein stabiler Ausfuehrungsvertrag, aber kein
Nachweis der historischen Same-Slot-Reihenfolge.

## Vertragsbefund

Mit Basis-Seed `20260001` entstehen fuer Perioden 2-49:

- 1.200 VU-Regelanwendungen;
- 7.200 VN-Regelanwendungen und 7.200 Schaden-/Settlement-Anwendungen;
- 47.904 uniforme und 29.184 normale moderne RNG-Werte;
- 1.584 Informationskosten je Periode, 76.032 insgesamt;
- 49 VU14-Zeilen einschliesslich der unabhaengigen Startperiode 1.

Der Vergleich ergibt 236/686 treffende Felder. Nur Periode 1 trifft als ganze
Zeile. Die erste Vollzustandsabweichung liegt in Periode 2, die erste
Abweichung der vier direkten VU14-Regelausgaben in Periode 10.

## Grenzen und Restplanung

- keine Legacy-Zeile als Erzeugungsinput;
- keine Datei wird geschrieben;
- kein historischer Scheduler und keine allgemeine Simulation;
- keine historische RNG-, Same-Slot- oder Vollgleichheitsbehauptung.

Nach PR 80 bleiben mindestens sechs reviewbare PRs bis PR 86:

1. PR 81: Schockgrenze und VU14-Perioden 50-100 schliessen;
2. PR 82: VU-Population auf SK1/all und VU-Klassen verbreitern;
3. PR 83 und PR 84: VN-Regelzustand in zwei kleinen Gruppen schliessen;
4. PR 85: VN-Klassen- und SK1/all-Exporte vergleichen;
5. PR 86: alle 15 Kernexporte gemeinsam vergleichen und die fachliche
   Freigabe menschlich neu bewerten.
