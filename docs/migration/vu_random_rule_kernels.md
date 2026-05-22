# VU-Regeln Vrvu01 und Vrvu02: Zufall I/II

## Ziel

Dieser Schritt portiert die deterministischen Formelkerne der historischen
VU-Regeln `Vrvu01` und `Vrvu02` in die Python-Domaenenlogik.

## Ursprung im Altcode

- `IMS.E`
- `act Vrvu01`
- `act Vrvu02`

`Vrvu01` berechnet Praemien und Werbung aus vier `myrndf()`-Ziehungen.
`Vrvu02` berechnet dieselben Zielgroessen aus vier `normal()`-Ziehungen.
Beide Regeln verzinsen die Reserven je Sparte um den aktuellen Zinssatz und
verwenden in Periode 1 die vorgegebenen Startwerte.

## Umsetzung in Python

Der Python-Port fuehrt explizite Snapshot-Typen ein:

- `VURandomUniformRuleParameters`
- `VURandomUniformRuleSnapshot`
- `VURandomUniformRuleResult`
- `VURandomUniformRuleApplication`
- `VURandomNormalRuleParameters`
- `VURandomNormalRuleSnapshot`
- `VURandomNormalRuleResult`
- `VURandomNormalRuleApplication`

Die Zufallswerte koennen als explizite Draw-Vektoren im Szenario uebergeben
werden. Fehlen sie, kann der VU-Periodenrunner reproduzierbare Python-Draws
aus dem `SimulationContext` erzeugen. Der Regelkern selbst bleibt
deterministisch und erhaelt weiterhin konkrete Draw-Vektoren.

## Grenzen

- keine Portierung des historischen `myrndf()`-Generators
- keine Portierung des historischen `normal()`-Generators
- keine automatische Regelwahl durch den Scheduler
- keine historische Herleitung der Draws aus Seeds
- keine vollstaendige historische Simulation
- keine Behauptung historischer Vollgleichheit

## Naechster sinnvoller Schritt

Ein anschliessender PR kann die Regelwahl und Aktivierungsbedingungen
schrittweise naeher an den historischen VU-Scheduler fuehren oder die
Zufallsziehung in einen separaten, reproduzierbaren RNG-Port auslagern.
