# Kontrollierter Vdefmd6-Vorschockvertrag

## Ziel

Der Vertrag `pr80-v1` schliesst den intern erzeugten VU14-Vollzustand fuer
Perioden 1-49. `run_vdefmd6_pre_shock_periods` nutzt die typisierte Population,
die Snapshotbuilder aus PR 78/79 und die bereits portierten Regelkerne. Der
Pfad ist eine kontrollierte moderne Ausfuehrung und keine Vollsimulation.

## Informationskosten

`VNSettlementSnapshot` und `VNDamageSettlementSnapshot` tragen nun ein
nichtnegatives `information_cost`-Feld. Der VN-Runner uebernimmt den Wert aus
dem Ergebnis von `sample_search` oder `best_info`. Das Settlement berechnet:

`end_wealth = previous_wealth - damages - premiums - information_cost`.

Der Kostenwert wird im Resultat diagnostisch ausgewiesen. Die sektoralen
Vermoegenswerte enthalten weiterhin nur sektoralen Schaden und Praemie, weil
`IMS.E` keine sektorale Verteilung der gemeinsamen Suchkosten belegt.

## Zustandsfortschreibung

Fuer jede Periode 2-49 gilt:

1. VU-Snapshots erfassen den noch getrennten `t-1`-/`t-2`-Zustand;
2. aktuelle Werte werden als `t-1` fuer `Frmdinf` markiert;
3. BAV und alle 25 VU-Regeln werden angewendet;
4. 150 VN-Snapshots lesen die aktuellen VU-Praemien und Werbung;
5. VN-Regel, Schaden und Settlement schreiben Versicherte, Schaeden,
   Reserven und Vermoegen;
6. VU14 wird in-memory aggregiert und exportiert.

Die Vrvn04-Historie wird aus den vorangegangenen Entscheidungen aufgebaut.
Alle RNG-Werte stammen aus einem expliziten `random.Random(20260001)`.

## Vergleichsbefund

| Kennzahl | Wert |
| --- | ---: |
| VU14-Zeilen | 49 |
| verglichene Felder | 686 |
| treffende Felder | 236 |
| voll treffende Perioden | 1 |
| erste Vollzustandsabweichung | 2 |
| erste direkte Regelausgabenabweichung | 10 |
| gesamte Informationskosten | 76.032 |

Der Befund ist eine Abweichungsklassifikation. Insbesondere die offene
historische Same-Slot-Reihenfolge und der unbekannte Referenzseed verhindern
eine historische Gleichheitsaussage.

Aus diesem Vergleich folgt keine historische Gleichheitsaussage und keine
fachliche Freigabe.

## Status

- `information_cost_application_ready = true`;
- `independent_periods_2_49_ready = true`;
- `full_state_projection_ready = true` fuer den Vorschockbereich;
- `generation_ready = false` fuer das geforderte 100-Perioden-Fenster.

PR 81 muss als naechstes die Aktivierung von 50 weiteren VN, die
Aenderungsschockparameter und Perioden 50-100 getrennt schliessen.
