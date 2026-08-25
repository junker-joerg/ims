# VU14-Quellenbindung fuer Vdefmd6

Stand: 2026-08-25
Vertragsversion: `pr73-v1`

## Ziel

PR 73 bindet Versicherer 14 erstmals an die konkrete historische
Modellkonfiguration `Vdefmd6` und erzeugt daraus unabhaengig die Periode 1 von
`imsvu014.dat`. Der Schritt startet keinen Runner und keine Simulation. Er
behauptet keine historische Vollgleichheit fuer die Perioden 1-100.

## Referenzkorrektur

Die zuvor versionierte `tests/references/legacy_agrsich/VU14L1.DAT` enthielt
linear konstruierte Testwerte ab `101.0` und stimmte nicht mit dem lokalen
Altdatenkandidaten ueberein. Sie wurde durch die gezielt gepruefte historische
Zeitreihe ersetzt.

Die uebernommene Reihe ist dreifach belegt:

- `incomming/IMS.DAT/VU14L1.DAT`: Perioden 1-100, SHA-256 `9cf9f137...`;
- `VU14P2.DAT` entspricht tokenweise den Perioden 1-50;
- `VU14P1.DAT` entspricht tokenweise den Perioden 51-100;
- `WVEMOD1.ZIP/IMSVU014.DAT` entspricht tokenweise in seinem Fenster 1-100.

Der normalisierte Hash der versionierten Reihe ist
`f568e2ec989e66832cd979591df95ad40c650b44774a05573f317322e587f49c`.
`incomming/` bleibt selbst unversioniert.

## C-zu-Python-Zuordnung

| Historischer Ursprung | Python-Anschluss | Bedeutung |
| --- | --- | --- |
| `IMS.E:4566-4706`, `Vdefmd6` | `vu14_vdefmd6_source_binding.json` | Modell, BAV und Population |
| `IMS.E:4602-4605` | `VUExpectedClaimRuleParameters` | VU14 ist Allianz mit `Vrvu06` |
| `IMS.E:4137-4184`, `Vuauini` | Quellenprofil | Aktivierung, Aktionszeit und Startwerte |
| `IMS.E:1578-1688`, `Vrvu06` | `apply_vu_expected_claim_rule_to_insurer` | Praemien-, Werbe- und Reservenregel |
| `IMSDATA.C:77-84` | Quellenprofil | Regel 6 gehoert zur VU-Regelklasse 2 |
| `IMS.E:402-446`, `Agrsich` | `agrsich_service.py`, `agrsich_export.py` | Periodenprojektion |

Das Profil beschreibt 25 Versicherer und 200 Versicherungsnehmer. Fuer VU14
gelten Startpraemien `40/40`, Werbung `10/10`, Regel 6, Regelklasse 2,
Aktivierung ab Periode 1 und logischer Aktionszeitpunkt 1.

## Historischer Widerspruch

Die ausfuehrbaren Schleifen in `Vdefmd6` ordnen VN 151-190 Regel 3 und VN
191-200 Regel 2 zu. Der spaetere Bildschirmtext nennt dagegen 151-180 und
181-200. Das Quellenprofil folgt konservativ den ausfuehrbaren Grenzen
151-190 und 191-200 und dokumentiert die abweichende Anzeige.

## Read-only Probe

Der Befehl

```powershell
python -m ims.api.vu14_source_binding --repo-root .
```

erzeugt zunaechst VU14/Periode 1 aus den `Vdefmd6`-Startwerten, wendet den
bereits portierten `Vrvu06`-Kern an, aggregiert und exportiert im Speicher und
liest erst danach die Legacy-Zeile. Ergebnis: 14/14 Vergleichsfelder stimmen.

Damit sind vier Herkunftsgruppen gebunden: Population, Startzustand,
VU14-Regel/Aktionszeit und Regel-/Zustandsursprung. Die direkte
Perioden-1-Erzeugung ist belegt, nicht das vollstaendige Zeitfenster.

## Offene Grenzen

- Der historische RNG-Algorithmus und die zeitbasierte Seed-Bildung sind
  belegt, der konkrete Seed des Referenzlaufs jedoch nicht.
- Die VN-Wahl-, Schaden- und Abrechnungsfolge fuer Perioden 2-100 ist noch
  nicht als gemeinsamer, unabhaengiger Zustandspfad geschlossen.
- Die vorhandenen Vier-Perioden-Fixtures bleiben direkte, nun an echte Zeilen
  ausgerichtete Writer-/Vergleichsproben und keine Erzeugungsinputs.
- Es gibt keine Freigabe und keine historische Vollgleichheit.

## Fortschreibung durch PR 74

PR 74 hat den ersten Schritt dieser Restplanung mit dem typisierten
`Vdefmd6`-Builder fuer 25 VU und 200 VN geschlossen. Der Perioden-1-Vergleich
bezieht VU14 nun aus diesem Builder.

Danach verbleiben mindestens acht reviewbare Schritte:

1. PR 75: logische Aktionsfolge und explizite moderne Seed-Policy anbinden,
   ohne den unbekannten historischen Seed zu behaupten;
2. PR 76: VU14-Zustandsweg fuer Perioden 2-49 schliessen und Abweichungen
   klassifizieren;
3. PR 77: Schockgrenze und Perioden 50-100 schliessen;
4. PR 78: dieselbe VU-Population auf SK1/all und VU-Klassen verbreitern;
5. PR 79 und PR 80: VN-Regelzustand in zwei kleinen Gruppen schliessen;
6. PR 81: VN-Klassen und SK1/all aus demselben Zustand vergleichen;
7. PR 82: alle 15 Exporte gemeinsam und anschliessend manuell bewerten.

Funde koennen diese Schritte weiter teilen. Eine fehlende historische
Seed-Aufzeichnung wird nicht durch eine erfundene Gleichheitsannahme ersetzt.
