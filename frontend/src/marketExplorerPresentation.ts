// Read-only AP8 arithmetic. Integers preserve all four monetary decimal places.
// Floating point belongs only in SVG geometry, never totals/ratios/book tables.
import { amountUnits, type Side } from "./seminarPresentation";

export type Row = Record<string, unknown>;
export type Actor = { insurer_id: number; name: string; insurance_group_id: string; sectors: string[] };
export type Family = { family_id: string; label: string; sector_id: string; rule: string; parameters: Row };
export type ExplorerResult = {
  valid: boolean; schema_version: string; content_digest: string; model_result_digest: string; input_digest: string;
  period_count: number; seed: number; title: string; actors: Actor[]; families: Family[];
  peer_groups: { group_id: string; label: string; insurer_ids: number[] }[];
  comparison_labels: Record<Side, string>; clock: Row | null; reference: Row | null;
  scope_notice: string; causal_limit: string;
  schedules: { events: Row[]; responses: Partial<Record<Side, Row[]>>; assignments: Record<Side, Row[]>; measures: Record<Side, Row[]>; ict: { assets?: Row[]; resources?: Row[]; services?: Row[] } };
  sides: Record<Side, Record<string, Row[]>>;
};
export const fields = ["opening_assets", "opening_liabilities", "opening_equity", "closing_assets", "closing_liabilities", "closing_equity", "period_profit", "premium_income", "investment_income", "insurance_expense", "claims_paid", "operating_expense", "measure_cost", "capital_contribution", "capital_distribution"] as const;
export type Field = typeof fields[number];
export type Totals = Record<Field, bigint>;
export const bookTerms: { key: Field; label: string; sign: bigint }[] = [
  { key: "opening_equity", label: "Anfangs-Eigenkapital", sign: 1n },
  { key: "premium_income", label: "Gebuchte Beiträge", sign: 1n },
  { key: "investment_income", label: "Kapitalanlage", sign: 1n },
  { key: "insurance_expense", label: "Versicherungsaufwand", sign: -1n },
  { key: "operating_expense", label: "Betriebskosten (inkl. Prozess / Maßnahmen)", sign: -1n },
  { key: "capital_contribution", label: "Kapitalzuführung", sign: 1n },
  { key: "capital_distribution", label: "Ausschüttung", sign: -1n },
];
export const str = (row: Row | undefined, key: string, fallback = "0") => String(row?.[key] ?? fallback);
export const num = (row: Row, key: string) => Number(row[key] ?? 0);
export const ids = (row: Row, key: string): number[] => Array.isArray(row[key]) ? row[key] as number[] : [];
export function total(rows: Row[]): Totals {
  return Object.fromEntries(fields.map(key => [key, rows.reduce((sum, row) => sum + amountUnits(str(row, key)), 0n)])) as Totals;
}
export function divided(numerator: bigint, denominator: bigint): bigint | null {
  if (denominator <= 0n) return null;
  const negative = numerator < 0n, n = negative ? -numerator : numerator;
  let quotient = n / denominator;
  const twice = (n % denominator) * 2n;
  if (twice > denominator || (twice === denominator && quotient % 2n === 1n)) quotient++;
  return negative ? -quotient : quotient;
}
export const ratio = (numerator: bigint, denominator: bigint) => divided(numerator * 1000000n, denominator);
export const raw = (units: bigint) => `${units < 0n ? "-" : ""}${(units < 0n ? -units : units) / 10000n}.${((units < 0n ? -units : units) % 10000n).toString().padStart(4, "0")}`;

export function indexResult(result: ExplorerResult) {
  return Object.fromEntries((["baseline", "variant"] as Side[]).map(side => {
    const index = new Map<number, Row[]>();
    for (const row of result.sides[side].financial_rows) {
      const period = num(row, "period"); if (!index.has(period)) index.set(period, []);
      index.get(period)!.push(row);
    }
    return [side, index];
  })) as Record<Side, Map<number, Row[]>>;
}
export type FinancialIndex = ReturnType<typeof indexResult>;
export function sectorRows(index: FinancialIndex, side: Side, period: number, sector: string) {
  return (index[side].get(period) || []).filter(row => sector === "total" || row.sector_id === sector);
}
export function selectedRows(result: ExplorerResult, rows: Row[], group: string) {
  const [kind, key] = group.split(":", 2);
  if (kind === "family") return rows.filter(row => row.family_id === key);
  if (kind === "insurance") return rows.filter(row => row.insurance_group_id === key);
  if (kind === "peer") {
    const members = new Set(result.peer_groups.find(peer => peer.group_id === key)?.insurer_ids || []);
    return rows.filter(row => members.has(num(row, "insurer_id")));
  }
  return rows;
}
export function actorsIn(rows: Row[]) { return new Set(rows.map(row => num(row, "insurer_id"))); }
export function position(rows: Row[]) {
  const byActor = new Map<number, { premium: bigint; active: boolean; rows: Row[] }>();
  for (const row of rows) {
    const aid = num(row, "insurer_id"), entry = byActor.get(aid) || { premium: 0n, active: false, rows: [] };
    entry.premium += amountUnits(str(row, "premium_income")); entry.active ||= row.active_in_period !== false;
    entry.rows.push(row); byActor.set(aid, entry);
  }
  const denominator = [...byActor.values()].reduce((sum, value) => sum + value.premium, 0n);
  const reason = [...byActor.values()].some(value => value.premium < 0n) ? "Negative Beitragsbasis" : denominator === 0n ? "Beitragsbasis null" : null;
  const squares = [...byActor.values()].reduce((sum, value) => sum + value.premium * value.premium, 0n);
  const entries = [...byActor].map(([aid, value]) => ({ aid, ...value,
    share: reason ? null : ratio(value.premium, denominator),
    rank: reason || !value.active ? null : 1 + [...byActor.values()].filter(other => other.active && other.premium > value.premium).length,
  })).sort((a, b) => a.premium > b.premium ? -1 : a.premium < b.premium ? 1 : a.aid - b.aid);
  return { entries, denominator, reason, hhi: reason ? null : divided(squares * 100000000n, denominator * denominator),
    active: entries.filter(value => value.active).length, registered: entries.length };
}
export function families(rows: Row[]) {
  const groups = new Map<string, Row[]>();
  for (const row of rows) { const fid = str(row, "family_id", ""); if (!groups.has(fid)) groups.set(fid, []); groups.get(fid)!.push(row); }
  return [...groups].map(([fid, members]) => {
    const totals = total(members), values = members.map(row => ratio(amountUnits(str(row,"period_profit")), amountUnits(str(row,"opening_assets")))).filter((value): value is bigint => value !== null);
    return { fid, members: [...actorsIn(members)].sort((a,b)=>a-b), totals, mean: ratio(totals.period_profit, totals.opening_assets),
      minimum: values.length ? values.reduce((a,b)=>a<b?a:b) : null,
      maximum: values.length ? values.reduce((a,b)=>a>b?a:b) : null, valid: values.length, count: members.length };
  }).sort((a,b)=>a.fid.localeCompare(b.fid));
}
export function periodRows(result: ExplorerResult, side: Side, name: string, period: number) {
  return (result.sides[side][name] || []).filter(row => num(row,"period") === period);
}
export function relevantRows(rows: Row[], members: Set<number>, sector: string) {
  return rows.filter(row => (sector === "total" || row.sector_id === sector) &&
    (members.has(num(row,"insurer_id")) || members.has(num(row,"previous_insurer_id"))));
}
export function decodeResult(body: Record<string, unknown>) {
  if (body.transport === "ims.market-row-table.v1") {
    const sides = body.sides as Record<Side, Record<string, { columns: string[]; rows: unknown[][]; missing?: Record<string,string[]> }>>;
    for (const side of ["baseline", "variant"] as Side[]) for (const key of Object.keys(sides[side])) {
      const table = sides[side][key];
      (sides[side] as unknown as Record<string,Row[]>)[key] = table.rows.map((values,i) => Object.fromEntries(table.columns.map((column,j)=>[column,values[j]]).filter(([column])=>!table.missing?.[String(i)]?.includes(column as string))));
    }
  }
  return body as unknown as ExplorerResult;
}
