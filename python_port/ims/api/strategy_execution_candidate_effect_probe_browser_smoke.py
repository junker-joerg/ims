from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from ims.api.app import create_app
from ims.api.metadata_import import MetadataImportError
from ims.api.metadata_repository import build_seeded_metadata_repository
from ims.api.strategy_execution_candidate_effect_probe import (
    StrategyExecutionCandidateEffectProbeRunner,
)
from ims.api.strategy_execution_candidate_store import (
    STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION,
    persist_strategy_execution_candidate,
)
from ims.strategies.execution_candidate_build import (
    build_default_strategy_execution_scenario_profiles,
    build_strategy_execution_candidate,
    strategy_execution_scenario_profile_root,
)


STRATEGY_CANDIDATE_BROWSER_SMOKE_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
STRATEGY_CANDIDATE_BROWSER_SMOKE_FIXTURE = (
    Path(__file__).resolve().parents[3]
    / "tests"
    / "fixtures"
    / "strategy_execution_candidate_input_v1.json"
)


def create_strategy_candidate_browser_smoke_app(
    *,
    db_path: str | Path,
    frontend_dist: str | Path,
    candidate_effect_probe_runner: (
        StrategyExecutionCandidateEffectProbeRunner | None
    ) = None,
) -> Any:
    """Baut eine frische, lokale PR132-Abnahmeinstanz mit einem Kandidaten."""

    resolved_db_path = Path(db_path).expanduser().resolve()
    resolved_frontend_dist = Path(frontend_dist).expanduser().resolve()
    if resolved_db_path.exists():
        raise MetadataImportError(
            "strategy candidate browser smoke requires a fresh metadata "
            f"database: {resolved_db_path}"
        )
    if not (resolved_frontend_dist / "index.html").is_file():
        raise MetadataImportError(
            "strategy candidate browser smoke requires a built frontend: "
            f"{resolved_frontend_dist}"
        )
    if not STRATEGY_CANDIDATE_BROWSER_SMOKE_FIXTURE.is_file():
        raise MetadataImportError(
            "strategy candidate browser smoke fixture is missing: "
            f"{STRATEGY_CANDIDATE_BROWSER_SMOKE_FIXTURE}"
        )

    try:
        candidate_input = json.loads(
            STRATEGY_CANDIDATE_BROWSER_SMOKE_FIXTURE.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise MetadataImportError(
            f"strategy candidate browser smoke fixture is unreadable: {exc}"
        ) from exc
    profiles = build_default_strategy_execution_scenario_profiles()
    profile_root = strategy_execution_scenario_profile_root()
    build = build_strategy_execution_candidate(
        candidate_input,
        profiles=profiles,
        trusted_profile_root=profile_root,
    )
    if not build.build_complete or build.candidate is None:
        issue_codes = ", ".join(issue.code for issue in build.issues)
        raise MetadataImportError(
            "strategy candidate browser smoke fixture cannot be built"
            + (f": {issue_codes}" if issue_codes else "")
        )

    resolved_db_path.parent.mkdir(parents=True, exist_ok=True)
    repository = build_seeded_metadata_repository(resolved_db_path)
    persist_strategy_execution_candidate(
        {
            "schema_version": STRATEGY_EXECUTION_CANDIDATE_STORE_REQUEST_VERSION,
            "candidate_input": candidate_input,
            "expected_candidate_id": build.candidate.candidate_id,
            "expected_content_digest": build.candidate.content_digest,
            "stored_at": "2026-09-11T09:00:00+02:00",
            "explicit_storage_release": True,
        },
        db_path=resolved_db_path,
        profiles=profiles,
        trusted_profile_root=profile_root,
    )
    return create_app(
        frontend_dist=resolved_frontend_dist,
        metadata_repository=repository,
        candidate_effect_probe_runner=candidate_effect_probe_runner,
    )


def require_strategy_candidate_browser_smoke_host(host: str) -> str:
    normalized_host = host.strip().lower()
    if normalized_host not in STRATEGY_CANDIDATE_BROWSER_SMOKE_HOSTS:
        raise MetadataImportError(
            "strategy candidate browser smoke server must use a loopback host: "
            + ", ".join(sorted(STRATEGY_CANDIDATE_BROWSER_SMOKE_HOSTS))
        )
    return normalized_host


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    host = require_strategy_candidate_browser_smoke_host(args.host)
    app = create_strategy_candidate_browser_smoke_app(
        db_path=args.db,
        frontend_dist=args.frontend_dist,
    )

    import uvicorn

    uvicorn.run(app, host=host, port=args.port)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Startet den isolierten PR132-Browser-Smoke fuer die "
            "Einperioden-Wirkungsprobe."
        )
    )
    parser.add_argument("--db", required=True, help="Frische SQLite-Datei.")
    parser.add_argument(
        "--frontend-dist",
        required=True,
        help="Pfad zum gebauten Workbench-Frontend.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8012)
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
