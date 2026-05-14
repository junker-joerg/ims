from dataclasses import dataclass
from pathlib import Path

from ims.model.agrsich_export import ExportTable, POLICYHOLDER_HEADER


POLICYHOLDER_FIELD_NAMES = [
    "Vu1",
    "Vs1",
    "Vp1",
    "Ev1",
    "Sh1",
    "Vu2",
    "Vs2",
    "Vp2",
    "Ev2",
    "Sh2",
    "Vm",
]


@dataclass(slots=True)
class LegacyPolicyholderRow:
    global_period: int
    insurer_1: float
    insured_1: float
    premium_1: float
    wealth_1: float
    claim_sum_1: float
    insurer_2: float
    insured_2: float
    premium_2: float
    wealth_2: float
    claim_sum_2: float
    wealth_total: float

    def metric_values(self) -> list[float]:
        return [
            self.insurer_1,
            self.insured_1,
            self.premium_1,
            self.wealth_1,
            self.claim_sum_1,
            self.insurer_2,
            self.insured_2,
            self.premium_2,
            self.wealth_2,
            self.claim_sum_2,
            self.wealth_total,
        ]


@dataclass(slots=True)
class LegacyPolicyholderTable:
    path: Path
    header: str
    rows: list[LegacyPolicyholderRow]


@dataclass(slots=True)
class LegacyPolicyholderFieldComparison:
    name: str
    actual: str | float | int
    expected: str | float | int
    matches: bool


@dataclass(slots=True)
class LegacyPolicyholderComparison:
    matches: bool
    field_comparisons: list[LegacyPolicyholderFieldComparison]


def _normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


def parse_legacy_policyholder_dat(path: str | Path) -> LegacyPolicyholderTable:
    file_path = Path(path)
    raw_text = file_path.read_text(encoding="utf-8")
    normalized_text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line for line in normalized_text.split("\n") if line.strip()]
    if not lines:
        raise ValueError(f"legacy policyholder file is empty: {file_path}")

    header = lines[0]
    rows: list[LegacyPolicyholderRow] = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) != 12:
            raise ValueError(f"legacy policyholder row must contain 12 columns: {line}")
        rows.append(
            LegacyPolicyholderRow(
                global_period=int(parts[0]),
                insurer_1=float(parts[1]),
                insured_1=float(parts[2]),
                premium_1=float(parts[3]),
                wealth_1=float(parts[4]),
                claim_sum_1=float(parts[5]),
                insurer_2=float(parts[6]),
                insured_2=float(parts[7]),
                premium_2=float(parts[8]),
                wealth_2=float(parts[9]),
                claim_sum_2=float(parts[10]),
                wealth_total=float(parts[11]),
            )
        )

    return LegacyPolicyholderTable(path=file_path, header=header, rows=rows)


def extract_legacy_policyholder_row(
    table: LegacyPolicyholderTable,
    global_period: int,
) -> LegacyPolicyholderRow | None:
    for row in table.rows:
        if row.global_period == global_period:
            return row
    return None


def compare_policyholder_export_record_to_legacy_row(
    export_record: ExportTable,
    legacy_row: LegacyPolicyholderRow,
    *,
    tolerance: float = 0.05,
) -> LegacyPolicyholderComparison:
    if not export_record.rows:
        raise ValueError("export record must contain at least one row")

    export_values = export_record.rows[0].values
    if len(export_values) != 12:
        raise ValueError("export policyholder row must contain 12 values")

    field_comparisons: list[LegacyPolicyholderFieldComparison] = []
    normalized_actual_header = _normalize_whitespace(export_record.header)
    normalized_expected_header = _normalize_whitespace(POLICYHOLDER_HEADER)
    field_comparisons.append(
        LegacyPolicyholderFieldComparison(
            name="header",
            actual=normalized_actual_header,
            expected=normalized_expected_header,
            matches=normalized_actual_header == normalized_expected_header,
        )
    )

    actual_period = int(export_values[0])
    field_comparisons.append(
        LegacyPolicyholderFieldComparison(
            name="global_period",
            actual=actual_period,
            expected=legacy_row.global_period,
            matches=actual_period == legacy_row.global_period,
        )
    )

    for name, actual, expected in zip(
        POLICYHOLDER_FIELD_NAMES,
        export_values[1:],
        legacy_row.metric_values(),
    ):
        actual_value = float(actual)
        expected_value = float(expected)
        field_comparisons.append(
            LegacyPolicyholderFieldComparison(
                name=name,
                actual=actual_value,
                expected=expected_value,
                matches=abs(actual_value - expected_value) <= tolerance,
            )
        )

    return LegacyPolicyholderComparison(
        matches=all(item.matches for item in field_comparisons),
        field_comparisons=field_comparisons,
    )
