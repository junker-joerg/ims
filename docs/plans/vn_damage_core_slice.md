# Plan: VN-Schadenerzeugungskern

## Ziel

Portiere den gemeinsamen deterministischen Schadenerzeugungskern aus den
historischen VN-Regeln `Vrvn01` bis `Vrvn03` als kleinen Python-Slice.

## Altcode-Bezug

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`

Alle drei Regeln nutzen je Sparte die Form:

- Schaden tritt ein, wenn `Sw > normal()`
- Schadenhoehe ist `a + b * normal()`
- im Aenderungsschockfall werden die alternativen Parameter genutzt

## Umsetzung

1. Dataclasses fuer Parameter, explizite Normalziehungen und Ergebnis in
   `python_port/ims/model/vn_damage_rules.py` ergaenzen.
2. Pure Apply-Funktion mit expliziten Draws implementieren.
3. Mapping-Loader fuer Szenario-/Fixture-nahe Daten ergaenzen.
4. Tests fuer Normalfall, Schockfall, Ausbleiben des Schadens und Loaderform
   schreiben.

## Bewusst nicht enthalten

- keine RNG-Integration
- keine VN-Versichererwahl
- keine Pflichtversicherungs-/Praeferenzlogik
- keine automatische Kopplung an den Settlement-Runner
- keine Vollsimulation
