# Plan: Kontrollierter Run-Control-UI-Start (PR 64)

## Ziel

Die bestehende Workbench-Karte `Run-Control-Ausfuehrungsflow` wird an die in
PR 63 geschaffene atomare Backend-Grenze angebunden. Der Browser darf einen
Start nur in zwei expliziten Schritten ausloesen: Freigabe pruefen und den
unveraenderten freigegebenen Payload starten.

## Umsetzungsschnitt

1. Nur ein ausgewaehlter Queue-Eintrag mit Status `validated` kann zur
   Freigabepruefung angeboten werden.
2. Die UI verlangt Freigebenden, Begruendung und eine sichtbare explizite
   Bestaetigung.
3. Fixture- und Ausgabepfade bleiben vollstaendig ausserhalb des Browsers;
   `release_profile_id` bleibt das serverseitig bekannte Profil
   `vu14-calculated-diagnostic`.
4. Beim Freigabecheck werden UTC-Zeitpunkt und ein stabiler
   `idempotency_key` erzeugt und fuer den anschliessenden Start unveraendert
   aufbewahrt.
5. Der Startbutton bleibt bis zu einem positiven
   `POST /api/run-control/adapter-release-check` gesperrt.
6. Nach Start oder Fehler werden Queue, Aktionsplan, Queue-Detail und
   Ergebnisanzeige neu geladen. Es gibt keinen automatischen Wiederholungsstart.

## Validierung

- Frontend-Build und bestehende Frontend-Vertragstests;
- Quelltests fuer die zweistufige Freigabe, Idempotenz und gesperrte Grenzen;
- API-Tests bleiben bei injizierten Adapterfunktionen;
- Browser-Smoke fuer Layout und gesperrten Ausgangszustand, ohne den
  Startbutton auszufuehren;
- kompletter Pytest-Lauf.

## Nicht-Ziele

- kein Queue-Worker oder Hintergrundlauf;
- kein Browser-Upload und keine freie Pfadauswahl;
- keine automatische Freigabe oder Wiederholung;
- keine neue Fachlogik oder automatische historische Regelwahl;
- keine Simulation;
- keine historische Vollgleichheitsbehauptung.
