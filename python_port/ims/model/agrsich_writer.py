from dataclasses import dataclass
from pathlib import Path

from ims.model.agrsich_export import ExportTable, render_export_header, render_export_row


@dataclass(slots=True)
class FileComparison:
    filename: str
    matches: bool
    actual_text: str
    reference_text: str


@dataclass(slots=True)
class ComparisonResult:
    all_match: bool
    comparisons: list[FileComparison]


def write_agrsich_export_tables(
    output_dir: str | Path,
    tables: list[ExportTable],
    *,
    append: bool = True,
) -> list[Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    written_files: list[Path] = []
    for table in tables:
        target = output_path / table.spec.filename
        file_exists = target.exists()
        mode = "a" if append and file_exists else "w"
        with target.open(mode, encoding="utf-8") as handle:
            if not file_exists or not append:
                handle.write(render_export_header(table))
            for row in table.rows:
                handle.write(render_export_row(row))
        written_files.append(target)
    return written_files


def compare_export_files_to_reference(
    output_dir: str | Path,
    reference_dir: str | Path,
    *,
    filenames: list[str] | None = None,
) -> ComparisonResult:
    output_path = Path(output_dir)
    reference_path = Path(reference_dir)

    if filenames is None:
        filenames = sorted({path.name for path in output_path.glob("*.dat")} | {path.name for path in reference_path.glob("*.dat")})

    comparisons: list[FileComparison] = []
    for filename in filenames:
        actual_file = output_path / filename
        reference_file = reference_path / filename
        actual_text = actual_file.read_text(encoding="utf-8") if actual_file.exists() else ""
        reference_text = reference_file.read_text(encoding="utf-8") if reference_file.exists() else ""
        comparisons.append(
            FileComparison(
                filename=filename,
                matches=actual_file.exists() and reference_file.exists() and actual_text == reference_text,
                actual_text=actual_text,
                reference_text=reference_text,
            )
        )

    return ComparisonResult(
        all_match=all(comparison.matches for comparison in comparisons),
        comparisons=comparisons,
    )
