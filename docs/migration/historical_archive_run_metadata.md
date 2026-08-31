# Archivlokale historische Laufmetadaten

Stand: 2026-08-31
Vertrag: `pr90-v1`

## Ziel und Methode

Der read-only Bericht `ims.api.historical_archive_run_metadata` wertet die
Begleitdateien der sieben in PR 88 inventarisierten ZIP-Archive aus. Ein
Eintrag mit einem Namen der Form `IMSV*.DAT` bleibt eine Ausgabedatei. Alle
anderen Eintraege werden archivlokal als Laufbericht, Modell-/Definitionsdatei,
Parameterdatei, Protokoll oder unklassifizierte Begleitdatei katalogisiert.

Inhaltlich interpretiert wird nur das bekannte Format `IMSREPOR.DAT`. Fehlende
Felder oder Begleitdateien erzeugen keine Standardwerte. Insbesondere werden
Seed, Initialisierung oder Laufstruktur nicht auf ein anderes Archiv
uebertragen. Die ZIPs werden nicht entpackt, es wird nichts geschrieben und
keine Simulation gestartet.

## Archivbefund

Die sieben Archive sind lesbar und enthalten zusammen 165 Eintraege. Davon
sind 164 `IMSV*.DAT`-Ausgaben. Genau ein weiterer Eintrag ist vorhanden:
`VDEFMD5A.ZIP/IMSREPOR.DAT`. Separate Modell-, Definitions- oder
Parameterdateien sind in keinem der sieben Archive enthalten.

| Archiv | Archiv-SHA-256 | Eintraege | Ausgaben | Begleiter | Metadatenstatus |
| --- | --- | ---: | ---: | ---: | --- |
| `VDEFMD5A.ZIP` | `ade1f91a4b6cf7b26df38ce82f45c07b3fad1d64738f20ec7ab09bc64a28ddb0` | 30 | 29 | 1 | `direct_run_report` |
| `VDEFMOD5.ZIP` | `61fe4268ceebb6f3af1288b51aac360744bc121fa48335f0f79ee6b09239f5b8` | 5 | 5 | 0 | `metadata_absent` |
| `ZINS000.ZIP` | `5839ddea724949e9e1065a4d9f1ac3f27e97c2ed444d819f466f3cd4ee97f190` | 29 | 29 | 0 | `metadata_absent` |
| `ZINS030.ZIP` | `a5caa7ca12fdece28991e7cf32b5768cdaed3a0cbf31a759506b05ab0fc05634` | 29 | 29 | 0 | `metadata_absent` |
| `WVEMOD1.ZIP` | `444c0bddf7a0dcee21e963167c36da56ed9b0a33172487914adf51e2a91206d9` | 24 | 24 | 0 | `metadata_absent` |
| `WVEMOD2.ZIP` | `d17f399139ced0c85db424aac46b585ee40f2d98eb84da43b3d5790d445c3eae` | 24 | 24 | 0 | `metadata_absent` |
| `WVEMOD3.ZIP` | `86a07aace01c47751a3320de580bbb66714ae6d28a74bafce876e14b6470f47b` | 24 | 24 | 0 | `metadata_absent` |

Die Archive und ihre Inhalte bleiben unter `incomming/` unversioniert. Diese
Notiz fixiert nur den lokal reproduzierbaren Befund und die Hashbezüge.

## Direkter Reportbefund

Der einzige Laufbericht hat den Mitgliedshash
`03c3ce742cfea6c5eef27f1434924b5969093a83e2401166ed5ffce181d2e133`,
72.892 Bytes und den ZIP-Zeitstempel `1995-09-07T13:26:48`. Folgende Werte
sind direkt im Text belegt:

| Feld | Beobachteter Wert |
| --- | --- |
| Version | `IMS Version MSDOS v1.0` |
| Kompiliertext | `Sep  7 1995 13:22:59` |
| Seed | `5616` |
| VU-Allokation | 25 VU, 199.200 Bytes |
| VN-Allokation | 200 VN, 1.923.200 Bytes |
| `Myinitbv` | `[1,1]` |
| `Newinibv` | zweimal `[1,1]` |
| `Frmdinf` | 300 Aufrufe, stets erstes Argument 1, 25 aktive VU und 200 aktive VN |
| `Agrsich` | 300 Aufrufe, stets erstes Argument 10 |
| beobachtete Periodensequenzen | dreimal zusammenhaengend `1-100` |
| Speicherfreigabe | 25 VU- und 200 VN-Eintraege, letzter Allokationswert 0 Bytes |
| Abschlussmarke | vorhanden |

Die 300 `Frmdinf`-/`Agrsich`-Paare werden nicht als ein fortlaufender
300-Perioden-Horizont ausgegeben. Der Report setzt die Periodennummer nach 100
zweimal auf 1 zurueck und schreibt davor jeweils `Newinibv:[1,1]`. PR 90
bezeichnet diese Struktur deshalb neutral als drei beobachtete Sequenzen. Ob
dies fachlich drei Laeufe, Wiederholungen oder eine andere historische
Steuerungsstruktur sind, wird ohne weiteren Beleg nicht behauptet.

## Grenze zu den Referenzschichten

Der Report gehoert ausschliesslich zu `VDEFMD5A.ZIP`. Die in PR 89
ausgewaehlten Referenzquellen liegen dagegen in anderen Schichten:

- `IMSVNR01.DAT` und `IMSVNR02.DAT` sind `ZINS000.ZIP` zugeordnet;
- elf vollstaendige Referenzen und das VU14-Fenster sind `WVEMOD1.ZIP`
  zugeordnet;
- vier belegte `IMSVUSK1.DAT`-Fenster stammen aus `WVEMOD2.ZIP`;
- `VUSK1L4.DAT` bleibt gegen die sieben Archive divergent.

Keines dieser drei Quellarchive enthaelt einen eigenen Laufbericht oder eine
separate Modell-, Definitions- oder Parameterdatei. Seed `5616`, die drei
beobachteten Sequenzen und die Initialisierungswerte duerfen daher nicht als
Laufmetadaten dieser Referenzen verwendet werden. Der Befund belegt weder
einen gemeinsamen historischen Lauf noch Archivfamilienkohaerenz,
Vollgleichheit oder Produktionsfreigabe.

## Reproduzierbarer Aufruf und Tests

Der lokale Bericht wird ohne Ausgabedatei erzeugt:

```powershell
$env:PYTHONPATH = "python_port"
python -m ims.api.historical_archive_run_metadata --root .
```

Die automatisierten Tests verwenden ausschliesslich synthetische ZIPs. Sie
pruefen direkte Reportfelder, wiederholte Periodensequenzen, Begleitdatei-
Kategorien, fehlende archivlokale Metadaten, fehlende Pflichtfelder,
abweichende Aufruffolgen, doppelte Reportnamen und defekte Archive. Die Tests
benoetigen `incomming/` nicht.

## Naechster Schritt

PR 91 hat fuer jedes der 19 Referenzziele den expliziten
Referenzschicht-Vertrag eingefroren. Der PR-90-Befund erlaubt fuer die
ausgewaehlten Quellen weiterhin keine Klasse `same_run_proven`;
`VUSK1L4.DAT` bleibt als eigene ungeklaerte Direktreferenz isoliert. Das Tor
`go_separate_reference_tests` erlaubt PR 92, den Horizontvertrag
vorzubereiten. Das Legacy-Bundle wird erst nach einem getrennten, belegten
Entscheid geaendert; PR 91 hat keine solche Aenderung vorgenommen. Ein
gemeinsamer historischer Lauf bleibt weiterhin unbelegt.
