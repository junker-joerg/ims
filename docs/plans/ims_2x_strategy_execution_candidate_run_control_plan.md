# PR129: Ausfuehrungskandidaten an die Run-Control-Freigabegrenze anbinden

Stand: 2026-09-08

## Ziel

PR129 loest einen in PR127 unveraenderlich gespeicherten
Einperioden-Ausfuehrungskandidaten kontrolliert ueber Kandidaten-ID und
erwarteten SHA-256-Digest auf. Der Digest wird beim Abruf erneut gegen den
gespeicherten Inhalt und dessen relationale Metadaten geprueft.

Der neue Pfad ist ein Freigabecheck, kein Startpfad. Er legt keinen
Queue-Eintrag an, fuehrt keinen Preflight aus und ruft weder Adapter noch
Runner auf.

## Historischer Bezug

Die Aktionen `Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06` in `IMS.E`
griffen auf den gemeinsamen Zustand des historischen Laufs zu. Dieser Zustand
wurde nicht ueber eine separate Kandidaten-ID oder einen kryptographischen
Digest freigegeben.

PR129 portiert daher keine historische Fachregel. Die neue Freigabegrenze ist
eine technische Absicherung fuer den bereits in PR126 gebauten modernen
Einperiodenzustand. Sie behauptet weder historische RNG-Gleichheit noch
fachliche Vollgleichheit.

## Request-Vertrag

`POST /api/run-control/strategy-candidate-release-check` akzeptiert exakt:

- `schema_version`;
- `candidate_id`;
- `expected_content_digest`;
- `idempotency_key`;
- `explicit_run_control_release = true`;
- `released_by`;
- `released_at` als UTC-Zeitpunkt mit `Z`;
- `release_reason`.

Kandidateninhalt, freie Datenbank- oder Fixturepfade, Queue-/Run-IDs,
Outputpfade und Ausfuehrungsfelder sind verboten. `released_by` und die
weiteren Auditfelder sind in PR129 deklarierte Angaben, noch keine
Authentisierung oder dauerhafte Freigabeakte.

## Prueffolge

1. exakte Request-Felder, Formate und explizite Freigabe pruefen;
2. Kandidaten-ID aus dem erwarteten Digest ableiten und mit dem Request
   vergleichen;
3. Kandidat aus der konfigurierten SQLite-Ablage read-only laden;
4. gespeicherten Payload-Digest und relationale Metadaten mit der bestehenden
   PR127-Pruefung erneut verifizieren;
5. vollstaendigen erwarteten Digest vergleichen, nicht nur das in der ID
   enthaltene Praefix;
6. bestaetigen, dass die Ausfuehrungsgrenzen im Kandidaten geschlossen sind.

Ein positiver Status `release_ready` bedeutet nur, dass Identitaet,
Speicherintegritaet und geschlossene Kandidatengrenzen belegt sind. Er
schreibt keine Freigabe und erlaubt noch keinen Start.

## API und Workbench

- `GET /api/run-control/strategy-candidate-contract` beschreibt die Grenze
  read-only.
- `POST /api/run-control/strategy-candidate-release-check` fuehrt nur die
  atomare Pruefung aus.
- Die bestehende fixture-basierte Run-Control-Strecke bleibt unveraendert.
- Die Workbench zeigt nur, dass die API-Pruefung verfuegbar ist. Sie erhaelt
  in PR129 keinen Freigabe- oder Startbutton.

## Validierung

- Parsertests fuer Pflichtfelder, Formate, Auditangaben und unbekannte Felder;
- positiver Resolver-Test mit erneut geprueftem Speicherdigest;
- Negativtests fuer inkonsistente ID/Digest-Paare, abweichenden Volldigest,
  unbekannte Kandidaten und beschaedigte Speichermetadaten;
- API-Methoden- und Statuscodetests;
- expliziter Test, dass der Runner nicht aufgerufen wird;
- Frontend-Build und Gesamtsuite ohne neuen Simulationsstart.

## Schutzgrenzen

- keine neue oder geaenderte VU-/VN-Fachlogik;
- keine Queue-Anlage, kein Preflight und keine Freigabepersistenz;
- kein Adapterstart, Runner, Scheduler oder Carryover;
- keine Ergebnisdatei und kein Legacy-Vergleich;
- keine Simulation;
- keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.

## Restplanung

- **PR130:** kontrollierte Einperioden-Wirkungsprobe auf einer isolierten
  Kandidatenkopie im Backend; keine Dateien, kein Legacy-Vergleich und kein
  Carryover.
- **PR131:** manuellen Workbench-Start und read-only Ergebnisansicht an die
  vorhandene Freigabe-, Idempotenz- und Verlaufskette anbinden.
- **PR132:** Browser-Smoke, Fehlerpfade und Handbuch-Screenshots fuer den eng
  benannten Einperiodenpfad abschliessen.

Nach PR129 verbleiben drei kleine PRs bis zur kontrolliert bedienbaren
Einperioden-Wirkungsprobe. Mehrperiodenlauf, Carryover und
Regulierungssimulation bleiben eigene spaetere Ausbaubloecke.

## Naechster Schritt

PR130 darf erstmals einen erneut verifizierten Kandidaten auf einer isolierten
Kopie an `run_loaded_explicit_period` uebergeben. Der Schnitt bleibt auf genau
eine Periode ohne Dateien, Legacy-Vergleich oder Carryover begrenzt.
