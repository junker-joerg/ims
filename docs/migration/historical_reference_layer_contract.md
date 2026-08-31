# Historischer Referenzschicht-Vertrag

Stand: 2026-08-31
Vertrag: `pr91-v1`

## Ziel und Methode

Der read-only Bericht `ims.api.historical_reference_layer_contract` friert
fuer alle 19 versionierten Referenzziele die Quellschicht, den Hashbezug, die
Koharenzklasse und die zulaessige Aussage ein. Er baut auf dem Archivvergleich
`pr89-v1` und der archivlokalen Laufmetadatenauswertung `pr90-v1` auf.

Der Bericht liest nur die versionierten Referenzdateien. Die Quellarchive
werden nicht erneut geoeffnet, `incomming/` wird nicht benoetigt und das
Legacy-Bundle bleibt unveraendert. Es wird nichts geschrieben, keine
Ausfuehrung gestartet und keine Simulation durchgefuehrt.

Die eingefrorenen Referenz-SHA-256-Werte bleiben unveraendert massgeblich.
Bei der Pruefung werden ausschliesslich die inhaltlich gleichen LF- und
CRLF-Checkout-Varianten akzeptiert. Damit bleibt derselbe historische Text in
Windows- und LF-Checkouts identisch gebunden; andere Inhaltsaenderungen
bleiben Hashfehler. Archiv- und Quellmitglied-Hashes werden unveraendert als
rohe PR-89-/PR-90-Evidenz uebernommen.

## Entscheidung

Der Vertrag prueft 19 von 19 Zielen und vier getrennte Referenzschichten. Der
Status ist bewusst `warning`:

- 18 Ziele sind `archive_family_only`;
- kein Ziel ist `same_run_proven`;
- `VUSK1L4.DAT` bleibt als einziges Ziel
  `contradictory_or_unresolved`, ist aber als eigene Schicht separiert;
- der Gesamtkorpus ist `mixed_reference_layers`;
- das Tor lautet `go_separate_reference_tests`;
- `full_window_phase_allowed = true` gilt ausschliesslich fuer getrennte
  Referenztests.

Damit durfte PR 92 den technischen Horizontvertrag vorbereiten. Nicht erlaubt
sind weiterhin eine Zusammenfassung der vier Schichten zu einem historischen
Lauf, eine Seed-Uebertragung, eine historische Vollgleichheitsbehauptung oder
eine Produktionsfreigabe.

## Schichten

| Layer-ID | Quelle | SHA-256 | Ziele | Laufmetadaten | Klasse | Zulaessige Aussage |
| --- | --- | --- | ---: | --- | --- | --- |
| `zins000_archive` | `incomming/IMS.DAT/VDEFMOD5/ZINS000.ZIP` | `5839ddea724949e9e1065a4d9f1ac3f27e97c2ed444d819f466f3cd4ee97f190` | 2 | `metadata_absent` | `archive_family_only` | `archive_content_match_only` |
| `wvemod1_archive` | `incomming/IMS.DAT/WVEMOD1.ZIP` | `444c0bddf7a0dcee21e963167c36da56ed9b0a33172487914adf51e2a91206d9` | 12 | `metadata_absent` | `archive_family_only` | `archive_content_match_only` |
| `wvemod2_archive` | `incomming/IMS.DAT/WVEMOD2.ZIP` | `d17f399139ced0c85db424aac46b585ee40f2d98eb84da43b3d5790d445c3eae` | 4 | `metadata_absent` | `archive_family_only` | `archive_content_match_only` |
| `vusk1l4_direct_04410ef` | versionierte Direktreferenz aus Commit `04410ef` | `dbb38cf052a7bf1260f716e65642269062ddefb0ffc2348bfe9c9023c5ab27e4` | 1 | `not_available` | `contradictory_or_unresolved` | `versioned_fixture_regression_only` |

Ein gemeinsamer ZIP-Container belegt fuer die ersten drei Schichten nur den
Archivkontext. Da alle drei Archive keinen eigenen Laufbericht enthalten,
bleiben Seed, Scheduler-, RNG- und konkrete Laufidentitaet offen.

## Zielvertrag

| Referenz | Referenz-SHA-256 | Layer | Quellmitglied | Archivvergleich | Basis | Fenster |
| --- | --- | --- | --- | --- | --- | --- |
| `VU14L1.DAT` | `20b8b082dbdc4ce187c18a50d2c9f8ed3e5a275a2456ce25300696714a686f8e` | `wvemod1_archive` | `IMSVU014.DAT` | `exact_window_slice` | `token_normalized` | 1-100 |
| `VUSK1L1.DAT` | `aa9fd4e13073231fc0b8286fe36ca63ee475f35365652161c675c3d592c10568` | `wvemod2_archive` | `IMSVUSK1.DAT` | `exact_window_slice` | `token_normalized` | 401-500 |
| `VUSK1L2.DAT` | `d77fab22e32c73ecaff95fc46ef43e9efb7548af6f882d9905983ddb28bbb38d` | `wvemod2_archive` | `IMSVUSK1.DAT` | `exact_window_slice` | `token_normalized` | 301-400 |
| `VUSK1L3.DAT` | `92a2b12f0e5715201b7af28572c5a2a912bc634d49a9038e2790000298c4d25e` | `wvemod2_archive` | `IMSVUSK1.DAT` | `exact_window_slice` | `token_normalized` | 201-300 |
| `VUSK1L4.DAT` | `dbb38cf052a7bf1260f716e65642269062ddefb0ffc2348bfe9c9023c5ab27e4` | `vusk1l4_direct_04410ef` | versionierte Direktreferenz | `same_name_divergent` | `versioned_reference_sha256` | 101-200 |
| `VUSK1L5.DAT` | `0d7f02f992d418baef0c259f8e6cab59bde452e34cd794aed1876dc52da6feec` | `wvemod2_archive` | `IMSVUSK1.DAT` | `exact_window_slice` | `token_normalized` | 1-100 |
| `IMSVNSK1.DAT` | `37189ca9058a0817f4623767a5758ccd2d870d1518f2f443a941d33c91929c88` | `wvemod1_archive` | `IMSVNSK1.DAT` | `exact_archive_member` | `byte_exact` | 1-500 |
| `IMSVNR01.DAT` | `79cff0463c0bd9489459fd92694e4650b59c0a52c0703d879e5142aeaea4b9c9` | `zins000_archive` | `IMSVNR01.DAT` | `exact_archive_member` | `byte_exact` | 1-300 |
| `IMSVNR02.DAT` | `695ca328675b1eb46bcb6e15c0e8c41ce78a48c98ac5216c7644423ced5a4eec` | `zins000_archive` | `IMSVNR02.DAT` | `exact_archive_member` | `byte_exact` | 1-300 |
| `IMSVNR03.DAT` | `8491bec0736fbf4fb95c9b7649338d0142207265024ec5c5e9c3e649bd49ffd4` | `wvemod1_archive` | `IMSVNR03.DAT` | `exact_archive_member` | `byte_exact` | 1-500 |
| `IMSVNR04.DAT` | `16bdf0b4329ec414990aaaec2ece0d48a8001b43d4a6bb8210625cfb56f3fce4` | `wvemod1_archive` | `IMSVNR04.DAT` | `exact_archive_member` | `byte_exact` | 1-500 |
| `IMSVNR05.DAT` | `80a83f47de5451cb9b660025ca3c0e511aa268602b0ced2301f82b4467549dfa` | `wvemod1_archive` | `IMSVNR05.DAT` | `exact_archive_member` | `byte_exact` | 1-500 |
| `IMSVNR06.DAT` | `1d18b3ce471f4b19f525956650b414e1fcfb8b93854eaaf60c8316b18b1eced0` | `wvemod1_archive` | `IMSVNR06.DAT` | `exact_archive_member` | `byte_exact` | 1-500 |
| `IMSVNVK1.DAT` | `bf21672275f325bc10584f9241827bdaf5288e471af23c3db94bd8fbfd308161` | `wvemod1_archive` | `IMSVNVK1.DAT` | `exact_archive_member` | `byte_exact` | 1-500 |
| `IMSVNVK2.DAT` | `cface3a3a521923c1b237985166930ef796872ada7d52265af3ab85b67b1cdf1` | `wvemod1_archive` | `IMSVNVK2.DAT` | `exact_archive_member` | `byte_exact` | 1-500 |
| `IMSVNVK3.DAT` | `766d5da11af81b6ff8fa98801f77ef0726a8b0237df27a090160490e831b93d4` | `wvemod1_archive` | `IMSVNVK3.DAT` | `exact_archive_member` | `byte_exact` | 1-500 |
| `IMSVUVK1.DAT` | `49ed53daaf6d13a9f850ed5628f79e4d9fb5e73b61359009159517ef35cb6e0f` | `wvemod1_archive` | `IMSVUVK1.DAT` | `exact_archive_member` | `byte_exact` | 1-500 |
| `IMSVUVK2.DAT` | `619fc2e5624ab575c9b73ab0891ab88b1883317efbab262b726f1237f0cc3b3d` | `wvemod1_archive` | `IMSVUVK2.DAT` | `exact_archive_member` | `byte_exact` | 1-500 |
| `IMSVUVK3.DAT` | `ed280b96d3f6daf4cf64de88c8de17b79b595d7ec928f8ca2df0ef0635a595bc` | `wvemod1_archive` | `IMSVUVK3.DAT` | `exact_archive_member` | `byte_exact` | 1-500 |

Alle fuenf `VUSK1L1-5`-Ziele bleiben Zeitfenster derselben Exportidentitaet
`IMSVUSK1.DAT`, desselben `SK1/all`-Aggregats und derselben Aggregatstufe IV.
Die Quellschichten sind trotzdem nicht zu einer koharenten historischen
500-Perioden-Datei zusammengefuehrt.

## Sondergrenze VUSK1L4

Die versionierte `VUSK1L4.DAT` wurde in Commit `04410ef` als direkte
Testreferenz aufgenommen. Ihr SHA-256 ist
`dbb38cf052a7bf1260f716e65642269062ddefb0ffc2348bfe9c9023c5ab27e4`.
Der heutige direkte Kandidat unter `incomming/IMS.DAT/VUSK1L4.DAT` hat dagegen
SHA-256
`4ec1473063895eb5bad6e4bf5d9cc5f1856f94166070a8d28ad07356815357b7`.
PR 89 hat ausserdem gegen alle sieben `IMSVUSK1.DAT`-Archiveintraege
`same_name_divergent` festgestellt.

Darum bleibt der historische Lauf- und Archivursprung offen. Die Datei darf
als stabile versionierte Fixture-Regression fuer Perioden 101-200 verwendet
werden. Sie darf die Archivquelle der anderen vier Fenster nicht erben und
keine koharente historische 500-Perioden-Reihe belegen. Eine spaetere bessere
Quelle darf nur in einem eigenen Review-PR mit neuem Hash- und Fensterbeleg
entschieden werden.

## Folgen fuer die Vollfensterphase

PR 93 bis PR 101 duerfen unter folgenden Grenzen fortfahren; PR 93 ist
inzwischen unter genau diesen Grenzen umgesetzt:

1. Jede Auswertung traegt `layer_id` und zulaessige Aussage weiter.
2. Ergebnisse verschiedener Layer werden getrennt berichtet.
3. PR 97 vergleicht die berechnete `imsvusk1.dat` gegen fuenf einzelne
   Fenster; es behauptet keine gemeinsame historische Archivquelle.
4. `VUSK1L4.DAT` zaehlt nur als `versioned_fixture_regression_only`.
5. Keine Layerkombination darf `same_run_proven`, historische Vollgleichheit
   oder Produktionsfreigabe setzen.

## Reproduzierbarer Aufruf

```powershell
$env:PYTHONPATH = "python_port"
python -m ims.api.historical_reference_layer_contract --root .
```

Der Aufruf benoetigt nur versionierte Dateien und liefert wegen der offenen
historischen Herkunft von `VUSK1L4.DAT` erwartungsgemaess Status `warning` mit
Exitcode 0.

## Naechster Schritt

PR 92 hat den Horizontvertrag 100/300/500 als `pr92-v1` umgesetzt. Er stellt
den exakten Prefix-Pruefer bereit und laesst die vier Referenzschichten
durchgehend getrennt. Noch wird kein 300-/500-Vollvergleich ausgefuehrt.
PR93 hat die zwei vollstaendigen 100er-Tabellen streng an den
Produktionskorpusbericht gebunden. PR94 erweitert als naechstes den
kontrollierten Zustand bis Periode 300 und muss den Prefix 1-100 stabil halten.
