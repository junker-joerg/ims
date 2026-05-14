# Autonomer Integrationslauf auf main

## Branch-Inventur

Ausgangspunkt war `origin/main` auf `f86d75b` (`Create skills.md`). Nicht in
`origin/main` enthalten waren fuenf Remote-Branches:

- `origin/codex/create-initial-pr-with-project-structure-and-tests-xjh38u`:
  integriert. Dieser Branch enthaelt die validierteste Agrsich-Linie inklusive
  Writer, Export, echter Legacy-Versichererdateien und Reserve-Modellkorrektur.
- `origin/codex/create-initial-pr-with-project-structure-and-tests-yo3214`:
  obsolet/ersetzt. Der fachliche Agrsich-Kern ist in `xjh38u` enthalten und dort
  durch Export- und Legacy-Vergleich weiter abgesichert.
- `origin/codex/create-initial-pr-with-project-structure-and-tests-l16gen`:
  obsolet/ersetzt. Frueher Scheduler-/Strukturstand; die Inhalte sind in der
  spaeteren, testbaren Python-Port-Linie enthalten.
- `origin/codex/create-initial-pr-with-project-structure-and-tests-nlv0b2`:
  obsolet/ersetzt. Import-/Platzhalter-Fix aus einem fruehen Stand; durch die
  konsolidierte Python-Port-Linie ersetzt.
- `origin/codex/create-initial-pr-with-project-structure-and-tests-4973jg`:
  bewusst ausgelassen. Reiner Dokumentations-/Inventarstand gegen eine aeltere
  Basis; die relevanten Architektur- und Inventarinhalte liegen bereits in der
  spaeteren Linie vor.

Alle bereits in `origin/main` gemergten `codex/create-initial...`-Branches wurden
als integriert bewertet.

## Integrationsentscheidung

Die offenen Branch-Endzustaende wurden nicht blind gemergt, weil sie gegen den
aktuellen `main` wie massive Loeschungen historischer Quellen und bereits
vorhandener Module wirken. Stattdessen wurde der saubere Stand aus `xjh38u` fuer
`python_port/`, `tests/`, `docs/migration/`, `docs/plans/`, `.gitignore` und
`README.md` manuell uebernommen. Root-Anweisungen, historische C-/PDF-Quellen und
die neuere `.agents`-Skill-Datei aus `main` blieben erhalten.

Groessere Konfliktentscheidungen:

- Validierter Agrsich-Pfad vor aelteren Agrsich-Zwischenstaenden.
- Saubere Python-Port-Dateien aus `xjh38u` vor den in `main` sichtbaren
  Konkatenations-/Importartefakten.
- Echte Legacy-Versichererdateien und Vergleichstests vor unvalidierten
  Exportnaeherungen.
- Keine Integration von Branch-Endzustaenden, die historische Quellen oder
  `AGENTS.md` aus dem aktuellen `main` entfernt haetten.

## Technischer Status

Stabilisiert wurden:

- Importpfade fuer Tests ueber `tests/conftest.py`.
- `python_port`-Pytest-Konfiguration, sodass der Lauf aus dem Paketordner die
  gemeinsamen Repo-Tests ausfuehrt.
- Agrsich-Testdaten mit sektorgetrennten Reserven (`reserves_current` als
  Zweiervektor).
- Eine kuratierte Agrsich-Referenzzeile, deren Float-Darstellung exakt dem
  aktuellen Writer entspricht.

Ausgefuehrte Pruefungen:

- `python -m pytest -q` vom Repo-Root: 125 Tests gruen.
- `cd python_port && python -m pytest -q`: Tests gruen.
- `git diff --check`: keine Whitespace-Fehler, nur CRLF-Hinweise der lokalen
  Windows-Checkout-Einstellung.

`pytest -q` direkt wurde versucht, ist in dieser lokalen Umgebung aber nicht als
Kommando im PATH verfuegbar. Der aequivalente Lauf ueber `python -m pytest -q`
wurde verwendet.

## Fachlicher Status

Der Integrationsstand enthaelt jetzt den substanziellen Agrsich-Slice:

- BAV-Service- und Agrsich-Aggregatgrundlage.
- Historisch orientierte Agrsich-Exporttabellen und Writer.
- Vergleich gegen kuratierte Referenzdateien.
- Parser und Comparator fuer echte Legacy-Versichererdateien.
- Echte Legacy-Dateien `VU14L1.DAT` und `VUSK1L4.DAT` im Testbestand.
- Modellkorrektur: `Insurer.reserves_current` ist sektorgetrennt als
  `list[float]`; Skalar-JSON bleibt im Loader abwaertskompatibel.

Der Stand behauptet keine vollstaendige historische Gleichheit. Validiert ist
gezielt der abgedeckte Versicherer-Agrsich-Slice auf Zeilenebene gegen reale
Legacy-Dateien.

## Fertigstellungsplan

1. PR sofort erstellen und reviewen: Integrationsbranch pruefen, Fokus auf
   Agrsich-Modellkorrektur, Testpfade und Erhalt historischer Quellen. Risiko:
   mittel, weil viele vorherige Branch-Inhalte konsolidiert wurden.
2. Danach VN-Legacy-Vergleich aufbauen: echte VN-Dateien identifizieren, Parser
   separat einfuehren, keine Vermischung mit Versichererparser. Risiko: mittel
   bis hoch wegen noch offener Dateisemantik.
3. Multi-Perioden-Neulauf aus Altinitialdaten vorbereiten: erst Szenario- und
   Seed-Reproduzierbarkeit absichern, dann Vergleichsfenster ausweiten. Risiko:
   hoch.
4. Export-/Writer-Formate weiter haerten: numerische Formatierung bewusst
   entscheiden, sobald weitere echte Legacy-Dateien vorliegen. Risiko: mittel.
5. Abschluss erst nach gruener Legacy-Abdeckung fuer die priorisierten Datei-
   familien und dokumentierten Abweichungen. Spaetere kosmetische Refactors
   bleiben nachrangig.
