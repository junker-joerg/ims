# PR155: Bewegungsrechnung und einfache Versicherer-Modellbilanz

Dies ist ein **read-only Vertrag** fuer eine spaetere Modellrechnung je
Versicherer, benannter Sparte und Periode. Es gibt noch keine Bilanzwerte,
keine Bilanz-Validierung, keinen Runner, keine Speicherung und keinen
Regulierungsnachweis. Der Vertrag ist unter
`GET /api/accounting/model-balance-contract` als
`ims.insurer-model-balance-contract.v1` abrufbar.

## Herkunft und Grenze

| Ursprung | Python / Modellfeld | Einordnung |
| --- | --- | --- |
| `IMSDATA.C`, `classVU.Sp[1/2].Rs`; `IMS.E`, Zins- und VN-Abrechnung | `Insurer.reserves_current` | Historischer Diagnosewert, **kein** Cash-, Verbindlichkeits- oder Eigenkapitalposten |
| `IMSDATA.C`, `classVU.Sp[1/2].Pr` | `Insurer.premiums_current_sector` | Tarif-/Strategiegroesse, keine vereinnahmte Praemie |
| `IMS.E`, VN-Praemienzahlung | `Policyholder.paid_premium_current` | Kandidat fuer Zahlungseingang, erst nach Zuordnung und Abstimmung verwendbar |
| `IMSDATA.C`, `classVU.Sp[1/2].Sh`; `IMS.E`, Schadenabwicklung | `Insurer.claims_sum_current` | Kandidat fuer bezahlte Schaeden, erst nach Abstimmung verwendbar |
| `IMSDATA.C`, `classVU.Sp[1/2].Wa` | `Insurer.advertising_current_sector` | Strategiegroesse; historisch nicht automatisch von `Rs` abgezogen |

Die historischen Positionen 1/2 sind weiterhin **nicht** als Kfz und
Sach-Haftpflicht identifiziert. Die zwei modernen Namen bezeichnen nur
geplante Modellsparten. Fuer Anfangsbestands-, Aufwands- und Kapitalwerte
fehlt im Altzustand ein belegter Buchungspfad; sie brauchen spaeter
explizite Szenarioeingaben. Der Vertrag bindet keine dieser Quellen.

## Einfaches Rechnungsmodell

Pro `insurer_id`, `sector_id` und `period` sind drei Anfangsbestaende
vorgesehen: Cash, Schadenverbindlichkeit und Eigenkapital. Die periodischen
Fluesse sind Praemie, Zinsertrag, angefallene Schaeden, bezahlte Schaeden,
laufender Aufwand, Kapitalzufuehrung und Kapitalausschuettung. Alle
Betragsfelder nutzen eine Modellwaehrungseinheit; die numerische Darstellung
und Rundung sind vor PR156 festzulegen. Keine implizite Rundung.

```text
Periodenergebnis = Praemie + Zinsertrag - angefallene Schaeden - Aufwand
Cash Schluss = Cash Anfang + Praemie + Zinsertrag + Kapitalzufuehrung
              - bezahlte Schaeden - Aufwand - Kapitalausschuettung
Schadenverbindlichkeit Schluss = Schadenverbindlichkeit Anfang
                                + angefallene Schaeden - bezahlte Schaeden
Eigenkapital Schluss = Eigenkapital Anfang + Periodenergebnis
                       + Kapitalzufuehrung - Kapitalausschuettung
```

Anfang und Schluss muessen jeweils `Cash = Schadenverbindlichkeit +
Eigenkapital` erfuellen. Cash und Schadenverbindlichkeit duerfen nicht
negativ sein; Eigenkapital und Ergebnis koennen negativ sein. Die drei
Schlussbestaende einer Periode werden nur als jeweils passende
Anfangsbestaende der Folgeperiode uebernommen. Kapitalzufuehrungen und
-ausschuettungen werden je Sparte explizit zugeordnet, nicht automatisch
zwischen Sparten verteilt.

Praemien gelten gleichzeitig als verdient und kassiert, Zins als verdient
und kassiert, Aufwand als angefallen und bezahlt. Das sind bewusste
Vereinfachungen, keine Aussagen ueber historische Buchfuehrung. Nur Cash
als Aktivum und nur Schadenverbindlichkeit als Schuld sind abgebildet.
Forderungen, Beitragsabgrenzung, Kapitalanlagen, Rueckversicherung,
Steuern, Leben, Kranken und Solvency-II-Kapital fehlen. Das ist eine
**Modellbilanz**, keine gesetzliche Bilanz oder Solvenzmeldung.

## Weiterarbeit

PR156 entscheidet Betragsdarstellung, Eingabeformat und Quellabstimmung,
rechnet die Nichtleben-Modellbilanz deterministisch und testet beide
Bilanzidentitaeten sowie Perioden-Carryover. Bis dahin beeinflusst dieser
Vertrag weder Strategien noch Simulationsergebnisse.
