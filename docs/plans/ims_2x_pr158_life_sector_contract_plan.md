# PR158: Zustands-, Fluss- und Strategievertrag fuer Leben

Stand: 2026-09-16

## Ziel und Schnitt

Ein versionierter, read-only Vertrag beschreibt das erste eigenstaendige
IMS-2.x-Lebenssegment. PR158 berechnet keine Lebenswerte. PR159 darf auf
dieser Grundlage einen kleinen deterministischen Fall implementieren,
muss offene Bewertungs- und Timingfragen dann ausdruecklich entscheiden.

1. Ein `life`-Segment je Versicherer und anfangs ein geschlossener,
   homogener Vertragsbestand. Laufzeiten sind Modellperioden, keine Jahre.
   Kein Neugeschaeft, keine mehreren Kohorten, keine Produktvarianten.
2. Zustaende: aktive Vertraege, Restlaufzeit, deckende Vermoegenswerte,
   Garantieverpflichtung und Eigenkapital. Garantievertragssatz ist bei
   Ausgabe fest und kein nachtraeglicher Strategiehebel.
3. Fluesse: Praemien, Anlageergebnis, Todesfall-/Ablauf-/Rueckkaufsleistungen,
   Aufwand, Kapitalbewegungen und getrennte Verpflichtungszugaenge und
   -freisetzungen. Zaehler fuer disjunkte Vertragsabgaenge.
4. Gleichungen und Carryover beschreiben Abstimmung von Vermoegen,
   Verpflichtung, Eigenkapital und Bestand. Keine regulatorische Bewertung.
5. Neue Strategie-Anschlussstellen fuer VU-Bonusgutschrift und VN-Rueckkauf
   sind benannt, aber ohne Katalog-ID, Zuweisung, Parameterberechnung,
   Snapshot oder Ausfuehrung. Alte Schadenregeln bleiben ausgeschlossen.
6. Read-only JSON-Payload und `GET /api/model/life-sector-contract` fuer
   FastAPI und Starlette-Fallback; gezielte Modell-, API- und Doku-Tests.

## Herkunft und Migrationsannahme

`IMSDATA.C` hat zwei `Sp`-/`Rk`-Positionen mit Praemie, Schaden und einer
einzigen Akteursregel. `IMS.E` bucht Risikoschaeden. Weder das Kuerzel
`LV` noch die Positionen belegen ein Lebensversicherungsmodell mit
Laufzeiten oder Garantien. Deshalb ist dies ein **neuer Zielvertrag**,
keine Portierung dieser Zahlen und keine historische Gleichheitsbehauptung.

## Offene Entscheidungen vor PR159

- Zeitpunkt der Praemienzahlung und Garantieverzinsung innerhalb einer
  Periode; Berechnungsbasis, Dezimalpraezision und Rundung der Gutschrift.
- Quelle und Hoehe der Verpflichtungsfreisetzung bei Tod, Ablauf und
  Rueckkauf; Auszahlung und Reservefreisetzung sind nicht identisch.
- Anlageergebnis wird zunaechst als expliziter Szenariofluss geliefert,
  nicht aus einer stillschweigenden Anlagestrategie abgeleitet.
- Keine Sterbetafel, keine Storno-/Neugeschaeftsautomatik und keine
  Solvency-II- oder gesetzliche Bilanzbewertung in diesem Schnitt.
