"""Measure complete synthetic AP5 markets, never the smaller offer-only probe."""
import argparse
import json
from pathlib import Path
from time import perf_counter

from ims.market.presets import workshop_case
from ims.market.runner import calculate
from ims.market.transport import wire_payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    records = []
    for count in (40, 41):
        source = workshop_case("market", 100, count)
        start = perf_counter()
        result = calculate(source)
        duration = perf_counter() - start
        if not result["valid"]:
            raise RuntimeError(result["issues"])
        records.append({"vu_count": count, "period_count": 100, "duration_seconds": duration,
            "input_bytes": len(json.dumps(source, separators=(",", ":")).encode("utf-8")),
            "response_bytes": len(json.dumps(wire_payload(result), separators=(",", ":"), ensure_ascii=False).encode("utf-8")),
            "content_digest": result["content_digest"], "rows_per_side": len(result["sides"]["variant"]["vu_rows"]),
            "customer_decisions_per_side": len(result["sides"]["variant"]["customer_decisions"])})
        print(json.dumps(records[-1]), flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"scope": "complete_ap5_product_baseline_and_variant", "measurements": records}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
