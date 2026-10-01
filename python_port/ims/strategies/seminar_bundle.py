"""Portable complete seminar sources; imported results are freshly verified."""

from copy import deepcopy

from ims.accounting.management_case import digest
from ims.api.guided_period_chain import GuidedChainError, build as build_guided
from ims.ict.simulation import calculate as calculate_ict
from ims.strategies.modern_bridge import ContractError, calculate, exact
from ims.strategies.seminar_capital import assumptions

BUNDLE_VERSION = "ims.seminar-bundle.v1"


def portable_numbers(value: object) -> object:
    """Preserve JSON numeric values across browser parse/stringify transport.

    Original sources are validated before this representation-only conversion;
    invalid typed periods/IDs must not be made valid by normalization.
    """
    if type(value) is float and value.is_integer():
        return int(value)
    if isinstance(value, dict):
        return {key: portable_numbers(item) for key, item in value.items()}
    if isinstance(value, list):
        return [portable_numbers(item) for item in value]
    return deepcopy(value)


def verified_sources(sources: object) -> dict:
    exact(sources, {"modern", "ict", "guided"}, "$.sources")
    modern = calculate(sources["modern"])
    if not modern["valid"]:
        issue = modern["issues"][0]
        raise ContractError("$.sources.modern" + issue["path"].removeprefix("$"), issue["message"])
    ict = calculate_ict(sources["ict"])
    if not ict["valid"]:
        issue = ict["issues"][0]
        raise ContractError("$.sources.ict" + issue["path"].removeprefix("$"), issue["message"])
    try: guided = build_guided(sources["guided"]).result
    except GuidedChainError as exc: raise ContractError("$.sources.guided" + exc.path.removeprefix("$"), str(exc)) from exc
    return {"modern": modern, "ict": ict, "guided": guided}


def _pack(sources: dict, title: object, results: dict) -> dict:
    if type(title) is not str or not title.strip() or len(title) > 200:
        raise ContractError("$.title", "Seminartitel mit 1–200 Zeichen erforderlich")
    core = {"schema_version": BUNDLE_VERSION, "title": title, "sources": deepcopy(sources),
        "expected_content_digests": {key: result["content_digest"] for key, result in results.items()},
        "scope": "modern_four_sector_and_separate_ict_and_anonymous_historical_chain",
        "capital_assumptions": assumptions(sources["modern"]["period_count"], sources["modern"]["case_id"])}
    return {**core, "bundle_digest": digest(core)}


def pack(sources: object, title: object) -> dict:
    results = verified_sources(sources)
    portable = portable_numbers(sources)
    if digest(portable) != digest(sources):
        results = verified_sources(portable)
    return _pack(portable, title, results)


def unpack(value: object) -> dict:
    doc = exact(value, {"schema_version", "title", "sources", "expected_content_digests", "scope", "capital_assumptions", "bundle_digest"}, "$")
    if doc["schema_version"] != BUNDLE_VERSION:
        raise ContractError("$.schema_version", "Versioniertes Seminarbündel erforderlich")
    core = {key: item for key, item in doc.items() if key != "bundle_digest"}
    try: expected = digest(core)
    except (ValueError, TypeError, RecursionError) as exc: raise ContractError("$", "Seminarbündel ist nicht kanonisch darstellbar") from exc
    if doc["bundle_digest"] != expected:
        raise ContractError("$.bundle_digest", "Seminarbündel wurde verändert; Inhaltsnachweis stimmt nicht")
    if digest(doc["sources"]) != digest(portable_numbers(doc["sources"])):
        raise ContractError("$.sources", "Portables JSON benötigt Ganzzahldarstellung für ganzzahlige Zahlenwerte")
    # Rebuild every source, even when the supplied envelope hash is consistent.
    results = verified_sources(doc["sources"])
    rebuilt = _pack(doc["sources"], doc["title"], results)
    if rebuilt != doc:
        raise ContractError("$.expected_content_digests", "Frisch gerechnete Quellen oder Vertragsgrenzen stimmen nicht mit dem Bündel überein")
    return {"valid": True, "issues": [], "content_digest": doc["bundle_digest"], "bundle": deepcopy(doc), "results": results,
        "demo_mode": "read_only_fresh_calculation", "writes_performed": False, "stored_candidates": False, "historical_runner_invoked": False}
