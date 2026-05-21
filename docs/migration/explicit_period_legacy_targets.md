# Legacy-Ziele fuer explizite VU/VN-Periodenlaeufe

## Ziel

Der kombinierte explizite VU/VN-Runner kann Agrsich-Exports jetzt gegen
explizite Legacy-Ziele vergleichen. Damit laesst sich ein kontrolliertes
Referenzfenster direkt nach der gemeinsamen VU- und VN-Fachlogik validieren.

## Ursprung im Altcode

Der fachliche Anschluss liegt bei den historischen Agrsich-Ausgaben wie
`IMSVU*.DAT` und `IMSVNR*.DAT`. Die zugrunde liegenden VU- und VN-Wirkungen sind
weiterhin die bereits portierten `Vrvu*`- und `Vrvn01`-bis-`Vrvn03`-Slices.
Dieser Schritt portiert keine neue historische Ablaufsteuerung.

## Python-Abbildung

- `ExplicitLegacyTarget` beschreibt Referenzdatei, Exportdatei, Subjekttyp und
  Toleranz.
- `run_explicit_multi_period_from_mappings` kann optionale Legacy-Ziele
  entgegennehmen und vergleicht die zusammengefuehrten Exporttabellen.
- `run_explicit_multi_period_from_fixture` laedt relative `legacy_targets` aus
  dem Fixture-Verzeichnis.
- Optional werden die vorhandenen Legacy-Validierungsreports geschrieben, wenn
  `legacy_report_name` und `output_dir` gesetzt sind.

## Annahmen und Grenzen

- Die Vergleiche laufen nur gegen explizit benannte Referenzfenster.
- Vollstaendige Legacy-Periodenabdeckung wird verlangt, damit fehlende
  Replay-Perioden sichtbar bleiben.
- Es wird keine historische Vollgleichheit behauptet und keine neue
  Regelentscheidung eingefuehrt.
