"""Rebuild the three curated AP3 source bundles from declared production cases."""
import json
from pathlib import Path

from ims.api.guided_period_chain import workshop_input
from ims.ict.presets import workshop_case as ict_case
from ims.strategies.modern_presets import CASES, workshop_case
from ims.strategies.seminar_bundle import pack


def main() -> None:
    destination = Path(__file__).resolve().parents[2] / "seminar_cases"
    destination.mkdir(exist_ok=True)
    for case_id, title in CASES.items():
        bundle = pack({"modern": workshop_case(case_id), "ict": ict_case(), "guided": workshop_input(1300, 0)}, title)
        path = destination / (case_id + ".json")
        path.write_text(json.dumps(bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        print(case_id, bundle["bundle_digest"], path.stat().st_size)


if __name__ == "__main__":
    main()
