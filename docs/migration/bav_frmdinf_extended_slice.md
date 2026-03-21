# BAV-Frmdinf-Slice: erweiterter Kern mit Vorperioden-Aktivität

Dieser PR erweitert den bisherigen kleinen BAV-Service-Slice substanziell,
bleibt aber weiterhin ein kontrollierter, quellenkritischer Portierschritt ohne
Behauptung historischer Vollgleichheit.

## Gegenüber PR 22 substanziell erweitert

- expliziter Aktivitätszustand für Vorperiode und aktuelle Periode
- explizite Berechnungsmetadaten zur Verfügbarkeit von Fremdinformation
- erweiterter `Frmdinf`-Kern mit Persistenz des Marktführers und klarer Vorperiodenbasis
- getrennte Ausweisung von Vorperiodenaktivität und aktueller Aktivität im BAV-Servicezustand

## Historische Aspekte jetzt besser abgebildet

- Fremdinformation wird nicht nur allgemein aus vorhandenen Werten gebildet,
  sondern explizit aus Vorperiodenwerten und Vorperiodenaktivität
- Marktführerlogik wird über Vorperiodenreserven im Servicezustand festgehalten
- der BAV-Servicezustand weist fachlich relevanter aus, welche Mengen für die
  Fremdinformationsbildung verwendet wurden und welche nur aktuell aktiv sind

## Bewusst noch nicht portiert

- keine vollständige Aktivierungsschock-Semantik
- keine vollständigen Aggregatvektoren `Vuag1/2/3` und `Vnag1/2/3`
- keine Portierung von `Agrsich`
- keine vollständige VU-/VN-Regelportierung
- keine historische Vollsimulation und keine Behauptung historischer Vollgleichheit

## Nächster sinnvoller BAV-Schritt

Der nächste BAV-PR sollte den erweiterten Frmdinf-Kern an weitere direkt belegbare
Altfelder anbinden, die Beziehung zu historischen Aggregatstrukturen präzisieren und
erst danach einen weiteren klar abgegrenzten, quellenbasierten Service-Slice ergänzen.
