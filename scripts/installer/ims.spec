# Explicit data and dynamic imports, no historical raw archives or developer tools.
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

root = Path(SPECPATH).parents[1]
staged = root / 'build' / 'installer-resources'
datas = [(str(staged), 'resources')] + collect_data_files('ims', includes=['strategies/profiles/*.json'])
for package in ('fastapi', 'starlette', 'uvicorn', 'pydantic', 'openpyxl', 'anyio'):
    datas += copy_metadata(package)

a = Analysis([str(root / 'scripts/installer/entry.py')],
    pathex=[str(root / 'python_port')], datas=datas,
    hiddenimports=['uvicorn.loops.asyncio', 'uvicorn.protocols.http.h11_impl',
                   'uvicorn.lifespan.on', 'tkinter', 'tkinter.filedialog',
                   'tkinter.messagebox', 'tkinter.simpledialog', 'tkinter.ttk'],
    excludes=['pytest', 'httpx', 'py2exe', 'setuptools', 'pip'])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='IMS-Workbench',
    console=False, debug=False, strip=False, upx=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='IMS-Workbench')
