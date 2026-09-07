from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

from ims.strategies.assignment_snapshot_translation import (
    translate_strategy_assignment_draft,
)
from ims.strategies.assignment_vu_snapshot_materialization_contract import (
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION,
    VU_SNAPSHOT_MATERIALIZATION_TARGETS,
    strategy_vu_snapshot_materialization_contract_issues,
)
from ims.strategies.assignment_vu_snapshot_materialization_validation import (
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION,
    STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION,
    validate_strategy_assignment_vu_snapshot_materialization_input,
)
from ims.strategies.catalog import StrategyActorType


STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VERSION = (
    "ims.strategy-assignment-vu-snapshot-state.v1"
)
STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VALIDATION_VERSION = (
    "ims.strategy-assignment-vu-snapshot-state-validation.v1"
)

_REQUEST_FIELDS = frozenset({"input", "state"})
_STATE_FIELDS = frozenset(
    {
        "schema_version",
        "input_schema_version",
        "base_model",
        "scope",
        "draft_id",
        "period",
        "period_state",
        "entries",
    }
)
_PERIOD_STATE_FIELDS = frozenset(
    {"interest_rate", "change_shock", "active_policyholder_count"}
)
_ENTRY_FIELDS = frozenset({"insurer_id", "strategy_id", "values"})
_ALL_VU_STRATEGY_IDS = tuple(f"vu.vrvu{index:02d}" for index in range(1, 11))
_STATE_VALUE_FIELDS_BY_STRATEGY = {
    strategy_id: () for strategy_id in _ALL_VU_STRATEGY_IDS
}
_STATE_VALUE_FIELDS_BY_STRATEGY.update(
    {
        "vu.vrvu03": ("aspiration_sector_1", "aspiration_sector_2"),
        "vu.vrvu04": (
            "aspiration_sector_1",
            "aspiration_sector_2",
            "policyholders_t_minus_2",
        ),
        "vu.vrvu05": ("aspiration_sector_1", "aspiration_sector_2"),
    }
)


@dataclass(frozen=True, slots=True)
class VUStateProvenanceDefinition:
    context_field: str
    state_path: str
    strategy_ids: tuple[str, ...]
    historical_source: str
    python_source: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


VU_STATE_PROVENANCE_DEFINITIONS = (
    VUStateProvenanceDefinition(
        "interest_rate",
        "period_state.interest_rate",
        _ALL_VU_STRATEGY_IDS,
        "IMS.E: z = Zins[gperiod]",
        "Vdefmd6VUPeriodInput.interest_rate",
    ),
    VUStateProvenanceDefinition(
        "change_shock",
        "period_state.change_shock",
        _ALL_VU_STRATEGY_IDS,
        "IMS.E: aenderung",
        "Vdefmd6VUPeriodInput.change_shock",
    ),
    VUStateProvenanceDefinition(
        "reserve_thresholds",
        "entries.values.aspiration_sector_1/2[0]",
        ("vu.vrvu03",),
        "IMS.E: A1[1], A2[1]",
        "Vdefmd6InsurerDefinition.aspiration_sector_1/2[0]",
    ),
    VUStateProvenanceDefinition(
        "net_switcher_thresholds",
        "entries.values.aspiration_sector_1/2[1]",
        ("vu.vrvu04",),
        "IMS.E: A1[2], A2[2]",
        "Vdefmd6InsurerDefinition.aspiration_sector_1/2[1]",
    ),
    VUStateProvenanceDefinition(
        "previous_policyholders_sector",
        "entries.values.policyholders_t_minus_2",
        ("vu.vrvu04",),
        "IMS.E: Vn[gperiod-2]",
        "Insurer.policyholders_prev_sector",
    ),
    VUStateProvenanceDefinition(
        "market_share_thresholds",
        "entries.values.aspiration_sector_1/2[2]",
        ("vu.vrvu05",),
        "IMS.E: A1[3], A2[3]",
        "Vdefmd6InsurerDefinition.aspiration_sector_1/2[2]",
    ),
    VUStateProvenanceDefinition(
        "active_policyholder_count",
        "period_state.active_policyholder_count",
        ("vu.vrvu05",),
        "IMS.E: akvn",
        "BAV activity_state.active_policyholder_count_current",
    ),
)

_TARGETS_BY_ID = {
    target.strategy_id: target for target in VU_SNAPSHOT_MATERIALIZATION_TARGETS
}


@dataclass(frozen=True, slots=True)
class VUSnapshotStateValidationIssue:
    stage: str
    path: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class VUSnapshotStateValidationReport:
    valid: bool
    input_valid: bool
    state_shape_valid: bool
    submitted_state_schema_version: str | None
    draft_id: str | None
    period: int | None
    expected_state_entry_count: int
    validated_state_entry_count: int
    expected_provenance_check_count: int
    matched_provenance_check_count: int
    expected_threshold_check_count: int
    matched_threshold_check_count: int
    issues: tuple[VUSnapshotStateValidationIssue, ...]
    schema_version: str = STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VALIDATION_VERSION
    mode: str = "strategy_assignment_vu_snapshot_state_validation"

    def to_dict(self) -> dict[str, object]:
        threshold_cross_check_complete = (
            self.expected_threshold_check_count > 0
            and self.expected_threshold_check_count
            == self.matched_threshold_check_count
        )
        return {
            "schema_version": self.schema_version,
            "mode": self.mode,
            "status": "ok" if self.valid else "error",
            "valid": self.valid,
            "input_valid": self.input_valid,
            "state_shape_valid": self.state_shape_valid,
            "submitted_state_schema_version": self.submitted_state_schema_version,
            "draft_id": self.draft_id,
            "period": self.period,
            "expected_state_entry_count": self.expected_state_entry_count,
            "validated_state_entry_count": self.validated_state_entry_count,
            "expected_provenance_check_count": self.expected_provenance_check_count,
            "matched_provenance_check_count": self.matched_provenance_check_count,
            "expected_threshold_check_count": self.expected_threshold_check_count,
            "matched_threshold_check_count": self.matched_threshold_check_count,
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "threshold_values_cross_checked_against_actor_state": (
                threshold_cross_check_complete
            ),
            "draw_values_cross_checked_against_draw_plan": False,
            "state_values_inspected": self.input_valid and self.state_shape_valid,
            "state_values_consumed": False,
            "snapshot_loader_invocation_performed": False,
            "snapshot_materialization_ready": False,
            "writes_performed": False,
            "snapshots_created": False,
            "execution_performed": False,
            "simulation_performed": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
        }


class _StateContractError(ValueError):
    def __init__(self, path: str, code: str, message: str) -> None:
        super().__init__(message)
        self.path = path
        self.code = code


def _issue(
    *,
    stage: str,
    path: str,
    code: str,
    message: str,
) -> VUSnapshotStateValidationIssue:
    return VUSnapshotStateValidationIssue(stage, path, code, message)


def _report(
    *,
    valid: bool = False,
    input_valid: bool = False,
    state_shape_valid: bool = False,
    submitted_state_schema_version: str | None = None,
    draft_id: str | None = None,
    period: int | None = None,
    expected_state_entry_count: int = 0,
    validated_state_entry_count: int = 0,
    expected_provenance_check_count: int = 0,
    matched_provenance_check_count: int = 0,
    expected_threshold_check_count: int = 0,
    matched_threshold_check_count: int = 0,
    issues: list[VUSnapshotStateValidationIssue],
) -> VUSnapshotStateValidationReport:
    return VUSnapshotStateValidationReport(
        valid=valid,
        input_valid=input_valid,
        state_shape_valid=state_shape_valid,
        submitted_state_schema_version=submitted_state_schema_version,
        draft_id=draft_id,
        period=period,
        expected_state_entry_count=expected_state_entry_count,
        validated_state_entry_count=validated_state_entry_count,
        expected_provenance_check_count=expected_provenance_check_count,
        matched_provenance_check_count=matched_provenance_check_count,
        expected_threshold_check_count=expected_threshold_check_count,
        matched_threshold_check_count=matched_threshold_check_count,
        issues=tuple(issues),
    )


def _object(
    value: object,
    fields: frozenset[str],
    *,
    path: str,
    noun: str,
) -> dict[str, object]:
    if not isinstance(value, dict):
        raise _StateContractError(
            path,
            "state_object_required",
            f"{noun} muss ein Objekt sein",
        )
    missing = fields - set(value)
    unknown = set(value) - fields
    if missing or unknown:
        detail = (
            f"fehlend: {', '.join(sorted(missing))}"
            if missing
            else f"unbekannt: {', '.join(sorted(unknown))}"
        )
        raise _StateContractError(
            path,
            "state_fields_mismatch",
            f"Felder in {noun} stimmen nicht exakt ({detail})",
        )
    return value


def _finite(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _number_array(
    value: object,
    length: int,
    *,
    non_negative: bool = False,
) -> bool:
    if not isinstance(value, list) or len(value) != length:
        return False
    if not all(_finite(item) for item in value):
        return False
    return not non_negative or all(float(item) >= 0.0 for item in value)


def _require_value(condition: bool, *, path: str, message: str) -> None:
    if not condition:
        raise _StateContractError(path, "state_value_shape_invalid", message)


def _load_state(
    value: object,
    *,
    draft_id: str,
    period: int,
    expected_entries: dict[int, str],
) -> tuple[dict[str, object], dict[int, dict[str, object]], str | None]:
    state = _object(value, _STATE_FIELDS, path="$.state", noun="state")
    submitted_version = (
        state["schema_version"] if isinstance(state["schema_version"], str) else None
    )
    exact_values = {
        "schema_version": STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VERSION,
        "input_schema_version": (
            STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION
        ),
        "base_model": "Vdefmd6",
        "scope": "vu_snapshot_materialization_provenance_state",
        "draft_id": draft_id,
    }
    for field_name, expected in exact_values.items():
        if state[field_name] != expected:
            raise _StateContractError(
                f"$.state.{field_name}",
                "state_contract_value_mismatch",
                f"{field_name} muss {expected!r} sein",
            )
    if (
        not isinstance(state["period"], int)
        or isinstance(state["period"], bool)
        or state["period"] != period
    ):
        raise _StateContractError(
            "$.state.period",
            "state_contract_value_mismatch",
            f"period muss {period!r} sein",
        )

    period_state = _object(
        state["period_state"],
        _PERIOD_STATE_FIELDS,
        path="$.state.period_state",
        noun="period_state",
    )
    _require_value(
        _finite(period_state["interest_rate"]),
        path="$.state.period_state.interest_rate",
        message="interest_rate muss eine endliche Zahl sein",
    )
    _require_value(
        isinstance(period_state["change_shock"], bool),
        path="$.state.period_state.change_shock",
        message="change_shock muss ein boolescher Wert sein",
    )
    active_count = period_state["active_policyholder_count"]
    _require_value(
        isinstance(active_count, int)
        and not isinstance(active_count, bool)
        and active_count >= 0,
        path="$.state.period_state.active_policyholder_count",
        message="active_policyholder_count muss eine nicht negative Ganzzahl sein",
    )

    raw_entries = state["entries"]
    if not isinstance(raw_entries, list):
        raise _StateContractError(
            "$.state.entries",
            "state_entries_list_required",
            "entries muss eine Liste sein",
        )
    entries: dict[int, dict[str, object]] = {}
    for index, value_entry in enumerate(raw_entries):
        path = f"$.state.entries[{index}]"
        entry = _object(value_entry, _ENTRY_FIELDS, path=path, noun="state entry")
        insurer_id = entry["insurer_id"]
        if (
            not isinstance(insurer_id, int)
            or isinstance(insurer_id, bool)
            or insurer_id < 1
        ):
            raise _StateContractError(
                f"{path}.insurer_id",
                "state_insurer_id_invalid",
                "insurer_id muss eine positive Ganzzahl sein",
            )
        if insurer_id in entries:
            raise _StateContractError(
                f"{path}.insurer_id",
                "duplicate_state_entry",
                "VU besitzt bereits einen Zustandseintrag",
            )
        expected_strategy = expected_entries.get(insurer_id)
        if expected_strategy is None:
            raise _StateContractError(
                f"{path}.insurer_id",
                "state_target_not_in_input",
                "VU ist im validierten Eingang nicht enthalten",
            )
        if entry["strategy_id"] != expected_strategy:
            raise _StateContractError(
                f"{path}.strategy_id",
                "state_strategy_id_mismatch",
                "Zustandsstrategie stimmt nicht mit dem Eingang ueberein",
            )

        expected_value_fields = frozenset(
            _STATE_VALUE_FIELDS_BY_STRATEGY[expected_strategy]
        )
        state_values = _object(
            entry["values"],
            expected_value_fields,
            path=f"{path}.values",
            noun="state values",
        )
        for field_name in ("aspiration_sector_1", "aspiration_sector_2"):
            if field_name in expected_value_fields:
                _require_value(
                    _number_array(state_values[field_name], 3),
                    path=f"{path}.values.{field_name}",
                    message=f"{field_name} muss drei endliche Zahlen enthalten",
                )
        if "policyholders_t_minus_2" in expected_value_fields:
            _require_value(
                _number_array(
                    state_values["policyholders_t_minus_2"],
                    2,
                    non_negative=True,
                ),
                path=f"{path}.values.policyholders_t_minus_2",
                message=(
                    "policyholders_t_minus_2 muss zwei nicht negative endliche "
                    "Zahlen enthalten"
                ),
            )
        entries[insurer_id] = entry

    missing_ids = set(expected_entries) - set(entries)
    if missing_ids:
        insurer_id = min(missing_ids)
        raise _StateContractError(
            "$.state.entries",
            "state_entry_missing",
            f"VU-Zustandseintrag fehlt fuer insurer {insurer_id}",
        )
    return period_state, entries, submitted_version


def _expected_check_counts(strategy_ids: tuple[str, ...]) -> tuple[int, int]:
    expected = sum(
        strategy_id in definition.strategy_ids
        for strategy_id in strategy_ids
        for definition in VU_STATE_PROVENANCE_DEFINITIONS
    )
    threshold_fields = {
        "reserve_thresholds",
        "net_switcher_thresholds",
        "market_share_thresholds",
    }
    thresholds = sum(
        strategy_id in definition.strategy_ids
        and definition.context_field in threshold_fields
        for strategy_id in strategy_ids
        for definition in VU_STATE_PROVENANCE_DEFINITIONS
    )
    return expected, thresholds


def _compare(
    actual: object,
    expected: object,
    *,
    path: str,
    code: str,
    message: str,
    issues: list[VUSnapshotStateValidationIssue],
) -> bool:
    if actual == expected:
        return True
    issues.append(
        _issue(
            stage="state_provenance",
            path=path,
            code=code,
            message=message,
        )
    )
    return False


def validate_strategy_assignment_vu_snapshot_state(
    value: object,
) -> VUSnapshotStateValidationReport:
    """Prueft VU-Kontextwerte gegen expliziten Zustand, ohne sie zu verwenden."""

    if not isinstance(value, dict):
        return _report(
            issues=[
                _issue(
                    stage="request_contract",
                    path="$",
                    code="request_object_required",
                    message="VU-Zustandspruefung muss ein Objekt sein",
                )
            ]
        )
    if set(value) != _REQUEST_FIELDS:
        return _report(
            issues=[
                _issue(
                    stage="request_contract",
                    path="$",
                    code="request_fields_mismatch",
                    message="VU-Zustandsanfrage benoetigt exakt input und state",
                )
            ]
        )

    input_value = value["input"]
    input_report = validate_strategy_assignment_vu_snapshot_materialization_input(
        input_value
    )
    input_issues = []
    for issue in input_report.issues:
        suffix = issue.path[1:] if issue.path.startswith("$") else f".{issue.path}"
        input_issues.append(
            _issue(
                stage="materialization_input",
                path=f"$.input{suffix}",
                code=issue.code,
                message=issue.message,
            )
        )
    if not input_report.valid:
        return _report(
            draft_id=input_report.draft_id,
            period=input_report.period,
            expected_state_entry_count=input_report.expected_vu_entry_count,
            issues=input_issues,
        )

    assert isinstance(input_value, dict)
    assert input_report.draft_id is not None
    assert input_report.period is not None
    translation = translate_strategy_assignment_draft(input_value["draft"])
    vu_entries = tuple(
        entry
        for entry in translation.entries
        if entry.assignment.actor_type is StrategyActorType.INSURER
    )
    expected_entries = {
        entry.assignment.target_id: entry.assignment.strategy_id for entry in vu_entries
    }
    strategy_ids = tuple(expected_entries.values())
    expected_checks, expected_threshold_checks = _expected_check_counts(strategy_ids)

    submitted_version = None
    if isinstance(value["state"], dict):
        candidate = value["state"].get("schema_version")
        submitted_version = candidate if isinstance(candidate, str) else None
    try:
        period_state, state_entries, submitted_version = _load_state(
            value["state"],
            draft_id=input_report.draft_id,
            period=input_report.period,
            expected_entries=expected_entries,
        )
    except _StateContractError as exc:
        return _report(
            input_valid=True,
            submitted_state_schema_version=submitted_version,
            draft_id=input_report.draft_id,
            period=input_report.period,
            expected_state_entry_count=len(vu_entries),
            expected_provenance_check_count=expected_checks,
            expected_threshold_check_count=expected_threshold_checks,
            issues=[
                _issue(
                    stage="state_contract",
                    path=exc.path,
                    code=exc.code,
                    message=str(exc),
                )
            ],
        )

    context = input_value["context"]
    assert isinstance(context, dict)
    context_entries = {
        entry["target_id"]: (index, entry)
        for index, entry in enumerate(context["entries"])
        if entry["actor_type"] == StrategyActorType.INSURER.value
    }
    issues: list[VUSnapshotStateValidationIssue] = []
    matched = 0
    matched_thresholds = 0
    for insurer_id, strategy_id in expected_entries.items():
        context_index, context_entry = context_entries[insurer_id]
        context_values = context_entry["values"]
        state_values = state_entries[insurer_id]["values"]
        assert isinstance(context_values, dict)
        assert isinstance(state_values, dict)
        path = f"$.input.context.entries[{context_index}].values"

        matched += _compare(
            context_values["interest_rate"],
            period_state["interest_rate"],
            path=f"{path}.interest_rate",
            code="period_state_mismatch",
            message="interest_rate stimmt nicht mit dem Periodenzustand ueberein",
            issues=issues,
        )
        matched += _compare(
            context_values["change_shock"],
            period_state["change_shock"],
            path=f"{path}.change_shock",
            code="period_state_mismatch",
            message="change_shock stimmt nicht mit dem Periodenzustand ueberein",
            issues=issues,
        )

        threshold_field = None
        threshold_index = None
        if strategy_id == "vu.vrvu03":
            threshold_field, threshold_index = "reserve_thresholds", 0
        elif strategy_id == "vu.vrvu04":
            threshold_field, threshold_index = "net_switcher_thresholds", 1
        elif strategy_id == "vu.vrvu05":
            threshold_field, threshold_index = "market_share_thresholds", 2
        if threshold_field is not None and threshold_index is not None:
            expected_thresholds = [
                state_values["aspiration_sector_1"][threshold_index],
                state_values["aspiration_sector_2"][threshold_index],
            ]
            threshold_matches = _compare(
                context_values[threshold_field],
                expected_thresholds,
                path=f"{path}.{threshold_field}",
                code="threshold_source_mismatch",
                message=(
                    f"{threshold_field} stimmt nicht mit dem Anspruchsprofil "
                    "des VU ueberein"
                ),
                issues=issues,
            )
            matched += threshold_matches
            matched_thresholds += threshold_matches

        if strategy_id == "vu.vrvu04":
            matched += _compare(
                context_values["previous_policyholders_sector"],
                state_values["policyholders_t_minus_2"],
                path=f"{path}.previous_policyholders_sector",
                code="previous_state_mismatch",
                message=(
                    "previous_policyholders_sector stimmt nicht mit dem "
                    "VU-Bestand t-2 ueberein"
                ),
                issues=issues,
            )
        elif strategy_id == "vu.vrvu05":
            matched += _compare(
                context_values["active_policyholder_count"],
                period_state["active_policyholder_count"],
                path=f"{path}.active_policyholder_count",
                code="market_state_mismatch",
                message=(
                    "active_policyholder_count stimmt nicht mit dem "
                    "Periodenzustand ueberein"
                ),
                issues=issues,
            )

    valid = not issues and matched == expected_checks
    return _report(
        valid=valid,
        input_valid=True,
        state_shape_valid=True,
        submitted_state_schema_version=submitted_version,
        draft_id=input_report.draft_id,
        period=input_report.period,
        expected_state_entry_count=len(vu_entries),
        validated_state_entry_count=len(state_entries),
        expected_provenance_check_count=expected_checks,
        matched_provenance_check_count=matched,
        expected_threshold_check_count=expected_threshold_checks,
        matched_threshold_check_count=matched_thresholds,
        issues=issues,
    )


def strategy_vu_snapshot_state_contract_issues() -> tuple[str, ...]:
    """Prueft die Herkunftsdefinitionen gegen den PR118-Zielbestand."""

    issues = list(strategy_vu_snapshot_materialization_contract_issues())
    if set(_STATE_VALUE_FIELDS_BY_STRATEGY) != set(_TARGETS_BY_ID):
        issues.append("VU-Zustandsvertrag deckt die Snapshotziele nicht exakt ab")
    for definition in VU_STATE_PROVENANCE_DEFINITIONS:
        for strategy_id in definition.strategy_ids:
            target = _TARGETS_BY_ID.get(strategy_id)
            if target is None:
                issues.append(
                    f"VU-Herkunft referenziert unbekannte Strategie: {strategy_id}"
                )
            elif definition.context_field not in target.open_snapshot_fields:
                issues.append(
                    "VU-Herkunft referenziert kein offenes Kontextfeld: "
                    f"{strategy_id}.{definition.context_field}"
                )
    return tuple(issues)


def strategy_assignment_vu_snapshot_state_contract_payload() -> dict[str, Any]:
    """Beschreibt den PR120-Zustandsbeleg und seine geschlossenen Grenzen."""

    return {
        "schema_version": STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VALIDATION_VERSION,
        "state_schema_version": STRATEGY_ASSIGNMENT_VU_SNAPSHOT_STATE_VERSION,
        "materialization_input_schema_version": (
            STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_INPUT_VERSION
        ),
        "materialization_validation_schema_version": (
            STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_VALIDATION_VERSION
        ),
        "inventory_contract_schema_version": (
            STRATEGY_ASSIGNMENT_VU_SNAPSHOT_MATERIALIZATION_CONTRACT_VERSION
        ),
        "mode": "strategy_assignment_vu_snapshot_state_contract_read_only",
        "base_model": "Vdefmd6",
        "scope": "vu_snapshot_materialization_provenance_state",
        "validation_endpoint": (
            "/api/strategies/assignment-vu-snapshot-state-validation"
        ),
        "request_fields": tuple(sorted(_REQUEST_FIELDS)),
        "state_document_fields": tuple(sorted(_STATE_FIELDS)),
        "period_state_fields": tuple(sorted(_PERIOD_STATE_FIELDS)),
        "state_entry_fields": tuple(sorted(_ENTRY_FIELDS)),
        "state_value_fields_by_strategy": dict(_STATE_VALUE_FIELDS_BY_STRATEGY),
        "provenance_definitions": [
            definition.to_dict() for definition in VU_STATE_PROVENANCE_DEFINITIONS
        ],
        "validated_strategy_count": len(_STATE_VALUE_FIELDS_BY_STRATEGY),
        "provenance_definition_count": len(VU_STATE_PROVENANCE_DEFINITIONS),
        "contract_issue_count": len(strategy_vu_snapshot_state_contract_issues()),
        "exact_vu_entry_match_required": True,
        "exact_state_field_match_required": True,
        "threshold_values_cross_checked_against_actor_state": True,
        "previous_policyholders_cross_checked_against_actor_state": True,
        "active_policyholder_count_cross_checked_against_period_state": True,
        "draw_values_cross_checked_against_draw_plan": False,
        "state_values_consumed": False,
        "snapshot_loader_invocation_enabled": False,
        "snapshot_materialization_enabled": False,
        "persistence_enabled": False,
        "runner_enabled": False,
        "execution_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
