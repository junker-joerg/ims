# VU14-Vorschockprojektion

## Ziel und Ergebnis

PR 76 erzeugt VU14 fuer Perioden 1-49 aus der typisierten
`Vdefmd6`-Initialisierung und dem portierten `Vrvu06`-Kern. Die 49 Zeilen
entstehen vollstaendig im Speicher, bevor `VU14L1.DAT` fuer die Diagnose
gelesen wird.

Der direkte VU-Regelpfad ist damit fuer alle 48 Folgeperioden ausfuehrbar und
klassifiziert. Er ist noch kein vollstaendiger VU14-Zustandsweg:

- Header und Periodenidentitaet: 49/49 Treffer;
- direkte Regelfelder `Pr1`, `Wa1`, `Pr2`, `Wa2`: Perioden 1-16 treffen;
- erste Regelausgabenabweichung: Periode 17;
- vollstaendig treffende Zeilen: nur Periode 1;
- insgesamt 188/686 Feldtreffer.

## Ursache der Grenze

`Vrvu06` liest fuer Periode `p` die Schadenanzahl `Sa` und Schadensumme `Sh`
aus Periode `p-1` und verwendet `Sh / Sa` als Verzweigungswert fuer Praemie
und Werbung. Die VN-Regeln erzeugen dieselben Schadenfelder und schreiben
ausserdem Versicherte und Reserven des Versicherers fort.

Die Projektion erfindet diesen offenen VN-/Schaden-/Settlement-Pfad nicht. Der
initiale Nullzustand bleibt deshalb unveraendert. Bis Periode 16 liegt der
historische erwartete Schaden unter der jeweiligen VU14-Praemie, sodass der
Nullpfad zufaellig denselben Vrvu06-Zweig waehlt. In Periode 17 wird der
fehlende Vorperiodenschaden erstmals entscheidungsrelevant. Diese
Prefix-Uebereinstimmung ist ein enger Regelbefund und keine historische
Vollgleichheit.

Einzelne weitere Nulltreffer in `Vn1`, `Sa1` oder `Sh1` sind lediglich
inzidentelle Ergebnisgleichheit. Der Vertrag setzt deshalb
`downstream_incidental_matches_are_evidence = false`.

## Mapping

| Historischer Ursprung | Python-Ziel | Grenze |
| --- | --- | --- |
| `IMS.E:1578-1688`, `Vrvu06` | `build_vu14_pre_shock_projection` | vorhandener deterministischer VU-Regelkern |
| `IMS.E:4602-4605`, VU14-Definition | `build_vdefmd6_population` | Startzustand, Regel 6 und Parameter |
| `IMS.E`, `Bavauin(50,...,0.02,...)` | Projektion 1-49 | Zinssatz 0,02; kein Schock vor 50 |
| VN-Regelbloecke ab `IMS.E:2186` | offene Blocker | Schaden, Versicherte und Settlement nicht automatisch gebunden |

## Read-only Bericht

`python -m ims.api.vu14_pre_shock_projection_report --repo-root .` prueft den
Vertrag `pr76-v1`, zehn historische Quellanker, die 49 erzeugten Zeilen und
die Abweichungsklassifikation. Der VU14-100-Perioden-Vertrag nimmt den Bericht
auf, markiert dadurch aber keine zusaetzliche Herkunftsgruppe als belegt.

Offen bleiben:

1. `policyholder_claim_origin_missing`;
2. `settlement_state_origin_missing`;
3. `historical_rng_draw_order_missing`.

## Grenzen

- Legacy-Zeilen werden nicht als Erzeugungsinput verwendet;
- keine neue Fachlogik;
- keine RNG-Ziehung;
- kein Scheduler- oder Simulationsstart;
- PR 80 setzt fuer den kontrollierten modernen Vollzustand
  `independent_periods_2_49_ready = true`;
- keine historische Vollgleichheits- oder Produktionsfreigabe.

## Restplanung

Der Quellenbefund hat die bisherige Planung weiter geteilt. PR 77 bis PR 80
sind erledigt; ab PR 81 bleiben mindestens sechs Schritte bis PR 86:

1. PR 81: Schockgrenze und VU14-Perioden 50-100 schliessen;
2. PR 82: dieselbe VU-Population auf SK1/all und VU-Klassen verbreitern;
3. PR 83 und PR 84: VN-Regelzustand in zwei kleinen Gruppen schliessen;
4. PR 85: VN-Klassen und SK1/all aus demselben Zustand vergleichen;
5. PR 86: alle 15 Exporte gemeinsam vergleichen und die Freigabe menschlich
   neu bewerten.

Weitere Quellenfunde duerfen diese Mindestplanung erneut teilen.
