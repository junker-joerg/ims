from hashlib import sha256
import json
from pathlib import Path

from ims.model.legacy_agrsich_reference import parse_legacy_insurer_dat
from ims.model.legacy_validation_coverage import build_legacy_validation_coverage_matrix


REPO_ROOT = Path(__file__).resolve().parents[1]
LAYER_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "legacy_zins000_reference_layer.json"
CORE_BUNDLE = REPO_ROOT / "tests" / "fixtures" / "legacy_validation_bundle.json"
CORE_REFERENCE_DIR = REPO_ROOT / "tests" / "references" / "legacy_agrsich"
ZINS000_REFERENCE_DIR = CORE_REFERENCE_DIR / "zins000"
MIGRATION_DOC = REPO_ROOT / "docs" / "migration" / "zins000_reference_layer.md"


def _load_layer_fixture() -> dict[str, object]:
    return json.loads(LAYER_FIXTURE.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _rows_by_period(path: Path) -> dict[int, list[float]]:
    table = parse_legacy_insurer_dat(path)
    return {row.global_period: row.metric_values() for row in table.rows}


def test_zins000_manifest_fixes_separate_layer_and_mapping() -> None:
    fixture = _load_layer_fixture()

    assert fixture["layer_id"] == "zins000"
    assert fixture["layer_status"] == "versioned_separate_reference_layer"
    assert fixture["source_context"] == "incomming/ZINS000"
    assert fixture["core_bundle_included"] is False
    assert fixture["comparison_scope"] == "parser_provenance_and_overlap_only"
    assert fixture["references"] == [
        {
            "legacy_path": "../references/legacy_agrsich/zins000/IMSVU014.DAT",
            "sha256": "0276eab7b1f80dfc39773eb0e5a4a5df02b69b140792be9f810baa222e8ce828",
            "subject_type": "insurer",
            "export_filename": "imsvu014.dat",
            "level": "I",
            "selector_kind": "entity",
            "selector_value": 14,
            "start_period": 1,
            "end_period": 300,
            "row_count": 300,
        },
        {
            "legacy_path": "../references/legacy_agrsich/zins000/IMSVUSK1.DAT",
            "sha256": "dc066d624c443fc165b0fb83481083dae33d823bd8a3a20d934adb4bf5426b2a",
            "subject_type": "insurer",
            "export_filename": "imsvusk1.dat",
            "level": "IV",
            "selector_kind": "all",
            "selector_value": "SK1",
            "start_period": 1,
            "end_period": 300,
            "row_count": 300,
        },
    ]


def test_zins000_references_match_hash_header_and_period_boundaries() -> None:
    fixture = _load_layer_fixture()
    expected_header = [
        "#t",
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

    for reference in fixture["references"]:
        path = (LAYER_FIXTURE.parent / reference["legacy_path"]).resolve()
        table = parse_legacy_insurer_dat(path)

        assert path.parent == ZINS000_REFERENCE_DIR.resolve()
        assert _sha256(path) == reference["sha256"]
        assert table.header.split() == expected_header
        assert len(table.rows) == reference["row_count"]
        assert [row.global_period for row in table.rows] == list(range(1, 301))


def test_zins000_layer_is_not_counted_as_core_bundle_coverage() -> None:
    core_bundle = json.loads(CORE_BUNDLE.read_text(encoding="utf-8"))
    result = build_legacy_validation_coverage_matrix(CORE_BUNDLE)

    assert all("zins000" not in target["legacy_path"].lower() for target in core_bundle["targets"])
    assert result.status == "ok"
    assert result.reference_count == 19
    assert result.available_reference_count == 19
    assert result.covered_file_count == 19
    assert result.covered_periods == 6300


def test_zins000_references_are_not_numeric_baseline_extensions() -> None:
    vu14_rows = _rows_by_period(ZINS000_REFERENCE_DIR / "IMSVU014.DAT")
    vu14_baseline = _rows_by_period(CORE_REFERENCE_DIR / "VU14L1.DAT")
    vu14_equal_rows = sum(vu14_rows[period] == values for period, values in vu14_baseline.items())

    sk1_rows = _rows_by_period(ZINS000_REFERENCE_DIR / "IMSVUSK1.DAT")
    sk1_baseline: dict[int, list[float]] = {}
    for filename in ("VUSK1L5.DAT", "VUSK1L4.DAT", "VUSK1L3.DAT"):
        sk1_baseline.update(_rows_by_period(CORE_REFERENCE_DIR / filename))
    sk1_equal_rows = sum(sk1_rows[period] == values for period, values in sk1_baseline.items())

    assert vu14_equal_rows == 0
    assert sk1_equal_rows == 0


def test_zins000_documentation_keeps_validation_claim_conservative() -> None:
    doc = MIGRATION_DOC.read_text(encoding="utf-8")

    assert "Getrennte historische Referenzschicht ZINS000" in doc
    assert "Kern bleibt bei 19 Dateien und 6.300 Vergleichsperioden" in doc
    assert "portiert keine C-Logik" in doc
    assert "insurer / Stufe I / `entity = 14`" in doc
    assert "insurer / Stufe IV / `all = SK1`" in doc
    assert "`0/100`" in doc
    assert "`0/300`" in doc
    assert "kein fachlicher Abweichungsbefund" in doc
    assert "keine historische" in doc and "Vollgleichheit behauptet" in doc
    assert "`incomming/` selbst bleibt unversioniert" in doc
