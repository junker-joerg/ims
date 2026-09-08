# PR121: VU-Snapshots atomar materialisieren

## Ziel

PR121 materialisiert einen vollstaendig gueltigen PR120-Eingang in die bereits
vorhandenen typisierten VU-Snapshots. Der Schritt verbindet die versionierten
Strategieentwuerfe, Parameter, Kontextwerte und Herkunftsnachweise, fuehrt die
VU-Regeln aber nicht aus.

## Voraussetzungen

- PR110 liefert je VU einen Snapshot-Bauplan und typisierte Parameter.
- PR119 verlangt alle offenen VU-Snapshotfelder ohne Loader- oder
  Runner-Fallbacks.
- PR120 prueft Periodenzustand, Anspruchsprofile, Bestand `t-2` und aktive
  VN-Zahl gegen einen expliziten Zustandsbeleg.

Ein Fehler in einer dieser Stufen verhindert jeden Snapshot-Loader-Aufruf.

## Umsetzung

1. Die vollstaendige PR120-Anfrage atomar validieren.
2. Ausschliesslich die VU-Eintraege aus der PR110-Uebersetzung auswaehlen.
3. Die bereits typisierten Strategieparameter und abgeglichenen
   PR119-Kontextwerte zu einem Loader-Payload zusammensetzen.
4. Den im PR118-Bestand dokumentierten Snapshotloader je Strategie aufrufen.
5. Loaderresultat gegen den erwarteten Snapshottyp pruefen.
6. Snapshots nur veroeffentlichen, wenn alle VU-Eintraege erfolgreich sind.

Der PR120-Zustandsbeleg bleibt eine Validierungsvoraussetzung. Seine Werte
werden nicht als zweite Quelle in den Snapshot kopiert.

## Atomare Grenze

- PR120-Fehler verhindern jeden Snapshot-Loader-Aufruf.
- Bei einem Loader- oder Typfehler werden bereits erzeugte Zwischenergebnisse
  verworfen.
- `partial_results_returned = false` gilt fuer alle Fehlerpfade.
- Es gibt keine Speicherung und keine Aenderung von VU-, VN- oder BAV-Zustand.

## Nachweis

- gemeinsamer positiver Test fuer alle zehn VU-Strategien und acht
  Snapshottypen;
- deterministische Wiederholung ohne Mutation der Anfrage;
- negativer Test fuer einen Herkunftsfehler vor dem ersten Loader;
- negativer Test fuer atomare Verwerfung bei einem spaeten Loaderfehler;
- Test, dass keine VU-Regelausfuehrung aufgerufen wird;
- API-Tests fuer Vertrag, Materialisierung, ungueltige Eingabe und Methoden;
- vollstaendige Python-Regression ohne Simulationsstart.

## Schutzgrenzen

- keine neue oder geaenderte VU-Fachlogik;
- keine Anwendung der erzeugten Snapshots;
- keine Speicherung, Runner-Kopplung oder Simulation;
- keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.

## Restplanung

- PR122: Die vollstaendig materialisierten VU-Snapshots in der Workbench rein
  lesend, fachlich gruppiert und mit sichtbarer Herkunftsgrenze anzeigen.
- Danach: Einen eigenen Plan-PR fuer die kontrollierte Verbindung von VU- und
  VN-Snapshots mit einem Ausfuehrungspfad erstellen. Dieser Plan muss
  Zustandsuebergang, Persistenz und Abbruchverhalten vor jeder Freigabe
  getrennt entscheiden.
