# Kontrollierter Vdefmd6-Vertrag fuer 100 Perioden

## Ziel

Der Vertrag `pr81-v1` fuehrt den kontrollierten modernen Zustand aus PR 80
ueber die Schockgrenze bis Periode 100 fort. Die 100 VU14-Zeilen werden im
Speicher erzeugt. Erst danach liest der Bericht `VU14L1.DAT` fuer eine
Abweichungsklassifikation.

## Historischer Ursprung

`Vdefmd6` ruft `Bavauin(50,0,0.8,0.02,1)` auf. `Bavauin` setzt den
Aenderungsschock fuer alle Perioden `j >= 50` und fuer alle Laeufe. Die VU-
und VN-Regeln besitzen bereits getrennte Parameter fuer Normal- und
Schockregime.

Die VN `151-190` sind in der Initialisierung als Praeferenzregel und die VN
`191-200` als Zufall-II-Regel jeweils mit `Ap = 50` definiert. Der
ausfuehrbare Regelcode prueft `gperiod >= Ap * Al[rl]`; deshalb aktiviert der
moderne Vertrag alle 50 VN in Periode 50. Abweichende Angaben im historischen
Bildschirmtext werden nicht stillschweigend harmonisiert.

## Umsetzung

- `build_vdefmd6_shock_vu_snapshot_batch` materialisiert VU-Inputs nur fuer
  Perioden 50-100 und setzt `change_shock = true`;
- `build_vdefmd6_shock_snapshot_batch` materialisiert 200 VN-Regel- und
  Schaden-Snapshots mit Schockparametern;
- `run_vdefmd6_100_periods` aktiviert VN `151-200` in Periode 50 und setzt den
  vorhandenen Zustand mit demselben expliziten RNG fort;
- `vdefmd6_100_period_run_report` vergleicht VU14 erst nach der Erzeugung.

## Kontrollierter Befund

| Kennzahl | Wert |
| --- | ---: |
| VU14-Zeilen | 100 |
| VU-Regelanwendungen | 2.475 |
| VN-Regelanwendungen | 17.400 |
| Schaden-/Settlement-Anwendungen | 17.400 |
| uniforme moderne RNG-Werte | 116.142 |
| normale moderne RNG-Werte | 70.392 |
| gesamte Informationskosten | 161.712 |
| verglichene VU14-Felder | 1.400 |
| treffende VU14-Felder | 488 |
| voll treffende Perioden | 1 |

Der Vergleich trifft `488/1400` Felder. Nur Periode 1 stimmt als ganze Zeile.
Die erste Vollzustandsabweichung bleibt Periode 2, die erste Abweichung der
vier direkten VU14-Regelausgaben Periode 10. Das ist eine Klassifikation und
keine historische Gleichheitsaussage.

## Status und Grenzen

- `shock_boundary_ready = true`;
- `late_policyholder_activation_ready = true`;
- `generation_ready = true` fuer den kontrollierten VU14-Pfad 1-100;
- `production_release_approved = false`;
- keine Legacy-Zeile als Erzeugungsinput;
- keine Datei geschrieben;
- kein Scheduler und keine allgemeine Simulation gestartet;
- keine historische RNG-, Same-Slot- oder Vollgleichheitsbehauptung.

Der historische Versicherungsgrad `BAV.Dg` fuer die informationsbasierten
VN-Regeln wird in diesem Schnitt weiterhin nicht neu abgeleitet. Diese
fachliche Eingangsfrage bleibt offen und wird nicht durch den erfolgreichen
100-Perioden-Lauf verdeckt.

Nach PR 81 bleiben mindestens fuenf geplante Schritte bis PR 86. PR 82
verbreitert als naechstes die VU-Population auf SK1/all und die drei
VU-Klassenaggregate.
