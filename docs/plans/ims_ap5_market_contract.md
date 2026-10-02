# AP5: Mehr-VU-, Risiko- und Gruppenvertrag zur fachlichen Prüfung

Stand 02.10.2026. **Vom Auftraggeber fachlich angenommen und zur Umsetzung
freigegeben:** „Vertrag annehmen und umsetzen“. Beleg:
`../reports/ims_ap5_contract_acceptance.md`. Produktabnahmen stehen noch aus.
Der AP5-Umsetzungsauftrag liegt vor. Dieser Vertrag konkretisiert die
angenommene Marktplanung und die separat angenommenen Ergänzungen E05-01/02
aus dem Vorstandsplan. Er ändert bisherige AP3-Ergebnisse nicht.
Neuer umgesetzter Vertrag: `ims.modern-market.v1`; AP3 bleibt
`ims.modern-strategy-input.v1` mit seiner Fokus-VU-Rechnung.

## Entscheidung in Alltagssprache

Kunden wählen aus den aktuell verfügbaren Angeboten. Ihre Prämie und ihre
künftigen Schäden werden genau einmal beim gewählten Versicherer gebucht.
Bereits entstandene Schadenreserven bleiben beim bisherigen Versicherer.
Ein Anbieter kann nur die ausdrücklich erklärte Menge aufnehmen. Reicht die
Kapazität sämtlicher geeigneter Anbieter nicht, bleibt Nachfrage sichtbar
unversichert. Marktwerte sind die Summe aller gemeinsam bilanzierten VUs.
Ein Filter verändert nur die Ansicht.

Neu gegenüber AP3 sind die gemeinsame Buchung, die mitwechselnden Risiken,
begrenzte Aufnahme und zeitabhängige Familien. Das ist eine erklärte moderne
Erweiterung, keine Behauptung vollständiger historischer Gleichheit.

## Gemeinsamer Ablauf je Modellperiode

1. Schlussbestände der Vorperiode werden zu Anfangsbeständen. VUs sehen den
   abgeschlossenen Vorperiodenstand; für Periode 1 ist der deklarierte
   Anfangssnapshot maßgeblich.
2. Fällige, vorher beschlossene Maßnahmen und Parameterfenster werden aktiv.
   Anschließend berechnen alle in dieser Sparte aktiven VUs ihr Angebot.
3. Kunden entscheiden anhand aktueller öffentlicher Angebote und deklarierter
   Schwellen. Kapazität wird innerhalb jeder Sparte in stabiler Kundengruppen-
   ID-Reihenfolge vergeben. Preisgleichstände entscheidet die kleinere VU-ID.
4. Prämie und die dieser Periode zugehörigen Risikoschäden werden einmal dem
   ausgewählten Träger zugeordnet. Alte Schadenverbindlichkeiten bleiben beim
   alten Träger. Unversicherte Mengen und deren Selbstbehalt/Schaden werden
   getrennt außerhalb der VU-Bilanz ausgewiesen.
5. Werbung, Betrieb, fällige Maßnahmenkosten, Anlagen-/Bestandsflüsse und
   erklärte Schaden-/Kapitalzahlungen werden einmal gebucht. Alle VUs werden
   geschlossen; Markt und Familien werden aus diesen Zeilen aggregiert.

Kundengruppen bilden homogene Kohorten mit stabiler Identität, Menge und
deklariertem Risikopfad. Eine Kohorte wird vollständig übernommen oder dem
nächsten geeigneten Anbieter angeboten. Sie wird im ersten Vertrag nicht
teilweise aufgeteilt. Diese Reihenfolge und die fehlende Aufteilung sind
bewusste Workshop-Annahmen; es wird keine optimale Markträumung behauptet.
Die Anfangsverträge müssen zu aktiven Sparten und deren Kapazität passen.
Die Versicherungsentscheidung nach Vrvn06 (Schadenindikator ≤ Schwelle) bleibt
kartiert. Kein aktives oder ausreichend großes Angebot bedeutet unversichert.

## Risiko, Cash und Bilanz

Für Kfz und Sach/Haftpflicht kommt der neue Schadenaufwand aus dem ausdrücklich
deklarierten Kohorten-/Periodenrisiko. Er folgt dem Träger dieser Periode.
AP3-Schäden werden beim Import nicht automatisch umgedeutet. Eine deklarierte
Zahlungsquote bestimmt den sofort bezahlten Anteil neuer Schäden; der Rest
bleibt Schadenverbindlichkeit. Eine gesonderte Altzahlung darf höchstens die
Anfangsverbindlichkeit dieser VU verbrauchen. Keine Zahlung wandert durch einen
Kundenwechsel. Vollständige Schadenjahrgänge, Rückversicherung und verzögerte
Recovery-Abrechnung sind weiterhin AP11.

Für die Cash-basierte Nichtleben-Seminarbilanz gilt:

```
Ergebnis = Prämie + Anlageertrag − neuer Schadenaufwand − Betrieb/Maßnahmen
A_end = A_start + Prämie + Anlageertrag + Kapitalzugang
        − neue/alte Schadenzahlung − Betrieb/Maßnahmen − Kapitalabgang
L_end = L_start + neuer Schadenaufwand − neue/alte Schadenzahlung
E_end = E_start + Ergebnis + Kapitalzugang − Kapitalabgang
A_end = L_end + E_end
```

Anfangsbilanz, Zahlungsgrenzen und vierstellige Dezimalbeträge werden geprüft.
Jede Kohortenbuchung wird einmal auf vier Nachkommastellen gerundet; Aggregate
addieren diese gebuchten Werte ohne erneute Rundung. Preis und Menge bleiben
bis zur Buchung erklärt. Negative Cash- oder Schadenverbindlichkeitsbestände
erzeugen einen sichtbaren ungültigen Gesamtlauf; keine stillen Kürzungen oder
weggelassenen VUs. Eigenkapital darf negativ sein und wird sichtbar ausgewiesen.
Ein dynamischer Insolvenz-/Finanzierungsmechanismus wird hier nicht behauptet.

Die vorhandenen begrenzten Lebens-/Krankenkanäle erhalten eigene, je VU
deklarierte Anfangsbestände und bestehende Bilanzregeln. Kein Lebens-Neugeschäft
aus einer noch nicht vorhandenen VN-Regel; kein verdeckter Transfer von
Lebens- oder Krankenpolicen durch die Nichtleben-Auswahl. Versicherungsgruppen
können nur benötigte Sparten aktivieren. Nicht betrieben ist explizit null
Aktivität; unbekannte benötigte Eingaben bleiben fehlend und verhindern den Lauf.

## Regeln, Familien, Gruppen und Information

Zunächst ausführbar: kartierte Vrvu01-Preis-/Werberegel mit erklärten Parametern,
Vrvn06-Auswahl mit ausdrücklich dokumentierter Kapazitätszulassung sowie die
vorhandenen begrenzten Lebens-Anlage-/Kranken-Preis- und Bestandskanäle.
Konstante Angebote werden als expliziter moderner Parameterpfad kenntlich
gemacht. Weitere historische Regelkerne werden nicht ohne eigenes Mapping
als neue Familie angeboten.

| Begriff | Vertrag |
| --- | --- |
| Versicherungsgruppe | Stabile Mutter-/Gruppen-ID; Modell-VUs werden ohne Doppelzählung zugeordnet. Noch keine Top-40-Auswahl oder echten Strategieprofile. |
| VU-Vergleichsgruppe | Benannte, gegebenenfalls überlappende Auswahl von VUs; Filter, keine additive Partition. |
| VN-Kundengruppe | Stabile Kohorte mit Menge, Risiko und ausführbarer Auswahlregel je genutzter Nichtleben-Sparte. |
| Strategiefamilie | Ausführbare Regel und Parameterprofil mit inklusivem Zeitfenster je VU und Sparte. Genau eine gültige Familie je aktiver VU/Sparte/Periode. |

Familien summieren disjunkte VU-/Spartenbuchungen. Summe aller Familien ergibt
den Markt; überlappende Vergleichsgruppen dürfen nicht addiert werden.
Preis wird mit tatsächlich gedeckter Menge gewichtet; bei Menge null bleibt
der gewichtete Preis undefiniert. Anteilnenner ist der ausgewiesene Modellmarkt.
API, Diagrammtabelle und Einzel-VU-Excel verwenden dieselben Zeilen und Quellen.
Filter ändern keine Entscheidung, Buchung oder Zufallszahl.

E05-02: VUs erhalten nur vorher abgeschlossene Marktinformationen; Kunden
kennen aktuelle öffentliche Angebote. Zukünftige Schäden und spätere Ereignisse
sind keine Entscheidungseingaben. Die Vrvu01-Regel verwendet ihre expliziten
Zufallswerte, nicht vorgespiegelte Rivalenreaktionen. Konkrete spätere Rivalen-
Informationsspiele bleiben AP10/AP14. Die begrenzte Aufnahme prüft dieselben
Mengen und Risiken, die anschließend gebucht werden.

## Maßnahmenkosten, Vorlauf und Dauer (E05-01)

Jede Maßnahme hat Entscheider, Sparte, Kosten, Entscheidungsperiode p, Vorlauf
v ≥ 0 und Wirkdauer d ≥ 1. Die Kosten werden in p als Betriebsaufwand/Cash-
Abgang gebucht. Wirkung gilt in p+v bis p+v+d−1, jeweils einschließlich.
Vorlauf null wirkt nach der Entscheidung vor der Kundenauswahl derselben
Periode. Ende des Fensters stellt das vorher erklärte Grundprofil wieder her.
Preis-/Werbe-/Aufnahmeparameter wirken nur über den benannten Modellkanal.
Überlappende widersprüchliche Maßnahmen werden abgelehnt, nicht still gestapelt.
Gleicher Vergleich mit und ohne Schock muss Maßnahmenkosten enthalten.
Neue ICT-Kopplung oder Fallback-Wirksamkeit wird hier nicht eingeführt.

Beispiel: Entscheidung p2, Kosten 3, Vorlauf 2, Dauer 2, Aufnahme 6→8:
Kosten in p2; Aufnahme 6 in p2/p3, 8 in p4/p5, wieder 6 in p6.
Die Wirkung macht eine unversicherte Menge erst ab p4 aufnahmefähig; sie
verändert keine vorherige Buchung rückwirkend.

## Handfall H1: Wechsel mit Altreserve

Zwei aktive Kfz-VUs, eine Kundengruppe mit Menge 10 und neuem Schaden 40.
Die vorherige Vertragsträgerin ist VU1. Aktuelle Preise 3 und 2 führen bei
genügend Kapazität zu VU2. Prämie 10 × 2 = 20, neuer Schaden/Zahlung 40
bei VU2. Eine alte Verbindlichkeit 20 und ihre Zahlung 5 bleiben bei VU1.
Anlage-/Kapitalflüsse null, Betrieb 2 bei VU1 und 1 bei VU2.

| Buchung / Bestand | VU1 | VU2 | Markt |
| --- | ---: | ---: | ---: |
| A_start | 100 | 100 | 200 |
| L_start | 20 | 0 | 20 |
| E_start | 80 | 100 | 180 |
| gedeckte Menge | 0 | 10 | 10 |
| Prämie | 0 | 20 | 20 |
| neuer Schadenaufwand | 0 | 40 | 40 |
| alte Schadenzahlung | 5 | 0 | 5 |
| neue Schadenzahlung | 0 | 40 | 40 |
| Betrieb | 2 | 1 | 3 |
| Ergebnis | −2 | −21 | −23 |
| A_end | 93 | 79 | 172 |
| L_end | 15 | 0 | 15 |
| E_end | 78 | 79 | 157 |

172 = 15 + 157. Ohne weitere Flüsse sind genau diese Schlusswerte die nächste
Anfangsbilanz. Ein unveränderter Schaden von 40 auch bei VU1 wäre eine
Doppelbuchung; ein Transfer der alten Reserve nach VU2 wäre unzulässig.

## Handfall H2: Kapazität, Preisgleichstand und unversichert

Drei VUs öffnen mit A=E=100 und L=0. Preise 2/2/3, Kapazitäten 6/8/4.
Kohorten in stabiler ID-Reihenfolge G1/G2/G3: Mengen 6/8/5, neue Schäden
9/4/7. Der Indikator liegt unter ihrer Versicherungsschwelle. Ohne Betrieb,
Anlage und Kapital; versicherte neue Schäden werden sofort bezahlt.

G1 nimmt VU1 (Preisgleichstand, kleinere ID). G2 nimmt VU2 (VU1 voll).
G3 findet keinen Anbieter mit freier Kapazität 5 und bleibt unversichert;
seine Menge 5 und sein Schaden 7 stehen ausdrücklich außerhalb der VU-Summe.

| Ergebnis | VU1 | VU2 | VU3 | Markt |
| --- | ---: | ---: | ---: | ---: |
| gedeckte Menge | 6 | 8 | 0 | 14 |
| Prämie | 12 | 16 | 0 | 28 |
| Schadenaufwand/Zahlung | 9 | 4 | 0 | 13 |
| Ergebnis | 3 | 12 | 0 | 15 |
| A_end = E_end, L_end=0 | 103 | 112 | 100 | 315 |

Angebotene Nachfrage 19 = gedeckt 14 + unversichert 5. Risikosumme 20 =
versicherter Schaden 13 + unversicherter Schaden 7. Mengenpreis 28/14=2.
Disjunkte Familien {VU1,VU2} und {VU3} ergeben 215 + 100 = 315.
Überlappende Vergleichsgruppen {VU1,VU2} und {VU2,VU3} ergeben 215 und 212;
deren Summe 427 ist kein Marktwert. Eine unveränderte Filterauswahl erhält 315.

## Herkunft und technische Grenzen

| Herkunft | Wiederverwendung / bewusste Erweiterung |
| --- | --- |
| `IMS.E`, Vrvu01, ab Zeile 1087 | Vier explizite Preis-/Werbe-Zufallswerte; kartierter Python-Kern `ims.model.vu_rules`. |
| `IMS.E`, Vrvn06, ab Zeile 3521 | Anfangsverträge, Schwelle, günstigste aktive VU, Gleichstand und aktuelle Trägerbuchung; `ims.model.vn_insurance_rules`. Kapazität/Kohortenrisiko sind moderne Ergänzungen. |
| `IMS.E`, Agrsich, ab Zeile 402 | Historische Aggregation enthält Aktivitätsmittel. Neue Marktadditionen und gewichtete Preise werden ausdrücklich getrennt. |
| `ESS.C`, sy_simltp/sy_xaktion, ab Zeile 88 | Historische Aktionen/teilweise zufällige Reihenfolge; neue feste Angebots-/Wahl-/Buchungsphasen sind kein identischer historischer Scheduler. |
| `IMSDATA.C`, vkrvu/vkrvn, ab Zeile 73 | Historische Klassen und 25er-Tabellen; neue VU-/Gruppen-IDs erhalten einen eigenen begrenzten Vertrag. |
| `ims.accounting.non_life_model_balance` | Geprüfte Cash/Reserve/Eigenkapitalformeln. Vdefmd6-ID-Limit bleibt im alten Validator bestehen; moderner Validator wird gesondert gebaut. |

RNG wird versioniert an Seed, Akteur, Periode und Kanal gebunden. Ein 41.
Anbieter verschiebt keine Zufallsfolge bestehender VUs. Exakte historische
myrndf-Gleichheit wird nicht behauptet. Baseline/Variante teilen Anfangsperioden
1–5; Eingriffe beginnen frühestens p6. Zwei/fünf Perioden sind echte Prefixe
desselben Vertrags, keine gesondert ausgewürfelten Fälle.

Die bisherigen Kernel prüfen positive VU-IDs und sortieren sie. Der alte
Bilanzvalidator beschränkt dagegen ausdrücklich auf 25. Ein Probelauf mit
41 Angeboten und alte Bilanzprüfung sind daher getrennte Nachweise; sie
belegen noch keinen gemeinsam bilanzierten 41-VU-Produktlauf. Vor endgültiger
Grenzfestlegung werden 40/41 VUs × 100 Perioden samt API-Ergebnisgröße gemessen.

Fertigstellung im selben AP5-PR: eigener Validator und gemeinsamer Runner,
Handfallregressionen, deterministische Größenläufe, API, nutzbare Marktsicht,
Familien-/Vergleichsfilter, Einzel-VU-Excel, Einsteigeranleitung und höherer
Installer-Release. Top-40-Ranking, vier neue Schocks und neue Lebens-Nachfrage
werden dadurch nicht vorweggenommen.

## Fachliches Entscheidungstor

Zur Annahme stehen insbesondere: prospektiv mitwandernde Risiken und beim
alten Träger verbleibende Altreserven; homogene ganze Kohorten mit erklärter
Kapazitätsreihenfolge; die getrennten Gruppen-/Familienbegriffe; Kosten/Vorlauf/
Dauer und der vorperiodische Informationsstand. H1/H2 und das Maßnahmenbeispiel
machen diese Entscheidungen konkret prüfbar. Technische Handfallproben sind
Vorbereitung des Tors und keine Anwenderabnahme der AP5-Lieferung. Der Auftraggeber
hat diesen konkreten Vorschlag anschließend ausdrücklich angenommen; der
[Annahmebeleg](../reports/ims_ap5_contract_acceptance.md) hält Umfang und Grenze fest.
