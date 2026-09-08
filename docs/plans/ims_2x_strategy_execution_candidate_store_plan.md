# PR127: Ausfuehrungskandidaten unveraenderlich speichern

Stand: 2026-09-08

## Ziel

PR127 speichert einen vollstaendigen PR126-Kandidaten nur nach gesonderter
expliziter Freigabe in der konfigurierten lokalen SQLite-Ablage. Der Server
baut den Kandidaten aus den originalen versionierten Eingaben erneut, prueft
ID und Inhaltsdigest vor dem Schreiben und liest den Datensatz fuer eine
zweite Digest-Pruefung wieder zurueck.

Run-Control, Runner und Simulation bleiben gesperrt.

## Historischer Bezug

Die historischen Aktionen `Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06`
aus `IMS.E` arbeiteten auf gemeinsamem Laufzustand. PR127 portiert keine
dieser Fachregeln. Die Ablage trennt lediglich den bereits kanonisch gebauten
Einperiodenzustand dauerhaft von spaeterer Freigabe und Ausfuehrung.

## Speichervertrag

Der Schreibrequest enthaelt exakt:

- Schemaversion;
- den vollstaendigen PR125-Kandidateneingang;
- erwartete Kandidaten-ID und erwarteten SHA-256-Digest aus einer vorherigen
  PR126-Vorschau;
- einen expliziten Speicherzeitpunkt mit Zeitzone;
- `explicit_storage_release = true`.

Ein fertiger Kandidaten-Payload aus dem Browser wird nicht akzeptiert. Freie
Datenbank-, Profil- oder Ausgabepfade werden ebenfalls nicht angenommen.

## Atomare Ablage

1. Requestform und Speicherfreigabe pruefen.
2. Erwartete ID aus dem erwarteten Digest ableiten und vergleichen.
3. Den Kandidaten serverseitig erneut nach PR126 bauen.
4. Kandidateninhalt kanonisch hashen und ID sowie Digest pruefen.
5. In einer Transaktion per reinem `INSERT` ablegen.
6. Den geschriebenen oder bereits vorhandenen Datensatz erneut lesen.
7. JSON-Inhalt, relationale Metadaten, ID und Digest gemeinsam pruefen.
8. Nur den vollstaendig verifizierten Datensatz zurueckgeben.

Ein identischer Wiederholungsrequest ist idempotent und veraendert auch den
urspruenglichen Speicherzeitpunkt nicht. Ein abweichender vorhandener Inhalt
wird weder aktualisiert noch repariert, sondern als Integritaetskonflikt
abgewiesen.

## API

- `GET /api/strategies/execution-candidate-store-contract` beschreibt die
  Speicher- und Sperrgrenzen read-only.
- `POST /api/strategies/execution-candidate-store` baut und speichert nach
  expliziter Freigabe.
- `GET /api/strategies/execution-candidates/{candidate_id}` liest genau einen
  Kandidaten und prueft seinen Digest erneut.

Alle Schreib- und Leseoperationen verlangen die bereits konfigurierte
Workbench-SQLite-Datei. Die API akzeptiert keinen Datenbankpfad im Request.

## Schutzgrenzen

- keine neue oder geaenderte VU-/VN-Fachregel;
- keine Aktualisierung oder Loeschung gespeicherter Kandidaten;
- kein Run-Control-Eintrag und keine Ausfuehrungsfreigabe;
- kein Runner-, Scheduler-, Carryover- oder Exportaufruf;
- keine Simulation und kein historischer Vergleich;
- keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.

## Validierung

- erstmalige Ablage und read-only Wiederaufruf mit zweiter Digest-Pruefung;
- idempotente identische Wiederholung ohne zweiten Schreibvorgang;
- fehlende Freigabe, falscher Erwartungsdigest und fehlgeschlagener
  Kandidatenbau erzeugen keine Ablage;
- veraenderte Metadaten und beschaedigter Kandidateninhalt werden erkannt und
  nicht ueberschrieben;
- API-Methoden-, Invalid-JSON- und fehlende-SQLite-Tests;
- Grenztest verhindert Runner und Simulation;
- Gesamtregression ohne neuen Simulationsstart.

## Naechster Schritt

PR128 zeigt Kandidatenreife, Herkunft, Digest und Speicherstatus jetzt rein
lesend in der Workbench. Als naechstes bindet PR129 Kandidaten-ID und erneut
geprueften Digest an die Run-Control-Freigabegrenze an; Start und Ausfuehrung
bleiben dort noch gesperrt.
