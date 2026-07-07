from dataclasses import dataclass, field
import argparse
import json
from pathlib import Path
from typing import Any

from ims.model.legacy_validation_coverage import (
    LegacyValidationCoverageBacklogEntry,
    LegacyValidationCoverageIssue,
    build_legacy_validation_coverage_matrix,
)


FAMILY_LABELS = {
    "insurer_stage_all": "Versicherer-Agrsich-Stufen",
    "policyholder_rule": "VN-Agrsich-Regeldateien",
    "policyholder_class": "VN-Agrsich-Klassenaggregate",
    "insurer_class": "Versicherer-Agrsich-Klassenaggregate",
    "parameter_output": "Agrsich-Parameterausgaben",
}


@dataclass(slots=True)
class LegacyValidationNextFamilyAction:
    family: str
    family_label: str
    next_action: str
    next_action_label: str
    available_files: list[str] = field(default_factory=list)
    covered_files: list[str] = field(default_factory=list)
    candidate_files: list[str] = field(default_factory=list)
    blocked_by: list[str] = field(default_factory=list)
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "family": self.family,
            "family_label": self.family_label,
            "next_action": self.next_action,
            "next_action_label": self.next_action_label,
            "available_files": list(self.available_files),
            "covered_files": list(self.covered_files),
            "candidate_files": list(self.candidate_files),
            "blocked_by": list(self.blocked_by),
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


@dataclass(slots=True)
class LegacyValidationNextFamilyPlan:
    status: str
    mode: str
    fixture_path: str
    reference_dir: str
    available_reference_count: int
    covered_file_count: int
    actions: list[LegacyValidationNextFamilyAction] = field(default_factory=list)
    issues: list[LegacyValidationCoverageIssue] = field(default_factory=list)
    writes_performed: bool = False
    execution_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "mode": self.mode,
            "fixture_path": self.fixture_path,
            "reference_dir": self.reference_dir,
            "available_reference_count": self.available_reference_count,
            "covered_file_count": self.covered_file_count,
            "actions": [action.to_dict() for action in self.actions],
            "issues": [issue.to_dict() for issue in self.issues],
            "writes_performed": self.writes_performed,
            "execution_performed": self.execution_performed,
        }


def _family_label(family: str) -> str:
    return FAMILY_LABELS.get(family, family)


def _action_from_backlog(entry: LegacyValidationCoverageBacklogEntry) -> LegacyValidationNextFamilyAction:
    uncovered_available = sorted(set(entry.available_files) - set(entry.covered_files))
    if uncovered_available:
        return LegacyValidationNextFamilyAction(
            family=entry.family,
            family_label=_family_label(entry.family),
            next_action="add_to_validation_bundle",
            next_action_label="Echte vorhandene Referenzdatei ins Validierungsfixture aufnehmen",
            available_files=entry.available_files,
            covered_files=entry.covered_files,
            candidate_files=uncovered_available,
        )
    missing_files = list(entry.missing_files)
    if missing_files:
        return LegacyValidationNextFamilyAction(
            family=entry.family,
            family_label=_family_label(entry.family),
            next_action="await_historical_reference",
            next_action_label="Historische Referenzdatei beschaffen, bevor diese Familie validiert wird",
            available_files=entry.available_files,
            covered_files=entry.covered_files,
            candidate_files=missing_files,
            blocked_by=["missing_historical_reference"],
        )
    return LegacyValidationNextFamilyAction(
        family=entry.family,
        family_label=_family_label(entry.family),
        next_action="covered",
        next_action_label="Diese belegte Dateifamilie ist im aktuellen Fixture abgedeckt",
        available_files=entry.available_files,
        covered_files=entry.covered_files,
    )


def _status(
    actions: list[LegacyValidationNextFamilyAction],
    issues: list[LegacyValidationCoverageIssue],
) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if any(action.next_action == "add_to_validation_bundle" for action in actions):
        return "ok"
    return "warning"


def build_legacy_validation_next_family_plan(
    fixture_path: str | Path,
    *,
    reference_dir: str | Path | None = None,
) -> LegacyValidationNextFamilyPlan:
    matrix = build_legacy_validation_coverage_matrix(fixture_path, reference_dir=reference_dir)
    actions = [_action_from_backlog(entry) for entry in matrix.backlog]
    if not any(action.next_action == "add_to_validation_bundle" for action in actions):
        actions = [action for action in actions if action.next_action != "covered"]
    return LegacyValidationNextFamilyPlan(
        status=_status(actions, matrix.issues),
        mode="legacy_agrsich_next_family_plan",
        fixture_path=matrix.fixture_path,
        reference_dir=matrix.reference_dir,
        available_reference_count=matrix.available_reference_count,
        covered_file_count=matrix.covered_file_count,
        actions=actions,
        issues=matrix.issues,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Plan the next Legacy-Agrsich validation family from existing historical references.",
    )
    parser.add_argument("fixture_path", help="Path to a legacy validation fixture JSON file.")
    parser.add_argument(
        "--reference-dir",
        help="Optional directory containing historical Legacy-Agrsich reference files.",
    )
    args = parser.parse_args(argv)

    result = build_legacy_validation_next_family_plan(args.fixture_path, reference_dir=args.reference_dir)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 2 if result.status == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
