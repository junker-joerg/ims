"""Render the AP3/AP4 guides as offline HTML, using their Markdown constructs."""
import argparse
from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def inline(value: str) -> str:
    value = escape(value)
    value = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1" loading="lazy">', value)
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", value)


def render(source: str) -> str:
    lines, result, index = source.splitlines(), [], 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith("#"):
            heading, text = line.split(" ", 1)
            level = len(heading)
            result.append(f"<h{level}>{inline(text)}</h{level}>")
            index += 1
        elif line.startswith("| "):
            rows = []
            while index < len(lines) and lines[index].startswith("| "):
                cells = lines[index].strip("| ").split("|")
                if not all(re.fullmatch(r"\s*:?-+:?\s*", cell) for cell in cells):
                    tag = "th" if not rows else "td"
                    rows.append("<tr>" + "".join(f"<{tag}>{inline(cell.strip())}</{tag}>" for cell in cells) + "</tr>")
                index += 1
            result.append('<div class="table-scroll" tabindex="0"><table>' + "".join(rows) + "</table></div>")
        elif re.match(r"\d+\. ", line):
            items = []
            while index < len(lines) and lines[index].strip():
                item = re.match(r"\d+\. (.*)", lines[index])
                if item:
                    items.append(item[1])
                elif lines[index].startswith("   ") and items:
                    items[-1] += " " + lines[index].strip()
                else:
                    break
                index += 1
            result.append("<ol>" + "".join("<li>" + inline(item) + "</li>" for item in items) + "</ol>")
        else:
            paragraph = []
            while index < len(lines) and lines[index].strip():
                paragraph.append(lines[index].strip())
                index += 1
            result.append("<p>" + inline(" ".join(paragraph)) + "</p>")
    return "\n".join(result)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guide", choices=("ap3", "ap4"), default="ap3")
    args = parser.parse_args()
    filename = "management_ap4" if args.guide == "ap4" else "seminar_ap3"
    source = (ROOT / f"docs/handbook/{filename}.md").read_text(encoding="utf-8")
    source = source.replace("../reports/ims_ap3_abschlussbericht.md", "https://github.com/junker-joerg/ims/blob/codex/ims-management-integration/docs/reports/ims_ap3_abschlussbericht.md")
    html = """<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IMS – Managementseminar AP3</title>
<style>body{font:18px/1.65 system-ui,sans-serif;color:#172c3c;background:#fff;max-width:1000px;margin:2rem auto;padding:0 1.25rem}h1,h2{line-height:1.25}h2{margin-top:2.5rem}a{color:#07558b}code{overflow-wrap:anywhere;font-size:.9em}img{max-width:100%;height:auto;border:1px solid #b4c1ca}li{margin:.7rem 0}.table-scroll{overflow-x:auto}table{border-collapse:collapse;font-size:.9em;min-width:650px}th,td{border:1px solid #b4c1ca;padding:.7rem;text-align:left;vertical-align:top}th{background:#eaf1f5}:focus-visible{outline:3px solid #07558b;outline-offset:3px}@media print{body{font-size:11pt;margin:0;padding:0}table{min-width:0}h2{break-after:avoid}img{max-height:230mm;object-fit:contain}}</style></head><body><main>
""" + render(source) + "\n</main></body></html>\n"
    if args.guide == "ap4":
        html = html.replace("IMS – Managementseminar AP3", "IMS – Managementlabor AP4")
    (ROOT / f"docs/handbook/{filename}.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
