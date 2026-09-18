# PR187a-f: Kettenaufbau und additive Vier-Sparten-Rechnung

Stand: 2026-09-18
Status: geplant nach PR187, vor PR187g-k und PR188, zwingend vor PR190

## Befund und Grenze

PR151 startet und zeigt eine **vorbereitete** 100-Perioden-Kette; es
erzeugt die hundert Einzelkandidaten nicht gefuehrt. PR170/170a
konsolidiert vier Sparten, doch der im Browser belegte gemeinsame
Bedienweg endet nach zwei Perioden. PR165 und PR169b liefern zwar
eigene 100er-Ketten fuer Leben und Kranken, beweisen aber noch keine
gemeinsame VU-/VN-/Vier-Sparten-Wirkung ueber 100 Perioden. Die
Nichtleben-Quelle besitzt heute noch keine gleichartige Szenario-ID;
eine blosse ID-Gleichheit kann die fachliche Zusammengehoerigkeit
deshalb nicht belegen.

Das sind zwei Produktluecken und kein Restpunkt von PR190. Die
historischen `IMSDATA.C`-Sektoren 1/2 bleiben neutral; Kfz und
Sach-Haftpflicht werden nicht aus ihnen geraten. Jeder Schritt nutzt
explizite Quellen, erhaelt Seeds/Perioden und behauptet keine
historische Vollgleichheit.

## PR-Schnitte und Abnahme

| PR | Liefergegenstand | Beleg vor dem naechsten Schnitt |
| --- | --- | --- |
| PR187a | Versionierter Vertrag fuer 100 Einzelkandidaten: Startzustand, VU-/VN-Strategiezeitfenster, Ziehungen/Seeds, Schockperiode, Marktkontext und Carryover | Perioden 1-100 lueckenlos; unbekannte oder widerspruechliche Werte atomar gesperrt; keine automatisch geratenen Defaults |
| PR187b | Serverseitiger, kontrollierter Bau der 100 Kandidaten und ihrer Kette aus PR187a | jeder Kandidat neu geprueft, Gesamtdigest, stabiler Prefix 1-5, ausdrueckliche unveraenderliche und idempotente Speicherung; noch kein Lauf |
| PR187c | Gefuehrte Workbench-Eingabe, Vorschau und PR151-Start aus der selbst gebauten Kette | Baseline/Variante und 100er-Download, Fehlerpfade, Zeitbudget, breiter/schmaler Browser und Tastatur; kein neuer Simulationskern |
| PR187d | Quellen- und Periodenvertrag fuer Kfz, Sach-Haftpflicht, Leben und Kranken | dieselbe VU, Perioden 1-100 und explizit erklaerte gemeinsame Szenario-Variante; Nonlife-/VU-VN-Marktbezug und fehlende technische Szenario-IDs werden nicht still gleichgesetzt; noch keine gemeinsame Rechnung |
| PR187e | Kontrollierte gemeinsame 100-Perioden-Vier-Sparten-Rechnung | bestehende Teilmodelle neu berechnet; jeder Periodenabschluss bilanziell abgestimmt, Prefix 1-2 stabil, deterministisch, begrenzt und atomar; keine neue spartenuebergreifende Verhaltensregel |
| PR187f | Gefuehrte 100er-Mehrspartenansicht mit Ergebnisabgabe | vier Sparten und Gesamtbilanz fuer Baseline/Variante, Periodenfilter, CSV/JSON/XLSX aus demselben Digest, Browserabnahme auf beiden Breiten und Handbuchbilder |

PR187a-c schliessen den gefuehrten **Kettenaufbau**. PR187d-f
schliessen die **additive Mehrspartenrechnung und -ansicht**. Sie
setzen die in PR154 validierten sektorbezogenen Strategieplaene noch
nicht in Entscheidungen um und belegen keine endogen gekoppelte
All-Sparten-Marktreaktion. Vor PR187e wird geprueft, ob die
vorhandenen Quellen ueberhaupt einen wirtschaftlich konsistenten
gemeinsamen 100er-Fall tragen. Wenn nicht, wird die Luecke offen
ausgewiesen und in weitere kleine PRs aufgeteilt; ein kuenstlich
gleichgemachter Stand ist kein Erfolg.

## Anschluss PR187g-k

Der [Restplan](ims_2x_restplan_ab_pr179.md) setzt vor PR188 fuenf
weitere kleine Schnitte: eindeutige Strategiequellen und Zeitfenster,
begrenzte Nichtleben- und Leben/Kranken-Anschluesse, gefuehrte
Workbench-Eingabe und eine belegte 100er-Reaktionskette bis zur Bilanz.
PR187g ist ein Entscheidungstor: Ohne fachlich gedecktes
Sektormapping wird keine historische Zuordnung erfunden. Der Umfang
einer Kopplung wird nach den Quellenbefunden gegebenenfalls weiter
aufgeteilt.

PR188 darf kuratierte 100er-Vier-Sparten-Seminarfaelle erst auf
PR187f und PR187k aufbauen. PR190 prueft Installation, Beispiel,
Lauf, Bilanz, Modellkapital, DORA-Wirkung und Export **gemeinsam**,
statt fehlende Vorarbeiten in der Abnahme zu verstecken. PR187a-k
sind in der Meilensteinzahl der aktiven Roadmap enthalten.
