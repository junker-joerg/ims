# PR168: Zustands-, Fluss- und Strategievertrag fuer Kranken

Stand: 2026-09-17

## Ziel und Schnitt

Ein versionierter, read-only Vertrag beschreibt `health` als eigenstaendiges
IMS-2.x-Modellsegment. PR168 nimmt keine Eingaben entgegen, berechnet keine
Werte und veraendert weder Altlaeufe noch die Lebens- oder
Zwei-Nichtleben-Bilanz. PR169 soll daraus einen kleinen deterministischen
Fall mit expliziten Szenariowerten und eigener Bilanzpruefung bauen.

1. Ein Versicherer, eine Periode und zunaechst ein geschlossener Bestand
   aktiver Krankenvertraege; weder Neugeschaeft noch Abgaenge in PR169.
2. Getrennte Bestands- und Bilanzgroessen: aktive Vertraege, Kasse,
   offene Leistungsverpflichtung und Eigenkapital. Die offene Verpflichtung
   betrifft bereits angefallene, noch nicht bezahlte Leistungen, keine
   Alterungsrueckstellung.
3. Getrennte Periodenfluesse: vereinnahmte und verdiente Beitraege,
   angefallene und ausgezahlte Leistungen, Anlageergebnis, bezahlter
   Aufwand sowie Kapitalzufuehrung und -ausschuettung. Bilanzgleichungen,
   Nichtnegativgrenzen und expliziter Carryover werden beschrieben.
4. Strategie-Anschlussstellen fuer VU-Beitragsgestaltung und VN-Bestandswahl
   bleiben ausschliesslich kuenftig und nicht ausfuehrbar. Leistungsanfall
   ist ein exogener Szenariowert, keine Versichererentscheidung; Auszahlung
   mindert die offene Verpflichtung und ist keine zweite Aufwandsbuchung.
5. `GET /api/model/health-sector-contract` liefert denselben JSON-Vertrag
   ueber FastAPI und Starlette. Tests pruefen Feldabschluss, Bilanzidentitaet,
   actor-/Quellentrennung, schreibfreie API und Dokumentation.

## Herkunft und Migrationsannahme

`IMSDATA.C` definiert `MAXSPARTEN 2`, `classVU.Sp[1/2]` und
`classVN.Rk[1/2]`. Die zweite C-Struktur heisst `KV`, fuehrt jedoch
Schadenwahrscheinlichkeit/-hoehe und die alten Risikofelder; `IMS.E`
verarbeitet sie als zweite Schadenposition. Das Kuerzel belegt weder
private Krankenversicherung mit eigenen Rueckstellungen noch eine
Zuordnung zu `health`. Die neuen Zustands- und Bilanznamen sind
ausdruecklich IMS-2.x-Entwurfsentscheidungen, keine Portierung dieser
historischen Werte. Der Python-Nichtleben-Bilanzvertrag dient nur als
Strukturvorbild fuer die Rechnung, nicht als automatische Feldzuordnung.

## Risiken und offene Entscheidungen

- Kein Tarif-, Alters-, Morbiditaets-, Behandlungs-, Beitragsanpassungs-
  oder Alterungsrueckstellungsmodell; daher keine Aussage ueber die
  oekonomische oder regulatorische Realitaet der Krankenversicherung.
- Beitrag und Anlageergebnis gelten im ersten Fall als periodengleich
  verdient und bezahlt; Forderungen, Storno und Neuabschluss sind offen.
- Eine spaetere Strategie darf angefallene Leistungen nicht einfach
  wegentscheiden. Quellen, Parameter, Wechselzeitpunkt und Bestandswirkung
  sind vor einer Ausfuehrung gesondert festzulegen.
- PR169 braucht ein eigenes Eingabeformat, atomare Validierung und feste
  ein- und zweiperiodige Beispiele; PR170 braucht eine explizite
  Spartenallokation vor einer Vier-Sparten-Konsolidierung.

Keine Simulation und keine historische Vollgleichheitsbehauptung in PR168.
