# AP6: erklärter Quellen- und Modellvertrag der BaFin-Referenz

Der [Umfang wurde ausdrücklich angenommen](../reports/ims_ap6_scope_acceptance.md).
Der [Quellenkatalog](../../seminar_cases/bafin_2024_catalog.json) bleibt als
gepinntes Original erhalten. Er ist vollständig offline verfügbar; seine
Quellenlinks sind Nachweise und werden beim Laden/Rechnen nicht aufgerufen.

## Was zur Auswahl zählt

326 Gesellschaftszeilen werden nach den 145 redaktionellen Gruppenzuordnungen
einmal summiert. Ein quellenbelegter ASCII-Strich ist null; unbekannte Beiträge
dürfen keine Auswahl ergeben. Die 40 größten verfügbaren Gruppensummen werden
absteigend sortiert. Exakte Dezimalgleichstände verwenden die stabile Gruppen-ID,
keine angenommene Reihenfolge innerhalb einer Rundungsunsicherheit. Namen,
Gruppen-ID, numerische Modell-VU-ID und Rang sind getrennt. Die Registry vergibt
IDs für alle 145 Kandidaten einmalig, unabhängig von den späteren Rangpositionen.

Das Originalgewicht ist Gruppenbeitrag geteilt durch 40er-Summe oder gesamtes
erfasstes Quellenvolumen, jeweils mit genanntem Nenner. Das ist kein gesamter
deutscher Direktmarkt. Die Grenze 40/41 und ihr ursprünglicher Präzisionsnachweis
gelten für den erklärten BaFin-Umfang; Overrides erzeugen eine Annahmenrangfolge.

## Faktenoriginal, Overrides und Modellquelle

Ein portables `ims.bafin-reference-bundle.v1` führt Originalkatalog samt Digest,
Workshop-Parameter, begründete Rechtsträger-Overrides und den bestehenden
`ims.modern-market.v1`-Rechenvertrag zusammen. Overrides geben Quellenzeile,
angenommenen Beitrag in Mio. Euro und Begründung an. Sie verändern die
Originalbeobachtung nicht und werden ausdrücklich als Workshop-Werte geführt.
Die neue Auswahl wird über alle Kandidaten gerechnet; allein die bisherigen
40 Gruppen neu zu sortieren wäre falsch.

Modellwerte können in einer eigenen Sitzung zusätzlich verändert werden.
`preset_mapping` heißt: Modellquelle stimmt mit der aus Quellen und Parametern
frisch erzeugten Vorlage überein. `custom_workshop_model` zeigt eine abweichend
bearbeitete Modellquelle. Damit bleiben ursprüngliche Quellengewichte und
berechnete Modellwerte getrennt. Die 40 ausgewählten stabilen Identitäten müssen
weiter passen; nach einer Auswahländerung muss die Modellvorlage neu erzeugt
werden. Alte Lauf-/Exportnachweise gelten anschließend nicht mehr.

## Anfangsabbildung und Handfälle

Alle Zahlen der folgenden Abbildung außer den genannten Quellbeiträgen sind
Workshop-Annahmen, keine Kalibrierung. Die Default-Parameter sind editierbar.

| Kanal | Deklarierte Default-Abbildung |
| --- | --- |
| Nichtleben | Breite Schaden/Unfall-Summe × 0,4 Kfz / × 0,4 Sach/Haftpflicht / × 0,2 Rest. Die tatsächliche Produktzweigaufteilung bleibt unbekannt. |
| Beitragsziel | Modellierte Beitragsbasis in Mio. Euro × 0,01 Modellwährung. |
| Kfz/Sach | Exposition = Ziel / Modellpreis 3; vierstellige Rundung. Kapazität 1,25 × Exposition, Schäden 0,6 × Modellpreis × Exposition, bezahlt im selben Modelljahr. |
| Anfangsaktiva | 100 × Beitragsziel, je Sparte getrennt. Nichtleben hat keine Anfangsreserve. |
| Leben | Eine deklarierte Modellpolice, bestehender Bestand-/Anlagekanal, Reserve 2 × Ziel, Eigenkapital = Aktiva − Reserve; laufende Prämie = Ziel, Betrieb 0,1 × Ziel, Anlagefamilie 0,0005 auf Anfangsaktiva. Garantie-/Ablaufvertrag aus AP5 bleibt erhalten. Keine neue Nachfrage. |
| Kranken | 100 deklarierte Modellpolicen; Ziel / 100 als auf vier Stellen gerundeter Preis, Reserve 2 × Ziel. Kosten 0,1 × Ziel, Leistungen 100 × gerundete Leistung je Police, Leistungssatz 0,6 × Ziel / 100. Explizites Neugeschäft und Abgänge null. |
| Variantenfamilie | Ab Periode 6 Preis 0,9 × Modellpreis bei der ersten Kfz-aktiven Auswahlgruppe. Echte Firmenstrategien werden dadurch nicht behauptet. |

Quelle Allianz, Schaden/Unfall 19.915: Kfz-Basis 7.966; Ziel 79,66;
Exposition 26,5533; Prämie 79,6599; angenommener Schaden 47,7959;
Anfangsaktiva 7.966; Schlussaktiva in P1 7.997,8640.
Das vierstellige Modell ist reproduzierbar, aber nicht exakt gleich dem
unrundeten Beitragsziel. Das Quellen-/Restledger bleibt ungerundet.

Quellenrest: 267.483,206 − 254.270,039 = 13.213,167 Mio. Euro außerhalb
der Auswahl. Angenommener Spartenrest: 117.168 × 0,2 = 23.433,6 innerhalb
der Auswahl. Modellierte Basis 230.836,439. Die drei Teile ergeben zusammen
267.483,206, ohne Überlappung. Beitragsgewichte sind keine Mengen-/Risikogewichte.

Override-Handfall: Itzehoers Schaden/Unfall-Quellenzeile wird ausdrücklich auf
1.000 Mio. Euro angenommen. Itzehoer kommt in die Auswahl, Münchener Verein
scheidet aus; Itzehoers zuvor registrierte Modell-ID bleibt gleich. Original-
beobachtung und BaFin-Grenze werden nicht rückwirkend auf diesen Handfall geändert.

## Prüf- und Liefergrenzen

AP5 bleibt für VU-/VN-Zuordnung, Risikobuchung, Zeit, RNG und Bilanzen zuständig.
API und Excel rechnen frisch; Inhaltsnachweis bindet auch Fakten und Annahmen.
Die bestehende Höchstgrenze 64 MiB gilt einschließlich des Referenzbündels.
Es gibt keine globale RNG-Änderung und keine stillschweigende Erweiterung der
alten 25er-Verträge, Lebens-Nachfrage oder Markt-/ICT-Kopplung.

Die redaktionelle Gruppierung ist im angenommenen Referenzumfang nutzbar,
aber weiterhin keine vollständig unabhängig bestätigte historische Konzern-
konsolidierung. EWR-Abdeckung, tatsächliche Produktzweige und konzerninterne
Eliminierung bleiben als Quellenlücken sichtbar. Das ist die angenommene
Abnahmeauswirkung dieses gekennzeichneten Falls, kein Beleg historischer Gleichheit.
