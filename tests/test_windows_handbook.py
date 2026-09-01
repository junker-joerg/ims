from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
HANDBOOK_ROOT = REPO_ROOT / "docs" / "handbook"


def _read(filename: str) -> str:
    return (HANDBOOK_ROOT / filename).read_text(encoding="utf-8")


def _jpeg_size(path: Path) -> tuple[int, int]:
    payload = path.read_bytes()
    assert payload.startswith(b"\xff\xd8")
    offset = 2
    start_of_frame_markers = {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
    while offset < len(payload):
        assert payload[offset] == 0xFF
        while offset < len(payload) and payload[offset] == 0xFF:
            offset += 1
        marker = payload[offset]
        offset += 1
        if marker in start_of_frame_markers:
            height = int.from_bytes(payload[offset + 3 : offset + 5], "big")
            width = int.from_bytes(payload[offset + 5 : offset + 7], "big")
            return width, height
        segment_length = int.from_bytes(payload[offset : offset + 2], "big")
        offset += segment_length
    raise AssertionError("JPEG contains no start-of-frame marker")


def test_windows_quickstart_is_complete_and_non_executing() -> None:
    quickstart = _read("quickstart_windows.md")
    normalized = " ".join(quickstart.split())

    for text in (
        'Set-Location "C:\\IMS Tests\\IMS Workbench 2026"',
        "python --version",
        ".\\install-workbench.cmd",
        ".\\check-workbench.cmd",
        ".\\start-workbench.cmd",
        "http://127.0.0.1:8000/",
        "/api/health",
        "Strg+C",
    ):
        assert text in quickstart
    assert "Node.js ist fuer diesen Weg nicht erforderlich" in normalized
    assert "kein eigenstaendiger Installer" in normalized
    assert "keine fachliche Produktionsfreigabe" in normalized
    assert "kein Installations- oder Importordner" in normalized


def test_windows_installation_separates_portable_and_checkout_paths() -> None:
    installation = _read("installation_windows.md")
    normalized = " ".join(installation.split())

    assert "Supportstufe: `verified_windows_hb3`" in installation
    assert "## Weg A: Vorbereiteter portabler Ordner" in installation
    assert "## Weg B: Entwickler-Checkout" in installation
    assert "Python 3.12 oder neuer" in installation
    assert "Node.js 22" in installation
    assert ".\\install-workbench.cmd" in installation
    assert "`app\\python_port\\requirements-web.txt` lokal" in installation
    assert "npm.cmd ci --prefix .\\frontend" in installation
    assert "npm.cmd run build --prefix .\\frontend" in installation
    assert "Ein fehlendes `tsc`" in normalized
    assert "127.0.0.1" in installation
    assert "Strg+C" in installation
    assert "Windows-Explorer entfernen" in normalized
    assert "keine Queue-Aktion, kein Adapter und keine Simulation" in normalized


def test_windows_data_guide_covers_backup_update_and_rollback() -> None:
    data = _read("data_and_updates.md")
    normalized = " ".join(data.split())

    for heading in (
        "## Backup",
        "## Restore in einen neuen Pfad",
        "## Update Side-by-Side",
        "## Rollback",
        "## Aufbewahrung und Loeschen",
    ):
        assert heading in data
    assert "metadata.sqlite-wal" in data
    assert "metadata.sqlite-shm" in data
    assert "WorkBench" not in data
    assert "Eine neue Version wird nicht ueber die alte kopiert" in normalized
    assert "kein Nachweis historischer Vollgleichheit" in normalized


def test_hb3_screenshots_are_versioned_readable_jpegs() -> None:
    expected = (
        "windows_workbench_start_hb3_2026-09-01.jpg",
        "windows_workbench_validation_hb3_2026-09-01.jpg",
    )
    for filename in expected:
        path = HANDBOOK_ROOT / "images" / filename
        width, height = _jpeg_size(path)
        assert width >= 1000
        assert height >= 600

    quickstart = _read("quickstart_windows.md")
    for filename in expected:
        assert f"images/{filename}" in quickstart
    assert quickstart.count("aufgenommen am 2026-09-01") == 2


def test_hb3_links_resolve_and_platform_limits_remain_open() -> None:
    for filename in (
        "quickstart_windows.md",
        "installation_windows.md",
        "data_and_updates.md",
    ):
        assert (HANDBOOK_ROOT / filename).is_file()

    reference = _read("technical_reference.md")
    normalized_reference = " ".join(reference.split())
    plan = (REPO_ROOT / "docs" / "plans" / "user_installation_handbook_plan.md").read_text(
        encoding="utf-8"
    )
    normalized_plan = " ".join(plan.split())

    assert "verified_windows_hb3" in reference
    assert "Linux bleibt bis HB4 `not_verified`" in normalized_reference
    assert "iOS/Juno bleibt bis HB5 `feasibility_open`" in normalized_reference
    assert "Nach HB3a bleiben **3 Handbuch-Schnitte**" in normalized_plan
    assert "PR102 und HB4 sind die naechsten getrennten Schnitte" in normalized_plan
