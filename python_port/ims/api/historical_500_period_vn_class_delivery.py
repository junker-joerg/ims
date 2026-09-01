from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from ims.api.historical_500_period_vn_rule_delivery import (
    CUMULATIVE_ROW_COUNTS as PR99_CUMULATIVE_ROW_COUNTS,
    Historical500PolicyholderDeliveryProfile,
    Historical500VNRuleDeliveryResult,
    build_historical_500_period_policyholder_delivery,
)
from ims.engine.vdefmd6_repeat_corpus import Vdefmd6RepeatCorpusResult
from ims.model.agrsich_export import ExportTable


CONTRACT_VERSION = "pr100-v1"
CALCULATION_ORIGIN = "vdefmd6_controlled_5x100_vn_class_diagnostics_pr100"
CLASS_FILENAMES = (
    "imsvnvk1.dat",
    "imsvnvk2.dat",
    "imsvnvk3.dat",
)
CUMULATIVE_ROW_COUNTS = {
    **PR99_CUMULATIVE_ROW_COUNTS,
    **{filename: 500 for filename in CLASS_FILENAMES},
}
EXPECTED_REFERENCE_PATHS = {
    filename: Path("tests/references/legacy_agrsich") / filename.upper()
    for filename in CLASS_FILENAMES
}
REFERENCE_SHA256 = {
    "imsvnvk1.dat": (
        "bf21672275f325bc10584f9241827bdaf5288e471af23c3db94bd8fbfd308161"
    ),
    "imsvnvk2.dat": (
        "cface3a3a521923c1b237985166930ef796872ada7d52265af3ab85b67b1cdf1"
    ),
    "imsvnvk3.dat": (
        "766d5da11af81b6ff8fa98801f77ef0726a8b0237df27a090160490e831b93d4"
    ),
}
EXPECTED_COMPARISON = {
    "imsvnvk1.dat": {
        "period_count": 500,
        "matched_rows": 0,
        "mismatched_rows": 500,
        "field_count": 6500,
        "exact_field_match_count": 1082,
        "tolerated_numeric_difference_count": 368,
        "blocking_numeric_difference_count": 4188,
        "open_field_question_count": 862,
    },
    "imsvnvk2.dat": {
        "period_count": 500,
        "matched_rows": 0,
        "mismatched_rows": 500,
        "field_count": 6500,
        "exact_field_match_count": 1425,
        "tolerated_numeric_difference_count": 491,
        "blocking_numeric_difference_count": 4121,
        "open_field_question_count": 463,
    },
    "imsvnvk3.dat": {
        "period_count": 500,
        "matched_rows": 0,
        "mismatched_rows": 500,
        "field_count": 6500,
        "exact_field_match_count": 1410,
        "tolerated_numeric_difference_count": 22,
        "blocking_numeric_difference_count": 5058,
        "open_field_question_count": 10,
    },
}
VN_CLASS_PROFILE = Historical500PolicyholderDeliveryProfile(
    contract_version=CONTRACT_VERSION,
    calculation_origin=CALCULATION_ORIGIN,
    mode="historical_500_row_vn_class_repeat_diagnostics",
    source_contracts=("pr91-v1", "pr98-v1", "pr99-v1", "pr100-v1"),
    target_label="PR100 VN class",
    summary_path="IMSVNVK1-3",
    filenames=CLASS_FILENAMES,
    level="III",
    selector_kind="rule_class",
    layer_ids=("wvemod1_archive",),
    allowed_claims=("archive_content_match_only",),
    expected_reference_paths=EXPECTED_REFERENCE_PATHS,
    reference_sha256=REFERENCE_SHA256,
    expected_comparison=EXPECTED_COMPARISON,
    cumulative_row_counts=CUMULATIVE_ROW_COUNTS,
)


def build_historical_500_period_vn_class_delivery(
    root: Path | str = ".",
    *,
    repeat_corpus: Vdefmd6RepeatCorpusResult | None = None,
    repeat_class_tables: Sequence[ExportTable] | None = None,
) -> Historical500VNRuleDeliveryResult:
    return build_historical_500_period_policyholder_delivery(
        root,
        profile=VN_CLASS_PROFILE,
        repeat_corpus=repeat_corpus,
        repeat_tables=repeat_class_tables,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ims.api.historical_500_period_vn_class_delivery",
        description=(
            "Vergleicht drei WVEMOD1-VN-Klassenaggregate mit je fuenf "
            "getrennten 100-Perioden-Laeufen und haelt die Freigabe gesperrt."
        ),
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    result = build_historical_500_period_vn_class_delivery(args.root)
    print(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if result.status == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
