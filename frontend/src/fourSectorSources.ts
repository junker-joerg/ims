export type ScenarioSide = "baseline" | "variant";

export type CheckedSectorInput = {
  input: unknown;
  insurerId: number;
  periodCount: number;
  evidenceDigest: string;
  scenarioId?: string;
  variantId?: ScenarioSide;
};

export type CheckedNonLife = Record<"motor" | "property_liability", CheckedSectorInput>;
export type CheckedSides = Record<ScenarioSide, CheckedSectorInput>;
