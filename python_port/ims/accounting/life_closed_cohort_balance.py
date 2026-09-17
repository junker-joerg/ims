"""Deterministic death and capital flows for one closed homogeneous life cohort."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext

from ims.accounting.life_model_balance import LifeBalanceIssue, LifeBalanceRow
from ims.model.life_sector_v3_contract import LIFE_SECTOR_V3_CONTRACT_VERSION
from ims.model.sector_taxonomy import SECTOR_TAXONOMY_VERSION
from ims.model.vdefmd6_population import VDEFMD6_INSURER_COUNT


LIFE_CLOSED_COHORT_INPUT_VERSION = "ims.life-closed-cohort-input.v1"
LIFE_CLOSED_COHORT_RESULT_VERSION = "ims.life-closed-cohort-result.v1"
_AMOUNT_PATTERN = re.compile(r"-?(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,4})?\Z")
_RATE_PATTERN = re.compile(r"(?:0(?:\.[0-9]{1,6})?|1(?:\.0{1,6})?)\Z")
_QUANTUM = Decimal("0.0001")
_DOCUMENT_FIELDS = frozenset((
    "schema_version", "life_sector_contract_schema_version",
    "sector_taxonomy_schema_version", "source_kind", "historical_mapping_status",
    "insurer_id", "sector_id", "opening", "guaranteed_rate_per_period", "periods",
))
_OPENING_AMOUNTS = (
    "opening_backing_assets", "opening_guarantee_liability", "opening_equity",
)
_PERIOD_AMOUNTS = (
    "renewal_premiums_collected", "renewal_liability_allocation",
    "investment_result", "death_benefits_paid", "operating_expense_paid",
    "capital_contribution", "capital_distribution",
)


@dataclass(frozen=True, slots=True)
class LifeClosedCohortRow(LifeBalanceRow):
    renewal_premiums_collected: Decimal
    renewal_liability_allocation: Decimal
    death_liability_release: Decimal
    maturity_liability_release: Decimal


@dataclass(frozen=True, slots=True)
class LifeClosedCohortReport:
    insurer_id: int | None
    requested_period_count: int
    rows: tuple[LifeClosedCohortRow, ...]
    issues: tuple[LifeBalanceIssue, ...]

    def to_dict(self) -> dict[str, object]:
        valid = not self.issues
        return {
            "schema_version": LIFE_CLOSED_COHORT_RESULT_VERSION,
            "input_schema_version": LIFE_CLOSED_COHORT_INPUT_VERSION,
            "life_sector_contract_schema_version": LIFE_SECTOR_V3_CONTRACT_VERSION,
            "status": "ok" if valid else "error",
            "valid": valid,
            "insurer_id": self.insurer_id,
            "sector_id": "life",
            "source_kind": "explicit_scenario",
            "historical_mapping_status": "unresolved",
            "requested_period_count": self.requested_period_count,
            "calculated_period_count": len(self.rows) if valid else 0,
            "rows": [row.to_dict() for row in self.rows] if valid else [],
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "writes_performed": False,
            "runner_invoked": False,
            "simulation_performed": False,
            "statutory_or_solvency_ii_claim": False,
            "historical_full_equality_claim": False,
        }


def _issue(issues: list[LifeBalanceIssue], path: str, code: str, message: str) -> None:
    issues.append(LifeBalanceIssue(path, code, message))


def _exact_fields(
    value: dict, expected: frozenset[str], path: str, issues: list[LifeBalanceIssue]
) -> None:
    actual = {key for key in value if type(key) is str}
    for key in sorted(expected - actual):
        _issue(issues, f"{path}.{key}", "field_missing", f"Pflichtfeld fehlt: {key}")
    for key in sorted(actual - expected):
        _issue(issues, f"{path}.{key}", "field_unknown", f"Unbekanntes Feld: {key}")
    if len(actual) != len(value):
        _issue(issues, path, "field_name_invalid", "Feldnamen muessen Text sein")


def _amount(
    value: object, path: str, issues: list[LifeBalanceIssue], *, signed: bool = False
) -> Decimal | None:
    if type(value) is not str or _AMOUNT_PATTERN.fullmatch(value) is None:
        _issue(issues, path, "decimal_string_required", "Dezimalstring mit hoechstens 12+4 Stellen erforderlich")
        return None
    amount = Decimal(value)
    if not signed and amount < 0:
        _issue(issues, path, "negative_amount", "Betrag darf nicht negativ sein")
        return None
    return amount


def _opening(value: object, issues: list[LifeBalanceIssue]) -> dict[str, Decimal | int]:
    if type(value) is not dict:
        _issue(issues, "$.opening", "object_required", "Anfangsbestand muss ein Objekt sein")
        return {}
    _exact_fields(
        value,
        frozenset(("opening_active_policies", "opening_remaining_periods", *_OPENING_AMOUNTS)),
        "$.opening", issues,
    )
    opening: dict[str, Decimal | int] = {}
    for name in ("opening_active_policies", "opening_remaining_periods"):
        if name not in value:
            continue
        limit = 100 if name == "opening_remaining_periods" else 1_000_000_000
        count = value[name]
        if type(count) is not int or not 1 <= count <= limit:
            _issue(issues, f"$.opening.{name}", "count_invalid", f"Ganzzahl von 1 bis {limit} erforderlich")
        else:
            opening[name] = count
    for name in _OPENING_AMOUNTS:
        if name in value:
            amount = _amount(value[name], f"$.opening.{name}", issues, signed=name == "opening_equity")
            if amount is not None:
                opening[name] = amount
    return opening


def _periods(value: object, issues: list[LifeBalanceIssue]) -> list[dict[str, Decimal | int]]:
    if type(value) is not list or not 1 <= len(value) <= 100:
        _issue(issues, "$.periods", "period_count_invalid", "1 bis 100 Perioden erforderlich")
        return []
    parsed: list[dict[str, Decimal | int]] = []
    expected = frozenset(("period", "deaths", *_PERIOD_AMOUNTS))
    for index, item in enumerate(value):
        path = f"$.periods[{index}]"
        if type(item) is not dict:
            _issue(issues, path, "object_required", "Periodenobjekt erforderlich")
            continue
        _exact_fields(item, expected, path, issues)
        if type(item.get("period")) is not int or item["period"] != index + 1:
            _issue(issues, f"{path}.period", "period_sequence_invalid", "Perioden muessen bei 1 beginnen und lueckenlos folgen")
        row: dict[str, Decimal | int] = {}
        deaths = item.get("deaths")
        if type(deaths) is not int or not 0 <= deaths <= 1_000_000_000:
            _issue(issues, f"{path}.deaths", "death_count_invalid", "Nichtnegative ganze Todesfallzahl erforderlich")
        else:
            row["deaths"] = deaths
        for name in _PERIOD_AMOUNTS:
            if name in item:
                amount = _amount(item[name], f"{path}.{name}", issues, signed=name == "investment_result")
                if amount is not None:
                    row[name] = amount
        if ("renewal_premiums_collected" in row and "renewal_liability_allocation" in row
                and row["renewal_liability_allocation"] > row["renewal_premiums_collected"]):
            _issue(issues, f"{path}.renewal_liability_allocation", "premium_allocation_exceeds_collected", "Zuweisung uebersteigt eingezogene Praemie")
        if row.get("deaths") == 0 and row.get("death_benefits_paid", Decimal(0)) > 0:
            _issue(issues, f"{path}.death_benefits_paid", "death_benefit_without_death", "Todesfallleistung ohne Todesfall unzulaessig")
        parsed.append(row)
    return parsed


def _calculate(
    insurer_id: int, opening: dict[str, Decimal | int], rate: Decimal,
    periods: list[dict[str, Decimal | int]],
) -> LifeClosedCohortReport:
    rows: list[LifeClosedCohortRow] = []
    with localcontext() as context:
        context.prec = 64
        for index, flow in enumerate(periods):
            path = f"$.periods[{index}]"
            issues: list[LifeBalanceIssue] = []
            if opening["opening_active_policies"] == 0:
                _issue(issues, path, "cohort_extinguished", "Geschlossener Bestand ist bereits erloschen")
                return LifeClosedCohortReport(insurer_id, len(periods), (), tuple(issues))
            deaths = flow["deaths"]
            if deaths > opening["opening_active_policies"]:
                _issue(issues, f"{path}.deaths", "deaths_exceed_opening", "Todesfaelle uebersteigen den Anfangsbestand")
                return LifeClosedCohortReport(insurer_id, len(periods), (), tuple(issues))

            guarantee = (opening["opening_guarantee_liability"] * rate).quantize(
                _QUANTUM, rounding=ROUND_HALF_EVEN
            )
            liability_before_exit = (
                opening["opening_guarantee_liability"] + guarantee
                + flow["renewal_liability_allocation"]
            )
            if deaths == opening["opening_active_policies"]:
                death_release = liability_before_exit
            else:
                death_release = (
                    liability_before_exit * deaths / opening["opening_active_policies"]
                ).quantize(_QUANTUM, rounding=ROUND_HALF_EVEN)
            survivors = opening["opening_active_policies"] - deaths
            final_period = opening["opening_remaining_periods"] == 1
            maturities = survivors if final_period else 0
            maturity_release = liability_before_exit - death_release if final_period else Decimal(0)
            release = death_release + maturity_release
            closing_liability = liability_before_exit - release
            closing_assets = (
                opening["opening_backing_assets"] + flow["renewal_premiums_collected"]
                + flow["investment_result"] + flow["capital_contribution"]
                - flow["death_benefits_paid"] - maturity_release
                - flow["operating_expense_paid"] - flow["capital_distribution"]
            )
            profit = (
                flow["renewal_premiums_collected"] + flow["investment_result"]
                - flow["death_benefits_paid"] - maturity_release
                - flow["operating_expense_paid"]
                - (closing_liability - opening["opening_guarantee_liability"])
            )
            closing_equity = (
                opening["opening_equity"] + profit
                + flow["capital_contribution"] - flow["capital_distribution"]
            )
            if closing_assets < 0:
                _issue(issues, path, "negative_closing_assets", "Deckende Vermoegenswerte waeren negativ")
            if closing_liability < 0:
                _issue(issues, path, "negative_closing_liability", "Garantieverpflichtung waere negativ")
            if closing_assets != closing_liability + closing_equity:
                _issue(issues, path, "closing_identity_invalid", "Schlussbilanz ist nicht ausgeglichen")
            if issues:
                return LifeClosedCohortReport(insurer_id, len(periods), (), tuple(issues))

            zero = Decimal(0)
            closing_policies = 0 if final_period else survivors
            closing_remaining = 0 if closing_policies == 0 else opening["opening_remaining_periods"] - 1
            rows.append(LifeClosedCohortRow(
                period=index + 1,
                **opening,
                guaranteed_rate_per_period=rate,
                premiums_collected=flow["renewal_premiums_collected"],
                investment_result=flow["investment_result"],
                death_benefits_paid=flow["death_benefits_paid"],
                maturity_benefits_paid=maturity_release,
                surrender_benefits_paid=zero,
                operating_expense_paid=flow["operating_expense_paid"],
                capital_contribution=flow["capital_contribution"],
                capital_distribution=flow["capital_distribution"],
                premium_liability_allocation=flow["renewal_liability_allocation"],
                guarantee_accretion=guarantee,
                bonus_accretion=zero,
                liability_release=release,
                deaths=deaths,
                maturities=maturities,
                surrenders=0,
                period_profit=profit,
                closing_active_policies=closing_policies,
                closing_remaining_periods=closing_remaining,
                closing_backing_assets=closing_assets,
                closing_guarantee_liability=closing_liability,
                closing_equity=closing_equity,
                renewal_premiums_collected=flow["renewal_premiums_collected"],
                renewal_liability_allocation=flow["renewal_liability_allocation"],
                death_liability_release=death_release,
                maturity_liability_release=maturity_release,
            ))
            opening = {
                "opening_active_policies": closing_policies,
                "opening_remaining_periods": closing_remaining,
                "opening_backing_assets": closing_assets,
                "opening_guarantee_liability": closing_liability,
                "opening_equity": closing_equity,
            }
    return LifeClosedCohortReport(insurer_id, len(periods), tuple(rows), ())


def build_life_closed_cohort_balance(value: object) -> LifeClosedCohortReport:
    """Validate all explicit inputs and return either all rows or none."""

    issues: list[LifeBalanceIssue] = []
    if type(value) is not dict:
        _issue(issues, "$", "object_required", "Lebensfall-Eingang muss ein Objekt sein")
        return LifeClosedCohortReport(None, 0, (), tuple(issues))
    _exact_fields(value, _DOCUMENT_FIELDS, "$", issues)
    for name, expected in (
        ("schema_version", LIFE_CLOSED_COHORT_INPUT_VERSION),
        ("life_sector_contract_schema_version", LIFE_SECTOR_V3_CONTRACT_VERSION),
        ("sector_taxonomy_schema_version", SECTOR_TAXONOMY_VERSION),
        ("source_kind", "explicit_scenario"),
        ("historical_mapping_status", "unresolved"),
        ("sector_id", "life"),
    ):
        if value.get(name) != expected:
            _issue(issues, f"$.{name}", "contract_value_mismatch", f"{name} muss {expected!r} sein")
    insurer_id = value.get("insurer_id")
    if type(insurer_id) is not int or not 1 <= insurer_id <= VDEFMD6_INSURER_COUNT:
        _issue(issues, "$.insurer_id", "insurer_id_invalid", "Vdefmd6-VU-ID von 1 bis 25 erforderlich")
        insurer_id = None
    opening = _opening(value.get("opening"), issues)
    raw_rate = value.get("guaranteed_rate_per_period")
    if type(raw_rate) is not str or _RATE_PATTERN.fullmatch(raw_rate) is None:
        _issue(issues, "$.guaranteed_rate_per_period", "rate_invalid", "Garantiesatz von 0 bis 1 mit hoechstens sechs Dezimalstellen erforderlich")
        rate = None
    else:
        rate = Decimal(raw_rate)
    raw_periods = value.get("periods")
    requested_count = len(raw_periods) if type(raw_periods) is list else 0
    periods = _periods(raw_periods, issues)
    if "opening_remaining_periods" in opening and requested_count > opening["opening_remaining_periods"]:
        _issue(issues, "$.periods", "periods_exceed_remaining_term", "Perioden ueberschreiten die Restlaufzeit")
    if issues:
        return LifeClosedCohortReport(insurer_id, requested_count, (), tuple(issues))
    assert insurer_id is not None and rate is not None
    with localcontext() as context:
        context.prec = 64
        if opening["opening_backing_assets"] != opening["opening_guarantee_liability"] + opening["opening_equity"]:
            _issue(issues, "$.opening", "opening_identity_invalid", "Vermoegen muss Garantieverpflichtung plus Eigenkapital sein")
            return LifeClosedCohortReport(insurer_id, requested_count, (), tuple(issues))
    return _calculate(insurer_id, opening, rate, periods)
