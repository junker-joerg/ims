# PR167: Gefuehrte Lebens-Workbench

Stand: 2026-09-17
Status: umgesetzt mit dokumentierter Browser-Download-/Screenshot-Testluecke

## Ziel und Grenze

Ein Seminarteilnehmer kann ohne JSON-Eingabe einen vorbereiteten
Lebensfall waehlen, Baseline und Variante veraendern, beide ueber die
PR166-Vorschau vergleichen und einen geprueften Stand ausdruecklich
speichern und als XLSX herunterladen. Kein neuer Lebens-Rechenkern,
keine Anbindung an den historischen Nichtleben-Runner und keine
Vier-Sparten-Gesamtbilanz.

## Schnitt

- Versionierte, serverseitig gepruefte Zwei-Perioden-Presets fuer
  Todesfall, Neugeschaeft sowie Anlage/Kapital. Alle haben dieselbe
  Ausgangslage; nur die benannte Variante aendert den Wirkungshebel.
- Strukturierte Eingaben fuer Versicherer, periodische Anlage- und
  Kapitalwerte sowie Policenfluesse. Anfangsbestand, Garantiesaetze und
  Laufzeiten bleiben in diesen kuratierten Faellen fest. Todesfall und
  Neugeschaeft werden als explizite Ja/Nein-Entscheidungen atomar mit
  ihren Folgefluessen
  umgeschaltet; keine neue Sterblichkeits- oder Abschlussstrategie.
- Baseline und Variante werden einzeln mit dem PR166-Preview berechnet.
  Zeitreihe, periodische Tabelle, Annahmequelle und Fehler werden ohne
  Roh-JSON-Pflicht gezeigt. Aenderung einer Seite entwertet nur deren
  Vorschau und Vergleich.
- Speicherung nur nach aktivierter Freigabe und erneutem PR166-Digest-
  Vergleich. Verlauf und XLSX kommen aus dem geprueften gespeicherten
  Ergebnis; fehlende SQLite-Konfiguration bleibt eine klare Grenze.

## Nachweis und offen

`IMSDATA.C`/`IMS.E` belegen kein historisches Leben; Presets sind
IMS-2.x-Seminarfaelle. Backend-Tests rechnen jedes Preset mit PR165,
pruefen stabile Baseline und Wirkungsdifferenzen. Frontend-Build,
breite/schmale Browserabnahme und Fehlerpfade sind erfolgt. Der
Browser-Download als Datei und neue statische Screenshots konnten hier
nicht nachgewiesen beziehungsweise abgelegt werden; dies bleibt als
explizite Testluecke fuer die naechste UI-Abnahme. Der Bedienpfad steht
im Handbuch. PR168 beginnt danach separat mit dem
Kranken-Vertrag. Der PR166-Backup-/Restore-Nachweis bleibt offen.
