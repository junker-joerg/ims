# Historisches Archivmanifest

Stand: 2026-08-31
Vertrag: `pr88-v1`

## Ziel und Grenze

Der read-only Bericht `ims.api.historical_archive_manifest` inventarisiert die
sieben bekannten lokalen ZIP-Archive. Er liest Archive und Eintraege direkt
mit `zipfile`, berechnet SHA-256-Hashes im Speicher und extrahiert keine Datei.
Die Roharchive unter `incomming/` bleiben unversioniert.

Fuer die 15 Kernexportnamen werden Eintragspfad, SHA-256, unkomprimierte
Groesse, ZIP-Zeitstempel, erwarteter VU-/VN-Header, Zeilenzahl und
Periodenfenster erfasst. ZIP-Zeitstempel enthalten keine Zeitzone und werden
daher nur als archivierte Metadaten, nicht als belastbare Laufzeit interpretiert.

Der Scan vergleicht noch keine versionierte Referenz mit einem Archiveintrag,
wertet keine Begleitdatei inhaltlich aus und ordnet keine Archive demselben
historischen Lauf zu. Er behauptet weder historische Vollgleichheit noch eine
Produktionsfreigabe.

## Ergebnis

- Status: `ok`, sieben von sieben Archiven lesbar, keine Strukturfehler.
- 165 Dateieintraege, alle mit Endung `.DAT`.
- 64 Archiveintraege treffen einen der 15 Kernexportnamen.
- `WVEMOD1.ZIP`, `WVEMOD2.ZIP` und `WVEMOD3.ZIP` enthalten jeweils alle
  15 Kernexportnamen.
- Alle 64 Kerneintraege haben den erwarteten VU- beziehungsweise VN-Header,
  numerische Zeilen und ein streng aufsteigendes, lueckenloses Periodenfenster.
- Ein Metadatenkandidat wurde nur ueber den Dateinamen erkannt:
  `VDEFMD5A.ZIP/IMSREPOR.DAT`. PR 90 hat ihn anschliessend ausschliesslich
  archivlokal ausgewertet.

Erwartete Header:

- VU: `#t Pr1 Wa1 Rs1 Vn1 Sa1 Sh1 Pr2 Wa2 Rs2 Vn2 Sa2 Sh2`
- VN: `#t Vu1 Vs1 Vp1 Ev1 Sh1 Vu2 Vs2 Vp2 Ev2 Sh2 Vm`

## Archive

| Archiv | SHA-256 | Bytes | Eintraege | Kern |
| --- | --- | ---: | ---: | ---: |
| `VDEFMD5A.ZIP` | `ade1f91a4b6cf7b26df38ce82f45c07b3fad1d64738f20ec7ab09bc64a28ddb0` | 179.731 | 30 | 5 |
| `VDEFMOD5.ZIP` | `61fe4268ceebb6f3af1288b51aac360744bc121fa48335f0f79ee6b09239f5b8` | 249.535 | 5 | 4 |
| `ZINS000.ZIP` | `5839ddea724949e9e1065a4d9f1ac3f27e97c2ed444d819f466f3cd4ee97f190` | 172.416 | 29 | 5 |
| `ZINS030.ZIP` | `a5caa7ca12fdece28991e7cf32b5768cdaed3a0cbf31a759506b05ab0fc05634` | 175.849 | 29 | 5 |
| `WVEMOD1.ZIP` | `444c0bddf7a0dcee21e963167c36da56ed9b0a33172487914adf51e2a91206d9` | 261.510 | 24 | 15 |
| `WVEMOD2.ZIP` | `d17f399139ced0c85db424aac46b585ee40f2d98eb84da43b3d5790d445c3eae` | 262.477 | 24 | 15 |
| `WVEMOD3.ZIP` | `86a07aace01c47751a3320de580bbb66714ae6d28a74bafce876e14b6470f47b` | 1.506.069 | 24 | 15 |

## Kerneintraege

Alle aufgefuehrten Eintraege liegen an der ZIP-Wurzel; die Spalte `Eintrag`
ist damit zugleich der vollstaendige Eintragspfad. `Header` bezeichnet den
erfolgreich geprueften VU- oder VN-Vertrag.

| Archiv | Eintrag | SHA-256 | Bytes | ZIP-Zeitstempel | Header | Zeilen | Fenster |
| --- | --- | --- | ---: | --- | --- | ---: | --- |
| `VDEFMD5A.ZIP` | `IMSVNR01.DAT` | `3335b7d136da5dde214a8eefc7b80bce254aa2431861944a0d52fafcb0e749a4` | 20.462 | `1995-09-07T13:26:44` | VN | 300 | 1-300 |
| `VDEFMD5A.ZIP` | `IMSVNR02.DAT` | `25c3752e878672d3114626bf9835864fe3d2904148b0ef1367653ae506673504` | 20.462 | `1995-09-07T13:26:44` | VN | 300 | 1-300 |
| `VDEFMD5A.ZIP` | `IMSVNSK1.DAT` | `9287a276931b2fcd93eba32ccc5bdf141859d8ae089415af379843080a47f612` | 20.462 | `1995-09-07T13:26:44` | VN | 300 | 1-300 |
| `VDEFMD5A.ZIP` | `IMSVU014.DAT` | `f1894621282f5152da9bb140983483abfa714ad22d1989b92259459b4c2df83a` | 23.775 | `1995-09-07T13:26:44` | VU | 300 | 1-300 |
| `VDEFMD5A.ZIP` | `IMSVUSK1.DAT` | `5889e90753c6d5cedf0cf1c56c8fec71329f43b3778e5be482382e107f7bc8b3` | 23.475 | `1995-09-07T13:26:44` | VU | 300 | 1-300 |
| `VDEFMOD5.ZIP` | `IMSVNR01.DAT` | `250df337be5a3aa4aedabd2f273e90decd8c2fc957b775d1ffb7238f66696af0` | 204.062 | `1995-09-07T11:28:30` | VN | 3.000 | 1-3000 |
| `VDEFMOD5.ZIP` | `IMSVNR02.DAT` | `699ac03e4709ca2ed53552d99989a24f8828378c56c78ce6fc2fcf5931573fcb` | 204.062 | `1995-09-07T11:28:30` | VN | 3.000 | 1-3000 |
| `VDEFMOD5.ZIP` | `IMSVNSK1.DAT` | `04027dd43ffff3b2f70ace7377c85564f8d149d5ac0a5ebeca6328483bbe6672` | 204.062 | `1995-09-07T11:28:30` | VN | 3.000 | 1-3000 |
| `VDEFMOD5.ZIP` | `IMSVUSK1.DAT` | `33195dc607869a6aa9435742de79f59deb2c60f85f9cae4dd2c701e120e47557` | 234.075 | `1995-09-07T11:28:30` | VU | 3.000 | 1-3000 |
| `ZINS000.ZIP` | `IMSVNR01.DAT` | `79cff0463c0bd9489459fd92694e4650b59c0a52c0703d879e5142aeaea4b9c9` | 20.462 | `1995-09-08T11:53:06` | VN | 300 | 1-300 |
| `ZINS000.ZIP` | `IMSVNR02.DAT` | `695ca328675b1eb46bcb6e15c0e8c41ce78a48c98ac5216c7644423ced5a4eec` | 20.462 | `1995-09-08T11:53:06` | VN | 300 | 1-300 |
| `ZINS000.ZIP` | `IMSVNSK1.DAT` | `48dbca3ec7b09dc3f05009c29171bc24140e50341b1b7e6dd46a2d054bb0dd1b` | 20.462 | `1995-09-08T11:53:06` | VN | 300 | 1-300 |
| `ZINS000.ZIP` | `IMSVU014.DAT` | `0276eab7b1f80dfc39773eb0e5a4a5df02b69b140792be9f810baa222e8ce828` | 23.775 | `1995-09-08T11:53:06` | VU | 300 | 1-300 |
| `ZINS000.ZIP` | `IMSVUSK1.DAT` | `dc066d624c443fc165b0fb83481083dae33d823bd8a3a20d934adb4bf5426b2a` | 23.475 | `1995-09-08T11:53:06` | VU | 300 | 1-300 |
| `ZINS030.ZIP` | `IMSVNR01.DAT` | `5d5cdb6ad9e1f62281d50f59afdbb38e3a20bd2cc815f4b1f0dcaa428a452880` | 20.462 | `1995-09-08T11:51:02` | VN | 300 | 1-300 |
| `ZINS030.ZIP` | `IMSVNR02.DAT` | `62e246806cd01e06666d35a39503e667785be8261a4463ba29600ff763c804f0` | 20.462 | `1995-09-08T11:51:02` | VN | 300 | 1-300 |
| `ZINS030.ZIP` | `IMSVNSK1.DAT` | `a6652f200ce9fc089bf30c30f6f601de059d3cd248d4a19babfdc3efaecfd886` | 20.462 | `1995-09-08T11:51:02` | VN | 300 | 1-300 |
| `ZINS030.ZIP` | `IMSVU014.DAT` | `f706bc9c566fe4e46586a41481a913a7d73d1fe82d66c2b3d706beb8c7d1f77d` | 23.775 | `1995-09-08T11:51:02` | VU | 300 | 1-300 |
| `ZINS030.ZIP` | `IMSVUSK1.DAT` | `f6204591cb961aded51361f961ce292a5573d40e5e8c96072114b7c8ee33f2a9` | 23.475 | `1995-09-08T11:51:02` | VU | 300 | 1-300 |
| `WVEMOD1.ZIP` | `IMSVNR01.DAT` | `7f9864726b3ffda913d673d7aa828447013a617dc26cb8fc2ec6594bf7fd0198` | 34.067 | `1995-07-27T10:34:30` | VN | 500 | 1-500 |
| `WVEMOD1.ZIP` | `IMSVNR02.DAT` | `205617e84ef66f2c8d7f32d82d43cdcfcd3de209b49f19c0cca650e9d3a7b57c` | 34.065 | `1995-07-27T10:34:30` | VN | 500 | 1-500 |
| `WVEMOD1.ZIP` | `IMSVNR03.DAT` | `8491bec0736fbf4fb95c9b7649338d0142207265024ec5c5e9c3e649bd49ffd4` | 34.065 | `1995-07-27T10:34:30` | VN | 500 | 1-500 |
| `WVEMOD1.ZIP` | `IMSVNR04.DAT` | `16bdf0b4329ec414990aaaec2ece0d48a8001b43d4a6bb8210625cfb56f3fce4` | 34.065 | `1995-07-27T10:34:30` | VN | 500 | 1-500 |
| `WVEMOD1.ZIP` | `IMSVNR05.DAT` | `80a83f47de5451cb9b660025ca3c0e511aa268602b0ced2301f82b4467549dfa` | 34.065 | `1995-07-27T10:34:30` | VN | 500 | 1-500 |
| `WVEMOD1.ZIP` | `IMSVNR06.DAT` | `1d18b3ce471f4b19f525956650b414e1fcfb8b93854eaaf60c8316b18b1eced0` | 34.065 | `1995-07-27T10:34:30` | VN | 500 | 1-500 |
| `WVEMOD1.ZIP` | `IMSVNSK1.DAT` | `37189ca9058a0817f4623767a5758ccd2d870d1518f2f443a941d33c91929c88` | 34.065 | `1995-07-27T10:34:30` | VN | 500 | 1-500 |
| `WVEMOD1.ZIP` | `IMSVNVK1.DAT` | `bf21672275f325bc10584f9241827bdaf5288e471af23c3db94bd8fbfd308161` | 34.065 | `1995-07-27T10:34:30` | VN | 500 | 1-500 |
| `WVEMOD1.ZIP` | `IMSVNVK2.DAT` | `cface3a3a521923c1b237985166930ef796872ada7d52265af3ab85b67b1cdf1` | 34.065 | `1995-07-27T10:34:30` | VN | 500 | 1-500 |
| `WVEMOD1.ZIP` | `IMSVNVK3.DAT` | `766d5da11af81b6ff8fa98801f77ef0726a8b0237df27a090160490e831b93d4` | 34.065 | `1995-07-27T10:34:30` | VN | 500 | 1-500 |
| `WVEMOD1.ZIP` | `IMSVU014.DAT` | `050c5668ce6ee3705237b96cc857b4e75a47887897041fbf97a69155a07ba39e` | 40.073 | `1995-07-27T10:34:30` | VU | 500 | 1-500 |
| `WVEMOD1.ZIP` | `IMSVUSK1.DAT` | `d9fa6b7a6611acdc6011b7f874b5c89f9e3eee41f8b82979c114a2fb1466e73e` | 39.073 | `1995-07-27T10:34:30` | VU | 500 | 1-500 |
| `WVEMOD1.ZIP` | `IMSVUVK1.DAT` | `49ed53daaf6d13a9f850ed5628f79e4d9fb5e73b61359009159517ef35cb6e0f` | 39.073 | `1995-07-27T10:34:30` | VU | 500 | 1-500 |
| `WVEMOD1.ZIP` | `IMSVUVK2.DAT` | `619fc2e5624ab575c9b73ab0891ab88b1883317efbab262b726f1237f0cc3b3d` | 39.073 | `1995-07-27T10:34:30` | VU | 500 | 1-500 |
| `WVEMOD1.ZIP` | `IMSVUVK3.DAT` | `ed280b96d3f6daf4cf64de88c8de17b79b595d7ec928f8ca2df0ef0635a595bc` | 39.073 | `1995-07-27T10:34:30` | VU | 500 | 1-500 |
| `WVEMOD2.ZIP` | `IMSVNR01.DAT` | `d1917bbcb2ae16212377629d59e0a0caa1314d61de2f37671dcf0a3ebbe269dd` | 34.069 | `1995-07-27T13:28:38` | VN | 500 | 1-500 |
| `WVEMOD2.ZIP` | `IMSVNR02.DAT` | `997fb5c673d2fa822289e1cb0e757d3b6057e55d3bb2bed2e1e499feceef0015` | 34.065 | `1995-07-27T13:28:38` | VN | 500 | 1-500 |
| `WVEMOD2.ZIP` | `IMSVNR03.DAT` | `1313464ab1ea3f0bd42e27bc51561cd8f7bcbf63895e5a0bd36919e54409f1f7` | 34.065 | `1995-07-27T13:28:38` | VN | 500 | 1-500 |
| `WVEMOD2.ZIP` | `IMSVNR04.DAT` | `25924ab1376bcad2de5833b1eb8e5fdd519e58dd9685dc7e379434a8e886fabb` | 34.065 | `1995-07-27T13:28:38` | VN | 500 | 1-500 |
| `WVEMOD2.ZIP` | `IMSVNR05.DAT` | `829eb4c3375ff9196d30e2794f21bfdf16a674e5dabd690125df2290c4b631e6` | 34.065 | `1995-07-27T13:28:38` | VN | 500 | 1-500 |
| `WVEMOD2.ZIP` | `IMSVNR06.DAT` | `4ef6f9187f7b61162f7018eabf071a2d6cda95ed4cca669abc6d7688e12d2c84` | 34.065 | `1995-07-27T13:28:38` | VN | 500 | 1-500 |
| `WVEMOD2.ZIP` | `IMSVNSK1.DAT` | `5417f1243ecf928eb6b37b67ebbf05617b4707e3c4fe652f624ad5f11ed6dae7` | 34.065 | `1995-07-27T13:28:38` | VN | 500 | 1-500 |
| `WVEMOD2.ZIP` | `IMSVNVK1.DAT` | `df78ee7b957c47282db880d7d242f7ebb298c79df1221e7e703316d8cfefebf0` | 34.065 | `1995-07-27T13:28:38` | VN | 500 | 1-500 |
| `WVEMOD2.ZIP` | `IMSVNVK2.DAT` | `3bc7cc2ba6f1e5d4b4ecbcd428d6678bf34ff99b247a4de7d6b25943a86f74d5` | 34.065 | `1995-07-27T13:28:38` | VN | 500 | 1-500 |
| `WVEMOD2.ZIP` | `IMSVNVK3.DAT` | `a020d71d869bafa184d26ab161c11088fb0428b379200ad5051c7e7f6d39d337` | 34.065 | `1995-07-27T13:28:38` | VN | 500 | 1-500 |
| `WVEMOD2.ZIP` | `IMSVU014.DAT` | `e6f27581fdaf6206f3e61caf53ca00ccbc973c4fb8cdc0d54240249a3c9c3683` | 40.073 | `1995-07-27T13:28:38` | VU | 500 | 1-500 |
| `WVEMOD2.ZIP` | `IMSVUSK1.DAT` | `7ec3ff08a77468ab5106b2daeacf877606f33acf9d299f907a5923fe14f0f001` | 39.073 | `1995-07-27T13:28:38` | VU | 500 | 1-500 |
| `WVEMOD2.ZIP` | `IMSVUVK1.DAT` | `20c621242c779b9fc2800a94fd4cf83b12956833edac1900229db728271d1f3c` | 39.073 | `1995-07-27T13:28:38` | VU | 500 | 1-500 |
| `WVEMOD2.ZIP` | `IMSVUVK2.DAT` | `ba6bc5cf6302401359428ae721a25fbfc0358e74f6f9025fe02e888d9082bbd0` | 39.073 | `1995-07-27T13:28:38` | VU | 500 | 1-500 |
| `WVEMOD2.ZIP` | `IMSVUVK3.DAT` | `2f156adc07ea55f09a9033bbd6aedb8d65b9e1946997846e280f03e49fa7930c` | 39.073 | `1995-07-27T13:28:38` | VU | 500 | 1-500 |
| `WVEMOD3.ZIP` | `IMSVNR01.DAT` | `876a9e35ef907fb2cd9b11bae9ac7329cc2ad196c7cfb3789a02c98845ab5b35` | 204.076 | `1995-07-27T15:03:22` | VN | 3.000 | 1-3000 |
| `WVEMOD3.ZIP` | `IMSVNR02.DAT` | `04516df4a81843a0ad2e69fb612878c9e49a6bc67367fd1a54911c1b0ae1283f` | 204.065 | `1995-07-27T15:03:22` | VN | 3.000 | 1-3000 |
| `WVEMOD3.ZIP` | `IMSVNR03.DAT` | `e09b8f52464c3ce27ca3fca17791dd9282620595d269fce1e70270e3f2403cad` | 204.065 | `1995-07-27T15:03:22` | VN | 3.000 | 1-3000 |
| `WVEMOD3.ZIP` | `IMSVNR04.DAT` | `0394322f5bb5dd44e03badefd9a3341ef2b095f9a9210be1d41b375e6c990936` | 204.065 | `1995-07-27T15:03:22` | VN | 3.000 | 1-3000 |
| `WVEMOD3.ZIP` | `IMSVNR05.DAT` | `0c923cac555dd8a21517034c374fcb9ef43e05d8a8af933c209fac4190b6404e` | 204.065 | `1995-07-27T15:03:22` | VN | 3.000 | 1-3000 |
| `WVEMOD3.ZIP` | `IMSVNR06.DAT` | `daf8038a1c2747b68b8206c8efae0aa2223e6f203d9ba08a0290b080ff60637f` | 204.065 | `1995-07-27T15:03:22` | VN | 3.000 | 1-3000 |
| `WVEMOD3.ZIP` | `IMSVNSK1.DAT` | `309c1fef741a8f3edf55c7a77ea4b2cd34eb1a302ee405c035a315801ffddac6` | 204.065 | `1995-07-27T15:03:24` | VN | 3.000 | 1-3000 |
| `WVEMOD3.ZIP` | `IMSVNVK1.DAT` | `8af024f6e12177c9515c7b43e6e86765c3fd822d5e5ff3ea058b95d1706f5844` | 204.065 | `1995-07-27T15:03:24` | VN | 3.000 | 1-3000 |
| `WVEMOD3.ZIP` | `IMSVNVK2.DAT` | `fbe55d3168d86c16362bda74a67d8609c5d79f006524459e68359d3067d5361f` | 204.065 | `1995-07-27T15:03:24` | VN | 3.000 | 1-3000 |
| `WVEMOD3.ZIP` | `IMSVNVK3.DAT` | `36be285d6ddf06d073b42bc9f0a703e90622b86e2f5a86f059a7ae383fd4ec6f` | 204.065 | `1995-07-27T15:03:24` | VN | 3.000 | 1-3000 |
| `WVEMOD3.ZIP` | `IMSVU014.DAT` | `98e87914bddf480edf7808e19d40348da40c858a8a17619b5e6ea68f92426604` | 240.073 | `1995-07-27T15:03:22` | VU | 3.000 | 1-3000 |
| `WVEMOD3.ZIP` | `IMSVUSK1.DAT` | `88add670c818bd84c2709b7acebdb3d1058f70f6e40d57a6c7d4924468373857` | 234.073 | `1995-07-27T15:03:22` | VU | 3.000 | 1-3000 |
| `WVEMOD3.ZIP` | `IMSVUVK1.DAT` | `0b273ab6da7cb974a1af01d4f3a34906323d1a606a8fd937ba2a3b5f1c1676c2` | 234.073 | `1995-07-27T15:03:22` | VU | 3.000 | 1-3000 |
| `WVEMOD3.ZIP` | `IMSVUVK2.DAT` | `b54c04d0e49fdaadb8100a8845665136fb4321dd6ec24d21c9400fa8a0b08798` | 234.073 | `1995-07-27T15:03:22` | VU | 3.000 | 1-3000 |
| `WVEMOD3.ZIP` | `IMSVUVK3.DAT` | `a58f0d3dc1f63ae057ccdf851ae0fdea2e86ec1b274b472b1116e4c9a78b2a10` | 234.073 | `1995-07-27T15:03:22` | VU | 3.000 | 1-3000 |

## Metadatenkandidat

| Archiv | Eintrag | SHA-256 | Bytes | ZIP-Zeitstempel | Dateinamenmerkmal |
| --- | --- | --- | ---: | --- | --- |
| `VDEFMD5A.ZIP` | `IMSREPOR.DAT` | `03c3ce742cfea6c5eef27f1434924b5969093a83e2401166ed5ffce181d2e133` | 72.892 | `1995-09-07T13:26:48` | `REPOR` |

Die Kandidatensuche ist absichtlich breit und rein namensbasiert. Sie erkennt
die Tokens `REPORT`, `REPOR`, `PROTO`, `LOG`, `RUN`, `PARAM`, `DEF` und `MOD`.
Dass in diesem Bestand nur `IMSREPOR.DAT` trifft, ist noch keine Aussage ueber
Vollstaendigkeit oder inhaltliche Zuordnung der Laufmetadaten.

## Reproduzierbarkeit

Der lokale Bericht kann ohne Ausgabedatei erzeugt werden:

```powershell
$env:PYTHONPATH = "python_port"
python -m ims.api.historical_archive_manifest --root .
```

Die automatisierten Tests bauen kleine synthetische ZIPs auf und pruefen
Hashes, Pfade, Headerfamilien, Zeilen, Periodenluecken, Duplikate, defekte
Archive sowie die Nicht-Extraktionsgrenze. Sie benoetigen `incomming/` nicht.

## Naechster Schritt

PR 89 hat auf den beobachteten Hash- und Fensterdaten eine getrennte
Referenz-zu-Archiv-Koharenzmatrix aufgebaut. PR 90 hat den einzigen direkten
Laufbericht ausschliesslich `VDEFMD5A.ZIP` zugeordnet und sechs Archive ohne
Laufmetadaten festgehalten. PR 91 hat anschliessend vier getrennte
Referenzschichten fuer alle 19 Ziele eingefroren. PR 92 hat den
Horizontvertrag 100/300/500 umgesetzt; `VUSK1L1-5` bleiben dabei fuenf
Zeitfenster desselben `SK1/all`-Aggregats auf Stufe IV. PR93 hat die zwei
vollstaendigen 100er-Tabellen an den Korpusbericht gebunden. PR94 hat den
modernen Zustand bis 300 erweitert, ohne daraus einen gemeinsamen
historischen Lauf der Archivquellen abzuleiten. PR95 hat die zwei
ZINS000-Regelfenster getrennt verglichen und dabei 600/600 abweichende Zeilen
dokumentiert. PR96 hat den modernen Zustand bis 500 erweitert. PR97 hat die
VU-SK1-Zeitfenster aus ihren getrennten Referenzschichten angebunden. PR98
bindet als Naechstes die vier VN-Regeltabellen 3-6 an.
