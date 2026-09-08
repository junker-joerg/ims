from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from ims.io.scenario_loader import (
    LoadedScenario,
    ScenarioValidationError,
    load_scenario_from_mapping,
)
from ims.strategies.assignment_snapshot_materialization import (
    materialize_strategy_assignment_snapshots,
)
from ims.strategies.assignment_vu_snapshot_materialization import (
    materialize_strategy_assignment_vu_snapshots,
)
from ims.strategies.execution_candidate_contract import (
    STRATEGY_EXECUTION_CANDIDATE_COLLECTIONS,
    STRATEGY_EXECUTION_CANDIDATE_CONTRACT_VERSION,
    STRATEGY_EXECUTION_CANDIDATE_VERSION,
    strategy_execution_candidate_contract_payload,
)
from ims.strategies.execution_candidate_validation import (
    STRATEGY_EXECUTION_CANDIDATE_INPUT_VERSION,
    STRATEGY_EXECUTION_CANDIDATE_VALIDATION_VERSION,
    STRATEGY_EXECUTION_VN_PROCESS_DRAW_SOURCE_POLICY_ID,
    validate_strategy_execution_candidate_input,
)


STRATEGY_EXECUTION_CANDIDATE_BUILD_VERSION = (
    "ims.strategy-execution-candidate-build.v1"
)
STRATEGY_EXECUTION_SCENARIO_PROFILE_VERSION = (
    "ims.strategy-execution-scenario-profile.v1"
)
STRATEGY_EXECUTION_SCENARIO_PROFILE_SCOPE = (
    "single_period_joint_vu_vn_market_ground_state"
)
STRATEGY_EXECUTION_CANDIDATE_DIGEST_ALGORITHM = "sha256"
DEFAULT_STRATEGY_EXECUTION_SCENARIO_PROFILE_ID = (
    "synthetic-joint-single-period-v1"
)

_PROFILE_FIELDS = frozenset(
    {
        "schema_version",
        "profile_id",
        "base_model",
        "scope",
        "period",
        "context",
        "bav",
        "insurers",
        "policyholders",
    }
)
_VU_COLLECTION_NAMES = tuple(
    definition.collection_name
    for definition in STRATEGY_EXECUTION_CANDIDATE_COLLECTIONS
    if definition.actor_scope == "insurer"
)
_VN_RULE_COLLECTION_NAMES = tuple(
    definition.collection_name
    for definition in STRATEGY_EXECUTION_CANDIDATE_COLLECTIONS
    if definition.snapshot_role == "vn_strategy_rule"
)
_VN_PROCESS_COLLECTION_NAMES = tuple(
    definition.collection_name
    for definition in STRATEGY_EXECUTION_CANDIDATE_COLLECTIONS
    if definition.alternative_group == "vn_process"
)


@dataclass(frozen=True, slots=True)
class StrategyExecutionScenarioProfileDefinition:
    """Serverseitige Zuordnung einer stabilen ID zu einem lokalen Profil."""

    profile_id: str
    path: Path


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateBuildIssue:
    stage: str
    path: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidate:
    candidate_id: str
    draft_id: str
    period: int
    content_digest: str
    profile_id: str
    profile_content_digest: str
    sections: dict[str, object]
    loaded_scenario: LoadedScenario = field(repr=False, compare=False)
    schema_version: str = STRATEGY_EXECUTION_CANDIDATE_VERSION
    mode: str = "strategy_execution_candidate"

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "mode": self.mode,
            "identity": {
                "candidate_id": self.candidate_id,
                "draft_id": self.draft_id,
                "period": self.period,
                "content_digest": self.content_digest,
            },
            **deepcopy(self.sections),
        }


@dataclass(frozen=True, slots=True)
class StrategyExecutionCandidateBuildReport:
    input_valid: bool
    draft_id: str | None
    period: int | None
    profile_id: str | None
    profile_resolved: bool
    profile_content_digest: str | None
    rematerialization_attempted: bool
    vu_materialization_complete: bool
    vn_materialization_complete: bool
    canonical_scenario_loaded: bool
    expected_vu_snapshot_count: int
    vu_snapshot_count: int
    expected_vn_snapshot_count: int
    vn_snapshot_count: int
    vn_process_snapshot_count: int
    rematerialization_snapshot_loader_invocation_count: int
    candidate: StrategyExecutionCandidate | None
    issues: tuple[StrategyExecutionCandidateBuildIssue, ...]
    schema_version: str = STRATEGY_EXECUTION_CANDIDATE_BUILD_VERSION
    mode: str = "strategy_execution_candidate_build"

    @property
    def build_complete(self) -> bool:
        return (
            self.input_valid
            and self.profile_resolved
            and self.vu_materialization_complete
            and self.vn_materialization_complete
            and self.canonical_scenario_loaded
            and not self.issues
            and self.candidate is not None
        )

    def to_dict(self) -> dict[str, object]:
        candidate_created = self.candidate is not None
        return {
            "schema_version": self.schema_version,
            "input_schema_version": STRATEGY_EXECUTION_CANDIDATE_INPUT_VERSION,
            "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
            "mode": self.mode,
            "status": "ok" if self.build_complete else "error",
            "build_complete": self.build_complete,
            "input_valid": self.input_valid,
            "draft_id": self.draft_id,
            "period": self.period,
            "profile_id": self.profile_id,
            "profile_content_digest": self.profile_content_digest,
            "expected_vu_snapshot_count": self.expected_vu_snapshot_count,
            "vu_snapshot_count": self.vu_snapshot_count,
            "expected_vn_snapshot_count": self.expected_vn_snapshot_count,
            "vn_snapshot_count": self.vn_snapshot_count,
            "vn_process_snapshot_count": self.vn_process_snapshot_count,
            "rematerialization_snapshot_loader_invocation_count": (
                self.rematerialization_snapshot_loader_invocation_count
            ),
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
            "candidate": self.candidate.to_dict() if self.candidate else None,
            "partial_candidate_returned": False,
            "scenario_profile_resolved": self.profile_resolved,
            "source_values_consumed": self.input_valid,
            "snapshot_loader_invocation_performed": (
                self.rematerialization_snapshot_loader_invocation_count > 0
            ),
            "snapshots_created": (
                self.vu_materialization_complete
                and self.vn_materialization_complete
            ),
            "server_side_rematerialization_performed": (
                self.rematerialization_attempted
            ),
            "canonical_loaded_scenario_created": (
                self.canonical_scenario_loaded
            ),
            "profile_digest_calculation_performed": (
                self.profile_content_digest is not None
            ),
            "digest_calculation_performed": candidate_created,
            "candidate_created": candidate_created,
            "candidate_persisted": False,
            "writes_performed": False,
            "run_control_connected": False,
            "runner_invocation_performed": False,
            "execution_performed": False,
            "simulation_performed": False,
            "historical_rng_equality_claim": False,
            "historical_full_equality_claim": False,
        }


@dataclass(frozen=True, slots=True)
class _ResolvedProfile:
    data: dict[str, object]
    loaded_scenario: LoadedScenario
    content_digest: str


def strategy_execution_scenario_profile_root() -> Path:
    return Path(__file__).resolve().parent / "profiles"


def build_default_strategy_execution_scenario_profiles(
) -> dict[str, StrategyExecutionScenarioProfileDefinition]:
    root = strategy_execution_scenario_profile_root()
    profile = StrategyExecutionScenarioProfileDefinition(
        profile_id=DEFAULT_STRATEGY_EXECUTION_SCENARIO_PROFILE_ID,
        path=(
            root
            / "strategy_execution_candidate_profile_v1.json"
        ),
    )
    return {profile.profile_id: profile}


def _issue(
    issues: list[StrategyExecutionCandidateBuildIssue],
    *,
    stage: str,
    path: str,
    code: str,
    message: str,
) -> None:
    issues.append(
        StrategyExecutionCandidateBuildIssue(
            stage=stage,
            path=path,
            code=code,
            message=message,
        )
    )


def _json_value(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return _json_value(asdict(value))
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def _content_digest(value: object) -> str:
    return f"sha256:{sha256(_canonical_bytes(value)).hexdigest()}"


def _sorted_payloads(
    values: list[object],
    *,
    id_field: str,
) -> list[object]:
    return sorted(
        (_json_value(value) for value in values),
        key=lambda item: int(item[id_field]) if isinstance(item, dict) else -1,
    )


def _loaded_scenario_payload(scenario: LoadedScenario) -> dict[str, object]:
    payload: dict[str, object] = {
        "context": {
            "period": scenario.context.period,
            "logtime": scenario.context.logtime,
            "max_periods": scenario.context.max_periods,
            "run_index": scenario.context.run_index,
            "rng_seed": scenario.context.rng_seed,
        },
        "bav": _json_value(scenario.bav),
        "insurers": _sorted_payloads(
            list(scenario.insurers),
            id_field="entity_id",
        ),
        "policyholders": _sorted_payloads(
            list(scenario.policyholders),
            id_field="entity_id",
        ),
    }
    for collection_name in (
        *_VU_COLLECTION_NAMES,
        *_VN_RULE_COLLECTION_NAMES,
        *_VN_PROCESS_COLLECTION_NAMES,
    ):
        snapshots = list(getattr(scenario, collection_name))
        id_field = (
            "insurer_id" if collection_name.startswith("vu_") else "policyholder_id"
        )
        payload[collection_name] = _sorted_payloads(
            snapshots,
            id_field=id_field,
        )
    return payload


def _market_ground_state_payload(
    scenario: LoadedScenario,
    *,
    profile_id: str,
    profile_content_digest: str,
) -> dict[str, object]:
    loaded = _loaded_scenario_payload(scenario)
    return {
        "profile_id": profile_id,
        "profile_schema_version": STRATEGY_EXECUTION_SCENARIO_PROFILE_VERSION,
        "profile_content_digest": profile_content_digest,
        "simulation_context": loaded["context"],
        "bav": loaded["bav"],
        "insurers": loaded["insurers"],
        "policyholders": loaded["policyholders"],
    }


def _sort_document_collection(
    document: dict[str, object],
    field_name: str,
    *,
    key_fields: tuple[str, ...],
) -> None:
    values = document.get(field_name)
    if not isinstance(values, list):
        return
    values.sort(
        key=lambda entry: tuple(
            entry.get(field) if isinstance(entry, dict) else None
            for field in key_fields
        )
    )


def _canonical_source_documents(
    request: dict[str, object],
    vu_materialization_input: dict[str, object],
) -> dict[str, object]:
    draft = deepcopy(request["assignment_draft"])
    context = deepcopy(request["snapshot_context"])
    vu_input = deepcopy(vu_materialization_input)
    vu_state = deepcopy(request["vu_state_provenance"])
    vn_process = deepcopy(request["vn_process_input"])
    profile_reference = deepcopy(request["scenario_profile_reference"])
    assert isinstance(draft, dict)
    assert isinstance(context, dict)
    assert isinstance(vu_input, dict)
    assert isinstance(vu_state, dict)
    assert isinstance(vn_process, dict)
    assert isinstance(profile_reference, dict)

    _sort_document_collection(
        draft,
        "assignments",
        key_fields=("actor_type", "target_id", "strategy_id"),
    )
    _sort_document_collection(
        context,
        "entries",
        key_fields=("actor_type", "target_id", "strategy_id"),
    )
    vu_input["draft"] = deepcopy(draft)
    vu_input["context"] = deepcopy(context)
    _sort_document_collection(
        vu_state,
        "entries",
        key_fields=("insurer_id", "strategy_id"),
    )
    _sort_document_collection(
        vn_process,
        "damage_settlement_snapshots",
        key_fields=("policyholder_id",),
    )
    _sort_document_collection(
        vn_process,
        "settlement_snapshots",
        key_fields=("policyholder_id",),
    )
    for field_name in ("expected_insurer_ids", "expected_policyholder_ids"):
        values = profile_reference.get(field_name)
        if isinstance(values, list):
            values.sort()

    return {
        "assignment_draft": draft,
        "snapshot_context": context,
        "vu_materialization_input": vu_input,
        "vu_state_provenance": vu_state,
        "vn_process_input": vn_process,
        "scenario_profile_id": profile_reference["profile_id"],
    }


def _resolve_profile(
    reference: dict[str, object],
    *,
    profiles: Mapping[str, StrategyExecutionScenarioProfileDefinition],
    trusted_profile_root: Path,
    issues: list[StrategyExecutionCandidateBuildIssue],
) -> _ResolvedProfile | None:
    profile_id = str(reference["profile_id"])
    definition = profiles.get(profile_id)
    if definition is None:
        _issue(
            issues,
            stage="scenario_profile_resolution",
            path="$.scenario_profile_reference.profile_id",
            code="unknown_scenario_profile",
            message="Szenarioprofil ist serverseitig nicht registriert",
        )
        return None
    if definition.profile_id != profile_id:
        _issue(
            issues,
            stage="scenario_profile_resolution",
            path="$.scenario_profile_reference.profile_id",
            code="profile_registry_identity_mismatch",
            message="Registrierte Profil-ID stimmt nicht mit der Referenz ueberein",
        )
        return None

    root = trusted_profile_root.resolve()
    try:
        path = definition.path.resolve()
    except OSError as exc:
        _issue(
            issues,
            stage="scenario_profile_resolution",
            path="$.scenario_profile_reference.profile_id",
            code="scenario_profile_path_rejected",
            message=str(exc),
        )
        return None
    if not path.is_relative_to(root):
        _issue(
            issues,
            stage="scenario_profile_resolution",
            path="$.scenario_profile_reference.profile_id",
            code="scenario_profile_outside_trusted_root",
            message="Registriertes Szenarioprofil liegt ausserhalb des erlaubten Verzeichnisses",
        )
        return None

    try:
        raw_profile = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _issue(
            issues,
            stage="scenario_profile_resolution",
            path="$.scenario_profile_reference.profile_id",
            code="scenario_profile_unreadable",
            message=str(exc),
        )
        return None
    if not isinstance(raw_profile, dict):
        _issue(
            issues,
            stage="scenario_profile_resolution",
            path="$",
            code="scenario_profile_object_required",
            message="Szenarioprofil muss ein JSON-Objekt sein",
        )
        return None

    actual_fields = frozenset(raw_profile)
    if actual_fields != _PROFILE_FIELDS:
        missing = sorted(_PROFILE_FIELDS - actual_fields)
        unknown = sorted(actual_fields - _PROFILE_FIELDS)
        if missing:
            _issue(
                issues,
                stage="scenario_profile_resolution",
                path="$",
                code="scenario_profile_fields_missing",
                message=f"Szenarioprofilfelder fehlen: {', '.join(missing)}",
            )
        if unknown:
            _issue(
                issues,
                stage="scenario_profile_resolution",
                path="$",
                code="scenario_profile_fields_unknown",
                message=f"Szenarioprofilfelder sind nicht erlaubt: {', '.join(unknown)}",
            )
        return None

    expected_values = {
        "schema_version": STRATEGY_EXECUTION_SCENARIO_PROFILE_VERSION,
        "profile_id": profile_id,
        "base_model": "Vdefmd6",
        "scope": STRATEGY_EXECUTION_SCENARIO_PROFILE_SCOPE,
        "period": reference["period"],
    }
    for field_name, expected in expected_values.items():
        if raw_profile.get(field_name) != expected:
            _issue(
                issues,
                stage="scenario_profile_resolution",
                path=f"$.{field_name}",
                code="scenario_profile_value_mismatch",
                message=f"Szenarioprofilwert {field_name} stimmt nicht ueberein",
            )
    if issues:
        return None

    ground_mapping = {
        field_name: deepcopy(raw_profile[field_name])
        for field_name in ("context", "bav", "insurers", "policyholders")
    }
    try:
        loaded = load_scenario_from_mapping(ground_mapping)
    except (ScenarioValidationError, TypeError, ValueError, OverflowError) as exc:
        _issue(
            issues,
            stage="scenario_profile_resolution",
            path="$",
            code="scenario_profile_loader_rejected",
            message=str(exc),
        )
        return None

    expected_period = int(reference["period"])
    expected_bav_id = int(reference["expected_bav_id"])
    expected_insurer_ids = sorted(int(item) for item in reference["expected_insurer_ids"])
    expected_policyholder_ids = sorted(
        int(item) for item in reference["expected_policyholder_ids"]
    )
    actual_insurer_ids = sorted(item.entity_id for item in loaded.insurers)
    actual_policyholder_ids = sorted(item.entity_id for item in loaded.policyholders)
    checks = (
        (
            loaded.context.period == expected_period,
            "$.context.period",
            "scenario_profile_period_mismatch",
            "Profilkontextperiode stimmt nicht mit der Referenz ueberein",
        ),
        (
            loaded.context.max_periods >= expected_period,
            "$.context.max_periods",
            "scenario_profile_horizon_too_short",
            "Profilhorizont endet vor der Kandidatenperiode",
        ),
        (
            loaded.bav.entity_id == expected_bav_id,
            "$.bav.entity_id",
            "scenario_profile_bav_mismatch",
            "Profil-BAV stimmt nicht mit der Referenz ueberein",
        ),
        (
            actual_insurer_ids == expected_insurer_ids,
            "$.insurers",
            "scenario_profile_insurer_population_mismatch",
            "Profil-VU entsprechen nicht der erwarteten Population",
        ),
        (
            actual_policyholder_ids == expected_policyholder_ids,
            "$.policyholders",
            "scenario_profile_policyholder_population_mismatch",
            "Profil-VN entsprechen nicht der erwarteten Population",
        ),
    )
    for passed, issue_path, code, message in checks:
        if not passed:
            _issue(
                issues,
                stage="scenario_profile_resolution",
                path=issue_path,
                code=code,
                message=message,
            )
    if issues:
        return None

    ground_payload = _loaded_scenario_payload(loaded)
    try:
        digest = _content_digest(
            {
                key: ground_payload[key]
                for key in ("context", "bav", "insurers", "policyholders")
            }
        )
    except (TypeError, ValueError, OverflowError) as exc:
        _issue(
            issues,
            stage="scenario_profile_resolution",
            path="$",
            code="scenario_profile_not_canonicalizable",
            message=str(exc),
        )
        return None
    return _ResolvedProfile(
        data=raw_profile,
        loaded_scenario=loaded,
        content_digest=digest,
    )


def _remap_materialization_issue(
    issue: object,
    *,
    source: str,
) -> StrategyExecutionCandidateBuildIssue:
    path = str(getattr(issue, "path"))
    mappings = (
        (
            "$.input.draft",
            "$.assignment_draft",
        ),
        (
            "$.input.context",
            "$.snapshot_context",
        ),
        (
            "$.state",
            "$.vu_state_provenance",
        ),
        (
            "$.draft",
            "$.assignment_draft",
        ),
        (
            "$.context",
            "$.snapshot_context",
        ),
    )
    for old_prefix, new_prefix in mappings:
        if path == old_prefix or path.startswith(f"{old_prefix}.") or path.startswith(
            f"{old_prefix}["
        ):
            path = f"{new_prefix}{path[len(old_prefix):]}"
            break
    return StrategyExecutionCandidateBuildIssue(
        stage=f"{source}_materialization.{getattr(issue, 'stage')}",
        path=path,
        code=str(getattr(issue, "code")),
        message=str(getattr(issue, "message")),
    )


def _empty_report(
    *,
    input_valid: bool,
    draft_id: str | None,
    period: int | None,
    profile_id: str | None,
    profile_resolved: bool,
    profile_content_digest: str | None,
    rematerialization_attempted: bool,
    vu_materialization_complete: bool,
    vn_materialization_complete: bool,
    expected_vu_snapshot_count: int,
    vu_snapshot_count: int,
    expected_vn_snapshot_count: int,
    vn_snapshot_count: int,
    vn_process_snapshot_count: int,
    rematerialization_snapshot_loader_invocation_count: int,
    issues: list[StrategyExecutionCandidateBuildIssue],
) -> StrategyExecutionCandidateBuildReport:
    return StrategyExecutionCandidateBuildReport(
        input_valid=input_valid,
        draft_id=draft_id,
        period=period,
        profile_id=profile_id,
        profile_resolved=profile_resolved,
        profile_content_digest=profile_content_digest,
        rematerialization_attempted=rematerialization_attempted,
        vu_materialization_complete=vu_materialization_complete,
        vn_materialization_complete=vn_materialization_complete,
        canonical_scenario_loaded=False,
        expected_vu_snapshot_count=expected_vu_snapshot_count,
        vu_snapshot_count=vu_snapshot_count,
        expected_vn_snapshot_count=expected_vn_snapshot_count,
        vn_snapshot_count=vn_snapshot_count,
        vn_process_snapshot_count=vn_process_snapshot_count,
        rematerialization_snapshot_loader_invocation_count=(
            rematerialization_snapshot_loader_invocation_count
        ),
        candidate=None,
        issues=tuple(issues),
    )


def build_strategy_execution_candidate(
    value: object,
    *,
    profiles: Mapping[str, StrategyExecutionScenarioProfileDefinition],
    trusted_profile_root: str | Path,
) -> StrategyExecutionCandidateBuildReport:
    """Baut einen validierten Kandidaten ohne Speicherung oder Ausfuehrung."""

    validation = validate_strategy_execution_candidate_input(value)
    if not validation.valid:
        validation_issues = [
            StrategyExecutionCandidateBuildIssue(
                stage=f"input_validation.{issue.stage}",
                path=issue.path,
                code=issue.code,
                message=issue.message,
            )
            for issue in validation.issues
        ]
        return _empty_report(
            input_valid=False,
            draft_id=validation.draft_id,
            period=validation.period,
            profile_id=None,
            profile_resolved=False,
            profile_content_digest=None,
            rematerialization_attempted=False,
            vu_materialization_complete=False,
            vn_materialization_complete=False,
            expected_vu_snapshot_count=validation.expected_vu_entry_count,
            vu_snapshot_count=0,
            expected_vn_snapshot_count=validation.expected_vn_entry_count,
            vn_snapshot_count=0,
            vn_process_snapshot_count=0,
            rematerialization_snapshot_loader_invocation_count=0,
            issues=validation_issues,
        )

    assert isinstance(value, dict)
    request = value
    assert isinstance(request["scenario_profile_reference"], dict)
    reference = request["scenario_profile_reference"]
    profile_id = str(reference["profile_id"])
    issues: list[StrategyExecutionCandidateBuildIssue] = []
    resolved_profile = _resolve_profile(
        reference,
        profiles=profiles,
        trusted_profile_root=Path(trusted_profile_root),
        issues=issues,
    )
    if resolved_profile is None:
        return _empty_report(
            input_valid=True,
            draft_id=validation.draft_id,
            period=validation.period,
            profile_id=profile_id,
            profile_resolved=False,
            profile_content_digest=None,
            rematerialization_attempted=False,
            vu_materialization_complete=False,
            vn_materialization_complete=False,
            expected_vu_snapshot_count=validation.expected_vu_entry_count,
            vu_snapshot_count=0,
            expected_vn_snapshot_count=validation.expected_vn_entry_count,
            vn_snapshot_count=0,
            vn_process_snapshot_count=0,
            rematerialization_snapshot_loader_invocation_count=0,
            issues=issues,
        )

    assert isinstance(request["vu_input_policy"], dict)
    vu_materialization_input = {
        **request["vu_input_policy"],
        "draft": request["assignment_draft"],
        "context": request["snapshot_context"],
    }
    vu_report = materialize_strategy_assignment_vu_snapshots(
        {
            "input": vu_materialization_input,
            "state": request["vu_state_provenance"],
        }
    )
    vn_report = materialize_strategy_assignment_snapshots(
        {
            "draft": request["assignment_draft"],
            "context": request["snapshot_context"],
        }
    )
    issues.extend(
        _remap_materialization_issue(issue, source="vu")
        for issue in vu_report.issues
    )
    issues.extend(
        _remap_materialization_issue(issue, source="vn")
        for issue in vn_report.issues
    )
    snapshot_loader_count = (
        vu_report.snapshot_loader_invocation_count
        + vn_report.snapshot_loader_invocation_count
    )
    if issues or not (
        vu_report.materialization_complete and vn_report.materialization_complete
    ):
        return _empty_report(
            input_valid=True,
            draft_id=validation.draft_id,
            period=validation.period,
            profile_id=profile_id,
            profile_resolved=True,
            profile_content_digest=resolved_profile.content_digest,
            rematerialization_attempted=True,
            vu_materialization_complete=vu_report.materialization_complete,
            vn_materialization_complete=vn_report.materialization_complete,
            expected_vu_snapshot_count=vu_report.expected_snapshot_count,
            vu_snapshot_count=len(vu_report.snapshots),
            expected_vn_snapshot_count=vn_report.expected_snapshot_count,
            vn_snapshot_count=len(vn_report.snapshots),
            vn_process_snapshot_count=0,
            rematerialization_snapshot_loader_invocation_count=(
                snapshot_loader_count
            ),
            issues=issues,
        )

    collection_payloads = {
        definition.collection_name: []
        for definition in STRATEGY_EXECUTION_CANDIDATE_COLLECTIONS
    }
    for entry in vu_report.snapshots:
        collection_payloads[entry.snapshot_collection].append(
            entry.to_dict()["snapshot"]
        )
    for entry in vn_report.snapshots:
        collection_payloads[entry.snapshot_collection].append(
            entry.to_dict()["snapshot"]
        )
    assert isinstance(request["vn_process_input"], dict)
    process_input = request["vn_process_input"]
    collection_payloads["vn_damage_settlement_snapshots"] = deepcopy(
        process_input["damage_settlement_snapshots"]
    )
    collection_payloads["vn_settlement_snapshots"] = deepcopy(
        process_input["settlement_snapshots"]
    )

    profile_ground = resolved_profile.data
    combined_mapping = {
        field_name: deepcopy(profile_ground[field_name])
        for field_name in ("context", "bav", "insurers", "policyholders")
    }
    combined_mapping.update(collection_payloads)
    try:
        loaded_scenario = load_scenario_from_mapping(combined_mapping)
    except (ScenarioValidationError, TypeError, ValueError, OverflowError) as exc:
        _issue(
            issues,
            stage="canonical_scenario_load",
            path="$",
            code="canonical_scenario_loader_rejected",
            message=str(exc),
        )
        return _empty_report(
            input_valid=True,
            draft_id=validation.draft_id,
            period=validation.period,
            profile_id=profile_id,
            profile_resolved=True,
            profile_content_digest=resolved_profile.content_digest,
            rematerialization_attempted=True,
            vu_materialization_complete=True,
            vn_materialization_complete=True,
            expected_vu_snapshot_count=vu_report.expected_snapshot_count,
            vu_snapshot_count=len(vu_report.snapshots),
            expected_vn_snapshot_count=vn_report.expected_snapshot_count,
            vn_snapshot_count=len(vn_report.snapshots),
            vn_process_snapshot_count=len(
                process_input["damage_settlement_snapshots"]
            ),
            rematerialization_snapshot_loader_invocation_count=(
                snapshot_loader_count
            ),
            issues=issues,
        )

    loaded_payload = _loaded_scenario_payload(loaded_scenario)
    contract_payload = strategy_execution_candidate_contract_payload()
    sections: dict[str, object] = {
        "contract_versions": {
            "candidate_contract": STRATEGY_EXECUTION_CANDIDATE_CONTRACT_VERSION,
            "candidate_input": STRATEGY_EXECUTION_CANDIDATE_INPUT_VERSION,
            "candidate_validation": STRATEGY_EXECUTION_CANDIDATE_VALIDATION_VERSION,
            "candidate_build": STRATEGY_EXECUTION_CANDIDATE_BUILD_VERSION,
            "scenario_profile": STRATEGY_EXECUTION_SCENARIO_PROFILE_VERSION,
            **contract_payload["upstream_contract_versions"],
        },
        "source_documents": _canonical_source_documents(
            request,
            vu_materialization_input,
        ),
        "market_ground_state": _market_ground_state_payload(
            loaded_scenario,
            profile_id=profile_id,
            profile_content_digest=resolved_profile.content_digest,
        ),
        "vu_rule_snapshots": {
            "collections": {
                name: loaded_payload[name] for name in _VU_COLLECTION_NAMES
            }
        },
        "vn_rule_snapshots": {
            "collections": {
                name: loaded_payload[name] for name in _VN_RULE_COLLECTION_NAMES
            }
        },
        "vn_process_snapshots": {
            "collections": {
                name: loaded_payload[name] for name in _VN_PROCESS_COLLECTION_NAMES
            },
            "explicit_draw_provenance": {
                "source_policy": STRATEGY_EXECUTION_VN_PROCESS_DRAW_SOURCE_POLICY_ID,
                "draft_id": validation.draft_id,
                "period": validation.period,
            },
        },
        "execution_boundaries": {
            "persistence_enabled": False,
            "run_control_enabled": False,
            "runner_enabled": False,
            "execution_enabled": False,
            "carryover_enabled": False,
            "output_files_enabled": False,
            "legacy_comparison_enabled": False,
            "simulation_performed": False,
        },
    }
    digest_basis = {
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "draft_id": validation.draft_id,
        "period": validation.period,
        **sections,
    }
    try:
        content_digest = _content_digest(digest_basis)
    except (TypeError, ValueError, OverflowError) as exc:
        _issue(
            issues,
            stage="candidate_digest",
            path="$",
            code="candidate_not_canonicalizable",
            message=str(exc),
        )
        return _empty_report(
            input_valid=True,
            draft_id=validation.draft_id,
            period=validation.period,
            profile_id=profile_id,
            profile_resolved=True,
            profile_content_digest=resolved_profile.content_digest,
            rematerialization_attempted=True,
            vu_materialization_complete=True,
            vn_materialization_complete=True,
            expected_vu_snapshot_count=vu_report.expected_snapshot_count,
            vu_snapshot_count=len(vu_report.snapshots),
            expected_vn_snapshot_count=vn_report.expected_snapshot_count,
            vn_snapshot_count=len(vn_report.snapshots),
            vn_process_snapshot_count=len(
                loaded_scenario.vn_damage_settlement_snapshots
            ),
            rematerialization_snapshot_loader_invocation_count=(
                snapshot_loader_count
            ),
            issues=issues,
        )
    digest_hex = content_digest.removeprefix("sha256:")
    candidate = StrategyExecutionCandidate(
        candidate_id=f"strategy-candidate-{digest_hex[:24]}",
        draft_id=str(validation.draft_id),
        period=int(validation.period),
        content_digest=content_digest,
        profile_id=profile_id,
        profile_content_digest=resolved_profile.content_digest,
        sections=sections,
        loaded_scenario=loaded_scenario,
    )
    return StrategyExecutionCandidateBuildReport(
        input_valid=True,
        draft_id=validation.draft_id,
        period=validation.period,
        profile_id=profile_id,
        profile_resolved=True,
        profile_content_digest=resolved_profile.content_digest,
        rematerialization_attempted=True,
        vu_materialization_complete=True,
        vn_materialization_complete=True,
        canonical_scenario_loaded=True,
        expected_vu_snapshot_count=vu_report.expected_snapshot_count,
        vu_snapshot_count=len(vu_report.snapshots),
        expected_vn_snapshot_count=vn_report.expected_snapshot_count,
        vn_snapshot_count=len(vn_report.snapshots),
        vn_process_snapshot_count=len(
            loaded_scenario.vn_damage_settlement_snapshots
        ),
        rematerialization_snapshot_loader_invocation_count=(
            snapshot_loader_count
        ),
        candidate=candidate,
        issues=(),
    )


def strategy_execution_candidate_build_contract_payload(
    *,
    known_profile_ids: tuple[str, ...] = (
        DEFAULT_STRATEGY_EXECUTION_SCENARIO_PROFILE_ID,
    ),
) -> dict[str, Any]:
    boundary_flags = {
        "input_validation_required": True,
        "scenario_profile_resolution_enabled": True,
        "server_side_rematerialization_enabled": True,
        "snapshot_loader_invocation_enabled": True,
        "canonical_loaded_scenario_enabled": True,
        "digest_calculation_enabled": True,
        "candidate_creation_enabled": True,
        "candidate_persistence_enabled": False,
        "writes_performed": False,
        "run_control_enabled": False,
        "runner_enabled": False,
        "execution_enabled": False,
        "carryover_enabled": False,
        "output_files_enabled": False,
        "legacy_comparison_enabled": False,
        "simulation_performed": False,
        "historical_rng_equality_claim": False,
        "historical_full_equality_claim": False,
    }
    return {
        "schema_version": STRATEGY_EXECUTION_CANDIDATE_BUILD_VERSION,
        "input_schema_version": STRATEGY_EXECUTION_CANDIDATE_INPUT_VERSION,
        "validation_schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_VALIDATION_VERSION
        ),
        "candidate_contract_schema_version": (
            STRATEGY_EXECUTION_CANDIDATE_CONTRACT_VERSION
        ),
        "candidate_schema_version": STRATEGY_EXECUTION_CANDIDATE_VERSION,
        "scenario_profile_schema_version": (
            STRATEGY_EXECUTION_SCENARIO_PROFILE_VERSION
        ),
        "mode": "strategy_execution_candidate_build_contract",
        "scope": "validated_joint_input_to_ephemeral_canonical_candidate",
        "contract_endpoint": (
            "/api/strategies/execution-candidate-build-contract"
        ),
        "build_endpoint": "/api/strategies/execution-candidate-build",
        "known_profile_ids": sorted(set(known_profile_ids)),
        "profile_source_policy": "server_registry_only",
        "free_profile_paths_accepted": False,
        "browser_materialization_reports_accepted": False,
        "digest": {
            "algorithm": STRATEGY_EXECUTION_CANDIDATE_DIGEST_ALGORITHM,
            "prefix": "sha256:",
            "encoding": "ascii",
            "json_sort_keys": True,
            "json_separators": [",", ":"],
            "non_finite_numbers_allowed": False,
            "identity_fields_excluded": ["candidate_id", "content_digest"],
        },
        "partial_candidates_allowed": False,
        "boundary_flags": boundary_flags,
        **boundary_flags,
    }
