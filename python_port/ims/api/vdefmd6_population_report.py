from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Sequence

from ims.model.vdefmd6_population import (
    VDEFMD6_INITIAL_PERIOD,
    VDEFMD6_INSURER_COUNT,
    VDEFMD6_MAX_PERIODS,
    VDEFMD6_POLICYHOLDER_COUNT,
    Vdefmd6Population,
    build_vdefmd6_population,
)


CONTRACT_VERSION = "pr74-v1"
DEFAULT_CONTRACT_PATH = Path("tests/fixtures/vdefmd6_population_contract.json")
_BOUNDARIES = {
    "runner_started": False,
    "simulation_performed": False,
    "historical_full_equality_claimed": False,
    "legacy_output_used_as_input": False,
}


@dataclass(frozen=True, slots=True)
class Vdefmd6PopulationIssue:
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "message": self.message, "path": self.path}


@dataclass(frozen=True, slots=True)
class Vdefmd6PopulationReport:
    repo_root: str
    contract_path: str
    summary: dict[str, object]
    source_anchor_count: int
    issues: tuple[Vdefmd6PopulationIssue, ...]
    mode: str = "vdefmd6_population"

    @property
    def population_ready(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "population_built" if self.population_ready else "error",
            "mode": self.mode,
            "contract_version": CONTRACT_VERSION,
            "repo_root": self.repo_root,
            "contract_path": self.contract_path,
            "source_anchor_count": self.source_anchor_count,
            "summary": dict(self.summary),
            "population_ready": self.population_ready,
            "writes_performed": False,
            "execution_performed": False,
            "runner_started": False,
            "simulation_performed": False,
            "legacy_output_used_as_input": False,
            "historical_full_equality_claimed": False,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def build_vdefmd6_population_report(
    repo_root: Path | str,
    *,
    contract_path: Path | str | None = None,
) -> Vdefmd6PopulationReport:
    root = Path(repo_root).expanduser().resolve()
    path = _resolve(root, contract_path, DEFAULT_CONTRACT_PATH)
    issues: list[Vdefmd6PopulationIssue] = []
    contract = _load_contract(path, issues)
    population = build_vdefmd6_population()
    summary = _population_summary(population)
    anchor_count = _validate_contract(root, path, contract, summary, population, issues)
    return Vdefmd6PopulationReport(
        repo_root=str(root),
        contract_path=str(path),
        summary=summary,
        source_anchor_count=anchor_count,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.vdefmd6_population_report",
        description="Prueft den read-only Vdefmd6-Populationsbuilder.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", type=Path)
    args = parser.parse_args(argv)
    report = build_vdefmd6_population_report(
        args.repo_root,
        contract_path=args.contract,
    )
    print(json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if report.population_ready else 1


def _resolve(root: Path, value: Path | str | None, default: Path) -> Path:
    path = Path(value) if value is not None else default
    return (path if path.is_absolute() else root / path).expanduser().resolve()


def _issue(
    issues: list[Vdefmd6PopulationIssue],
    code: str,
    message: str,
    path: Path | None = None,
) -> None:
    issues.append(
        Vdefmd6PopulationIssue(
            code=code,
            message=message,
            path=str(path) if path is not None else None,
        )
    )


def _load_contract(
    path: Path,
    issues: list[Vdefmd6PopulationIssue],
) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _issue(issues, "contract_unreadable", str(exc), path)
        return {}
    if not isinstance(payload, dict):
        _issue(issues, "contract_shape_invalid", "contract must be an object", path)
        return {}
    return payload


def _population_summary(population: Vdefmd6Population) -> dict[str, object]:
    insurer_rule_counts = Counter(item.rule_id for item in population.insurers)
    insurer_class_counts = Counter(item.rule_class for item in population.insurers)
    policyholder_rule_counts = Counter(item.rule_id for item in population.policyholders)
    policyholder_class_counts = Counter(item.rule_class for item in population.policyholders)
    activation_counts = Counter(
        item.activation.activation_period
        for item in population.policyholder_definitions
    )
    return {
        "initial_period": population.initial_period,
        "insurer_count": len(population.insurers),
        "policyholder_count": len(population.policyholders),
        "active_insurer_count": sum(item.active for item in population.insurers),
        "active_policyholder_count": sum(item.active for item in population.policyholders),
        "insurer_rule_counts": _string_key_counts(insurer_rule_counts),
        "insurer_rule_class_counts": _string_key_counts(insurer_class_counts),
        "policyholder_rule_counts": _string_key_counts(policyholder_rule_counts),
        "policyholder_rule_class_counts": _string_key_counts(policyholder_class_counts),
        "policyholder_activation_period_counts": _string_key_counts(activation_counts),
    }


def _string_key_counts(counts: Counter[int | None]) -> dict[str, int]:
    return {str(key): counts[key] for key in sorted(counts, key=lambda item: item or 0)}


def _validate_contract(
    root: Path,
    path: Path,
    contract: dict[str, object],
    summary: dict[str, object],
    population: Vdefmd6Population,
    issues: list[Vdefmd6PopulationIssue],
) -> int:
    if contract.get("schema_version") != CONTRACT_VERSION:
        _issue(issues, "contract_version_mismatch", f"expected {CONTRACT_VERSION}", path)
    signature = (
        contract.get("model_id"),
        contract.get("initial_period"),
        contract.get("max_periods"),
    )
    if signature != ("Vdefmd6", VDEFMD6_INITIAL_PERIOD, VDEFMD6_MAX_PERIODS):
        _issue(issues, "model_signature_mismatch", str(signature), path)
    expected = contract.get("expected")
    actual = {key: value for key, value in summary.items() if key != "initial_period"}
    if expected != actual:
        _issue(issues, "population_summary_mismatch", "expected summary differs", path)
    if contract.get("boundaries") != _BOUNDARIES:
        _issue(issues, "execution_boundary_mismatch", "read-only boundaries differ", path)
    _validate_population_shape(population, issues)
    _validate_vu14(contract, population, path, issues)
    return _validate_source_anchors(root, contract, issues)


def _validate_population_shape(
    population: Vdefmd6Population,
    issues: list[Vdefmd6PopulationIssue],
) -> None:
    insurer_ids = [item.entity_id for item in population.insurers]
    policyholder_ids = [item.entity_id for item in population.policyholders]
    if insurer_ids != list(range(1, VDEFMD6_INSURER_COUNT + 1)):
        _issue(issues, "insurer_ids_incomplete", str(insurer_ids))
    if policyholder_ids != list(range(1, VDEFMD6_POLICYHOLDER_COUNT + 1)):
        _issue(issues, "policyholder_ids_incomplete", str(policyholder_ids))
    definitions = (
        *population.insurer_definitions,
        *population.policyholder_definitions,
    )
    if any(item.action.logical_time != 1 for item in definitions):
        _issue(issues, "logical_action_time_mismatch", "all actions must start at 1")
    if any(item.activation.active_through_run != 100 for item in definitions):
        _issue(issues, "active_run_boundary_mismatch", "all definitions require run 100")
    if any(len(item.parameters) != 16 for item in definitions):
        _issue(issues, "parameter_vector_length_mismatch", "all vectors require 16 values")


def _validate_vu14(
    contract: dict[str, object],
    population: Vdefmd6Population,
    path: Path,
    issues: list[Vdefmd6PopulationIssue],
) -> None:
    expected = contract.get("vu14")
    definition = population.insurer_definitions[13]
    actual = {
        "entity_id": definition.entity_id,
        "name": definition.name,
        "rule_id": definition.action.rule_id,
        "rule_class": definition.rule_class,
        "activation_period": definition.activation.activation_period,
        "logical_action_time": definition.action.logical_time,
        "initial_premiums": list(definition.initial_premiums),
        "initial_advertising": list(definition.initial_advertising),
        "parameters": list(definition.parameters),
    }
    if expected != actual:
        _issue(issues, "vu14_definition_mismatch", "VU14 definition differs", path)


def _validate_source_anchors(
    root: Path,
    contract: dict[str, object],
    issues: list[Vdefmd6PopulationIssue],
) -> int:
    anchors = contract.get("source_anchors")
    if not isinstance(anchors, list):
        _issue(issues, "source_anchors_missing", "source_anchors must be a list")
        return 0
    texts: dict[Path, str] = {}
    for anchor in anchors:
        if not isinstance(anchor, dict):
            _issue(issues, "source_anchor_invalid", str(anchor))
            continue
        source_path = (root / str(anchor.get("path", ""))).resolve()
        if source_path not in texts:
            try:
                texts[source_path] = source_path.read_text(encoding="latin-1")
            except OSError as exc:
                _issue(issues, "source_unreadable", str(exc), source_path)
                continue
        text = texts[source_path]
        needle = str(anchor.get("needle", ""))
        if not needle or needle not in text:
            _issue(issues, "source_anchor_missing", needle, source_path)
    return len(anchors)


if __name__ == "__main__":
    raise SystemExit(main())
