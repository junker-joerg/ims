# AP1: Windows-Installer – Umsetzung und Prüfplan

Basis: Planungs-PR #287, main e00f8e7; Auftrag vom 30.09.2026.

1. Explizite Ressourcenwurzel und Benutzerablage ergänzen. Bestehende Modell-
   und Ausführungsfreigaben beibehalten; keine C-Fachlogik ändern.
2. Eigenen eingefrorenen Einstiegspunkt mit Loopback, Health-Check,
   Einzelinstanz, sichtbarem Beenden, Backup/Übernahme und Diagnoseexport bauen.
3. Python 3.12 x64, gepinnte Build-Abhängigkeiten, PyInstaller One-folder und
   Inno Setup: ein Download, Installation ohne Administratorrechte.
4. Tatsächlichen Installer einschließlich Update/Deinstallation/Neuinstallation,
   Modellfall und Export prüfen; vorhandenen Windows-Release-Gate ausführen.
5. CI-Artefakt/Hash, Anwenderanleitung, Abnahmecheckliste, Übergabe und Bericht
   im selben Draft-PR sichern. done/Ready erst nach allen Abnahmen.

Mapping: `scripts/workbench/build-user-test-package.ps1` ist der bisherige
Entwicklerpaketweg; neuer Installer unter `scripts/installer/`.
`ims/api/app.py` bleibt Backend; neue `ims/desktop/`-Module regeln ausschließlich
Ressourcen, Benutzerdaten und Prozesslebenszyklus. Historische C-Quellen,
Scheduler, Seeds, Regeln und Aggregatdefinitionen bleiben unverändert.

Risiken: relative Referenzpfade, dynamische Imports, Bundle-Schreibzugriffe,
laufender Prozess beim Update, belegter Port, SQLite-Backup mit WAL,
unsignierte EXE, unvollständige Lizenzfreigabe, fehlende saubere Windows-VM.
Der P52 ist Windows 11 mit Entwicklerwerkzeugen und ersetzt diese VM nicht.
