from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from ims.api.historical_reference_archive_coherence import (
    REFERENCE_SPECS,
    HistoricalReferenceSpec,
)
from ims.model.agrsich_export import INSURER_HEADER, POLICYHOLDER_HEADER
from ims.model.legacy_agrsich_reference import parse_legacy_insurer_dat
from ims.model.legacy_vn_reference import parse_legacy_policyholder_dat


CONTRACT_VERSION = "pr91-v1"
COHERENCE_CLASSES = (
    "same_run_proven",
    "archive_family_only",
    "mixed_reference_layers",
    "contradictory_or_unresolved",
)


@dataclass(frozen=True)
class HistoricalReferenceLayerDefinition:
    layer_id: str
    source_kind: str
    source_path: str
    source_sha256: str
    evidence_contracts: tuple[str, ...]
    run_metadata_status: str
    coherence_class: str
    historical_origin_status: str
    allowed_claim: str
    separated_for_reference_testing: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "layer_id": self.layer_id,
            "source_kind": self.source_kind,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "evidence_contracts": list(self.evidence_contracts),
            "run_metadata_status": self.run_metadata_status,
            "coherence_class": self.coherence_class,
            "historical_origin_status": self.historical_origin_status,
            "allowed_claim": self.allowed_claim,
            "separated_for_reference_testing": self.separated_for_reference_testing,
        }


@dataclass(frozen=True)
class HistoricalReferenceLayerBinding:
    reference_filename: str
    reference_sha256: str
    layer_id: str
    source_member_path: str
    source_member_sha256: str
    archive_comparison_classification: str
    matching_basis: str


@dataclass(frozen=True)
class HistoricalReferenceLayerIssue:
    code: str
    severity: str
    path: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity,
            "path": self.path,
            "message": self.message,
        }


@dataclass(frozen=True)
class HistoricalReferenceLayerTarget:
    reference_path: str
    reference_filename: str
    expected_reference_sha256: str
    actual_reference_sha256: str | None
    subject_type: str
    level: str
    selector_kind: str
    selector_value: int | str
    period_start: int
    period_end: int
    row_count: int | None
    layer_id: str
    source_kind: str
    source_path: str
    source_sha256: str
    source_member_path: str
    source_member_sha256: str
    evidence_contracts: tuple[str, ...]
    run_metadata_status: str
    coherence_class: str
    historical_origin_status: str
    allowed_claim: str
    separated_for_reference_testing: bool
    archive_comparison_classification: str
    matching_basis: str
    binding_verified: bool
    same_run_claim_allowed: bool
    historical_full_equality_claim_allowed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "reference_path": self.reference_path,
            "reference_filename": self.reference_filename,
            "expected_reference_sha256": self.expected_reference_sha256,
            "actual_reference_sha256": self.actual_reference_sha256,
            "subject_type": self.subject_type,
            "level": self.level,
            "selector_kind": self.selector_kind,
            "selector_value": self.selector_value,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "row_count": self.row_count,
            "layer_id": self.layer_id,
            "source_kind": self.source_kind,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "source_member_path": self.source_member_path,
            "source_member_sha256": self.source_member_sha256,
            "evidence_contracts": list(self.evidence_contracts),
            "run_metadata_status": self.run_metadata_status,
            "coherence_class": self.coherence_class,
            "historical_origin_status": self.historical_origin_status,
            "allowed_claim": self.allowed_claim,
            "separated_for_reference_testing": self.separated_for_reference_testing,
            "archive_comparison_classification": self.archive_comparison_classification,
            "matching_basis": self.matching_basis,
            "binding_verified": self.binding_verified,
            "same_run_claim_allowed": self.same_run_claim_allowed,
            "historical_full_equality_claim_allowed": (
                self.historical_full_equality_claim_allowed
            ),
        }


@dataclass(frozen=True)
class HistoricalReferenceLayerContractResult:
    status: str
    mode: str
    contract_version: str
    root: str
    reference_dir: str
    target_count: int
    verified_target_count: int
    layer_count: int
    coherence_class_counts: dict[str, int]
    corpus_coherence_class: str
    same_run_proven_target_count: int
    unresolved_historical_origin_target_count: int
    separated_unresolved_target_count: int
    gate_decision: str
    full_window_phase_allowed: bool
    separate_reference_tests_required: bool
    layers: tuple[HistoricalReferenceLayerDefinition, ...]
    targets: tuple[HistoricalReferenceLayerTarget, ...]
    prior_evidence_reused: bool
    source_archives_read: bool
    legacy_bundle_changed: bool
    files_extracted: bool
    writes_enabled: bool
    execution_enabled: bool
    simulation_performed: bool
    seed_transferred_between_archives: bool
    coherent_vusk1_500_period_archive_source_claimed: bool
    historical_run_identity_claimed: bool
    historical_full_equality_claimed: bool
    production_release_approved: bool
    issues: tuple[HistoricalReferenceLayerIssue, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "mode": self.mode,
            "contract_version": self.contract_version,
            "root": self.root,
            "reference_dir": self.reference_dir,
            "target_count": self.target_count,
            "verified_target_count": self.verified_target_count,
            "layer_count": self.layer_count,
            "coherence_class_counts": self.coherence_class_counts,
            "corpus_coherence_class": self.corpus_coherence_class,
            "same_run_proven_target_count": self.same_run_proven_target_count,
            "unresolved_historical_origin_target_count": (
                self.unresolved_historical_origin_target_count
            ),
            "separated_unresolved_target_count": self.separated_unresolved_target_count,
            "gate_decision": self.gate_decision,
            "full_window_phase_allowed": self.full_window_phase_allowed,
            "separate_reference_tests_required": self.separate_reference_tests_required,
            "layers": [layer.to_dict() for layer in self.layers],
            "targets": [target.to_dict() for target in self.targets],
            "prior_evidence_reused": self.prior_evidence_reused,
            "source_archives_read": self.source_archives_read,
            "legacy_bundle_changed": self.legacy_bundle_changed,
            "files_extracted": self.files_extracted,
            "writes_enabled": self.writes_enabled,
            "execution_enabled": self.execution_enabled,
            "simulation_performed": self.simulation_performed,
            "seed_transferred_between_archives": self.seed_transferred_between_archives,
            "coherent_vusk1_500_period_archive_source_claimed": (
                self.coherent_vusk1_500_period_archive_source_claimed
            ),
            "historical_run_identity_claimed": self.historical_run_identity_claimed,
            "historical_full_equality_claimed": self.historical_full_equality_claimed,
            "production_release_approved": self.production_release_approved,
            "issues": [issue.to_dict() for issue in self.issues],
        }


LAYER_DEFINITIONS = (
    HistoricalReferenceLayerDefinition(
        layer_id="zins000_archive",
        source_kind="archive",
        source_path="incomming/IMS.DAT/VDEFMOD5/ZINS000.ZIP",
        source_sha256="5839ddea724949e9e1065a4d9f1ac3f27e97c2ed444d819f466f3cd4ee97f190",
        evidence_contracts=("pr89-v1", "pr90-v1"),
        run_metadata_status="metadata_absent",
        coherence_class="archive_family_only",
        historical_origin_status="archive_hash_bound_run_unproven",
        allowed_claim="archive_content_match_only",
        separated_for_reference_testing=True,
    ),
    HistoricalReferenceLayerDefinition(
        layer_id="wvemod1_archive",
        source_kind="archive",
        source_path="incomming/IMS.DAT/WVEMOD1.ZIP",
        source_sha256="444c0bddf7a0dcee21e963167c36da56ed9b0a33172487914adf51e2a91206d9",
        evidence_contracts=("pr89-v1", "pr90-v1"),
        run_metadata_status="metadata_absent",
        coherence_class="archive_family_only",
        historical_origin_status="archive_hash_bound_run_unproven",
        allowed_claim="archive_content_match_only",
        separated_for_reference_testing=True,
    ),
    HistoricalReferenceLayerDefinition(
        layer_id="wvemod2_archive",
        source_kind="archive",
        source_path="incomming/IMS.DAT/WVEMOD2.ZIP",
        source_sha256="d17f399139ced0c85db424aac46b585ee40f2d98eb84da43b3d5790d445c3eae",
        evidence_contracts=("pr89-v1", "pr90-v1"),
        run_metadata_status="metadata_absent",
        coherence_class="archive_family_only",
        historical_origin_status="archive_hash_bound_run_unproven",
        allowed_claim="archive_content_match_only",
        separated_for_reference_testing=True,
    ),
    HistoricalReferenceLayerDefinition(
        layer_id="vusk1l4_direct_04410ef",
        source_kind="versioned_direct_reference",
        source_path="tests/references/legacy_agrsich/VUSK1L4.DAT",
        source_sha256="dbb38cf052a7bf1260f716e65642269062ddefb0ffc2348bfe9c9023c5ab27e4",
        evidence_contracts=("git-04410ef", "pr89-v1", "pr90-v1"),
        run_metadata_status="not_available",
        coherence_class="contradictory_or_unresolved",
        historical_origin_status="historical_run_and_archive_unresolved",
        allowed_claim="versioned_fixture_regression_only",
        separated_for_reference_testing=True,
    ),
)


def _binding(
    reference_filename: str,
    reference_sha256: str,
    layer_id: str,
    source_member_path: str,
    source_member_sha256: str,
    archive_comparison_classification: str,
    matching_basis: str,
) -> HistoricalReferenceLayerBinding:
    return HistoricalReferenceLayerBinding(
        reference_filename=reference_filename,
        reference_sha256=reference_sha256,
        layer_id=layer_id,
        source_member_path=source_member_path,
        source_member_sha256=source_member_sha256,
        archive_comparison_classification=archive_comparison_classification,
        matching_basis=matching_basis,
    )


REFERENCE_LAYER_BINDINGS = (
    _binding(
        "VU14L1.DAT",
        "20b8b082dbdc4ce187c18a50d2c9f8ed3e5a275a2456ce25300696714a686f8e",
        "wvemod1_archive",
        "IMSVU014.DAT",
        "050c5668ce6ee3705237b96cc857b4e75a47887897041fbf97a69155a07ba39e",
        "exact_window_slice",
        "token_normalized",
    ),
    _binding(
        "VUSK1L1.DAT",
        "aa9fd4e13073231fc0b8286fe36ca63ee475f35365652161c675c3d592c10568",
        "wvemod2_archive",
        "IMSVUSK1.DAT",
        "7ec3ff08a77468ab5106b2daeacf877606f33acf9d299f907a5923fe14f0f001",
        "exact_window_slice",
        "token_normalized",
    ),
    _binding(
        "VUSK1L2.DAT",
        "d77fab22e32c73ecaff95fc46ef43e9efb7548af6f882d9905983ddb28bbb38d",
        "wvemod2_archive",
        "IMSVUSK1.DAT",
        "7ec3ff08a77468ab5106b2daeacf877606f33acf9d299f907a5923fe14f0f001",
        "exact_window_slice",
        "token_normalized",
    ),
    _binding(
        "VUSK1L3.DAT",
        "92a2b12f0e5715201b7af28572c5a2a912bc634d49a9038e2790000298c4d25e",
        "wvemod2_archive",
        "IMSVUSK1.DAT",
        "7ec3ff08a77468ab5106b2daeacf877606f33acf9d299f907a5923fe14f0f001",
        "exact_window_slice",
        "token_normalized",
    ),
    _binding(
        "VUSK1L4.DAT",
        "dbb38cf052a7bf1260f716e65642269062ddefb0ffc2348bfe9c9023c5ab27e4",
        "vusk1l4_direct_04410ef",
        "tests/references/legacy_agrsich/VUSK1L4.DAT",
        "dbb38cf052a7bf1260f716e65642269062ddefb0ffc2348bfe9c9023c5ab27e4",
        "same_name_divergent",
        "versioned_reference_sha256",
    ),
    _binding(
        "VUSK1L5.DAT",
        "0d7f02f992d418baef0c259f8e6cab59bde452e34cd794aed1876dc52da6feec",
        "wvemod2_archive",
        "IMSVUSK1.DAT",
        "7ec3ff08a77468ab5106b2daeacf877606f33acf9d299f907a5923fe14f0f001",
        "exact_window_slice",
        "token_normalized",
    ),
    _binding(
        "IMSVNSK1.DAT",
        "37189ca9058a0817f4623767a5758ccd2d870d1518f2f443a941d33c91929c88",
        "wvemod1_archive",
        "IMSVNSK1.DAT",
        "37189ca9058a0817f4623767a5758ccd2d870d1518f2f443a941d33c91929c88",
        "exact_archive_member",
        "byte_exact",
    ),
    _binding(
        "IMSVNR01.DAT",
        "79cff0463c0bd9489459fd92694e4650b59c0a52c0703d879e5142aeaea4b9c9",
        "zins000_archive",
        "IMSVNR01.DAT",
        "79cff0463c0bd9489459fd92694e4650b59c0a52c0703d879e5142aeaea4b9c9",
        "exact_archive_member",
        "byte_exact",
    ),
    _binding(
        "IMSVNR02.DAT",
        "695ca328675b1eb46bcb6e15c0e8c41ce78a48c98ac5216c7644423ced5a4eec",
        "zins000_archive",
        "IMSVNR02.DAT",
        "695ca328675b1eb46bcb6e15c0e8c41ce78a48c98ac5216c7644423ced5a4eec",
        "exact_archive_member",
        "byte_exact",
    ),
    _binding(
        "IMSVNR03.DAT",
        "8491bec0736fbf4fb95c9b7649338d0142207265024ec5c5e9c3e649bd49ffd4",
        "wvemod1_archive",
        "IMSVNR03.DAT",
        "8491bec0736fbf4fb95c9b7649338d0142207265024ec5c5e9c3e649bd49ffd4",
        "exact_archive_member",
        "byte_exact",
    ),
    _binding(
        "IMSVNR04.DAT",
        "16bdf0b4329ec414990aaaec2ece0d48a8001b43d4a6bb8210625cfb56f3fce4",
        "wvemod1_archive",
        "IMSVNR04.DAT",
        "16bdf0b4329ec414990aaaec2ece0d48a8001b43d4a6bb8210625cfb56f3fce4",
        "exact_archive_member",
        "byte_exact",
    ),
    _binding(
        "IMSVNR05.DAT",
        "80a83f47de5451cb9b660025ca3c0e511aa268602b0ced2301f82b4467549dfa",
        "wvemod1_archive",
        "IMSVNR05.DAT",
        "80a83f47de5451cb9b660025ca3c0e511aa268602b0ced2301f82b4467549dfa",
        "exact_archive_member",
        "byte_exact",
    ),
    _binding(
        "IMSVNR06.DAT",
        "1d18b3ce471f4b19f525956650b414e1fcfb8b93854eaaf60c8316b18b1eced0",
        "wvemod1_archive",
        "IMSVNR06.DAT",
        "1d18b3ce471f4b19f525956650b414e1fcfb8b93854eaaf60c8316b18b1eced0",
        "exact_archive_member",
        "byte_exact",
    ),
    _binding(
        "IMSVNVK1.DAT",
        "bf21672275f325bc10584f9241827bdaf5288e471af23c3db94bd8fbfd308161",
        "wvemod1_archive",
        "IMSVNVK1.DAT",
        "bf21672275f325bc10584f9241827bdaf5288e471af23c3db94bd8fbfd308161",
        "exact_archive_member",
        "byte_exact",
    ),
    _binding(
        "IMSVNVK2.DAT",
        "cface3a3a521923c1b237985166930ef796872ada7d52265af3ab85b67b1cdf1",
        "wvemod1_archive",
        "IMSVNVK2.DAT",
        "cface3a3a521923c1b237985166930ef796872ada7d52265af3ab85b67b1cdf1",
        "exact_archive_member",
        "byte_exact",
    ),
    _binding(
        "IMSVNVK3.DAT",
        "766d5da11af81b6ff8fa98801f77ef0726a8b0237df27a090160490e831b93d4",
        "wvemod1_archive",
        "IMSVNVK3.DAT",
        "766d5da11af81b6ff8fa98801f77ef0726a8b0237df27a090160490e831b93d4",
        "exact_archive_member",
        "byte_exact",
    ),
    _binding(
        "IMSVUVK1.DAT",
        "49ed53daaf6d13a9f850ed5628f79e4d9fb5e73b61359009159517ef35cb6e0f",
        "wvemod1_archive",
        "IMSVUVK1.DAT",
        "49ed53daaf6d13a9f850ed5628f79e4d9fb5e73b61359009159517ef35cb6e0f",
        "exact_archive_member",
        "byte_exact",
    ),
    _binding(
        "IMSVUVK2.DAT",
        "619fc2e5624ab575c9b73ab0891ab88b1883317efbab262b726f1237f0cc3b3d",
        "wvemod1_archive",
        "IMSVUVK2.DAT",
        "619fc2e5624ab575c9b73ab0891ab88b1883317efbab262b726f1237f0cc3b3d",
        "exact_archive_member",
        "byte_exact",
    ),
    _binding(
        "IMSVUVK3.DAT",
        "ed280b96d3f6daf4cf64de88c8de17b79b595d7ec928f8ca2df0ef0635a595bc",
        "wvemod1_archive",
        "IMSVUVK3.DAT",
        "ed280b96d3f6daf4cf64de88c8de17b79b595d7ec928f8ca2df0ef0635a595bc",
        "exact_archive_member",
        "byte_exact",
    ),
)


def build_historical_reference_layer_contract(
    *,
    root: Path | str = ".",
    reference_dir: Path | str = Path("tests/references/legacy_agrsich"),
    reference_specs: Sequence[HistoricalReferenceSpec] = REFERENCE_SPECS,
    layers: Sequence[HistoricalReferenceLayerDefinition] = LAYER_DEFINITIONS,
    bindings: Sequence[HistoricalReferenceLayerBinding] = REFERENCE_LAYER_BINDINGS,
) -> HistoricalReferenceLayerContractResult:
    resolved_root = Path(root).expanduser().resolve()
    resolved_reference_dir = _resolve_against_root(resolved_root, reference_dir)
    issues: list[HistoricalReferenceLayerIssue] = []
    layer_by_id = _index_layers(layers, issues)
    binding_by_name = _index_bindings(bindings, issues)
    spec_names = {spec.reference_filename for spec in reference_specs}
    binding_names = set(binding_by_name)
    for filename in sorted(spec_names - binding_names):
        issues.append(
            HistoricalReferenceLayerIssue(
                code="target_binding_missing",
                severity="error",
                path=filename,
                message=f"reference target has no layer binding: {filename}",
            )
        )
    for filename in sorted(binding_names - spec_names):
        issues.append(
            HistoricalReferenceLayerIssue(
                code="target_binding_unexpected",
                severity="error",
                path=filename,
                message=f"layer binding has no declared reference target: {filename}",
            )
        )
    _validate_layers(layers, issues)
    targets = tuple(
        _inspect_target(
            resolved_root,
            resolved_reference_dir,
            spec,
            binding_by_name.get(spec.reference_filename),
            layer_by_id,
            issues,
        )
        for spec in reference_specs
        if spec.reference_filename in binding_by_name
    )
    error_present = any(issue.severity == "error" for issue in issues)
    unresolved_targets = tuple(
        target
        for target in targets
        if target.coherence_class == "contradictory_or_unresolved"
    )
    unseparated_unresolved = tuple(
        target for target in unresolved_targets if not target.separated_for_reference_testing
    )
    full_window_allowed = not error_present and not unseparated_unresolved
    if error_present:
        gate_decision = "blocked_contract_invalid"
    elif unseparated_unresolved:
        gate_decision = "blocked_unseparated_reference_layer"
    else:
        gate_decision = "go_separate_reference_tests"
    counts = {
        coherence_class: sum(
            target.coherence_class == coherence_class for target in targets
        )
        for coherence_class in COHERENCE_CLASSES
    }
    return HistoricalReferenceLayerContractResult(
        status=_status_from_issues(issues),
        mode="historical_reference_layer_contract",
        contract_version=CONTRACT_VERSION,
        root=str(resolved_root),
        reference_dir=_display_path(resolved_root, resolved_reference_dir),
        target_count=len(targets),
        verified_target_count=sum(target.binding_verified for target in targets),
        layer_count=len(layer_by_id),
        coherence_class_counts=counts,
        corpus_coherence_class="mixed_reference_layers",
        same_run_proven_target_count=counts["same_run_proven"],
        unresolved_historical_origin_target_count=len(unresolved_targets),
        separated_unresolved_target_count=sum(
            target.separated_for_reference_testing for target in unresolved_targets
        ),
        gate_decision=gate_decision,
        full_window_phase_allowed=full_window_allowed,
        separate_reference_tests_required=True,
        layers=tuple(layers),
        targets=targets,
        prior_evidence_reused=True,
        source_archives_read=False,
        legacy_bundle_changed=False,
        files_extracted=False,
        writes_enabled=False,
        execution_enabled=False,
        simulation_performed=False,
        seed_transferred_between_archives=False,
        coherent_vusk1_500_period_archive_source_claimed=False,
        historical_run_identity_claimed=False,
        historical_full_equality_claimed=False,
        production_release_approved=False,
        issues=tuple(issues),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = build_historical_reference_layer_contract(
        root=args.root,
        reference_dir=args.reference_dir,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 1 if result.status == "error" else 0


def _inspect_target(
    root: Path,
    reference_dir: Path,
    spec: HistoricalReferenceSpec,
    binding: HistoricalReferenceLayerBinding | None,
    layer_by_id: dict[str, HistoricalReferenceLayerDefinition],
    issues: list[HistoricalReferenceLayerIssue],
) -> HistoricalReferenceLayerTarget:
    assert binding is not None
    reference_path = reference_dir / spec.reference_filename
    display_path = _display_path(root, reference_path)
    layer = layer_by_id.get(binding.layer_id)
    if layer is None:
        issues.append(
            HistoricalReferenceLayerIssue(
                code="target_layer_missing",
                severity="error",
                path=display_path,
                message=f"target references unknown layer: {binding.layer_id}",
            )
        )
        layer = _invalid_layer(binding.layer_id)
    actual_hash, row_count, content_valid = _inspect_reference(
        reference_path,
        display_path,
        spec,
        binding.reference_sha256,
        issues,
    )
    binding_valid = _validate_binding(binding, layer, display_path, issues)
    hash_valid = actual_hash == binding.reference_sha256
    if actual_hash is not None and not hash_valid:
        issues.append(
            HistoricalReferenceLayerIssue(
                code="reference_hash_mismatch",
                severity="error",
                path=display_path,
                message=(
                    f"reference SHA-256 differs from layer contract: "
                    f"{actual_hash} != {binding.reference_sha256}"
                ),
            )
        )
    return HistoricalReferenceLayerTarget(
        reference_path=display_path,
        reference_filename=spec.reference_filename,
        expected_reference_sha256=binding.reference_sha256,
        actual_reference_sha256=actual_hash,
        subject_type=spec.subject_type,
        level=spec.level,
        selector_kind=spec.selector_kind,
        selector_value=spec.selector_value,
        period_start=spec.period_start,
        period_end=spec.period_end,
        row_count=row_count,
        layer_id=layer.layer_id,
        source_kind=layer.source_kind,
        source_path=layer.source_path,
        source_sha256=layer.source_sha256,
        source_member_path=binding.source_member_path,
        source_member_sha256=binding.source_member_sha256,
        evidence_contracts=layer.evidence_contracts,
        run_metadata_status=layer.run_metadata_status,
        coherence_class=layer.coherence_class,
        historical_origin_status=layer.historical_origin_status,
        allowed_claim=layer.allowed_claim,
        separated_for_reference_testing=layer.separated_for_reference_testing,
        archive_comparison_classification=(
            binding.archive_comparison_classification
        ),
        matching_basis=binding.matching_basis,
        binding_verified=content_valid and hash_valid and binding_valid,
        same_run_claim_allowed=layer.coherence_class == "same_run_proven",
        historical_full_equality_claim_allowed=False,
    )


def _inspect_reference(
    path: Path,
    display_path: str,
    spec: HistoricalReferenceSpec,
    expected_sha256: str,
    issues: list[HistoricalReferenceLayerIssue],
) -> tuple[str | None, int | None, bool]:
    if not path.is_file():
        issues.append(
            HistoricalReferenceLayerIssue(
                code="reference_missing",
                severity="error",
                path=display_path,
                message=f"versioned historical reference is missing: {display_path}",
            )
        )
        return None, None, False
    data = path.read_bytes()
    actual_hash = _checkout_stable_reference_sha256(data, expected_sha256)
    try:
        if spec.subject_type == "insurer":
            table = parse_legacy_insurer_dat(path)
            expected_header = INSURER_HEADER
        elif spec.subject_type == "policyholder":
            table = parse_legacy_policyholder_dat(path)
            expected_header = POLICYHOLDER_HEADER
        else:
            raise ValueError(f"unsupported subject type: {spec.subject_type}")
    except (OSError, UnicodeError, ValueError) as error:
        issues.append(
            HistoricalReferenceLayerIssue(
                code="reference_invalid",
                severity="error",
                path=display_path,
                message=f"versioned historical reference is invalid: {error}",
            )
        )
        return actual_hash, None, False
    header_valid = _normalize_whitespace(table.header) == _normalize_whitespace(
        expected_header
    )
    if not header_valid:
        issues.append(
            HistoricalReferenceLayerIssue(
                code="reference_header_mismatch",
                severity="error",
                path=display_path,
                message="reference header differs from the declared subject contract",
            )
        )
    periods = tuple(row.global_period for row in table.rows)
    expected_periods = tuple(range(spec.period_start, spec.period_end + 1))
    periods_valid = periods == expected_periods
    if not periods_valid:
        issues.append(
            HistoricalReferenceLayerIssue(
                code="reference_period_window_mismatch",
                severity="error",
                path=display_path,
                message=(
                    f"reference periods do not match declared window "
                    f"{spec.period_start}-{spec.period_end}"
                ),
            )
        )
    return actual_hash, len(table.rows), header_valid and periods_valid


def _index_layers(
    layers: Sequence[HistoricalReferenceLayerDefinition],
    issues: list[HistoricalReferenceLayerIssue],
) -> dict[str, HistoricalReferenceLayerDefinition]:
    result: dict[str, HistoricalReferenceLayerDefinition] = {}
    for layer in layers:
        if layer.layer_id in result:
            issues.append(
                HistoricalReferenceLayerIssue(
                    code="layer_id_duplicate",
                    severity="error",
                    path=layer.layer_id,
                    message=f"layer ID occurs more than once: {layer.layer_id}",
                )
            )
        result[layer.layer_id] = layer
    return result


def _index_bindings(
    bindings: Sequence[HistoricalReferenceLayerBinding],
    issues: list[HistoricalReferenceLayerIssue],
) -> dict[str, HistoricalReferenceLayerBinding]:
    result: dict[str, HistoricalReferenceLayerBinding] = {}
    for binding in bindings:
        if binding.reference_filename in result:
            issues.append(
                HistoricalReferenceLayerIssue(
                    code="target_binding_duplicate",
                    severity="error",
                    path=binding.reference_filename,
                    message=(
                        "reference target occurs in more than one layer binding: "
                        f"{binding.reference_filename}"
                    ),
                )
            )
        result[binding.reference_filename] = binding
    return result


def _validate_layers(
    layers: Sequence[HistoricalReferenceLayerDefinition],
    issues: list[HistoricalReferenceLayerIssue],
) -> None:
    for layer in layers:
        if layer.coherence_class not in COHERENCE_CLASSES:
            issues.append(
                HistoricalReferenceLayerIssue(
                    code="layer_coherence_class_invalid",
                    severity="error",
                    path=layer.layer_id,
                    message=f"unsupported coherence class: {layer.coherence_class}",
                )
            )
        if (
            layer.coherence_class == "same_run_proven"
            and layer.run_metadata_status != "direct_run_report"
        ):
            issues.append(
                HistoricalReferenceLayerIssue(
                    code="same_run_metadata_missing",
                    severity="error",
                    path=layer.layer_id,
                    message="same_run_proven requires a direct run report in the same layer",
                )
            )
        if layer.coherence_class == "contradictory_or_unresolved":
            if layer.separated_for_reference_testing:
                issues.append(
                    HistoricalReferenceLayerIssue(
                        code="historical_origin_unresolved",
                        severity="warning",
                        path=layer.layer_id,
                        message=(
                            "historical origin remains unresolved; the layer is isolated "
                            "for versioned fixture regression only"
                        ),
                    )
                )
            else:
                issues.append(
                    HistoricalReferenceLayerIssue(
                        code="unresolved_layer_not_separated",
                        severity="error",
                        path=layer.layer_id,
                        message="unresolved layer must be separated before full-window work",
                    )
                )


def _validate_binding(
    binding: HistoricalReferenceLayerBinding,
    layer: HistoricalReferenceLayerDefinition,
    display_path: str,
    issues: list[HistoricalReferenceLayerIssue],
) -> bool:
    valid = True
    if layer.source_kind == "archive":
        if binding.archive_comparison_classification not in {
            "exact_archive_member",
            "exact_window_slice",
        }:
            valid = False
        if binding.matching_basis not in {"byte_exact", "token_normalized"}:
            valid = False
        if layer.coherence_class != "archive_family_only":
            valid = False
        if layer.run_metadata_status != "metadata_absent":
            valid = False
    elif layer.source_kind == "versioned_direct_reference":
        if binding.archive_comparison_classification != "same_name_divergent":
            valid = False
        if binding.matching_basis != "versioned_reference_sha256":
            valid = False
        if binding.source_member_sha256 != binding.reference_sha256:
            valid = False
        if layer.allowed_claim != "versioned_fixture_regression_only":
            valid = False
    else:
        valid = False
    if not valid:
        issues.append(
            HistoricalReferenceLayerIssue(
                code="target_binding_invalid",
                severity="error",
                path=display_path,
                message=f"target binding is inconsistent with layer {layer.layer_id}",
            )
        )
    return valid


def _invalid_layer(layer_id: str) -> HistoricalReferenceLayerDefinition:
    return HistoricalReferenceLayerDefinition(
        layer_id=layer_id,
        source_kind="invalid",
        source_path="",
        source_sha256="",
        evidence_contracts=(),
        run_metadata_status="unknown",
        coherence_class="contradictory_or_unresolved",
        historical_origin_status="unresolved",
        allowed_claim="none",
        separated_for_reference_testing=False,
    )


def _normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


def _checkout_stable_reference_sha256(data: bytes, expected_sha256: str) -> str:
    raw_sha256 = hashlib.sha256(data).hexdigest()
    if raw_sha256 == expected_sha256:
        return raw_sha256
    normalized_lf = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    checkout_variants = (
        hashlib.sha256(normalized_lf).hexdigest(),
        hashlib.sha256(normalized_lf.replace(b"\n", b"\r\n")).hexdigest(),
    )
    return expected_sha256 if expected_sha256 in checkout_variants else raw_sha256


def _resolve_against_root(root: Path, path: Path | str) -> Path:
    candidate = Path(path).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _status_from_issues(issues: Sequence[HistoricalReferenceLayerIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if issues:
        return "warning"
    return "ok"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.historical_reference_layer_contract",
        description=(
            "Prueft den versionierten Referenzschicht-Vertrag, ohne Archive zu "
            "lesen, Dateien zu schreiben oder eine Simulation zu starten."
        ),
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repo-Wurzel fuer relative Referenzpfade.",
    )
    parser.add_argument(
        "--reference-dir",
        type=Path,
        default=Path("tests/references/legacy_agrsich"),
        help="Verzeichnis der versionierten historischen Referenzen.",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
