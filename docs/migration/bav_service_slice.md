# BAV-Service-Slice: erster substanzieller Python-Teilschnitt

Dieser PR portiert bewusst nur einen kleinen, testbaren Ausschnitt des historischen BAV-Servicekerns nach Python.
Es gibt in diesem Stand keine Behauptung historischer Vollgleichheit.

## In diesem Slice portiert

- kleine Python-Datencontainer für BAV-Fremdinformation
- kleine Initialisierungsschnitte als Python-Servicefunktionen für `Myinitbv` und `Newinibv`
- ein enger `Frmdinf`-Teilschnitt für wenige Durchschnitts- und Extremwerte aus Vorperioden-Snapshots
- automatische Tests mit expliziten Erwartungswerten

## Direkt adressierte Altbestandteile

- `Myinitbv`: hier nur als kleiner Nullsetzungs-Schnitt für Fremdinformationsfelder
- `Newinibv`: hier nur als kleiner Nullsetzungs-Schnitt für Fremdinformationsfelder nach Folgeläufen
- `Frmdinf`: hier nur als kleiner Teilschnitt für `Dp`, `Dw`, `Dg`, `Pm`, `Wm`, `Mp` und `Mw`

## Bewusst nicht enthalten

- keine Portierung von `Agrsich`
- keine vollständige historische Schockreihenfolge
- keine vollständige Altvektorstruktur
- keine Portierung von VU-/VN-Verhaltensregeln
- keine Vollsimulation

## Nächster sinnvoller BAV-Schritt

Der nächste Fach-PR sollte den Altcodebezug der bereits portierten Felder weiter schärfen,
weitere direkt belegbare Teilfelder von `Frmdinf` prüfen und erst danach einen weiteren kleinen,
quellenbasierten BAV-Service-Slice ergänzen.
