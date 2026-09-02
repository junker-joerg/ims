# PR111: Snapshot-Bauplaene read-only in der Workbench anzeigen

Stand: 2026-09-02

## Ziel

PR111 macht die in PR110 eingefuehrte, zustandslose Uebersetzung in der
Workbench sichtbar. Ein Anwender kann einen im Tab `Entwurf` erfolgreich
geprueften Entwurf als Snapshot-Bauplanvorschau anzeigen und je Zuordnung
erkennen, welche Werte bereits aus dem Entwurf stammen und welche
periodenspezifischen Laufzeitwerte noch fehlen.

Die Vorschau speichert und materialisiert keinen Snapshot und fuehrt keine
Regel aus.

## Grundlage

- `IMSDATA.C`: `ACTION.st`, `vkrvu` und `vkrvn` als historische Regelbindung;
- `IMS.E`: `Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06`;
- PR108/109: lokaler, validierter Strategieentwurf in der Workbench;
- PR110: Vertrag und API fuer die deterministische Uebersetzung in partielle
  Bauplaene vorhandener VU-/VN-Regel-Snapshottypen.

## Bedienpfad

1. Entwurf lokal erfassen und erfolgreich pruefen.
2. In den Tab `Bauplaene` wechseln.
3. Die zustandslose Vorschau explizit anfordern.
4. Je VU/VN Snapshottyp, Zielcontainer und Zeitbindung lesen.
5. Vorbereitete und noch erforderliche Snapshotfelder getrennt vergleichen.

Technische Feldnamen bleiben als kleine Referenz sichtbar. Die Haupttexte
benennen die Werte fuer Anwender verstaendlich, etwa Zufallsziehungen,
Zinssatz, Schockstatus, Schwellen, aktive Versicherer oder Marktinput.

## Lieferumfang

- fuenfter Strategie-Tab `Bauplaene`;
- Laden des read-only PR110-Uebersetzungsvertrags;
- expliziter POST gegen die zustandslose PR110-Uebersetzung;
- kompakte Zusammenfassung fuer Zuordnungen und offene Felder;
- responsive Bauplanliste mit vorbereiteten und offenen Werten;
- Frontend-, Dokumentations-, Build- und Browsertests.

## Geschlossene Grenzen

- keine Datei-, Browser- oder Datenbankspeicherung;
- kein Import oder Export von Entwuerfen;
- keine Anwendung von Snapshot-Defaults;
- keine Snapshot-Materialisierung;
- keine Run-Control-, Runner- oder Simulationskopplung;
- keine historische Vollgleichheitsbehauptung.

## Validierung

- Vorschau nur nach erfolgreicher Entwurfspruefung freigeben;
- Aenderungen am Entwurf verwerfen eine vorhandene Vorschau;
- API-Fehler und ungueltige Berichte sichtbar behandeln;
- alle offenen Feldnamen ohne Layoutueberlauf darstellen;
- Desktop- und Mobilansicht visuell pruefen;
- Frontend-Produktionsbuild und vollstaendige Python-Regression ohne
  Simulationsstart ausfuehren.

## Anschlussplanung

PR112 kann den expliziten Kontextvertrag fuer Periode, Ziehungen, Zinssatz,
Schockstatus, Markt- und Vorperiodenwerte definieren. Auch dieser Vertrag soll
zunaechst nur validieren. Die Materialisierung vollstaendiger Snapshots und
eine spaetere Runner-Freigabe bleiben getrennte weitere PRs.
