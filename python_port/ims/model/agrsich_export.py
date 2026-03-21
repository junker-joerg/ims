from dataclasses import dataclass

from ims.engine.context import SimulationContext
from ims.model.agrsich_service import AgrsichResult, AggregateRecord


INSURER_HEADER = "#t Pr1 Wa1 Rs1 Vn1 Sa1 Sh1 Pr2 Wa2 Rs2 Vn2 Sa2 Sh2"
POLICYHOLDER_HEADER = "#t Pz1 Se1 St1 Vu1 Sh1 Pz2 Se2 St2 Vu2 Sh2 Ev"


@dataclass(slots=True)
class ExportFileSpec:
    filename: str
    subject_type: str
    level: str
    selector_kind: str
    selector_value: int | str | None


@dataclass(slots=True)
class ExportRow:
    values: list[float | int | None]


@dataclass(slots=True)
class ExportTable:
    spec: ExportFileSpec
    header: str
    rows: list[ExportRow]


def compute_global_period(context: SimulationContext) -> int:
    if context.max_periods <= 0:
        return context.period
    return context.run_index * context.max_periods + context.period


def _format_filename(record: AggregateRecord) -> str:
    if record.subject_type == "insurer" and record.aggregate_level == "I":
        return f"imsvu{int(record.aggregate_key):03d}.dat"
    if record.subject_type == "policyholder" and record.aggregate_level == "I":
        return f"imsvn{int(record.aggregate_key):03d}.dat"
    if record.subject_type == "insurer" and record.aggregate_level == "II":
        return f"imsvur{int(record.aggregate_key):02d}.dat"
    if record.subject_type == "policyholder" and record.aggregate_level == "II":
        return f"imsvnr{int(record.aggregate_key):02d}.dat"
    if record.subject_type == "insurer" and record.aggregate_level == "III":
        return f"imsvuvk{int(record.aggregate_key)}.dat"
    if record.subject_type == "policyholder" and record.aggregate_level == "III":
        return f"imsvnvk{int(record.aggregate_key)}.dat"
    if record.subject_type == "insurer" and record.aggregate_level == "IV":
        return "imsvusk1.dat"
    if record.subject_type == "policyholder" and record.aggregate_level == "IV":
        return "imsvnsk1.dat"
    raise ValueError(f"unsupported aggregate record for export: {record}")


def _selector_kind(record: AggregateRecord) -> str:
    if record.aggregate_level == "I":
        return "entity"
    if record.aggregate_level == "II":
        return "rule"
    if record.aggregate_level == "III":
        return "rule_class"
    return "all"


def _insurer_values(global_period: int, metrics: dict[str, float | int | None]) -> list[float | int | None]:
    return [
        global_period,
        metrics["premium_1"],
        metrics["advertising_1"],
        metrics["reserves_1"],
        metrics["policyholders_1"],
        metrics["claims_count_1"],
        metrics["claims_sum_1"],
        metrics["premium_2"],
        metrics["advertising_2"],
        metrics["reserves_2"],
        metrics["policyholders_2"],
        metrics["claims_count_2"],
        metrics["claims_sum_2"],
    ]


def _policyholder_values(global_period: int, metrics: dict[str, float | int | None]) -> list[float | int | None]:
    return [
        global_period,
        metrics["paid_premium_1"],
        metrics["self_damage_1"],
        metrics["coverage_1"],
        metrics["chosen_insurer_1"],
        metrics["claim_sum_1"],
        metrics["paid_premium_2"],
        metrics["self_damage_2"],
        metrics["coverage_2"],
        metrics["chosen_insurer_2"],
        metrics["claim_sum_2"],
        metrics["end_wealth"],
    ]


def build_agrsich_export_tables(context: SimulationContext, agrsich_result: AgrsichResult) -> list[ExportTable]:
    global_period = compute_global_period(context)
    tables: list[ExportTable] = []
    for record in agrsich_result.insurer_records + agrsich_result.policyholder_records:
        header = INSURER_HEADER if record.subject_type == "insurer" else POLICYHOLDER_HEADER
        values = _insurer_values(global_period, record.metrics) if record.subject_type == "insurer" else _policyholder_values(global_period, record.metrics)
        tables.append(
            ExportTable(
                spec=ExportFileSpec(
                    filename=_format_filename(record),
                    subject_type=record.subject_type,
                    level=record.aggregate_level,
                    selector_kind=_selector_kind(record),
                    selector_value=record.aggregate_key,
                ),
                header=header,
                rows=[ExportRow(values=values)],
            )
        )
    return tables
