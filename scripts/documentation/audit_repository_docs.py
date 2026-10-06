"""Inventory repo documentation, preserving historical approvals and evidence."""
import argparse
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[2]
PATTERN=re.compile(r'!?\[[^\]\n]*\]\(([^)\n]+)\)|(?:href|src)="([^"]+)"')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='docs/reports/ims_ap8_documentation_inventory.json');args=parser.parse_args()
    tracked=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','docs','README.md','AGENTS.md'],text=True,cwd=ROOT).splitlines()
    entries=[];missing=[]
    for name in sorted(set(tracked)):
        p=ROOT/name
        if not p.is_file() or p.suffix.lower() not in ('.md','.html','.json','.txt'):continue
        if name==args.out:continue
        kind='current_handbook' if name.startswith('docs/handbook/') else 'historical_report' if name.startswith('docs/reports/') else 'versioned_plan' if name.startswith('docs/plans/') else 'research_source' if name.startswith('docs/research/') else 'component_migration' if name.startswith('docs/migration/') else 'entry_or_other'
        content=p.read_text(encoding='utf-8-sig',errors='replace');links=[]
        if p.suffix in ('.md','.html'):
            for match in PATTERN.finditer(content):
                target=match[1] or match[2]
                if target.startswith(('http:','https:','mailto:','#','data:','app:','codex:','/api/')):continue
                target=unquote(urlsplit(target.strip('<>')).path)
                if not target or any(c in target for c in ('{','}','*')):continue
                staged_help=name=='docs/handbook/installer_windows.html'
                resolved=(ROOT/target if staged_help else p.parent/target).resolve()
                if staged_help and target=='Bedienungsanleitung.pdf':resolved=ROOT/'output/pdf/IMS-Bedienungsanleitung.pdf'
                exists=resolved.exists()
                links.append({'target':target,'exists_in_checkout':exists,'resolution':'installer help.html resource root' if staged_help else 'document-relative'})
                if not exists:missing.append({'file':name,'target':target,'kind':kind})
        entries.append({'path':name,'classification':kind,'links':links,'review':'navigation_and_current_scope_manually_checked' if name.startswith('docs/handbook/') or name in ('README.md','AGENTS.md','docs/plans/ims_delivery_handoff.md','docs/migration/README.md') else 'inventoried; dated component/plan/report evidence retained'})
    result={'schema':'ims.repository-doc-audit.v1','date':'2026-10-06','method':'Tracked/unignored documentation inventory; relative local link existence scan; current handbook navigation and scope review. Historical reports/plans are not rewritten or represented as newly verified.', 'files':entries,'missing_local_links':missing,'counts':{'files':len(entries),'links':sum(len(e['links']) for e in entries),'missing':len(missing),'missing_current_handbook':sum(e['kind']=='current_handbook' for e in missing)}}
    (ROOT/args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result['counts']))
    for entry in missing:
        if entry['kind']=='current_handbook':print(json.dumps(entry,ensure_ascii=False))

if __name__=='__main__':main()
