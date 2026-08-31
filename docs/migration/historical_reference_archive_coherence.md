# Referenz-zu-Archiv-Kohaerenz

Stand: 2026-08-31
Vertrag: `pr89-v1`

## Ziel und Methode

Der read-only Bericht `ims.api.historical_reference_archive_coherence`
vergleicht die 19 versionierten Kernreferenzen mit allen gleichnamigen
Eintraegen der sieben in PR 88 inventarisierten ZIP-Archive. Es werden zwei
Vergleichsarten getrennt ausgewiesen:

- `byte_exact`: ausgewaehlter Inhalt und Referenz sind bytegleich;
- `token_normalized`: die UTF-8-/ASCII-Tokensequenz ist nach reiner
  Whitespace-Normalisierung gleich, die Bytes sind es nicht.

Ein Vergleich ueber das vollstaendige Periodenfenster des Archiveintrags wird
als `exact_archive_member` klassifiziert. Eine exakte Teilmenge nach den
deklarierten Perioden wird als `exact_window_slice` klassifiziert. Ein
gleichnamiger Eintrag ohne Inhaltsgleichheit ist `same_name_divergent`; ohne
Kandidat bleibt ein Ziel `unresolved`.

Die Archive werden nicht entpackt. Der Bericht veraendert weder
`incomming/` noch das Legacy-Bundle und startet keine Ausfuehrung oder
Simulation. Inhaltskohaerenz ist kein Nachweis eines gemeinsamen historischen
Laufs, Seeds, Schedulers oder einer RNG-Ziehfolge.

## Gesamtergebnis

- 19 Referenzziele und 92 gleichnamige Archivkandidaten wurden geprueft.
- 13 Ziele sind `exact_archive_member`, jeweils mit `byte_exact`.
- 5 Ziele sind `exact_window_slice`, jeweils mit `token_normalized`.
- `VUSK1L4.DAT` ist als einziges Ziel `same_name_divergent`.
- Kein Ziel ist `unresolved`; der Bericht hat Status `ok`.

## Zielbefund

| Referenz | SHA-256 | Fenster | Zeilen | Klasse | Ausgewaehltes Archiv | Basis |
| --- | --- | --- | ---: | --- | --- | --- |
| `VU14L1.DAT` | `20b8b082dbdc4ce187c18a50d2c9f8ed3e5a275a2456ce25300696714a686f8e` | 1-100 | 100 | `exact_window_slice` | `WVEMOD1.ZIP/IMSVU014.DAT` | `token_normalized` |
| `VUSK1L1.DAT` | `aa9fd4e13073231fc0b8286fe36ca63ee475f35365652161c675c3d592c10568` | 401-500 | 100 | `exact_window_slice` | `WVEMOD2.ZIP/IMSVUSK1.DAT` | `token_normalized` |
| `VUSK1L2.DAT` | `d77fab22e32c73ecaff95fc46ef43e9efb7548af6f882d9905983ddb28bbb38d` | 301-400 | 100 | `exact_window_slice` | `WVEMOD2.ZIP/IMSVUSK1.DAT` | `token_normalized` |
| `VUSK1L3.DAT` | `92a2b12f0e5715201b7af28572c5a2a912bc634d49a9038e2790000298c4d25e` | 201-300 | 100 | `exact_window_slice` | `WVEMOD2.ZIP/IMSVUSK1.DAT` | `token_normalized` |
| `VUSK1L4.DAT` | `dbb38cf052a7bf1260f716e65642269062ddefb0ffc2348bfe9c9023c5ab27e4` | 101-200 | 100 | `same_name_divergent` | kein exakter Kandidat | `none` |
| `VUSK1L5.DAT` | `0d7f02f992d418baef0c259f8e6cab59bde452e34cd794aed1876dc52da6feec` | 1-100 | 100 | `exact_window_slice` | `WVEMOD2.ZIP/IMSVUSK1.DAT` | `token_normalized` |
| `IMSVNSK1.DAT` | `37189ca9058a0817f4623767a5758ccd2d870d1518f2f443a941d33c91929c88` | 1-500 | 500 | `exact_archive_member` | `WVEMOD1.ZIP/IMSVNSK1.DAT` | `byte_exact` |
| `IMSVNR01.DAT` | `79cff0463c0bd9489459fd92694e4650b59c0a52c0703d879e5142aeaea4b9c9` | 1-300 | 300 | `exact_archive_member` | `ZINS000.ZIP/IMSVNR01.DAT` | `byte_exact` |
| `IMSVNR02.DAT` | `695ca328675b1eb46bcb6e15c0e8c41ce78a48c98ac5216c7644423ced5a4eec` | 1-300 | 300 | `exact_archive_member` | `ZINS000.ZIP/IMSVNR02.DAT` | `byte_exact` |
| `IMSVNR03.DAT` | `8491bec0736fbf4fb95c9b7649338d0142207265024ec5c5e9c3e649bd49ffd4` | 1-500 | 500 | `exact_archive_member` | `WVEMOD1.ZIP/IMSVNR03.DAT` | `byte_exact` |
| `IMSVNR04.DAT` | `16bdf0b4329ec414990aaaec2ece0d48a8001b43d4a6bb8210625cfb56f3fce4` | 1-500 | 500 | `exact_archive_member` | `WVEMOD1.ZIP/IMSVNR04.DAT` | `byte_exact` |
| `IMSVNR05.DAT` | `80a83f47de5451cb9b660025ca3c0e511aa268602b0ced2301f82b4467549dfa` | 1-500 | 500 | `exact_archive_member` | `WVEMOD1.ZIP/IMSVNR05.DAT` | `byte_exact` |
| `IMSVNR06.DAT` | `1d18b3ce471f4b19f525956650b414e1fcfb8b93854eaaf60c8316b18b1eced0` | 1-500 | 500 | `exact_archive_member` | `WVEMOD1.ZIP/IMSVNR06.DAT` | `byte_exact` |
| `IMSVNVK1.DAT` | `bf21672275f325bc10584f9241827bdaf5288e471af23c3db94bd8fbfd308161` | 1-500 | 500 | `exact_archive_member` | `WVEMOD1.ZIP/IMSVNVK1.DAT` | `byte_exact` |
| `IMSVNVK2.DAT` | `cface3a3a521923c1b237985166930ef796872ada7d52265af3ab85b67b1cdf1` | 1-500 | 500 | `exact_archive_member` | `WVEMOD1.ZIP/IMSVNVK2.DAT` | `byte_exact` |
| `IMSVNVK3.DAT` | `766d5da11af81b6ff8fa98801f77ef0726a8b0237df27a090160490e831b93d4` | 1-500 | 500 | `exact_archive_member` | `WVEMOD1.ZIP/IMSVNVK3.DAT` | `byte_exact` |
| `IMSVUVK1.DAT` | `49ed53daaf6d13a9f850ed5628f79e4d9fb5e73b61359009159517ef35cb6e0f` | 1-500 | 500 | `exact_archive_member` | `WVEMOD1.ZIP/IMSVUVK1.DAT` | `byte_exact` |
| `IMSVUVK2.DAT` | `619fc2e5624ab575c9b73ab0891ab88b1883317efbab262b726f1237f0cc3b3d` | 1-500 | 500 | `exact_archive_member` | `WVEMOD1.ZIP/IMSVUVK2.DAT` | `byte_exact` |
| `IMSVUVK3.DAT` | `ed280b96d3f6daf4cf64de88c8de17b79b595d7ec928f8ca2df0ef0635a595bc` | 1-500 | 500 | `exact_archive_member` | `WVEMOD1.ZIP/IMSVUVK3.DAT` | `byte_exact` |

`IMSVNSK1.DAT` wird hier als ganze versionierte 500-Zeilen-Datei geprueft.
Der bestehende Produktionskorpus nutzt davon weiterhin bewusst nur das Fenster
1-100; PR 89 aendert diese Validierungsgrenze nicht.

## Kandidatenmatrix

Legende: `E/B` = `exact_archive_member`/`byte_exact`, `W/T` =
`exact_window_slice`/`token_normalized`, `D` =
`same_name_divergent`, `-` = kein gleichnamiger Eintrag.

| Referenz | VDEFMD5A | VDEFMOD5 | ZINS000 | ZINS030 | WVEMOD1 | WVEMOD2 | WVEMOD3 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `VU14L1.DAT` | D | - | D | D | W/T | D | D |
| `VUSK1L1.DAT` | D | D | D | D | D | W/T | D |
| `VUSK1L2.DAT` | D | D | D | D | D | W/T | D |
| `VUSK1L3.DAT` | D | D | D | D | D | W/T | D |
| `VUSK1L4.DAT` | D | D | D | D | D | D | D |
| `VUSK1L5.DAT` | D | D | D | D | D | W/T | D |
| `IMSVNSK1.DAT` | D | D | D | D | E/B | D | D |
| `IMSVNR01.DAT` | D | D | E/B | D | D | D | D |
| `IMSVNR02.DAT` | D | D | E/B | D | D | D | D |
| `IMSVNR03.DAT` | - | - | - | - | E/B | D | D |
| `IMSVNR04.DAT` | - | - | - | - | E/B | D | D |
| `IMSVNR05.DAT` | - | - | - | - | E/B | D | D |
| `IMSVNR06.DAT` | - | - | - | - | E/B | D | D |
| `IMSVNVK1.DAT` | - | - | - | - | E/B | D | D |
| `IMSVNVK2.DAT` | - | - | - | - | E/B | D | D |
| `IMSVNVK3.DAT` | - | - | - | - | E/B | D | D |
| `IMSVUVK1.DAT` | - | - | - | - | E/B | D | D |
| `IMSVUVK2.DAT` | - | - | - | - | E/B | D | D |
| `IMSVUVK3.DAT` | - | - | - | - | E/B | D | D |

## Einordnung der Schichten

- `IMSVNR01.DAT` und `IMSVNR02.DAT` sind bytegleich mit `ZINS000.ZIP`.
- `IMSVNSK1.DAT`, `IMSVNR03.DAT` bis `IMSVNR06.DAT`, die drei VN-Klassen
  und die drei VU-Klassen sind bytegleich mit `WVEMOD1.ZIP`.
- `VU14L1.DAT` entspricht tokennormalisiert dem Fenster 1-100 aus
  `WVEMOD1.ZIP/IMSVU014.DAT`.
- `VUSK1L5`, `VUSK1L3`, `VUSK1L2` und `VUSK1L1` entsprechen den Fenstern
  1-100, 201-300, 301-400 und 401-500 aus
  `WVEMOD2.ZIP/IMSVUSK1.DAT`.
- `VUSK1L4.DAT` fuer 101-200 entspricht keinem der sieben bekannten
  `IMSVUSK1.DAT`-Eintraege.

Die fuenf `VUSK1L1-5`-Dateien bleiben fachlich Zeitfenster derselben
Exportidentitaet `IMSVUSK1.DAT`, desselben `SK1/all`-Aggregats und derselben
Aggregatstufe IV. Der Befund zeigt jedoch, dass die aktuell versionierten
Fenster nicht als ein byte- oder tokenkohaerenter 500-Perioden-Archiveintrag
belegt sind. Diese fehlende Quellkohaerenz darf nicht als neue Aggregatebene
oder als Beleg eines gemeinsamen Laufs umgedeutet werden.

## Naechster Schritt

PR 90 hat `IMSREPOR.DAT` und alle archivlokalen Begleitdateien ausgewertet.
Der einzige direkte Bericht gehoert zu `VDEFMD5A.ZIP`; `ZINS000`, `WVEMOD1`
und `WVEMOD2` enthalten keinen eigenen Beleg. Seed oder Laufparameter werden
nicht uebertragen. PR 91 hat fuer alle 19 Ziele vier getrennte Schichten und
das Tor `go_separate_reference_tests` eingefroren. PR 92 bereitet als
naechstes den Horizontvertrag 100/300/500 vor, noch ohne Vollvergleich.
