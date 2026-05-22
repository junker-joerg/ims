# Slice-Plan: VN-Regeldispatch fuer Schaden-Abrechnung nutzen

## Ziel

Explizite VN-Schaden-Abrechnungs-Snapshots sollen ihre
Versicherungsentscheidungen kontrolliert aus dem bereits portierten
VN-Regeldispatch beziehen koennen.

## Umsetzung

- `VNDamageSettlementSnapshot.insurance_decisions` optional machen
- direkte Modellanwendung weiterhin mit klarem Fehler abbrechen, wenn
  Entscheidungen fehlen
- VN-Periodenrunner wendet Insurance-Rule-Snapshots zuerst an
- VN-Periodenrunner fuellt fehlende Schaden-Abrechnungs-Entscheidungen aus der
  passenden `VNInsuranceRuleApplication`
- Tests fuer Loader, direkten Modellschutz und Runner-Kopplung ergaenzen

## Grenzen

- Keine automatische historische Regelwahl
- Keine Erzeugung von Schaden- oder Settlement-Snapshots ohne explizite
  Schadenparameter und Schwellen
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit
