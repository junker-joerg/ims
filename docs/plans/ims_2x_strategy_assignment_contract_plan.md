# PR106: Strategiezuordnungs- und Parametrisierungsvertrag

Stand: 2026-09-02

## Ziel

PR106 legt einen kleinen, versionierten und rein lesenden Vertrag fuer die
Zuordnung vorhandener Strategien zu VU und VN sowie fuer die bereits
implementierten Parameterformen fest. Der Vertrag beantwortet drei Fragen:

1. Welcher Akteurstyp darf welche Katalogstrategie verwenden?
2. Auf welcher Ebene gilt die Zuordnung heute?
3. Welche vorhandenen Parameterfelder gehoeren zu welcher Strategie?

Der Schritt macht keine Zuordnung editierbar und fuehrt keine Regel aus.

## Historische Grundlage

- `IMSDATA.C`: `ACTION`, `vkrvu` und `vkrvn`;
- `IMS.E`: `Vuauini`, `Vnauini` und die Gruppen in `Vdefmd6`;
- `ims.model.vdefmd6_population`: typisierte 25 VU und 200 VN;
- vorhandene Parameter-Dataclasses und Mapping-Loader in `vu_rules.py` und
  `vn_insurance_rules.py`;
- vorhandene Vdefmd6-Snapshotadapter fuer die belegte Parameterprojektion.

## Vertragsentscheidungen

1. Die Strategie gilt je einzelnem VU oder VN, nicht je Regelklasse.
2. Ein Akteur besitzt heute hoechstens eine Katalogstrategie.
3. Dieselbe Strategie gilt fuer beide historischen Sektorpositionen.
4. Strategieparameter sind Zweiervektoren fuer diese Positionen.
5. Die zwei Positionen erhalten noch keine modernen Spartennamen.
6. Gruppenbearbeitung, sektorweise Strategien und geplante Strategiewechsel
   bleiben gesperrt.
7. Vorhandene Loader-Pruefungen werden dokumentiert; neue Wertebereiche,
   Defaults oder Fachregeln werden nicht eingefuehrt.

## Lieferumfang

- Vertrag `ims.strategy-assignment-contract.v1` im Paket `ims.strategies`;
- zwei Zuordnungstypen mit zehn VU- und sechs VN-Strategien;
- dreizehn unterschiedliche Parameterschemata fuer fuenfzehn
  parametrisierte Strategien;
- achtzehn aus `Vdefmd6` abgeleitete Quellprofile fuer 25 VU und 200 VN;
- GET-Endpunkt `/api/strategies/assignment-contract`;
- Integritaets- und API-Tests sowie Migrationsdokumentation.

Die Quellprofile enthalten keine Parameterwerte. Ein SHA-256-Fingerabdruck
unterscheidet vorhandene Parameterprofile, insbesondere VU14 von VU15-16,
ohne daraus neue Semantik abzuleiten.

## Nicht in PR106

- keine Strategieauswahl oder Parameterbearbeitung in der Workbench;
- keine Speicherung neuer Zuordnungen oder Parameter;
- keine Zuordnung einer anderen Strategie je Sparte;
- keine Benennung als Kfz, Sach-Haftpflicht, Leben oder Kranken;
- kein Strategieplan oder automatischer Wechsel nach Perioden;
- kein Compiler in Regel-Snapshots, kein Runner-Start und keine Simulation;
- keine historische Vollgleichheitsbehauptung.

## Validierung

- Katalogabdeckung nach Akteurstyp exakt pruefen;
- Parameterschemata gegen reale Dataclass-Felder und Loader pruefen;
- Vdefmd6-Gruppen, Zielbereiche, Aktivierungsperioden und Regelklassen
  rueckbinden;
- vollstaendige und ueberlappungsfreie Abdeckung von 25 VU und 200 VN
  nachweisen;
- falsche Ziel-, Schema- und Profilvertraege negativ testen;
- API-Schreibmethoden abweisen;
- vollstaendige Python-Regression ohne Simulationsstart ausfuehren.

## Anschlussplanung

PR107 soll die Quellprofile und Parameterschemata in einer kompakten
read-only Workbench-Ansicht darstellen. PR108 kann danach ein versioniertes
Entwurfsformat fuer konkrete Zuordnungen und Parameterwerte samt reiner
Validierung vorbereiten. Erst ein weiterer eigener PR darf einen validierten
Entwurf in bestehende Regel-Snapshots uebersetzen; UI-Schreiben und
Ausfuehrung bleiben davon getrennte Freigaben.
