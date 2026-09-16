from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
import json
import multiprocessing as mp
import os
from pathlib import Path
import shutil
import sys
from time import monotonic
from typing import Callable

from ims.api.strategy_execution_candidate_effect_probe import (
    build_strategy_execution_candidate_scenario_mapping,
    build_strategy_execution_period_effect,
    project_strategy_execution_state,
)
from ims.api.strategy_execution_candidate_store import get_strategy_execution_candidate
from ims.api.strategy_execution_period_chain_build import (
    build_strategy_execution_period_chain,
)
from ims.api.strategy_execution_period_chain_five_period_effect_probe import (
    _transition_effect_payload,
)
from ims.api.strategy_execution_period_chain_five_period_effect_probe_start import (
    get_strategy_execution_five_period_effect_probe_result,
)
from ims.api.strategy_execution_period_chain_run_control import (
    parse_strategy_execution_period_chain_run_control_request,
)
from ims.engine.explicit_period_runner import run_loaded_explicit_period
from ims.engine.vn_rule_runner import apply_vn_state_carryover
from ims.engine.vu_rule_runner import apply_vu_foreign_info_carryover
from ims.io.scenario_loader import load_scenario_from_mapping
from ims.model.agrsich_export import compute_global_period
from ims.strategies.execution_period_chain_bounded_runner_contract import (
    STABLE_PREFIX_PERIOD_EFFECT_FIELDS,
    STABLE_PREFIX_TRANSITION_EFFECT_FIELDS,
    canonical_strategy_execution_prefix_bytes,
)
from ims.strategies.execution_period_chain_horizon_contract import (
    STRATEGY_EXECUTION_HORIZON_DEFINITIONS,
)


EXTENDED_PROBE_REQUEST_VERSION = "ims.strategy-execution-extended-probe-request.v1"
EXTENDED_PROBE_RESULT_VERSION = "ims.strategy-execution-extended-probe-result.v1"
_ENABLED_HORIZONS = {
    entry.period_count: entry for entry in STRATEGY_EXECUTION_HORIZON_DEFINITIONS[:3]
}
_MIB = 1024 * 1024
_MAX_WORKER_RSS = 1024 * _MIB
_MAX_PAYLOAD = 64 * _MIB
_MIN_DISK = 256 * _MIB
_PERIOD_SECONDS = 30


class ExtendedProbeError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class ExtendedProbeRequest:
    period_chain_input: dict[str, object]
    five_period_baseline: dict[str, str]
    release: dict[str, object]


def parse_extended_probe_request(value: object) -> ExtendedProbeRequest:
    expected = {
        "schema_version",
        "period_chain_input",
        "five_period_baseline",
        "release",
        "explicit_extended_effect_probe_execution",
    }
    if not isinstance(value, dict) or set(value) != expected:
        raise ExtendedProbeError(
            "invalid_request_fields", "Eindeutiger PR148-Eingang erforderlich"
        )
    if (
        value["schema_version"] != EXTENDED_PROBE_REQUEST_VERSION
        or value["explicit_extended_effect_probe_execution"] is not True
    ):
        raise ExtendedProbeError(
            "explicit_release_required",
            "Version und ausdrueckliche Freigabe erforderlich",
        )
    chain_input = value["period_chain_input"]
    if (
        not isinstance(chain_input, dict)
        or type(chain_input.get("max_periods")) is not int
        or chain_input["max_periods"] not in _ENABLED_HORIZONS
    ):
        raise ExtendedProbeError(
            "horizon_not_released", "Nur 10, 25 und 50 Perioden sind freigegeben"
        )
    baseline = value["five_period_baseline"]
    if (
        not isinstance(baseline, dict)
        or set(baseline)
        != {"chain_id", "expected_content_digest", "expected_result_digest"}
        or not all(isinstance(item, str) and item for item in baseline.values())
    ):
        raise ExtendedProbeError(
            "baseline_invalid", "Gespeicherte Fuenf-Perioden-Referenz erforderlich"
        )
    try:
        release = parse_strategy_execution_period_chain_run_control_request(
            value["release"]
        )
    except ValueError as exc:
        raise ExtendedProbeError("release_invalid", str(exc)) from exc
    return ExtendedProbeRequest(
        deepcopy(chain_input), dict(baseline), release.to_dict()
    )


def run_extended_probe(
    request: ExtendedProbeRequest,
    *,
    db_path: Path | str,
    worker_runner: Callable | None = None,
    cancel_requested: Callable[[], bool] | None = None,
) -> dict[str, object]:
    """Preflight in the parent; only the child sees mutable simulation state."""

    started = monotonic()
    period_count = request.period_chain_input.get("max_periods")
    if type(period_count) is not int or period_count not in _ENABLED_HORIZONS:
        raise ExtendedProbeError(
            "horizon_not_released", "Horizont ist nicht freigegeben"
        )
    budget = _ENABLED_HORIZONS[period_count].max_wall_seconds
    try:
        input_bytes = len(_canonical(request.period_chain_input))
    except (TypeError, ValueError, OverflowError) as exc:
        raise ExtendedProbeError("chain_input_not_canonical", str(exc)) from exc
    if input_bytes > _MAX_PAYLOAD:
        raise ExtendedProbeError(
            "chain_budget_exceeded", "Ketteneingang ueberschreitet 64 MiB"
        )
    db_path = Path(db_path).resolve()
    try:
        free_bytes = shutil.disk_usage(db_path.parent).free
    except OSError as exc:
        raise ExtendedProbeError("disk_measurement_unavailable", str(exc)) from exc
    if free_bytes < _MIN_DISK:
        raise ExtendedProbeError(
            "disk_budget_exceeded", "Nicht genug freier Speicherplatz"
        )
    build = build_strategy_execution_period_chain(
        request.period_chain_input, db_path=db_path
    )
    if not build.build_complete or build.chain is None:
        raise ExtendedProbeError("chain_not_ready", str(build.issues[:1]))
    chain = build.chain.to_dict()
    chain_bytes = len(_canonical(chain))
    if chain_bytes > _MAX_PAYLOAD:
        raise ExtendedProbeError(
            "chain_budget_exceeded", "Kettenpayload ueberschreitet 64 MiB"
        )
    release = request.release
    if (
        release.get("chain_id") != build.chain.chain_id
        or release.get("expected_content_digest") != build.chain.content_digest
        or release.get("explicit_run_control_release") is not True
    ):
        raise ExtendedProbeError(
            "release_mismatch", "Freigabe passt nicht zur erneut gebauten Kette"
        )
    ref = request.five_period_baseline
    try:
        stored = get_strategy_execution_five_period_effect_probe_result(
            ref["chain_id"], db_path=db_path
        ).record
    except ValueError as exc:
        raise ExtendedProbeError("baseline_invalid", str(exc)) from exc
    if (
        stored is None
        or stored.content_digest != ref["expected_content_digest"]
        or stored.result_digest != ref["expected_result_digest"]
    ):
        raise ExtendedProbeError(
            "baseline_mismatch",
            "Gespeicherter Fuenf-Perioden-Nachweis fehlt oder weicht ab",
        )
    baseline = stored.result_payload
    if (
        baseline.get("period_count") != 5
        or baseline.get("two_period_prefix_verified") is not True
        or baseline.get("prefix_proof", {}).get("prefix_equal") is not True
    ):
        raise ExtendedProbeError(
            "baseline_invalid",
            "Gespeicherter Nachweis enthaelt keinen stabilen Prefix 1-2",
        )
    baseline_prefix = _prefix(
        baseline["period_effects"], baseline["transition_effects"]
    )
    if monotonic() - started >= budget:
        raise ExtendedProbeError(
            "wall_budget_exceeded", "Zeitbudget vor Start verbraucht"
        )

    context = mp.get_context("spawn")
    receiving, sending = context.Pipe(duplex=False)
    worker = context.Process(
        target=_run_worker,
        args=(sending, chain, str(db_path), baseline_prefix, worker_runner),
        daemon=True,
    )
    try:
        worker.start()
    except (OSError, TypeError, ValueError) as exc:
        receiving.close()
        sending.close()
        raise ExtendedProbeError("worker_unavailable", str(exc)) from exc
    sending.close()
    period_started = None
    peak_rss = 0
    try:
        while True:
            if (
                period_started is None
                and cancel_requested is not None
                and cancel_requested()
            ):
                raise ExtendedProbeError("cancelled", "Expliziter Abbruch")
            if monotonic() - started > budget:
                raise ExtendedProbeError(
                    "wall_budget_exceeded", "Gesamtzeitbudget ueberschritten"
                )
            if (
                period_started is not None
                and monotonic() - period_started > _PERIOD_SECONDS
            ):
                raise ExtendedProbeError(
                    "period_budget_exceeded", "Periodenzeitbudget ueberschritten"
                )
            rss = _peak_worker_rss(worker.pid)
            if rss is None and worker.is_alive():
                raise ExtendedProbeError(
                    "rss_measurement_unavailable", "Peak-RSS kann nicht gemessen werden"
                )
            if rss is not None:
                peak_rss = max(peak_rss, rss)
            if peak_rss > _MAX_WORKER_RSS:
                raise ExtendedProbeError(
                    "rss_budget_exceeded", "Worker-RSS ueberschreitet 1024 MiB"
                )
            if receiving.poll(0.05):
                try:
                    kind, payload = receiving.recv()
                except EOFError as exc:
                    raise ExtendedProbeError(
                        "worker_failed", "Worker ohne Ergebnis beendet"
                    ) from exc
                if kind == "period_start":
                    period_started = monotonic()
                elif kind == "period_done":
                    period_started = None
                elif kind == "error":
                    raise ExtendedProbeError(payload["code"], payload["message"])
                elif kind == "result":
                    payload, final_rss = payload
                    if type(final_rss) is not int or final_rss <= 0:
                        raise ExtendedProbeError(
                            "rss_measurement_unavailable",
                            "Peak-RSS kann nicht gemessen werden",
                        )
                    peak_rss = max(peak_rss, final_rss)
                    if peak_rss > _MAX_WORKER_RSS:
                        raise ExtendedProbeError(
                            "rss_budget_exceeded", "Worker-RSS ueberschreitet 1024 MiB"
                        )
                    if len(payload) > _MAX_PAYLOAD:
                        raise ExtendedProbeError(
                            "result_budget_exceeded", "Ergebnis ueberschreitet 64 MiB"
                        )
                    result = json.loads(payload)
                    if (
                        result.get("period_count") != period_count
                        or result.get("prefix_equal") is not True
                    ):
                        raise ExtendedProbeError(
                            "worker_result_invalid",
                            "Worker-Ergebnis ist unvollstaendig",
                        )
                    result["effect_digest"] = "sha256:" + sha256(payload).hexdigest()
                    result["prefix_proof"] = {
                        "baseline_chain_id": ref["chain_id"],
                        "baseline_content_digest": ref["expected_content_digest"],
                        "baseline_result_digest": ref["expected_result_digest"],
                        "projection_digest": "sha256:"
                        + sha256(baseline_prefix).hexdigest(),
                        "canonical_json_byte_count": len(baseline_prefix),
                        "semantic_equal": True,
                        "canonical_json_byte_equal": True,
                    }
                    result["peak_worker_rss_bytes"] = peak_rss
                    result["chain_payload_bytes"] = chain_bytes
                    result["result_payload_bytes"] = len(payload)
                    result["wall_elapsed_seconds"] = monotonic() - started
                    if result["wall_elapsed_seconds"] > budget:
                        raise ExtendedProbeError(
                            "wall_budget_exceeded", "Gesamtzeitbudget ueberschritten"
                        )
                    if len(_canonical(result)) > _MAX_PAYLOAD:
                        raise ExtendedProbeError(
                            "result_budget_exceeded",
                            "Gesamtergebnispayload ueberschreitet 64 MiB",
                        )
                    return result
            elif not worker.is_alive():
                raise ExtendedProbeError(
                    "worker_failed", f"Worker beendet (exit={worker.exitcode})"
                )
    finally:
        if worker.is_alive():
            worker.terminate()
        worker.join(timeout=2)
        if worker.is_alive():
            worker.kill()
            worker.join()
        receiving.close()


def _run_worker(
    pipe,
    chain: dict[str, object],
    db_path: str,
    baseline_prefix: bytes,
    runner: Callable | None,
) -> None:
    try:
        result = _execute_chain(
            pipe, chain, db_path, baseline_prefix, runner or run_loaded_explicit_period
        )
        payload = _canonical(result)
        if len(payload) > _MAX_PAYLOAD:
            raise ExtendedProbeError(
                "result_budget_exceeded", "Ergebnis ueberschreitet 64 MiB"
            )
        peak_rss = _peak_worker_rss(os.getpid())
        if peak_rss is None:
            raise ExtendedProbeError(
                "rss_measurement_unavailable", "Peak-RSS kann nicht gemessen werden"
            )
        pipe.send(("result", (payload, peak_rss)))
    except Exception as exc:
        pipe.send(
            (
                "error",
                {"code": getattr(exc, "code", "worker_failed"), "message": str(exc)},
            )
        )
    finally:
        pipe.close()


def _execute_chain(
    pipe,
    chain: dict[str, object],
    db_path: str,
    baseline_prefix: bytes,
    runner: Callable,
) -> dict[str, object]:
    horizon = chain["horizon"]
    count = horizon["period_count"]
    references = chain["period_candidates"]
    transitions = chain["transitions"]
    if (
        count not in _ENABLED_HORIZONS
        or len(references) != count
        or len(transitions) != count - 1
    ):
        raise ExtendedProbeError("chain_invalid", "Kettenlaenge weicht ab")
    loaded = []
    originals = []
    for index, reference in enumerate(references, 1):
        record = get_strategy_execution_candidate(
            reference["candidate_id"], db_path=db_path
        ).record
        if (record.content_digest, record.period) != (
            reference["content_digest"],
            index,
        ):
            raise ExtendedProbeError("candidate_changed", f"Kandidat {index} weicht ab")
        originals.append(deepcopy(record.candidate))
        loaded.append(
            load_scenario_from_mapping(
                build_strategy_execution_candidate_scenario_mapping(
                    deepcopy(record.candidate)
                )
            )
        )
    identities = []
    for index, scenario in enumerate(loaded, 1):
        if (
            scenario.context.period != index
            or scenario.context.max_periods != count
            or scenario.context.run_index != horizon["run_index"]
        ):
            raise ExtendedProbeError("context_mismatch", f"Kontext {index} weicht ab")
        identities.append(
            (
                scenario.bav.entity_id,
                tuple(sorted(i.entity_id for i in scenario.insurers)),
                tuple(sorted(v.entity_id for v in scenario.policyholders)),
            )
        )
    if len(set(identities)) != 1:
        raise ExtendedProbeError("actor_mismatch", "Akteursidentitaet wechselt")
    if [compute_global_period(s.context) for s in loaded] != list(
        range(
            compute_global_period(loaded[0].context),
            compute_global_period(loaded[0].context) + count,
        )
    ):
        raise ExtendedProbeError(
            "global_period_mismatch", "Globalperioden sind nicht lueckenlos"
        )
    effects = []
    transition_effects = []
    carryover_count = 0
    for index, scenario in enumerate(loaded):
        period = index + 1
        pipe.send(("period_start", period))
        before = project_strategy_execution_state(scenario)
        execution = runner(scenario, output_dir=None)
        if execution.period != period or execution.written_files:
            raise ExtendedProbeError(
                "runner_invalid", f"Runner Periode {period} weicht ab"
            )
        effects.append(
            build_strategy_execution_period_effect(
                execution,
                state_before=before,
                state_after=project_strategy_execution_state(scenario),
            )
        )
        if period == 5 and _prefix(effects, transition_effects) != baseline_prefix:
            raise ExtendedProbeError(
                "prefix_mismatch", "Prefix 1-5 weicht vor Periode 6 ab"
            )
        if index == count - 1:
            pipe.send(("period_done", period))
            break
        transition = transitions[index]
        if (
            transition["from_period"] != period
            or transition["to_period"] != period + 1
            or type(transition["carry_forward_vu_state"]) is not bool
            or type(transition["carry_forward_vn_state"]) is not bool
        ):
            raise ExtendedProbeError(
                "transition_invalid", f"Uebergang {period} weicht ab"
            )
        next_scenario = loaded[index + 1]
        state_before = project_strategy_execution_state(next_scenario)
        vu = (
            apply_vu_foreign_info_carryover(execution.vu_result, next_scenario)
            if transition["carry_forward_vu_state"]
            else None
        )
        vn = (
            apply_vn_state_carryover(execution.vn_result, next_scenario)
            if transition["carry_forward_vn_state"]
            else None
        )
        if (transition["carry_forward_vu_state"] and vu is None) or (
            transition["carry_forward_vn_state"] and vn is None
        ):
            raise ExtendedProbeError(
                "carryover_missing", f"Angeforderter Carryover {period} fehlt"
            )
        for item in (vu, vn):
            if item is not None and (item.from_period, item.to_period) != (
                period,
                period + 1,
            ):
                raise ExtendedProbeError(
                    "carryover_invalid", f"Carryover {period} weicht ab"
                )
        carryover_count += int(vu is not None) + int(vn is not None)
        transition_effects.append(
            _transition_effect_payload(
                execution,
                next_scenario,
                transition=transition,
                vu_carryover=vu,
                vn_carryover=vn,
                state_before=state_before,
                state_after=project_strategy_execution_state(next_scenario),
            )
        )
        pipe.send(("period_done", period))
    for reference, original in zip(references, originals):
        if (
            get_strategy_execution_candidate(
                reference["candidate_id"], db_path=db_path
            ).record.candidate
            != original
        ):
            raise ExtendedProbeError(
                "candidate_changed", "Quellkandidat nach Lauf veraendert"
            )
    return {
        "schema_version": EXTENDED_PROBE_RESULT_VERSION,
        "status": "ok",
        "period_count": count,
        "period_chain_identity": chain["identity"],
        "period_effects": effects,
        "transition_effects": transition_effects,
        "runner_invocation_count": count,
        "carryover_invocation_count": carryover_count,
        "candidate_reverified_count": count,
        "prefix_equal": True,
        "result_persisted": False,
        "partial_result_returned": False,
        "simulation_performed": False,
        "historical_full_equality_claim": False,
    }


def _prefix(effects: list, transitions: list) -> bytes:
    if len(effects) < 5 or len(transitions) < 4:
        raise ExtendedProbeError("prefix_incomplete", "Prefix 1-5 unvollstaendig")
    return canonical_strategy_execution_prefix_bytes(
        {
            "period_effects": [
                {name: effect[name] for name in STABLE_PREFIX_PERIOD_EFFECT_FIELDS}
                for effect in effects[:5]
            ],
            "transition_effects": [
                {name: effect[name] for name in STABLE_PREFIX_TRANSITION_EFFECT_FIELDS}
                for effect in transitions[:4]
            ],
        }
    )


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("ascii")


def _peak_worker_rss(pid: int | None) -> int | None:
    if pid is None:
        return None
    if sys.platform.startswith("linux"):
        try:
            for line in Path(f"/proc/{pid}/status").read_text().splitlines():
                if line.startswith("VmHWM:"):
                    return int(line.split()[1]) * 1024
        except (OSError, ValueError):
            return None
    elif os.name == "nt":
        import ctypes
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
                (name, ctypes.c_size_t)
                for name in (
                    "PeakWorkingSetSize",
                    "WorkingSetSize",
                    "QuotaPeakPagedPoolUsage",
                    "QuotaPagedPoolUsage",
                    "QuotaPeakNonPagedPoolUsage",
                    "QuotaNonPagedPoolUsage",
                    "PagefileUsage",
                    "PeakPagefileUsage",
                )
            ]

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        psapi.GetProcessMemoryInfo.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(Counters),
            wintypes.DWORD,
        )
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        handle = kernel.OpenProcess(0x1000 | 0x0400 | 0x0010, False, pid)
        if handle:
            try:
                counters = Counters()
                counters.cb = ctypes.sizeof(counters)
                if psapi.GetProcessMemoryInfo(
                    handle, ctypes.byref(counters), counters.cb
                ):
                    return counters.PeakWorkingSetSize
            finally:
                kernel.CloseHandle(handle)
    return None
