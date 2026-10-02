"""Follow-up previews and explicitly authorized orders; never starts a package."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

MARKET_SCHEMA = "ims.explainable-market-plan.v1"
BOARD_SCHEMA = "ims.board-strategy-plan.v1"
PLAN_STATES = {"proposed", "accepted", "deferred"}
WORK_STATES = {"proposed", "deferred", "planned", "in_progress", "blocked", "done"}
DISPOSITIONS = {"retained", "moved", "amendment", "unchanged", "deferred"}
MARKET_BENEFITS = {
    "AP4": "Einsteiger und Wiedereinsteiger können Fall, nächsten Schritt und eine Ergebnisänderung bis Eingabe/Regel/Buchung erklären.",
    "AP5": "Kunden-/Risikowechsel und Strategiefamilien mit konsistenten Einzel-VU- und Marktsummen vergleichen.",
    "AP6": "Einen begrenzten deutschen Modellmarkt mit nachvollziehbaren Gruppen und sichtbaren Datenlücken laden.",
    "AP7": "Vier deklarierte Schockverläufe und Gegenmaßnahmen mit erklärter Markt-/ICT-Wirkung untersuchen.",
    "AP8": "Marktprozesse, Gruppen und Strategiefamilien unmittelbar in IMS bis zur Buchung interpretieren.",
    "AP9": "Den vorhandenen Seminarumfang mit tatsächlichen Anwender-, Dokumentations- und Installer-Nachweisen abnehmen.",
}
EXPECTED_REQUIREMENTS = (
    {f"AP{ap}-R{i:02}" for ap, count in [(10,7),(11,7),(12,8),(13,8),(14,8)] for i in range(1,count+1)}
    | {"E05-01","E05-02","E07-01","E08-01","E09-01","E04-01","E06-01"}
    | {f"REF-{i:02}" for i in range(1,13)} | {f"RES-{i:02}" for i in range(1,6)}
    | {f"DEF-{i:02}" for i in range(1,4)}
)


class FollowupError(ValueError):
    """Invalid plan or absent authorization/provenance."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FollowupError(message)


def texts(value: object, label: str, *, empty: bool = False) -> list[str]:
    require(isinstance(value, list) and (empty or bool(value)), f"{label}: Liste fehlt.")
    require(all(isinstance(v, str) and v.strip() for v in value), f"{label}: Texte fehlen.")
    return value


def local_file(value: object, root: Path) -> Path:
    require(isinstance(value, str) and bool(value), "Quellpfad fehlt.")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts and "\\" not in value, f"Ungültiger Quellpfad: {value}")
    resolved = (root / value).resolve()
    require(resolved.is_relative_to(root.resolve()) and resolved.is_file(), f"Quelle fehlt: {value}")
    return resolved


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON-Objekt fehlt: {path}")
    return value


def normalize(raw: dict, plan: dict, path: str, legacy: bool = False) -> dict:
    pid = raw["id"]
    return {**raw, "branch": raw.get("branch", raw.get("branch_proposal")),
        "plan_status": "accepted" if legacy else raw.get("plan_status", plan["status"]),
        "decision_benefit": raw.get("decision_benefit", MARKET_BENEFITS.get(pid, "Angenommene Lieferung: " + raw["title"])),
        "source_files": raw.get("source_files", [path, plan["plan_document"]]),
        "source_ids": raw.get("source_ids", []),
        "requirement_ids": raw.get("requirement_ids", [r["id"] for r in plan.get("requirements", []) if pid in r.get("packages", [])]),
        "technically_complete": raw.get("technically_complete", raw["status"] == "done"),
        "_manifest": path, "_raw": raw, "_legacy": legacy}


def load_portfolio(plan: dict, plan_path: Path, root: Path, legacy_validator) -> dict:
    require(plan.get("schema_version") in {MARKET_SCHEMA, BOARD_SCHEMA}, "Unbekanntes Folgeschema.")
    require(plan.get("status") in PLAN_STATES, "Planstatus ungültig.")
    relative = str(plan_path.resolve().relative_to(root.resolve())).replace("\\", "/")
    local_file(plan.get("plan_document"), root)
    if plan["schema_version"] == BOARD_SCHEMA:
        market_path = plan["market_plan"]
        market = read_json(local_file(market_path, root))
        require(market.get("schema_version") == MARKET_SCHEMA, "Angenommene Marktbaseline fehlt.")
        legacy_path = plan["legacy_plan"]
        require(legacy_path == market["legacy_acceptance_manifest"], "Widersprüchliche Altbaseline.")
    else:
        market, market_path = plan, relative
        legacy_path = market["legacy_acceptance_manifest"]
    legacy = legacy_validator(read_json(local_file(legacy_path, root)), root)
    require(market.get("status") in PLAN_STATES, "Marktplanstatus ungültig.")
    local_file(market["plan_document"], root)
    require([p.get("id") for p in market.get("packages", [])] == [f"AP{i}" for i in range(4,10)], "Markt-IDs müssen AP4–AP9 sein.")
    packages = [normalize(p, legacy, legacy_path, True) for p in legacy["packages"]]
    packages += [normalize(p, market, market_path) for p in market["packages"]]
    if plan["schema_version"] == BOARD_SCHEMA:
        require([p.get("id") for p in plan.get("packages", [])] == [f"AP{i}" for i in range(10,15)], "Board-IDs müssen AP10–AP14 sein.")
        packages += [normalize(p, plan, relative) for p in plan["packages"]]
        validate_board(plan, root)
    ids = [p["id"] for p in packages]
    require(len(set(ids)) == len(ids), "Doppelte Paket-IDs.")
    by_id = {p["id"]: p for p in packages}
    branches = []
    for p in packages:
        pid = p["id"]
        require(p["status"] in WORK_STATES and p["plan_status"] in PLAN_STATES, f"{pid}: Status ungültig.")
        require(isinstance(p.get("title"), str) and p["title"].strip(), f"{pid}: Titel fehlt.")
        require(isinstance(p["branch"], str) and re.fullmatch(r"codex/[A-Za-z0-9_/-]+", p["branch"]) is not None, f"{pid}: Branch ungültig.")
        branches.append(p["branch"])
        deps = texts(p.get("depends_on"), f"{pid}.depends_on", empty=True)
        require(len(set(deps)) == len(deps) and all(d in by_id and d != pid for d in deps), f"{pid}: doppelte/unbekannte/eigene Abhängigkeit.")
        for field in ("deliverables", "acceptance", "gates", "source_files"):
            texts(p.get(field), f"{pid}.{field}")
        for path in p["source_files"]:
            local_file(path, root)
        evidence = texts(p.get("completion_evidence"), f"{pid}.completion_evidence", empty=True)
        require(type(p["technically_complete"]) is bool, f"{pid}: technischer Status muss bool sein.")
        require((p["status"] == "done") == p["technically_complete"], f"{pid}: done und technische Fertigstellung widersprechen sich.")
        if p["status"] == "done":
            require(bool(evidence), f"{pid}: done ohne Abschlussbelege.")
            require(p["plan_status"] == "accepted", f"{pid}: vorgeschlagenes Paket kann nicht done sein.")
        if p.get("merged_to_main"):
            require(p["status"] == "done" and bool(p.get("merge_evidence")), f"{pid}: Merge ohne done/Merge-Belege.")
        if p["plan_status"] != "accepted" or p["status"] in {"proposed", "deferred"}:
            require(not p.get("implementation_authorized", False) and not evidence, f"{pid}: Vorschlag/Zurückstellung darf keine Freigabe/Abschlussbelege tragen.")
    require(len(set(branches)) == len(branches), "Doppelte Branches.")
    visited = set()
    def visit(pid: str, stack: set[str]):
        require(pid not in stack, f"Zyklische Abhängigkeit: {pid}")
        if pid in visited:
            return
        for dep in by_id[pid]["depends_on"]:
            visit(dep, stack | {pid})
        visited.add(pid)
    for pid in ids:
        visit(pid, set())
    for p in packages:
        if p["status"] in {"done", "in_progress"}:
            require(all(by_id[d]["status"] == "done" for d in p["depends_on"]), f"{p['id']}: aktive/erledigte Arbeit mit offenen Abhängigkeiten.")
    return dict(plan=plan, path=relative, packages=packages, by_id=by_id)


def validate_board(plan: dict, root: Path) -> None:
    for field in ("reference_case", "research_manifest", "evidence_report"):
        local_file(plan.get(field), root)
    research = read_json(root / plan["research_manifest"])
    require(research.get("schema_version") == "ims.competition-evidence.v1" and len(research.get("dimensions", [])) == 9,
            "Neun versionierte Vergleichsdimensionen erforderlich.")
    require({r["provider"] for r in research["rows"]} == {
        "BCG", "McKinsey", "Bain", "Swiss Re / Eurapco", "Aon ReMetrica / Tyche", "Abgalis", "ISLE / Versicherungsmarktforschung"
    } and len(research["rows"]) == 7, "Wettbewerbsabdeckung unvollständig/doppelt.")
    source_ids = [s["id"] for s in research["sources"]]
    require(len(source_ids) == len(set(source_ids)), "Doppelte Quellen-IDs.")
    for s in research["sources"]:
        require(s.get("url", "").startswith("https://") and s.get("accessed") and s.get("locator") and s.get("evidence_type"), f"{s['id']}: Quellenmetadaten fehlen.")
    for row in research["rows"]:
        require([d["dimension"] for d in row["dimensions"]] == research["dimensions"] and len(row["layers"]) == 5, "Evidenzmatrix unvollständig.")
        require({c["category"] for c in row["layers"]} == {"method", "software_description", "vendor_application", "inspectable_technical", "unconfirmed_vendor_claim"},
                "Fünf verschiedene Evidenzebenen erforderlich.")
        for claim in row["dimensions"] + row["layers"]:
            require(bool(claim["source_ids"]) and all(s in source_ids for s in claim["source_ids"]), "Aussage ohne gültige Quelle.")
    require(all(gap in {g["id"] for g in research.get("gaps", [])} for gap in plan.get("missing_sources", [])),
            "Unbekannte Quellenlücke.")
    reqs = plan.get("requirements", [])
    ids = [r.get("id") for r in reqs]
    require(len(ids) == len(set(ids)), "Doppelte Anforderungs-IDs.")
    require(set(ids) == EXPECTED_REQUIREMENTS, "Anforderungsabdeckung unvollständig/unbekannt.")
    for r in reqs:
        require(r.get("disposition") in DISPOSITIONS, f"{r['id']}: Disposition ungültig.")
        for field in ("description", "original_assignment", "reason", "acceptance_impact"):
            require(isinstance(r.get(field), str) and bool(r[field].strip()), f"{r['id']}: {field} fehlt.")
        targets = texts(r.get("packages"), r["id"], empty=r["disposition"] == "deferred")
        require(len(targets) == len(set(targets)) and all(t in {f"AP{i}" for i in range(4,15)} for t in targets), f"{r['id']}: Zielzuordnung ungültig.")
        require(bool(targets) != (r["disposition"] == "deferred"), f"{r['id']}: zurückgestellte Zuordnung widerspricht sich.")
    for p in plan["packages"]:
        expected = {r["id"] for r in reqs if p["id"] in r["packages"]}
        assigned = texts(p.get("requirement_ids"), p["id"])
        require(len(assigned) == len(set(assigned)) and set(assigned) == expected, f"{p['id']}: Anforderungszuordnung unvollständig.")
        require(bool(p.get("decision_benefit")) and bool(p.get("goal")), f"{p['id']}: Entscheidungsnutzen/Ziel fehlt.")
        texts(p.get("milestones"), p["id"] + ".milestones")
        require(all(s in source_ids for s in texts(p.get("source_ids"), p["id"])), f"{p['id']}: unbekannte Quellen-ID.")
    backlog = plan.get("backlog", [])
    require({b.get("id") for b in backlog} == {r["id"] for r in reqs if r["disposition"] == "deferred"}, "Zurückgestellte Anforderungen fehlen im Backlog.")
    require(all(b.get("status") == "deferred" and b.get("reopen_when") for b in backlog), "Backlogstatus/Entscheidungstor fehlt.")
    for a in plan.get("candidate_amendments", []):
        require(a.get("status") in PLAN_STATES and a.get("package") in {"AP5","AP7","AP8"}, "Ergänzungsstatus ungültig.")
        require(all(r in ids for r in texts(a.get("requirement_ids"), "Ergänzung")), "Ergänzungsanforderung fehlt.")
    require(set(plan.get("recommended_order", [])) == {f"AP{i}" for i in range(10,15)} and len(plan["recommended_order"]) == 5, "Empfohlene Reihenfolge unvollständig.")
    if plan["status"] == "accepted":
        require(isinstance(plan.get("approval"), dict) and bool(plan["approval"].get("user_request")), "Angenommener Boardplan ohne Planannahmebeleg.")


def read_at_ref(root: Path, ref: str, path: str) -> dict:
    result = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=root, capture_output=True, text=True, encoding="utf-8", check=False)
    require(result.returncode == 0, f"Plan/Beleg fehlt in {ref}: {path}")
    return json.loads(result.stdout)


def resolve_ref(root: Path, ref: str) -> str:
    require(re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_./-]*", ref) is not None, "Ungültige main-Referenz.")
    result = subprocess.run(["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], cwd=root, capture_output=True, text=True, check=False)
    require(result.returncode == 0, f"main-Referenz fehlt: {ref}; origin vorher aktualisieren.")
    return result.stdout.strip()


def main_done(p: dict, root: Path, main_sha: str) -> bool:
    try:
        recorded = read_at_ref(root, main_sha, p["_manifest"])
        item = next(v for v in recorded["packages"] if v["id"] == p["id"])
        return (item["status"] == "done" and bool(item.get("completion_evidence"))
                and (p["_legacy"] or recorded["status"] == "accepted")
                and (recorded.get("schema_version") != BOARD_SCHEMA or item.get("merged_to_main") is True))
    except (FollowupError, KeyError, StopIteration, ValueError):
        return False


def dependency_ids(portfolio: dict, pid: str) -> set[str]:
    result = set()
    def visit(key):
        for dep in portfolio["by_id"][key]["depends_on"]:
            if dep not in result:
                result.add(dep)
                visit(dep)
    visit(pid)
    return result


def authorize(portfolio: dict, p: dict, root: Path, main_sha: str, receipt_path: Path | None) -> dict:
    require(p["plan_status"] == "accepted" and p["status"] in {"planned","in_progress"}, f"{p['id']}: Vorschlag/zurückgestellt/blockiert/erledigt; kein freigegebener Auftrag.")
    main_plan = read_at_ref(root, main_sha, p["_manifest"])
    require(main_plan.get("status") == "accepted", "Planannahme fehlt in main.")
    recorded = next((v for v in main_plan["packages"] if v["id"] == p["id"]), None)
    require(recorded == p["_raw"], "Arbeitsumfang weicht von angenommenem main ab; zuerst Planung übernehmen.")
    require(receipt_path is not None, "Ausdrückliche Umsetzungsfreigabe fehlt: --authorization-file.")
    receipt = read_json(receipt_path)
    require(receipt.get("schema_version") == "ims.execution-authorization.v1" and receipt.get("package") == p["id"]
        and receipt.get("scope") == "implementation" and receipt.get("plan_commit") == main_sha,
        "Freigabebeleg: Schema/Paket/Umfang/aktueller main-Commit falsch.")
    require(bool(receipt.get("authorized_by")) and bool(receipt.get("user_request")), "Freigabebeleg ohne menschlichen Auftrag.")
    try:
        date = datetime.fromisoformat(receipt.get("authorized_at", ""))
        require(date.tzinfo is not None, "Freigabezeit braucht Zeitzone.")
    except (TypeError, ValueError) as exc:
        raise FollowupError("Freigabezeit ungültig.") from exc
    missing = [d for d in sorted(dependency_ids(portfolio,p["id"])) if not main_done(portfolio["by_id"][d],root,main_sha)]
    require(not missing, f"Abhängigkeiten ohne erledigte main-Belege: {', '.join(missing)}")
    # A receipt documents the actual human instruction. Its JSON format cannot
    # authenticate a human; an operator must never fabricate one to clear gates.
    return receipt


def select(portfolio: dict, selection: str, mode: str, root: Path, main_sha: str, receipt: Path | None) -> dict | None:
    candidates = [p for p in portfolio["packages"] if not p["_legacy"] and p["status"] not in {"done","deferred"} and p["plan_status"] != "deferred"]
    if selection == "auto":
        if mode == "authorized":
            require(receipt is not None, "auto benötigt eine ausdrückliche paketbezogene Umsetzungsfreigabe.")
            selection = read_json(receipt).get("package", "")
        else:
            return next((p for p in candidates if p["plan_status"] == "accepted"), next(iter(candidates),None))
    require(selection in portfolio["by_id"], f"Unbekanntes Paket: {selection}")
    p = portfolio["by_id"][selection]
    require(not p["_legacy"], "AP1–AP3 mit dem bisherigen Manifest aufrufen.")
    require(p["status"] not in {"done","deferred"} and p["plan_status"] != "deferred", f"{selection}: erledigt/zurückgestellt; kein Auftrag.")
    if mode == "authorized":
        authorize(portfolio,p,root,main_sha,receipt)
    return p


def bullets(values: list[str]) -> str:
    return "\n".join(f"- {v}" for v in values)


def render_order(portfolio: dict, p: dict, mode: str, commit: str, main_sha: str, root: Path, receipt: Path | None) -> str:
    label = "VORSCHAU – NICHT ZUR UMSETZUNG FREIGEGEBEN" if mode == "preview" else "FREIGEGEBENER ARBEITSAUFTRAG – kein automatischer Start"
    unmet = [d for d in sorted(dependency_ids(portfolio,p["id"])) if not main_done(portfolio["by_id"][d],root,main_sha)]
    amendments = [a for a in portfolio["plan"].get("candidate_amendments",[]) if a["package"] == p["id"]]
    proposal_note = "\n".join(f"- {a['status']}: {', '.join(a['requirement_ids'])}; nicht automatisch angenommener Lieferumfang." for a in amendments) or "Keine Erweiterung des angenommenen Umfangs durch diesen Auftrag."
    authority = "Keine Umsetzungsfreigabe in dieser Vorschau."
    if mode == "authorized":
        record = read_json(receipt)
        authority = f"Beleg: {record['authorized_by']}, {record['authorized_at']}; Umfang {record['scope']}.\n\nDokumentierter Auftrag: {record['user_request']}"
    return f"""# {label}: {p['id']} – {p['title']}

Geprüfter Checkout: {commit}; geprüfte main-Referenz: {main_sha}.
Planstatus: {p['plan_status']}; technischer Status: {p['status']}.
Umsetzungsfreigabe: {str(receipt) if mode == 'authorized' else 'keine (Vorschau)'}.
Branchvorschlag: {p['branch']}; Paketmanifest: {p['_manifest']}.
Abhängigkeiten: {', '.join(p['depends_on'])}; offene main-Belege: {', '.join(unmet) or 'keine'}.

{authority}

## Entscheidungsnutzen

{p['decision_benefit']}

## Umfang in einem Paket-PR

{bullets(p['deliverables'])}

## Abnahmen

{bullets(p['acceptance'])}

## Voraussetzungen / fachliche Entscheidungstore

{bullets(p['gates'])}

## Quellen / Anforderungen / Meilensteine

{bullets(p['source_files'])}

Quellen-IDs: {', '.join(p['source_ids']) or 'angenommener Folgeplan'}.
Anforderungs-IDs: {', '.join(p['requirement_ids'])}.

{bullets(p.get('milestones', ['Meilensteine im angenommenen Paket-PR festhalten.']))}

## Separat vorgeschlagene Ergänzungen

{proposal_note}

## Fortsetzen und abschließen

Vor Arbeit origin aktualisieren, AGENTS.md, Handoff und Paketquellen lesen.
Bei veraltetem main oder neuer Planung Auftrag erneut erzeugen. Vorhandenen
passenden Branch/Draft-PR fortsetzen; keine fremden Änderungen überschreiben.
Eigene editable Umgebung je Checkout; Windows: .venv/Scripts/python.exe und npm.cmd.
Ein Paket mit Implementierung/API/UI/Tests/Anleitung/Installer über mehrere
Meilensteine und Sitzungen. Quellenmapping, Annahmen und Modellgrenzen erhalten.
Vor Pause Commit, Fortschritt, Tests, Blocker und nächsten Schritt im selben PR
dokumentieren. Technisch done erst nach echten Abnahmen und Abschlussbelegen.
Übernahme in main mit gesondertem Merge-Beleg; Folgepakete benötigen diese
main-Belege. Planannahme, Umsetzungsfreigabe, technische Fertigstellung und Merge
bleiben getrennt. Vorschau startet keine Umsetzung; Merge/Release nur nach
gesondertem tatsächlichem Auftrag. Freigabedateien niemals zum Umgehen eines
fehlenden menschlichen Auftrags erfinden.
"""


def run(plan: dict, args, root: Path, legacy_validator, commit: str) -> int:
    require(args.main_ref == "origin/main", "Freigabe-/Mergeprüfung ausschließlich gegen origin/main; vorher aktualisieren.")
    require(resolve_ref(root, "HEAD") == commit, "Folgeplan-Commit muss dem tatsächlichen Checkout entsprechen.")
    portfolio = load_portfolio(plan,args.plan,root,legacy_validator)
    mode = args.mode or "preview"
    main_sha = resolve_ref(root,args.main_ref)
    selected = select(portfolio,args.package,mode,root,main_sha,args.authorization_file)
    lines = ["# IMS-Folgeplanprüfung", "", f"Modus: {mode}; kein automatisch gestarteter Lauf.", f"Checkout: {commit}; main: {main_sha}.", "", "| Paket | Plan | Technik | Erledigt in geprüfter main-Referenz | Abhängigkeiten |", "| --- | --- | --- | --- | --- |"]
    for p in portfolio["packages"]:
        lines.append(f"| {p['id']} | {p['plan_status']} | {p['status']} | {main_done(p,root,main_sha)} | {', '.join(p['depends_on'])} |")
    lines += ["", f"Auftrag: {selected['id'] if selected else 'keiner'}. Vorschläge sind keine Umsetzungsfreigabe.", "Zurückgestellte Anforderungen: " + ", ".join(b['id'] for b in plan.get('backlog',[])), "", "Strukturprüfung ersetzt keine fachliche Validierung oder Benutzerabnahme."]
    (args.out / "plan-report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    if selected:
        (args.out / "codex-work-order.md").write_text(render_order(portfolio,selected,mode,commit,main_sha,root,args.authorization_file),encoding="utf-8")
    print(f"PLAN OK: {len(portfolio['packages'])} Pakete; Modus={mode}; Auftrag={selected['id'] if selected else 'keiner'}")
    return 0
