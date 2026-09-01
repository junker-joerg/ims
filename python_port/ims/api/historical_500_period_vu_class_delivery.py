from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from ims.api.historical_500_period_vn_class_delivery import (
    CUMULATIVE_ROW_COUNTS as PR100_CUMULATIVE_ROW_COUNTS,
)
from ims.api.historical_500_period_vn_rule_delivery import (
    Historical500AggregateDeliveryProfile,
    Historical500VNRuleDeliveryResult,
    build_historical_500_period_aggregate_delivery,
)
from ims.engine.vdefmd6_repeat_corpus import Vdefmd6RepeatCorpusResult
from ims.model.agrsich_export import INSURER_HEADER, ExportTable


CONTRACT_VERSION = "pr101-v1"
CALCULATION_ORIGIN = "vdefmd6_controlled_5x100_vu_class_diagnostics_pr101"
CLASS_FILENAMES = (
    "imsvuvk1.dat",
    "imsvuvk2.dat",
    "imsvuvk3.dat",
)
CUMULATIVE_ROW_COUNTS = {
    **PR100_CUMULATIVE_ROW_COUNTS,
    **{filename: 500 for filename in CLASS_FILENAMES},
}
EXPECTED_REFERENCE_PATHS = {
    filename: Path("tests/references/legacy_agrsich") / filename.upper()
    for filename in CLASS_FILENAMES
}
REFERENCE_SHA256 = {
    "imsvuvk1.dat": (
        "49ed53daaf6d13a9f850ed5628f79e4d9fb5e73b61359009159517ef35cb6e0f"
    ),
    "imsvuvk2.dat": (
        "619fc2e5624ab575c9b73ab0891ab88b1883317efbab262b726f1237f0cc3b3d"
    ),
    "imsvuvk3.dat": (
        "ed280b96d3f6daf4cf64de88c8de17b79b595d7ec928f8ca2df0ef0635a595bc"
    ),
}
EXPECTED_COMPARISON = {
    "imsvuvk1.dat": {
        "period_count": 500,
        "matched_rows": 5,
        "mismatched_rows": 495,
        "field_count": 7000,
        "exact_field_match_count": 1146,
        "tolerated_numeric_difference_count": 29,
        "blocking_numeric_difference_count": 5825,
        "open_field_question_count": 0,
    },
    "imsvuvk2.dat": {
        "period_count": 500,
        "matched_rows": 0,
        "mismatched_rows": 500,
        "field_count": 7000,
        "exact_field_match_count": 1105,
        "tolerated_numeric_difference_count": 12,
        "blocking_numeric_difference_count": 5883,
        "open_field_question_count": 0,
    },
    "imsvuvk3.dat": {
        "period_count": 500,
        "matched_rows": 0,
        "mismatched_rows": 500,
        "field_count": 7000,
        "exact_field_match_count": 1079,
        "tolerated_numeric_difference_count": 0,
        "blocking_numeric_difference_count": 5921,
        "open_field_question_count": 0,
    },
}
VU_CLASS_PROFILE = Historical500AggregateDeliveryProfile(
    contract_version=CONTRACT_VERSION,
    calculation_origin=CALCULATION_ORIGIN,
    mode="historical_500_row_vu_class_repeat_diagnostics",
    source_contracts=(
        "pr91-v1",
        "pr98-v1",
        "pr99-v1",
        "pr100-v1",
        "pr101-v1",
    ),
    target_label="PR101 VU class",
    summary_path="IMSVUVK1-3",
    filenames=CLASS_FILENAMES,
    subject_type="insurer",
    level="III",
    selector_kind="rule_class",
    expected_header=INSURER_HEADER,
    expected_row_width=13,
    layer_ids=("wvemod1_archive",),
    allowed_claims=("archive_content_match_only",),
    expected_reference_paths=EXPECTED_REFERENCE_PATHS,
    reference_sha256=REFERENCE_SHA256,
    expected_comparison=EXPECTED_COMPARISON,
    cumulative_row_counts=CUMULATIVE_ROW_COUNTS,
)


def build_historical_500_period_vu_class_delivery(
    root: Path | str = ".",
    *,
    repeat_corpus: Vdefmd6RepeatCorpusResult | None = None,
    repeat_class_tables: Sequence[ExportTable] | None = None,
) -> Historical500VNRuleDeliveryResult:
    return build_historical_500_period_aggregate_delivery(
        root,
        profile=VU_CLASS_PROFILE,
        repeat_corpus=repeat_corpus,
        repeat_tables=repeat_class_tables,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.historical_500_period_vu_class_delivery",
        description=(
            "Vergleicht drei WVEMOD1-VU-Klassenaggregate mit je fuenf "
            "getrennten 100-Perioden-Laeufen und haelt die Freigabe gesperrt."
        ),
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    result = build_historical_500_period_vu_class_delivery(args.root)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if result.status == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
