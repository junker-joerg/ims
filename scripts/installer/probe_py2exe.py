"""Short freezer alternative probe, not a second distribution of IMS."""
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / '.tmp-pr-ap1' / 'py2exe-probe'
WORK.mkdir(parents=True, exist_ok=True)
(WORK / 'hello.py').write_text("print('py2exe-probe-ok')\n")
if len(sys.argv) > 1:
    from py2exe import freeze
    mode = int(sys.argv[1])
    freeze(console=[str(WORK / 'hello.py')], options={
        'bundle_files': mode, 'dist_dir': str(WORK / f'mode-{mode}'),
    })
else:
    results = []
    for mode in (1, 3):
        started = time.perf_counter()
        result = subprocess.run([sys.executable, __file__, str(mode)], capture_output=True, text=True)
        (WORK / f'mode-{mode}.log').write_text(result.stdout + result.stderr, encoding='utf-8')
        entry = {'bundle_files': mode, 'exit_code': result.returncode,
                 'seconds': time.perf_counter() - started}
        if result.returncode == 0:
            exe = next((WORK / f'mode-{mode}').glob('*.exe'))
            check = subprocess.run([str(exe)], capture_output=True, text=True)
            entry.update(run_exit_code=check.returncode, output=check.stdout.strip(),
                         files=len(list(exe.parent.rglob('*'))))
        results.append(entry)
    (WORK / 'evidence.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(json.dumps(results))
