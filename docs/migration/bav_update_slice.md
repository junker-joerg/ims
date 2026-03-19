# BAV-Update-Slice

Dieses Dokument beschreibt einen kleinen BAV-nahen Aktualisierungsschritt im Python-Port.
Der Schritt bleibt bewusst konservativ und ist noch keine historische BAV-Regelportierung.

## Was dieser Schritt leistet

- aktualisiert wenige zentrale Zustandsfelder direkt auf `BAV`
- übernimmt `period` und `logtime` aus dem `SimulationContext`
- zählt aktive Versicherer und aktive Versicherungsnehmer
- kann optional genau einen RNG-Sample-Wert auf `BAV` schreiben

## Warum dieser Schritt BAV-nah ist

`BAV` wird hier als zentrale Aggregations- und Zustandsreferenz verwendet, ohne bereits komplexe Fachlogik oder Marktverhalten zu modellieren.

## Was ausdrücklich noch nicht portiert wurde

- keine vollständigen BAV-/VU-/VN-Regeln
- keine Simulationsschleife oder UI
- keine historische Kompatibilität des fachlichen Verhaltens
- keine komplexe Markt- oder Vertragslogik

## Warum dies noch keine historische BAV-Regelportierung ist

Die Aktualisierung beschränkt sich auf wenige eindeutig ableitbare Zähl- und Zeitwerte sowie optional einen technischen RNG-Sample.
Weitergehende Fachbedeutung und Altverhalten müssen in späteren PRs separat validiert werden.
