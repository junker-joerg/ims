# Ergebnisse und historische Validierung verstehen

Stand: 2026-09-01
Kernvalidierungsstand: PR101

## Zwei verschiedene Fragen

Die Workbench beantwortet zwei voneinander getrennte Fragen:

1. **Laeuft die moderne Anwendung technisch kontrolliert?**
   Dazu gehoeren Backend, Frontend, Metadaten, Preflight, Freigabe, Adapter und
   Ergebnisablage.
2. **Wie verhalten sich moderne Berechnungen zu den historischen Dateien?**
   Dazu gehoeren Tabellen-, Zeilen- und Feldvergleiche sowie offene
   Herkunfts-, Parameter- und RNG-Fragen.

Ein gruener technischer Check beantwortet die zweite Frage nicht automatisch.
Ein blockierter historischer Vergleich bedeutet umgekehrt nicht automatisch,
dass die Browseranwendung technisch defekt ist.

## Stand nach PR101

Der kontrollierte historische Kernkorpus umfasst insgesamt 15 berechnete
Tabellen und 6.300 eingetragene Ergebniszeilen. Davon sind derzeit:

| Stand | Tabellen | Ergebniszeilen |
| --- | ---: | ---: |
| angeschlossen | 15/15 | 6.300/6.300 |
| noch offen | 0/15 | 0/6.300 |

Die drei in PR101 angeschlossenen VU-Klassenaggregate umfassen 1.500 Zeilen
und 21.000 verglichene Felder. Davon sind 3.330 exakt, 41 innerhalb der
bestehenden Toleranz und 17.629 blockierend abweichend. Fuenf der 1.500 Zeilen
stimmen in allen Feldern ueberein.

Damit sind alle vorgesehenen Tabellen und Ergebniszeilen technisch an den
kontrollierten Vergleich angeschlossen. Dieser Stand lautet trotzdem weiterhin
`blocked_calculated_core_validation`: PR102 bewertet den gemeinsamen
Vollkorpus und seine Abweichungsgruppen. Vollstaendige Anschlussabdeckung ist
weder historische Vollgleichheit noch automatisch eine Produktionsfreigabe.

## Was die Vergleichsbegriffe bedeuten

| Anzeige | Bedeutung |
| --- | --- |
| exakt | moderner und historischer Feldwert sind nach dem Vergleichsvertrag gleich |
| toleriert | Zahlenwert weicht nur innerhalb der bereits festgelegten numerischen Toleranz ab |
| blockierend | Abweichung liegt ausserhalb der Toleranz und verhindert eine automatische Freigabe |
| offen | Feldsemantik oder historische Vergleichbarkeit ist noch nicht ausreichend geklaert |
| vollstaendig passende Zeile | alle verglichenen Felder dieser Ergebniszeile bestehen gemeinsam |

Wichtig: Viele abweichende Felder koennen aus unterschiedlichen historischen
Parametern, Zinssaetzen, Compilerumgebungen, Aggregatakkumulatoren oder
Zufallsfolgen entstehen. Ohne belegte Laufmetadaten darf aus der Abweichung
nicht direkt geschlossen werden, dass die moderne Fachlogik falsch ist.

## Warum 500 Zeilen nicht 500 Perioden bedeuten

Das historische Modell lief nach dem belegten Quellstand hoechstens 100
Perioden je Lauf. Die 300- und 500-Zeilen-Dateien zaehlen mehrere Laeufe
fortlaufend:

- 300 Ergebniszeilen entsprechen drei getrennten 100-Perioden-Laeufen;
- 500 Ergebniszeilen entsprechen fuenf getrennten 100-Perioden-Laeufen.

Der moderne Diagnosekorpus verwendet daher fuer eine 500-Zeilen-Referenz
fuenf getrennte 100-Perioden-Laeufe. Das ist kein historischer
500-Perioden-Lauf und keine Rekonstruktion seiner damaligen Zufallsfolge.

## Was historische Referenzen leisten

Historische Referenzdateien sind Vergleichsdaten. Sie koennen belegen:

- welchen Header und welche Feldfolge eine Datei hat;
- welche Ergebniszeilen vorhanden sind;
- aus welcher bekannten Archivschicht eine versionierte Referenz stammt;
- wie der heutige deterministische Diagnosepfad gegen diese Datei abschneidet.

Sie belegen ohne Laufbericht nicht automatisch:

- identische Eingabeparameter oder Zinssaetze;
- denselben Seed oder dieselbe RNG-Ziehfolge;
- identische Scheduler- und Akkumulatorreihenfolge;
- einen gemeinsamen historischen Lauf fuer alle Dateien;
- historische Vollgleichheit oder Produktionsreife.

Die Referenzzeilen werden nicht als Eingabe in die moderne Berechnung
zurueckgespielt. Dadurch bleibt der Vergleich diagnostisch und kann sich nicht
selbst bestaetigen.

## Entscheidung fuer Anwender

Fuer eine fachliche Freigabe werden mindestens drei Dinge getrennt betrachtet:

1. Der technische Release-Pfad ist gruen.
2. Alle vorgesehenen Tabellen und Ergebniszeilen sind angeschlossen.
3. Die verbleibenden Abweichungen sind fachlich bewertet und von einer Person
   freigegeben oder als begruendete historische Varianz dokumentiert.

Bis diese Bewertung erfolgt ist, darf das System fuer kontrollierte Tests und
Demonstrationen verwendet werden, aber der historische Vergleich darf nicht
als Vollgleichheitsnachweis bezeichnet werden.
