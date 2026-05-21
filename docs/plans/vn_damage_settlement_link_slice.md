# Plan: VN-Schaden-Abrechnungs-Kopplung

## Ziel

Verbinde den bereits portierten VN-Schadenerzeugungskern mit dem
deterministischen VN-Abrechnungskern ueber explizite
Versicherungsentscheidungen. Der Slice soll groesser als reine Validierung
sein, aber weiterhin keine historische VN-Wahl-, Praeferenz- oder
RNG-Automatik behaupten.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`

In den historischen Regeln stehen Schadenziehung, Entscheidung je Sparte und
anschliessende Abrechnung direkt nebeneinander. Die bisherigen Python-Slices
bilden Schadenerzeugung und Abrechnung getrennt ab; dieser Schritt stellt die
belegte Kopplung als reine Adapterfunktion her.

## Umsetzung

1. Explizite Versicherungsentscheidung ohne Schadenhoehe einfuehren.
2. Schadenresultat plus Versicherungsentscheidungen in einen
   `VNSettlementSnapshot` ueberfuehren.
3. Skalar vorhandene VU-Versichertenzaehler beim sektoriellen VN-Settlement
   erhalten, wenn kein Sektorvektor vorhanden ist.
4. Tests fuer Kopplung, Loader-Validierung und den Zaehler-Fallback ergaenzen.

## Grenzen

- keine Portierung der historischen Versichererwahl
- keine Praeferenz- oder Pflichtversicherungslogik
- keine versteckte RNG-Nutzung
- keine Scheduler-Kopplung und keine Vollsimulation
