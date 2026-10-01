"""Digest-bound exact dossier exports from the same ICT calculation."""

import csv
import json
from io import BytesIO, StringIO

from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell


def csv_export(result: dict) -> bytes:
    stream = StringIO(newline="")
    fields = ["content_digest", "scenario_id", "variant_id", "side", *result["baseline"]["balance_rows"][0]]
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for side in ("baseline", "variant"):
        for row in result[side]["balance_rows"]:
            writer.writerow({"content_digest": result["content_digest"], "scenario_id": result["scenario_id"],
                             "variant_id": result["variant_id"], "side": side, **row})
    return stream.getvalue().encode("utf-8")


def workbook_export(result: dict) -> bytes:
    workbook = Workbook(write_only=True)

    def sheet(name: str, rows: list[dict]) -> None:
        target = workbook.create_sheet(name)
        fields = list(rows[0]) if rows else []
        target.append(fields)
        for row in rows:
            cells = []
            for field in fields:
                value = row[field]
                if type(value) in (dict, list):
                    value = json.dumps(value, sort_keys=True, ensure_ascii=False)
                if type(value) is str:
                    cell = WriteOnlyCell(target, value=value)
                    cell.data_type = "s"  # exact amounts and inert scenario text
                    value = cell
                cells.append(value)
            target.append(cells)
        target.freeze_panes = "B2"

    for side, name in (("baseline", "Baseline"), ("variant", "Variante")):
        sheet(name + " Bilanz", result[side]["balance_rows"])
        sheet(name + " Prozesse", result[side]["service_rows"])
    sheet("Zeitlinie", result["timeline"])
    sheet("Anbieter", result["provider_concentration"])
    sheet("Herkunft", [{"schema_version": result["schema_version"], "content_digest": result["content_digest"],
                        "input_digest": result["input_digest"], "scenario_id": result["scenario_id"],
                        "variant_id": result["variant_id"], "amount_unit": result["amount_unit"],
                        "period_hours": result["period_hours"], "assumption_note": result["assumption_note"],
                        "source_contract": "Vollständiger JSON-Vertrag im Blatt Quelle", "regulatory_metrics": result["regulatory_metrics"],
                        "compliance_decision_enabled": False}])
    # Excel silently truncates long cell strings. Large but valid declared
    # dependencies must retain their entire input, not just the first 32767 chars.
    source = json.dumps(result["source_contract"], sort_keys=True, ensure_ascii=False, allow_nan=False)
    sheet("Quelle", [{"chunk_index": index // 30000, "source_contract_json": source[index:index + 30000]}
                      for index in range(0, len(source), 30000)])
    stream = BytesIO()
    workbook.save(stream)
    return stream.getvalue()
