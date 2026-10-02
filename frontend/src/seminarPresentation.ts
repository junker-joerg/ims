// Presentation of checked AP3 rows; no simulation or booking takes place here.
export type Side = "baseline" | "variant";
export type Assignment = { actor_type: string; target_id: string; sector_id: string; strategy_id: string; period_from: number; period_through: number; parameters: Record<string, string | number> };
export type SeminarInput = {
  period_count: number; case_id: string;
  policyholder_groups: { group_id: string; sector_id: string; exposure: string; initial_insurer_id: number }[];
  strategies: Record<Side, Assignment[]>;
};
export type BalanceRow = {
  period: number; opening_assets: string; opening_liabilities: string; opening_equity: string;
  capital_contribution: string; capital_distribution: string; period_profit: string;
  closing_assets: string; closing_liabilities: string; closing_equity: string;
};
export type DecisionTrace = {
  period: number; sector_id: string; insurer_group?: string; strategy_id?: string;
  parameters?: Record<string, string | number>; draws?: string[];
  quoted_price?: string; covered_exposure?: string; premium_income?: string; advertising_expense?: string;
  group_decisions?: { group_id: string; chosen_insurer_id: number | null; booked_premium: string; strategy_id?: string; declared_exposure?: string }[];
  source_decisions?: { strategy_id: string; target_id: string; parameters: Record<string, string | number> }[];
  generated_period_source?: Record<string, string | number>; model_balance: BalanceRow;
};
export type SeminarResult = {
  valid: boolean; content_digest: string; insurer_id: number; scenario_id: string; period_count: number;
  generated_sources: Record<Side, object>;
  sides: Record<Side, { content_digest: string; total_rows: BalanceRow[]; sectors: { sector_id: string; rows: BalanceRow[] }[] }>;
  decision_traces: Record<Side, DecisionTrace[]>;
};
export const sectorNames: Record<string, string> = { motor: "Kfz", property_liability: "Sach / Haftpflicht", life: "Leben", health: "Kranken" };
export const ruleNames: Record<string, string> = {
  "vu.vrvu01": "Preis und Werbung · Zufall I", "vn.vrvn06": "Kundenwahl · Beste Information",
  "life.opening_assets_rate": "Anlagesatz auf Anfangsaktiva", "health.opening_policy_price": "Beitrag auf Anfangspolicen",
  "health.declared_new_business": "Deklariertes Neugeschäft", "health.declared_exits": "Deklarierte Abgänge",
  "declared_opening_offer": "Deklariertes Anfangsangebot", "declared_initial_contract": "Anfangsvertrag",
};
export const parameterNames: Record<string, string> = {
  premium_factor: "Preisfaktor", advertising_factor: "Werbefaktor", premium_factor_shock: "Preisfaktor bei Änderungsschock",
  advertising_factor_shock: "Werbefaktor bei Änderungsschock", insurance_threshold: "Versicherungsschwelle",
  insurance_threshold_shock: "Schwelle bei Änderungsschock", rate_per_period: "Anlagesatz je Periode",
  amount_per_opening_policy: "Beitrag je Anfangspolice", count: "Anzahl je Periode",
};

// Monetary API rows use decimal strings with four fractional places. Preserve
// them exactly for sums/differences; floating point is used only for SVG geometry.
export function amountUnits(value: string | number): bigint {
  const match = /^(-?)(\d+)(?:\.(\d{1,4}))?$/.exec(String(value));
  if (!match) throw new Error("Betrag entspricht nicht dem Vier-Nachkommastellen-Vertrag.");
  return BigInt(match[2] + (match[3] || "").padEnd(4, "0")) * (match[1] ? -1n : 1n);
}
export function amountText(value: bigint | string, signed = false): string {
  const units = typeof value === "bigint" ? value : amountUnits(value);
  const absolute = (units < 0n ? -units : units).toString().padStart(5, "0");
  const whole = absolute.slice(0, -4).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return `${units < 0n ? "−" : signed && units > 0n ? "+" : ""}${whole},${absolute.slice(-4)}`;
}
export function percentText(variant: string, baseline: string): string {
  const base = amountUnits(baseline), difference = amountUnits(variant) - base;
  if (base === 0n) return "Nicht definiert (Baseline 0)";
  const denominator = base < 0n ? -base : base;
  const numerator = difference * 10000n;
  let rounded = numerator / denominator;
  const remainder = numerator % denominator;
  if ((remainder < 0n ? -remainder : remainder) * 2n >= denominator) rounded += difference < 0n ? -1n : 1n;
  const digits = (rounded < 0n ? -rounded : rounded).toString().padStart(3, "0");
  return `${rounded < 0n ? "−" : rounded > 0n ? "+" : ""}${digits.slice(0, -2)},${digits.slice(-2)} %`;
}
export function cumulativeFlows(traces: DecisionTrace[], through: number) {
  return traces.filter(trace => trace.period <= through).reduce((total, trace) => ({
    premium: total.premium + amountUnits(trace.premium_income ?? trace.generated_period_source?.premium_income ?? "0"),
    advertising: total.advertising + amountUnits(trace.advertising_expense ?? "0"),
    investment: total.investment + amountUnits(trace.generated_period_source?.investment_result ?? "0"),
  }), { premium: 0n, advertising: 0n, investment: 0n });
}
export function profitReconciliation(result: SeminarResult, through: number) {
  const pairs = result.sides.variant.total_rows.slice(0, through).map((row, index) => ({ row, base: result.sides.baseline.total_rows[index] }));
  const differences = pairs.map(({ row, base }) => amountUnits(row.period_profit) - amountUnits(base.period_profit));
  const totalProfit = differences.reduce((sum, value) => sum + value, 0n);
  const totalCapital = pairs.reduce((sum, { row, base }) => sum + amountUnits(row.capital_contribution) - amountUnits(row.capital_distribution) - amountUnits(base.capital_contribution) + amountUnits(base.capital_distribution), 0n);
  const changed = differences.map((difference, index) => ({ difference, period: index + 1 })).filter(item => item.difference !== 0n);
  const constant = changed.length > 0 && changed.every((item, index) => item.difference === changed[0].difference && item.period === changed[0].period + index);
  return { totalProfit, totalCapital, constant, changed, firstDifference: changed[0]?.difference ?? 0n };
}
