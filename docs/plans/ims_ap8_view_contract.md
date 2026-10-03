# AP8: Darstellungs-, Nenner- und Erklärvertrag

03.10.2026. Konkretisierung des angenommenen AP8-Anzeigeumfangs einschließlich
E08-01; kein neuer Simulationskanal und keine erfundene zusätzliche menschliche
Vertragsannahme. [Paketauftrag](ims_ap8_implementation.md).

## Gemeinsamer Lauf und sichtbare Auswahl

Die bestehende AP5-/AP6-/AP7-Rechnung bleibt die einzige finanzielle Wahrheit.
Eine reine Projektion liest deren gültige Zeilen, verändert keine Quelle, keine
RNG-Draws, Garantie, Entscheidung, Queue oder Buchung. Quellen-/Modell-/Ansicht-
Nachweise sind getrennt. Frische API-Rechnung unter derselben Rechensperre;
ungültige Quelle oder Budgetverletzung liefert keine halbe Ansicht.

Periode, Sparte, Seite und Vergleichsgruppe gelten gemeinsam für sechs Ansichten.
Familiemitgliedschaft stammt aus den tatsächlich wirksamen VU-/Spartenzeilen
dieser Periode und Seite. Unterschiedliche Mitgliedschaften zwischen Seiten
sind sichtbar; eine Zusammensetzungsänderung ist kein isolierter Strategieeffekt.
Versicherungsgruppen/Peers werden als eindeutige VU-Mengen ausgewählt; überlappende
Peers werden nicht addiert. Fokusauswahl und Rollenpfad erhalten Lauf und Filter.

## Sechs Ansichten

| Ansicht | Werte / belegter Zeitpunkt | Nenner, Gewicht oder Grenze |
| --- | --- | --- |
| Markt/Sparten | Summen der ausgewählten VU-/Spartenbuchungen, Verlauf beider Seiten | Modellwährung; Bestände am Periodenende, Flüsse je Periode; keine Summe verschiedener Expositionseinheiten |
| Anteile/Konzentration | Gebuchte Modellbeiträge pro VU, registriert/aktiv getrennt | Beiträge aller Modell-VUs derselben Periode/Sparte bleiben Nenner, auch bei Gruppenausschnitt; keine realen BaFin-Marktanteile |
| Familien | Aktuelle Mitglieder, Summe, Streuung und gewichteter Vergleich | Periodenergebnis/Anfangsaktiva mit explizitem Anfangsaktiva-Gewicht; keine ungewichteten Mittel ungleicher Portfolios |
| Wechsel | Tatsächlicher Eigentümerwechsel aus aufeinanderfolgenden Vertragsentscheidungen | P1 ist Anfangsbestand, kein Wechsel; Nichtleben-Sparten getrennt, unversichert als eigene Gegenpartei; keine wartenden Anträge als ausgegebene Verträge |
| Zeitlinie | Deklarierte Ereignisse/Entscheidung/Vorlauf plus tatsächliche Aktiv-/Kostenzeilen | Ereignis/Verfügbarkeit/wirklicher Effekt unterscheiden; AP7 24 Prozessstunden, kein historischer Kalender; Zukunft im Nachschauplan ist kein damals verfügbares VU-Wissen |
| Provider/Prozesse | Tatsächlicher deklarierter Graph, Ausfallstunden, gemeinsame Ressourcen und ausgewählte Queues | Gemeinsamer Graph/Budget bleiben benannter Gesamtkontext; Queueauswahl folgt Filter; Vorgangszahl und Arbeitseinheiten nicht vermischen |

Marktanteil `100 × VU-Beiträge / gesamte Modellbeiträge`. Konzentration HHI
`10.000 × Σ Beiträge_i² / Gesamtbeiträge²`, 0–10.000. Negative Beitragswerte oder
Nullnenner ergeben keinen erfundenen Anteil/HHI. Anteile werden einzeln gerundet;
eine kleine Differenz zu 100 Prozent ist sichtbare Rundung, keine neue Verteilung.

Familienmittel `100 × Σ Periodenergebnis_i / Σ Anfangsaktiva_i`, mit der
entsprechenden Einzelquote und Min/Max bei positivem Nenner. Null-Anfangsaktiva
bekommen keine erfundene individuelle Quote. Beiträge/Exposition sind nur
innerhalb einer Sparte sinnvoll: Nichtleben gedeckte Menge, Leben/Gesundheit
Anfangspolicen; ein gebuchter Durchschnitt ist kein neuer Tarif.

Handrechnung: Anfangsaktiva 90/10 und Ergebnis 9/3 ergeben Familienquote 12 %,
Einzelquoten 10/30 %. Ihr ungewichtetes Mittel 20 % wäre eine andere Kennzahl.
Modellbeiträge 90/10 ergeben Anteile 90/10 % und HHI 8.200. Diese unabhängigen
Handwerte sind Prüfanforderungen, keine bereits ausgelieferten AP8-Laufwerte.

E08-01: Fokus zeigt absolute Beiträge, Periodenergebnis und Eigenkapital neben
Beitragsanteil/Position. Rivalen sind alle übrigen Modell-VUs derselben Periode/
Sparte; Modellmarkt ist die gesamte vergleichbare Basis. Der Nenner folgt nicht
unbemerkt einem Familienfilter. Beitragsrang mit gleichen Beiträgen als gleichem
Rang; inaktive Anbieter und undefinierte Basis sind ausdrücklich gekennzeichnet.

## Exakte Addition, Kanal und Korrelation

Die überprüfbare Buchungsbrücke lautet:

`Δ Schluss-Eigenkapital = Δ Anfangs-Eigenkapital + Δ Beiträge + Δ Kapitalanlage
− Δ Versicherungsaufwand − Δ Betriebskosten + Δ Kapitalzuführung − Δ Ausschüttung`.

Δ ist Variante minus Basis innerhalb der bezeichneten Auswahl. Versicherungs-
aufwand ist der bestehende Kernposten; bezahlte Leistungen sind darin nicht
noch einmal als separater Verlust abzuziehen. Maßnahmen-/Prozesskosten sind
im Betriebskostenposten enthalten und werden nicht doppelt abgezogen.

Eine exakte Buchungsidentität ist eine arithmetische Zerlegung, keine isolierte
Kausalzuordnung zu einem Schock. Der sichtbare Kanal Ereignis → tatsächliche
Strategie/Abhängigkeit → Vorgang/Vertrag → Buchung nennt belegte Rechenzeilen.
Gleichzeitige Mechanismen und wechselnde Gruppen können gemeinsam wirken;
ohne zusätzliche Gegenfaktoren wird kein unabhängiger Schock-/Strategieanteil
erfunden. Ein parallel verlaufendes Diagramm wird als Beobachtung gekennzeichnet.

Begrenzte Claims-/Service-Kopplung bleibt administrative Arbeit/Kosten. Keine
verzögerten Versicherungszahlungen, SCR/MCR-, Storno-, Insolvenz-, Kalibrierungs-
oder Compliancebehauptung. Reale Quellen und Workshop-Provider-/Produkt-/
Prozessannahmen bleiben getrennt; kein verifizierter deutscher Direktmarkt.
