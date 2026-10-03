# AP7: Produktprüfung der vier erklärbaren Schockfälle

03.10.2026. **AP7 technisch fertig im angenommenen begrenzten Workshop-Umfang.**
Produkt **2.0.0-alpha.7**, Windows-Dateiversion **2.0.0.7**. Lieferung in
[Draft-PR #296](https://github.com/junker-joerg/ims/pull/296).
[Vertragsannahme](ims_ap7_contract_acceptance.md) und
[maschinenlesbare Verifikation](ims_ap7_verification.json).
Anwenderabnahme und Merge sind weiterhin offen; kein öffentliches Release.

## Umsetzung und ICT-Erklärung

Vier offline ladbare 100-Perioden-Fälle leiten sich aus dem übernommenen
BaFin-Referenzfall ab: fiktiver Kfz-Anbieter 41, geringere Lebens-Neunachfrage,
hypothetische DORA-Umstellung und gemeinsamer Ausfall deklarierter US-Provider.
Original und eigene Sitzung, frische Rechnung, JSON-Wiederaufnahme und
Einzel-VU-Excel sind an dieselbe versionierte Schockhülle angeschlossen.

Der sichtbare Weg lautet **Ereignis → Abhängigkeit → Arbeitsbudget/Rückstand
→ Vertrag → Buchung**. Zeitlinie und zwei Verlaufskurven markieren das
Ereignisfenster. CIO, COO, CSO Vertrieb und CEO springen zur passenden Erklärung;
Perioden und Einzel-VU-Filter führen zu den tatsächlichen Rechenzeilen.
Primär- und Ersatzpfade nennen IAM, DNS, Schlüssel, Daten und Netzwerk.
Unbekannte Kontrolle ist sichtbar und kein Unabhängigkeitsnachweis.

Im US-Fall trifft der 36-Stunden-Ausfall ab Stunde 480 die ganze P21 und zwölf
Stunden in P22. In P21 hat die Basis 0 Arbeitseinheiten und 84 wartende Vorgänge;
der unabhängige vorbereitete Q-Pfad erlaubt 96 Einheiten, bearbeitet 84 und
schließt ohne Rückstand. Ein Q-Pfad mit demselben ausgefallenen US-IAM bleibt
blockiert. DORA halbiert das Arbeitsbudget von 96 auf 48; die vorbereitete
Personalmaßnahme stellt 96 wieder her. Gemeinsames Budget gilt über alle Dienste,
nicht einmal pro VU. Wartendes, teilweise bearbeitetes und abgeschlossenes
Neugeschäft werden getrennt gezeigt; Horizont-Rückstand ist kein dauerhafter Verlust.

Lebens-Neugeschäft stammt aus einem gemeinsamen deterministischen Pool; im
Nachfrageschock P21 werden ohne/mit Maßnahme ein/zwei Anträge gestellt. Erst
Bearbeitung führt ab Folgeperiode zu einer neuen Police. Alte Garantien und
alte Todes-/Ablaufleistungen bleiben erhalten. Während eines wartenden
Nichtleben-Wechsels gelten bisheriger Anbieter, Schutz, Prämie und Risiko weiter.
Der fiktive Anbieter ist erst ab P21 aktiv; 100.000 externes Kapital wird einmal
gebucht. Entscheidungs-, Ereignis-, Vorhalte-, Betriebs- und Haltekosten erscheinen
genau einmal in den betroffenen VU-/Sparten-/Marktbuchungen.

Historischer Ursprung und moderne Erweiterungen sind in
[C-/Python-Mapping](../migration/ap7_shock_contract.md) erklärt. Bestehende AP5-
Finanzbuchung und Lebens-Garantie-/Policenkette werden wiederverwendet;
alte Vertragsversionen erhalten keinen still eingefügten Nachfragekanal.

## Tatsächliche Prüfungen am festgehaltenen Produkt

Produktkommitt `37fe79117c87c504df0ee945092040d3e329a690`, Tree
`5d587300b8db89ae83dd66d0133df82001ab4636`. CI-Mergekommitt
`c954b5928265cce53a970a58c6311fd58b29861a` hat die Eltern tatsächliches AP6-main
`88841290113a37faa6bf117d4cd67dcd9ff0867c` und Produktkommitt; sein Tree ist exakt gleich.
Alle vier erforderlichen Checks an diesem Produktkommitt erfolgreich:

- [Planprüfung](https://github.com/junker-joerg/ims/actions/runs/37111434981/job/111169962500).
- [Windows-Release-Gate](https://github.com/junker-joerg/ims/actions/runs/37111434997/job/111169962258): 2.755 Python-Tests,
  14 Subtests bestanden, eine bestehende Warnung,
  1049.19 s. Frontend-, Paket- und Portable-Prüfungen bestanden.
- [Browser-CI](https://github.com/junker-joerg/ims/actions/runs/37111434967/job/111169962550): alle 70 Fälle bestanden,
  1605.657 s. Darunter elf neue AP7-Fälle.
- [Installer-CI](https://github.com/junker-joerg/ims/actions/runs/37111434943/job/111169962419): 14 Lifecycle-Prüfungen bestanden,
  1630.292 s; alle 70 Browserfälle am tatsächlich installierten
  Produkt bestanden, 1604.221 s.

Kein übersprungener, fehlgeschlagener oder instabiler Browserfall. Alle vier
100er-Rechnungen wurden frisch im echten Browser angefordert, samt exaktem
25er-Prefixvergleich, gemeinsamer P1–P5, Bilanz/Carryover, Markt=VU-Summe,
disjunkten Familien-/Gruppensummen sowie Risiko-/Queue-/Kostenkonservation.
Checkout und installierte Anwendung liefern dieselben vollständigen Ergebnis-
Digests, Mengen, P100-Bilanzen und P21-Kapazitätszeilen.

| Fall | Checkout-Rechnung/Anzeige | Installierte Rechnung/Anzeige | Antwortbytes | Ergebnisdigest beider Produkte |
| --- | --- | --- | --- | --- |
| `us_hyperscaler_outage` | 126.745 s | 123.653 s | 55,758,655 | `7ee786bf1266f74c4e95aaca4f01bd50e60c1a9c708cea6169d1be32b8b10c66` |
| `google_motor_entry` | 128.525 s | 126.234 s | 56,000,022 | `8d5e165ab934891c5abedf1d10dce231d06e0bcbc5b69844b98dc7514611225f` |
| `life_demand_shock` | 132.929 s | 134.790 s | 55,324,216 | `b5e4dcc1f876e5f76ec6ebf6abdef705eec1a975a1d750a36205dbfb191ae96a` |
| `dora_2_workshop` | 129.664 s | 129.215 s | 55,788,005 | `f2a21bdc95f946eb77b479f489dd81b7ec0308ccbde9fabe8e1f48fc2c3c2a38` |

Antworten bleiben unter dem 64-MiB-Budget. Dies sind einzelne Messungen dieser
CI-Maschinen, keine allgemeine Laufzeitgarantie. Ein 100er-Fall braucht sichtbar
mehr Zeit als ein kurzer Handfall; die Oberfläche nennt den laufenden Zustand.

Kleine Tests prüfen Stundenkanten/Teilfortschritt, echte/abhängige/unbekannte
Ersatzpfade, überlappende Ereignisse, Personal-/Fallback-Reihenfolge, einmalige
Kosten samt Rundungsrest, wirksame Wechsel, neue Lebensgarantie, Eintritt,
Finanzierung, No-shock-Vorsorge, falsche Quellen/Antworten, atomare Budgetfehler
und vollständige Unicode-JSON-Rekonstruktion aus Excel. Lokale AP5- und AP6-
Regressionen bestanden; genaue Zwischenstände bleiben separat in der Verifikation.

Hell/Dunkel × 1440×900, 1024×768, 390×844: Tastatur und Rollen-Fokusnavigation,
keine Axe-Verstöße, kein seitlicher Seitenüberlauf; minimaler Textkontrast
6,13:1 hell und 6,85:1 dunkel. Original/eigene Sitzung, ungültiges importiertes
JSON, Entwertung alter Ergebnisse, frisches JSON/Excel sowie acht echte Bilder
über die App-Anleitung sind geprüft. Zwölf aktuelle Browserbilder sind geliefert.

## Installer und Offline-Ressourcen

[CI-Artefakt](https://github.com/junker-joerg/ims/actions/runs/37111434943/artifacts/11270276173)
mit echtem Installer **21.201.657 Bytes**, SHA-256
`8241658f36d04dc756bf22a57d109ae3697e901214d09b6a4f44ba8ae02b8156`. Archivgröße/-Hash und Installergröße/-Hash wurden gegen
GitHub und Buildnachweis unabhängig geprüft. Version, sauberer Buildkommitt,
Windows-Dateiversion und Ressourceninventar passen zum oben festgehaltenen Tree.
Lokale Kopie: `dist/installer/IMS-Setup-2.0.0-alpha.7-win-x64.exe` samt `.sha256`.
Kein GitHub-Release erstellt.

372 kuratierte Ressourcen sind gebunden: 46
Rohhashes entsprechen dem Git-Blob, 326 ausschließlich der
Windows-CRLF-Umsetzung. Alle Inhalte entsprechen dem Produktstand, einschließlich
AP7-HTML und zwölf PNGs. [Offline-Anleitung](../handbook/market_ap7.html) erklärt
den Einstieg, vier Geschichten, Gegenmaßnahmen, Bilanzwirkung und Grenzen.

Der Installer-Lifecycle umfasst Unicode-/Leerzeichenpfade, laufendes Update,
getrennte Datenablage, JSON/CSV/Excel, explizite Übernahme mit Sicherungen,
Deinstallation, Wiederinstallation und Erhalt gespeicherter Ergebnisse.
Der CI-Vorgänger alpha.0 enthält dasselbe alpha.7-Bundle: geprüfter Update-
Lifecycle, kein behauptetes echtes alpha.6→alpha.7-Anwendungsupgrade.
Vorhandene lokale IMS-Verknüpfungen wurden nicht überschrieben; deshalb kein
lokaler Lifecycle im Benutzerkonto. Eine unabhängige Anwenderprüfung auf einem
Windows-Gerät ohne Entwicklerwerkzeuge steht aus. Installer unsigniert.

## Abnahmegrenzen

BaFin verdiente Beiträge einschließlich Ausland und übernommener Rückversicherung,
redaktionelle Gruppen ohne konzerninterne Eliminierung; kein belegter deutscher
Direktmarkt. Provider, Kontrolle, Produkte, Strategien, Prozess-/Kostenbasis und
Spartenmix sind Workshop-Annahmen. Claims-/Service-Kopplung betrifft administrative
Arbeit und Kosten; Versicherungszahlungen werden nicht verschoben. Keine Storno-/
Rückkauflogik, verdecktes Sparten-Funding, dynamische Insolvenz, SCR/MCR,
Compliancekalibrierung oder historische Vollgleichheit. DORA 2.0 ist hypothetisch.
Diese Begrenzungen gehören zum ausdrücklich angenommenen Vertrag.

Technisch fertig (`done`) bedeutet weder Anwenderabnahme noch Merge. Der
Abschlussdokumentationskommitt folgt diesem geprüften Produktkommitt und ändert
keine Installer-Ressource oder Anwendung. Seine eigenen CI-Checks sind im PR
separat sichtbar. Nach Fortschreibung des Manifests bestanden die 35 lokalen
Plan-/Freigabe-/Abhängigkeitstests erneut (5,421 s); historische Umfänge und
andere Pakete blieben gleich. AP7 bleibt in Draft-PR #296; kein AP8–AP14-Auftrag.
