"""Validate the IMS delivery plan and prepare a local Codex work order.

Standard library only. No model calls, Git writes, code execution or feature
completion inference: this validates the plan, not the product.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PLAN = ROOT / "docs/plans/ims_ai_sprint_plan.json"
LEGACY_IDS = {f"PR{n}" for n in range(179, 193)} | {
    f"PR187{letter}" for letter in "abcdefghijk"
}
STATUSES = {"planned", "in_progress", "blocked", "done"}


class PlanError(ValueError):
    """A plan or requested package cannot be used safely."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PlanError(message)


def strings(value: object, label: str, *, empty: bool = False) -> list[str]:
    require(isinstance(value, list), f"{label}: Liste erwartet.")
    require(empty or bool(value), f"{label}: darf nicht leer sein.")
    require(all(isinstance(s, str) and s.strip() for s in value),
            f"{label}: nichtleere Texte erwartet.")
    return value


def source_file(value: object, root: Path) -> None:
    require(isinstance(value, str) and bool(value), "Quelldatei fehlt.")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts and "\\" not in value,
            f"Ungültiger relativer Quellpfad: {value}")
    resolved = (root / value).resolve()
    require(resolved.is_relative_to(root.resolve()) and resolved.is_file(),
            f"Quelldatei fehlt oder liegt außerhalb des Repos: {value}")


def validate(plan: object, root: Path = ROOT) -> dict:
    require(isinstance(plan, dict), "Plan muss ein JSON-Objekt sein.")
    require(plan.get("schema_version") == 1, "Unbekannte schema_version.")
    require(plan.get("execution_mode") == "local_codex",
            "Dieser Workflow unterstützt nur die Vorbereitung für local_codex.")
    require(plan.get("pr_strategy") == "three_implementation_prs",
            "PR-Strategie geändert: Plan und Prüfer gemeinsam anpassen.")
    sha = plan.get("baseline_commit")
    require(isinstance(sha, str) and len(sha) == 40
            and all(c in "0123456789abcdef" for c in sha), "Baseline-SHA ungültig.")
    try:
        date.fromisoformat(plan.get("baseline_date", ""))
    except (TypeError, ValueError) as exc:
        raise PlanError("baseline_date: ISO-Datum erwartet.") from exc
    for field in ("plan_document", "legacy_source"):
        source_file(plan.get(field), root)
    packages = plan.get("packages")
    require(isinstance(packages, list) and bool(packages), "Pakete fehlen.")
    require(all(isinstance(p, dict) for p in packages), "Paket muss ein Objekt sein.")
    ids = [p.get("id") for p in packages]
    require(ids == ["AP1", "AP2", "AP3"], "Pakete müssen genau AP1, AP2, AP3 sein.")
    by_id = {p["id"]: p for p in packages}
    branches = []
    legacy = []
    for package in packages:
        pid = package["id"]
        require(package.get("status") in STATUSES, f"{pid}: ungültiger Status.")
        require(isinstance(package.get("title"), str) and package["title"].strip(),
                f"{pid}: Titel fehlt.")
        branch = package.get("branch")
        require(isinstance(branch, str) and branch.startswith("codex/")
                and len(branch) > len("codex/")
                and all(c.isascii() and (c.isalnum() or c in "/-_") for c in branch)
                and not branch.endswith("/") and "//" not in branch,
                f"{pid}: ungültiger Arbeitsbranch.")
        branches.append(branch)
        deps = strings(package.get("depends_on"), f"{pid}.depends_on", empty=True)
        require(len(deps) == len(set(deps)), f"{pid}: doppelte Abhängigkeit.")
        require(all(d in by_id and d != pid for d in deps),
                f"{pid}: unbekannte oder eigene Abhängigkeit.")
        legacy.extend(strings(package.get("old_plan_ids"), f"{pid}.old_plan_ids",
                              empty=True))
        for field in ("deliverables", "acceptance", "gates", "source_files"):
            strings(package.get(field), f"{pid}.{field}")
        for path in package["source_files"]:
            source_file(path, root)
        evidence = strings(package.get("completion_evidence"),
                           f"{pid}.completion_evidence", empty=True)
        if package["status"] == "done":
            require(bool(evidence), f"{pid}: done benötigt completion_evidence.")
        if package["status"] in {"in_progress", "done"}:
            require(all(by_id[d].get("status") == "done" for d in deps),
                    f"{pid}: aktive/erledigte Arbeit hat unerledigte Abhängigkeiten.")

    require(len(branches) == len(set(branches)), "Arbeitsbranches sind nicht eindeutig.")
    counts = Counter(legacy)
    duplicates = sorted(k for k, count in counts.items() if count > 1)
    require(not duplicates, f"Doppelte alte Plan-IDs: {', '.join(duplicates)}")
    missing, unknown = sorted(LEGACY_IDS - set(legacy)), sorted(set(legacy) - LEGACY_IDS)
    require(not missing and not unknown,
            f"Alte Plan-IDs unvollständig: fehlt={missing}, unbekannt={unknown}")

    def visit(pid: str, active: set[str], visited: set[str]) -> None:
        require(pid not in active, f"Zyklische Abhängigkeit bei {pid}.")
        if pid in visited:
            return
        for dep in by_id[pid]["depends_on"]:
            visit(dep, active | {pid}, visited)
        visited.add(pid)

    visited: set[str] = set()
    for pid in ids:
        visit(pid, set(), visited)
    require(sum(p["status"] == "in_progress" for p in packages) <= 1,
            "Höchstens ein Paket darf gleichzeitig in_progress sein.")
    # Changing these gates requires an explicit change to this delivery decision.
    require([p["depends_on"] for p in packages] == [[], ["AP1"], ["AP1", "AP2"]],
            "Lieferreihenfolge muss AP1 → AP2 → AP3 bleiben.")
    require(set(packages[0]["old_plan_ids"]) == {"PR191", "PR192"}
            and not packages[1]["old_plan_ids"],
            "Windows-Schritte gehören zu AP1; AP2 ist der zusätzliche UI-Auftrag.")
    return plan


def select_package(plan: dict, selection: str) -> dict | None:
    packages = plan["packages"]
    by_id = {p["id"]: p for p in packages}

    def ready(p: dict) -> bool:
        return p["status"] in {"planned", "in_progress"} and all(
            by_id[d]["status"] == "done" for d in p["depends_on"]
        )

    if selection == "auto":
        return next((p for p in packages if ready(p)), None)
    require(selection in by_id, f"Unbekanntes Paket: {selection}")
    package = by_id[selection]
    require(ready(package),
            f"{selection} ist blockiert, bereits erledigt oder hat offene Abhängigkeiten.")
    return package


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render_report(plan: dict, selected: dict | None, commit: str) -> str:
    rows = "\n".join(
        f"| {p['id']} | {p['title']} | {p['status']} | "
        f"{', '.join(p['depends_on']) or '—'} | {len(p['old_plan_ids'])} |"
        for p in plan["packages"]
    )
    next_step = (f"Arbeitsauftrag vorbereitet: {selected['id']} – {selected['title']}."
                 if selected else "Kein Paket vorbereitbar: Status/Blocker im Manifest prüfen.")
    return f"""# IMS AI sprint plan

Planstruktur geprüft: 25 alte Plan-IDs vollständig und eindeutig zugeordnet.
Ausgewerteter Commit: {commit}
Historische Baseline: {plan['baseline_commit']}

| Paket | Ergebnis | Status im geprüften Manifest | Abhängigkeiten | Alte Schritte |
| --- | --- | --- | --- | ---: |
{rows}

{next_step}

Dies ist eine Prüfung der Planstruktur, kein Nachweis fertiger Features.
Status und completion_evidence sind Angaben im Manifest; die genannten Belege
werden hier nicht fachlich geprüft. Vor Umsetzung Planannahme und erledigte
Abhängigkeiten im aktuellen main prüfen. Ein PR-Test kann Vorschau-Status zeigen.
Kein Modellaufruf, Produktcode-Commit, Merge oder Start der lokalen Codex-App.
"""


def render_order(plan: dict, package: dict, commit: str) -> str:
    return f"""# Codex-Arbeitsauftrag: {package['id']} – {package['title']}

Arbeitsauftrag für die lokale Codex-App; kein automatisch gestarteter Lauf.
Erzeugt aus Commit: {commit}
Geplanter Arbeitsbranch: {package['branch']}
Alte Anforderungs-IDs: {', '.join(package['old_plan_ids']) or 'neuer UI-Auftrag'}
Abhängigkeiten: {', '.join(package['depends_on']) or 'keine'}

## Vor dem Start

1. Lies AGENTS.md, {plan['plan_document']} und docs/plans/ims_ai_sprint_plan.json.
2. Prüfe den aktuellen main: Planungs-PR angenommen? Abhängigkeiten dort mit
   verifizierter Abnahme erledigt? Bei veraltetem Auftrag neu erzeugen.
3. Prüfe git status und vorhandene Arbeit. Keine fremden Änderungen überschreiben.
   Vorhandenen passenden Arbeitsbranch/Draft-PR fortsetzen oder neu anlegen.
4. Im aktuellen Checkout eine eigene Python-Umgebung verwenden; unter Windows
   explizit .venv/Scripts/python.exe und npm.cmd. Ein Worktree braucht eine eigene
   Umgebung inklusive editable install. Keine Umgebung eines anderen Checkouts.

## Fachliche und technische Quellen

{bullets(package['source_files'])}

## Vollständiger Lieferumfang in einem PR

{bullets(package['deliverables'])}

## Verbindliche Abnahme

{bullets(package['acceptance'])}

## Entscheidungstore

{bullets(package['gates'])}

## Arbeitsweise und Abschluss

Bearbeite das zusammenhängende Paket über mehrere Commits/Sitzungen. Nicht für
jeden Teiltest oder API-/UI-Baustein einen neuen PR erstellen. Tests passend
zum Risiko ausführen; vor Abschluss den vorhandenen Windows-Release-Gate und
alle Paketabnahmen dokumentieren. Der Plancheck ersetzt keinen Produkttest.

Bei fehlender fachlicher Grundlage den konkreten Blocker dokumentieren.
Keine Annahme erfinden, Anforderung streichen oder blockierte Arbeit als fertig
melden. Vor Sitzungspause Fortschritt, Commit, Tests, offene Punkte und nächsten
Schritt im Draft-PR festhalten; im selben PR fortsetzen.

Status und completion_evidence mit echten Nachweisen im Paket-PR aktualisieren.
done erst nach bestandenen Abnahmen; für Nachfolgepakete zählt der in main
übernommene Status. Keine automatische Zusammenführung oder Veröffentlichung.
Bericht am Ende: Ergebnis, Commit/PR, Tests, Blocker und nächster Schritt.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--package", default="auto", choices=["auto", "AP1", "AP2", "AP3"])
    parser.add_argument("--out", type=Path, default=ROOT / ".tmp-pr-sprint")
    parser.add_argument("--commit", help="Commit of the checked-out manifest; defaults to git HEAD.")
    args = parser.parse_args(argv)
    try:
        # Remove a previous work order first: invalid/blocked runs must not leave
        # a stale actionable-looking artifact behind.
        args.out.mkdir(parents=True, exist_ok=True)
        for name in ("codex-work-order.md", "plan-report.md"):
            (args.out / name).unlink(missing_ok=True)
        plan = validate(json.loads(args.plan.read_text(encoding="utf-8")), ROOT)
        selected = select_package(plan, args.package)
        commit = args.commit
        if not commit:
            result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                    text=True, capture_output=True, check=False)
            require(result.returncode == 0, "Git-Commit fehlt; --commit explizit angeben.")
            commit = result.stdout.strip()
        require(len(commit) == 40 and all(c in "0123456789abcdef" for c in commit),
                "--commit muss ein vollständiger Git-SHA sein.")
        (args.out / "plan-report.md").write_text(
            render_report(plan, selected, commit), encoding="utf-8")
        if selected:
            (args.out / "codex-work-order.md").write_text(
                render_order(plan, selected, commit), encoding="utf-8")
        print(f"PLAN OK: 25 Anforderungen; Auftrag={selected['id'] if selected else 'keiner'}")
        print(f"Ausgabe: {args.out}")
        return 0
    except (PlanError, OSError, ValueError) as exc:
        print(f"PLAN FEHLER: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
