# Vdefmd6-VN-Eingabe- und Draw-Plan

## Ziel

PR 77 kartiert fuer die Vorschockperioden 1-49 die Eingaben der sechs
`Vdefmd6`-VN-Regeln, ihre Schaden- und Settlement-Anschluesse sowie die aus dem
Altcode belegbare Reihenfolge. Der Schritt ist read-only: Er erzeugt keine
Snapshots, zieht keine Zufallszahlen und startet weder Runner noch Simulation.

## Umfang

- 150 ab Periode 1 aktive VN;
- 50 erst ab Periode 50 aktive VN als abgegrenzter Nachschockbestand;
- sechs Regelarten `Vrvn01` bis `Vrvn06`;
- gemeinsamer Schadenpfad mit zwei Sparten;
- gemeinsame VN-/VU-Settlement-Schreibflaechen;
- Abgleich mit den vorhandenen expliziten Python-Snapshottypen.

## Reihenfolge und Grenze

Der C-Quelltext berechnet zuerst Schaden 1 und Schaden 2, danach die
regelabhaengige Versicherungsentscheidung, danach Settlement fuer Sparte 1 und
2 und zuletzt das VN-Vermoegen. Jede Schadenformel enthaelt zwei `normal()`-
Aufrufe als Operanden einer Multiplikation. Deren Reihenfolge ist in C nicht
festgelegt. Auch die historische Reihenfolge der VN im gemeinsamen
Aktionsslot ist nicht belegt.

Der aktuelle Python-Runner wendet dagegen zuerst explizite
Versicherungsregel-Snapshots und danach Schaden-/Settlement-Snapshots an. PR 78
muss deshalb alle benoetigten Draws in einer eigenen, dokumentierten modernen
Reihenfolge materialisieren, bevor der bestehende Runner sie verarbeitet. Das
ist eine reproduzierbare Portierungsentscheidung und keine Behauptung
historischer RNG-Gleichheit.

## Restplanung

PR 78 hat die VN-Snapshots und moderne Drawfolge fuer eine einzelne Periode
materialisiert. Die dabei belegte Abhaengigkeit von allen 25 VU-Regeln und der
offenen Informationskostenanwendung trennt den Mehrperiodenschritt. Nach PR 78
bleiben deshalb mindestens acht reviewbare PRs bis PR 86; die aktuelle Folge
steht in `vdefmd6_pre_shock_snapshot_plan.md` und
`production_readiness_pr_plan.md`.

Konkrete Funde koennen weitere kleine Slices erfordern. Es gilt weiterhin:
keine Simulation in diesem Schritt, keine neue Fachlogik und keine historische
Vollgleichheitsbehauptung.
