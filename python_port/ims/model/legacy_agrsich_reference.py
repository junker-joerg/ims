from dataclasses import dataclass
from pathlib import Path

from ims.model.agrsich_export import INSURER_HEADER, ExportTable


INSURER_FIELD_NAMES = [
    "Pr1",
    "Wa1",
    "Rs1",
    "Vn1",
    "Sa1",
    "Sh1",
    "Pr2",
    "Wa2",
    "Rs2",
    "Vn2",
    "Sa2",
    "Sh2",
]


@dataclass(slots=True)
class LegacyInsurerRow:
    global_period: int
    premium_1: float
    advertising_1: float
    reserves_1: float
    policyholders_1: float
    claims_count_1: float
    claims_sum_1: float
    premium_2: float
    advertising_2: float
    reserves_2: float
    policyholders_2: float
    claims_count_2: float
    claims_sum_2: float

    def metric_values(self) -> list[float]:
        return [
            self.premium_1,
            self.advertising_1,
            self.reserves_1,
            self.policyholders_1,
            self.claims_count_1,
            self.claims_sum_1,
            self.premium_2,
            self.advertising_2,
            self.reserves_2,
            self.policyholders_2,
            self.claims_count_2,
            self.claims_sum_2,
        ]


@dataclass(slots=True)
class LegacyInsurerTable:
    path: Path
    header: str
    rows: list[LegacyInsurerRow]


@dataclass(slots=True)
class LegacyFieldComparison:
    name: str
    actual: str | float | int
    expected: str | float | int
    matches: bool


@dataclass(slots=True)
class LegacyComparison:
    matches: bool
    field_comparisons: list[LegacyFieldComparison]


@dataclass(slots=True)
class LegacyRowComparison:
    global_period: int | None
    matches: bool
    field_comparisons: list[LegacyFieldComparison]


@dataclass(slots=True)
class LegacyWindowComparison:
    matches: bool
    export_path: Path
    legacy_path: Path
    start_period: int
    end_period: int
    row_comparisons: list[LegacyRowComparison]


def _normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


def _parse_float(value: str) -> float:
    return float(value)


def parse_legacy_insurer_dat(path: str | Path) -> LegacyInsurerTable:
    file_path = Path(path)
    raw_text = file_path.read_text(encoding="utf-8")
    normalized_text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line for line in normalized_text.split("\n") if line.strip()]
    if not lines:
        raise ValueError(f"legacy insurer file is empty: {file_path}")

    header = lines[0]
    rows: list[LegacyInsurerRow] = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) != 13:
            raise ValueError(f"legacy insurer row must contain 13 columns: {line}")
        rows.append(
            LegacyInsurerRow(
                global_period=int(parts[0]),
                premium_1=_parse_float(parts[1]),
                advertising_1=_parse_float(parts[2]),
                reserves_1=_parse_float(parts[3]),
                policyholders_1=_parse_float(parts[4]),
                claims_count_1=_parse_float(parts[5]),
                claims_sum_1=_parse_float(parts[6]),
                premium_2=_parse_float(parts[7]),
                advertising_2=_parse_float(parts[8]),
                reserves_2=_parse_float(parts[9]),
                policyholders_2=_parse_float(parts[10]),
                claims_count_2=_parse_float(parts[11]),
                claims_sum_2=_parse_float(parts[12]),
            )
        )

    return LegacyInsurerTable(path=file_path, header=header, rows=rows)


def extract_legacy_row(table: LegacyInsurerTable, global_period: int) -> LegacyInsurerRow | None:
    for row in table.rows:
        if row.global_period == global_period:
            return row
    return None


def extract_legacy_window(
    table: LegacyInsurerTable,
    start_period: int,
    end_period: int,
) -> list[LegacyInsurerRow]:
    return [row for row in table.rows if start_period <= row.global_period <= end_period]


def compare_export_record_to_legacy_row(
    export_record: ExportTable,
    legacy_row: LegacyInsurerRow,
    *,
    tolerance: float = 0.05,
) -> LegacyComparison:
    if not export_record.rows:
        raise ValueError("export record must contain at least one row")

    export_values = export_record.rows[0].values
    if len(export_values) != 13:
        raise ValueError("export insurer row must contain 13 values")

    field_comparisons: list[LegacyFieldComparison] = []
    normalized_actual_header = _normalize_whitespace(export_record.header)
    normalized_expected_header = _normalize_whitespace(INSURER_HEADER)
    field_comparisons.append(
        LegacyFieldComparison(
            name="header",
            actual=normalized_actual_header,
            expected=normalized_expected_header,
            matches=normalized_actual_header == normalized_expected_header,
        )
    )

    actual_period = int(export_values[0])
    field_comparisons.append(
        LegacyFieldComparison(
            name="global_period",
            actual=actual_period,
            expected=legacy_row.global_period,
            matches=actual_period == legacy_row.global_period,
        )
    )

    for name, actual, expected in zip(INSURER_FIELD_NAMES, export_values[1:], legacy_row.metric_values()):
        actual_value = float(actual)
        expected_value = float(expected)
        field_comparisons.append(
            LegacyFieldComparison(
                name=name,
                actual=actual_value,
                expected=expected_value,
                matches=abs(actual_value - expected_value) <= tolerance,
            )
        )

    return LegacyComparison(
        matches=all(item.matches for item in field_comparisons),
        field_comparisons=field_comparisons,
    )


def _parse_export_rows(export_path: Path) -> tuple[str, list[list[float]]]:
    raw_text = export_path.read_text(encoding="utf-8")
    normalized_text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line for line in normalized_text.split("\n") if line.strip()]
    if not lines:
        raise ValueError(f"export file is empty: {export_path}")

    rows: list[list[float]] = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) != 13:
            raise ValueError(f"export insurer row must contain 13 columns: {line}")
        rows.append([float(part) for part in parts])
    return lines[0], rows


def _missing_export_row_comparison(expected_period: int) -> LegacyRowComparison:
    return LegacyRowComparison(
        global_period=expected_period,
        matches=False,
        field_comparisons=[
            LegacyFieldComparison(
                name="global_period",
                actual="missing export row",
                expected=expected_period,
                matches=False,
            )
        ],
    )


def _unexpected_export_row_comparison(actual_period: int) -> LegacyRowComparison:
    return LegacyRowComparison(
        global_period=actual_period,
        matches=False,
        field_comparisons=[
            LegacyFieldComparison(
                name="global_period",
                actual=actual_period,
                expected="outside legacy window",
                matches=False,
            )
        ],
    )


def _duplicate_export_row_comparison(actual_period: int) -> LegacyRowComparison:
    return LegacyRowComparison(
        global_period=actual_period,
        matches=False,
        field_comparisons=[
            LegacyFieldComparison(
                name="global_period",
                actual=actual_period,
                expected="unique global period",
                matches=False,
            )
        ],
    )


def compare_export_file_to_legacy_window(
    export_path: str | Path,
    legacy_table: LegacyInsurerTable,
    start_period: int,
    end_period: int,
    *,
    tolerance: float = 0.05,
) -> LegacyWindowComparison:
    file_path = Path(export_path)
    export_header, export_rows = _parse_export_rows(file_path)
    export_rows_by_period: dict[int, list[float]] = {}
    duplicate_periods: set[int] = set()
    for row in export_rows:
        global_period = int(row[0])
        if global_period in export_rows_by_period:
            duplicate_periods.add(global_period)
            continue
        export_rows_by_period[global_period] = row

    legacy_rows = extract_legacy_window(legacy_table, start_period, end_period)
    legacy_periods = {row.global_period for row in legacy_rows}
    normalized_actual_header = _normalize_whitespace(export_header)
    normalized_expected_header = _normalize_whitespace(INSURER_HEADER)

    row_comparisons: list[LegacyRowComparison] = []
    for legacy_row in legacy_rows:
        export_values = export_rows_by_period.get(legacy_row.global_period)
        if export_values is None:
            row_comparisons.append(_missing_export_row_comparison(legacy_row.global_period))
            continue

        field_comparisons = [
            LegacyFieldComparison(
                name="header",
                actual=normalized_actual_header,
                expected=normalized_expected_header,
                matches=normalized_actual_header == normalized_expected_header,
            ),
            LegacyFieldComparison(
                name="global_period",
                actual=int(export_values[0]),
                expected=legacy_row.global_period,
                matches=int(export_values[0]) == legacy_row.global_period,
            ),
        ]
        for name, actual, expected in zip(INSURER_FIELD_NAMES, export_values[1:], legacy_row.metric_values()):
            actual_value = float(actual)
            expected_value = float(expected)
            field_comparisons.append(
                LegacyFieldComparison(
                    name=name,
                    actual=actual_value,
                    expected=expected_value,
                    matches=abs(actual_value - expected_value) <= tolerance,
                )
            )
        row_comparisons.append(
            LegacyRowComparison(
                global_period=legacy_row.global_period,
                matches=all(item.matches for item in field_comparisons),
                field_comparisons=field_comparisons,
            )
        )

    for actual_period in sorted(set(export_rows_by_period) - legacy_periods):
        row_comparisons.append(_unexpected_export_row_comparison(actual_period))
    for actual_period in sorted(duplicate_periods):
        row_comparisons.append(_duplicate_export_row_comparison(actual_period))

    return LegacyWindowComparison(
        matches=bool(row_comparisons) and all(row.matches for row in row_comparisons),
        export_path=file_path,
        legacy_path=legacy_table.path,
        start_period=start_period,
        end_period=end_period,
        row_comparisons=row_comparisons,
    )
