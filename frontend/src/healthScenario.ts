export const HEALTH_HORIZONS = [1, 2, 5, 10, 25, 50, 100] as const;

export type HealthSide = "baseline" | "variant";

export type HealthDraft = {
  insurerId: number;
  scenarioId: string;
  periodCount: number;
  openingActivePolicies: number;
  openingCash: string;
  openingLiability: string;
  openingEquity: string;
  newBusinessPerPeriod: number;
  exitsPerPeriod: number;
  premiumPerPolicy: string;
  benefitPerPolicy: string;
  benefitsPaid: string;
  investmentResult: string;
  operatingExpensePaid: string;
  capitalContribution: string;
  capitalDistribution: string;
  variantStartPeriod: number;
  variantPremiumPerPolicy: string;
  variantBenefitPerPolicy: string;
  variantBenefitsPaid: string;
};

type CountSource = {
  actor_type: "market" | "policyholder";
  mode: "explicit_scenario_counts";
  periods: { period: number; count: number }[];
};

type WindowSource = {
  actor_type: "insurer" | "exogenous";
  mode: "explicit_insurer_price_windows" | "explicit_benefit_cost_windows";
  windows: { start_period: number; end_period: number; amount_per_opening_policy: string }[];
};

export type HealthChainInput = {
  schema_version: "ims.health-period-chain-input.v1";
  health_sector_contract_schema_version: "ims.health-sector-contract.v2";
  sector_taxonomy_schema_version: "ims.sector-taxonomy.v1";
  source_kind: "versioned_health_period_chain";
  historical_mapping_status: "unresolved";
  insurer_id: number;
  sector_id: "health";
  opening: {
    opening_active_policies: number;
    opening_cash: string;
    opening_benefit_liability: string;
    opening_equity: string;
  };
  sources: {
    schema_version: "ims.health-period-sources-input.v1";
    health_sector_contract_schema_version: "ims.health-sector-contract.v2";
    sector_taxonomy_schema_version: "ims.sector-taxonomy.v1";
    source_kind: "versioned_health_period_sources";
    historical_mapping_status: "unresolved";
    insurer_id: number;
    sector_id: "health";
    scenario_id: string;
    variant_id: HealthSide;
    period_count: number;
    opening_active_policies: number;
    new_business: CountSource;
    exits: CountSource;
    pricing: WindowSource;
    benefits: WindowSource;
  };
  periods: {
    period: number;
    benefits_paid: string;
    investment_result: string;
    operating_expense_paid: string;
    capital_contribution: string;
    capital_distribution: string;
  }[];
};

export function defaultHealthDraft(): HealthDraft {
  return {
    insurerId: 1,
    scenarioId: "seminar_health_01",
    periodCount: 25,
    openingActivePolicies: 100,
    openingCash: "1000.00",
    openingLiability: "200.00",
    openingEquity: "800.00",
    newBusinessPerPeriod: 1,
    exitsPerPeriod: 1,
    premiumPerPolicy: "3.00",
    benefitPerPolicy: "1.80",
    benefitsPaid: "180.00",
    investmentResult: "2.00",
    operatingExpensePaid: "30.00",
    capitalContribution: "0.00",
    capitalDistribution: "0.00",
    variantStartPeriod: 6,
    variantPremiumPerPolicy: "3.00",
    variantBenefitPerPolicy: "2.40",
    variantBenefitsPaid: "240.00"
  };
}

function windows(
  count: number, start: number, baseline: string, variant: string, side: HealthSide
): WindowSource["windows"] {
  if (side === "baseline" || start > count) return [{ start_period: 1, end_period: count, amount_per_opening_policy: baseline }];
  if (start === 1) return [{ start_period: 1, end_period: count, amount_per_opening_policy: variant }];
  return [
    { start_period: 1, end_period: start - 1, amount_per_opening_policy: baseline },
    { start_period: start, end_period: count, amount_per_opening_policy: variant }
  ];
}

export function buildHealthInput(draft: HealthDraft, side: HealthSide): HealthChainInput {
  const count = draft.periodCount;
  const start = draft.variantStartPeriod;
  const counts = (value: number) => Array.from({ length: count }, (_, index) => ({ period: index + 1, count: value }));
  return {
    schema_version: "ims.health-period-chain-input.v1",
    health_sector_contract_schema_version: "ims.health-sector-contract.v2",
    sector_taxonomy_schema_version: "ims.sector-taxonomy.v1",
    source_kind: "versioned_health_period_chain",
    historical_mapping_status: "unresolved",
    insurer_id: draft.insurerId,
    sector_id: "health",
    opening: {
      opening_active_policies: draft.openingActivePolicies,
      opening_cash: draft.openingCash,
      opening_benefit_liability: draft.openingLiability,
      opening_equity: draft.openingEquity
    },
    sources: {
      schema_version: "ims.health-period-sources-input.v1",
      health_sector_contract_schema_version: "ims.health-sector-contract.v2",
      sector_taxonomy_schema_version: "ims.sector-taxonomy.v1",
      source_kind: "versioned_health_period_sources",
      historical_mapping_status: "unresolved",
      insurer_id: draft.insurerId,
      sector_id: "health",
      scenario_id: draft.scenarioId,
      variant_id: side,
      period_count: count,
      opening_active_policies: draft.openingActivePolicies,
      new_business: { actor_type: "market", mode: "explicit_scenario_counts", periods: counts(draft.newBusinessPerPeriod) },
      exits: { actor_type: "policyholder", mode: "explicit_scenario_counts", periods: counts(draft.exitsPerPeriod) },
      pricing: {
        actor_type: "insurer", mode: "explicit_insurer_price_windows",
        windows: windows(count, start, draft.premiumPerPolicy, draft.variantPremiumPerPolicy, side)
      },
      benefits: {
        actor_type: "exogenous", mode: "explicit_benefit_cost_windows",
        windows: windows(count, start, draft.benefitPerPolicy, draft.variantBenefitPerPolicy, side)
      }
    },
    periods: Array.from({ length: count }, (_, index) => ({
      period: index + 1,
      benefits_paid: side === "variant" && index + 1 >= start ? draft.variantBenefitsPaid : draft.benefitsPaid,
      investment_result: draft.investmentResult,
      operating_expense_paid: draft.operatingExpensePaid,
      capital_contribution: draft.capitalContribution,
      capital_distribution: draft.capitalDistribution
    }))
  };
}
