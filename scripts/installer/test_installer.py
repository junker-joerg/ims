"""Exercise the actual installer on Windows; does not claim a clean-VM test."""
from __future__ import annotations

import argparse
import csv
import hashlib
from io import BytesIO, StringIO
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import time
from urllib.error import URLError
from urllib.request import build_opener, ProxyHandler, Request
import uuid
import winreg
import zipfile

from openpyxl import load_workbook

from ims.release import VERSION, windows_file_version


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--installer', type=Path, required=True)
    parser.add_argument('--previous-installer', type=Path, required=True,
                        help='Preceding installer; synthetic same-bundle predecessor by default')
    parser.add_argument('--previous-version',
                        help='Actual preceding application version; omit for synthetic same-bundle tests')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--browser-checks', action='store_true',
                        help='Run AP2 real-browser acceptance against the installed executable')
    args = parser.parse_args()
    if args.previous_version:
        preceding = tuple(map(int, windows_file_version(args.previous_version).split('.')))
        current = tuple(map(int, windows_file_version(VERSION).split('.')))
        if preceding >= current:
            parser.error('Actual preceding application version must be lower than the current release')
    installer, previous = args.installer.resolve(), args.previous_installer.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    work = out / ('Installer Prüfung Ä ' + uuid.uuid4().hex[:8])
    work.mkdir()
    app = work / 'Programm mit Leerzeichen Ö'
    fake_local = work / 'Benutzerablage Ü'
    data = fake_local / 'IMS/Workbench'
    exe = app / 'IMS-Workbench.exe'
    group_name = 'IMS Workbench'
    group = Path(os.environ['APPDATA']) / 'Microsoft/Windows/Start Menu/Programs' / group_name
    environment = {key: value for key, value in os.environ.items()
                   if not key.startswith(('PYTHON', 'IMS_'))}
    environment['PATH'] = os.path.join(os.environ['SystemRoot'], 'System32')
    environment['LOCALAPPDATA'] = str(fake_local)
    environment['HTTP_PROXY'] = environment['HTTPS_PROXY'] = 'http://127.0.0.1:1'
    env = environment
    process = None
    evidence = []
    success = False
    failure = None
    total = time.perf_counter()
    # Refuse to overwrite any existing installation in this user's registry.
    key = r'Software\Microsoft\Windows\CurrentVersion\Uninstall\{097487D9-FA11-47A1-B2C6-6906858C2E78}_is1'
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key):
            raise RuntimeError('IMS already installed in this user account; use a separate test account.')
    except FileNotFoundError:
        pass
    if group.exists() and list(group.glob('*.lnk')):
        raise RuntimeError('Existing IMS shortcuts found; use a separate test account.')

    def run(command: list[str], timeout: int = 90, expect: int = 0):
        started = time.perf_counter()
        result = subprocess.run(command, cwd=work, env=env, timeout=timeout,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        assert result.returncode == expect, (command[0], result.returncode, expect)
        return time.perf_counter() - started

    def install(path: Path, label: str):
        seconds = run([str(path), '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART',
                       '/CURRENTUSER', f'/DIR={app}', f'/GROUP={group_name}',
                       f'/LOG={work / (label + ".log")}'])
        assert exe.is_file()
        assert (group / 'IMS Workbench.lnk').is_file()
        evidence.append({'test': label, 'result': 'passed', 'seconds': seconds})

    with socket.socket() as port_probe:
        port_probe.bind(('127.0.0.1', 0))
        port = port_probe.getsockname()[1]
    base = f'http://127.0.0.1:{port}'

    def request(path: str, payload=None, headers=None):
        body = json.dumps(payload).encode() if payload is not None else None
        req = Request(base + path, data=body,
                      headers={'Content-Type': 'application/json', **(headers or {})})
        return build_opener(ProxyHandler({})).open(req, timeout=25)

    def get_json(path: str, payload=None):
        with request(path, payload) as response:
            return json.load(response)

    def start(label: str, expected_version: str = VERSION):
        nonlocal process
        began = time.perf_counter()
        process = subprocess.Popen([str(exe), '--headless', '--no-browser', '--port', str(port)],
                                   cwd=work, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
        deadline = time.monotonic() + 40
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f'Frozen executable exited: {process.returncode}; see {data / "logs"}')
            try:
                health = get_json('/api/health')
                if health.get('frontend_available') and (data / 'instance.json').is_file():
                    break
            except (OSError, ValueError, URLError):
                time.sleep(0.1)
        else:
            raise RuntimeError('Frozen health-check timeout')
        with request('/') as response:
            assert b'<html' in response.read().lower()
        assert health['version'] == expected_version
        assert get_json('/api/version')['version'] == expected_version
        assert get_json('/api/model/health-sector-contract')['schema_version']
        evidence.append({'test': label, 'result': 'passed', 'seconds': time.perf_counter() - began})

    def stop():
        run([str(exe), '--stop', '--headless'])
        if process is not None:
            assert process.wait(timeout=40) == 0
        assert not (data / 'instance.json').exists()

    try:
        install(previous, 'install_actual_previous_release' if args.previous_version else 'install_synthetic_previous_version')
        start('frozen_start_path_with_spaces_umlauts', args.previous_version or VERSION)
        state = json.loads((data / 'instance.json').read_text())
        elapsed = run([str(exe), '--headless', '--no-browser'])
        assert json.loads((data / 'instance.json').read_text())['pid'] == state['pid']
        evidence.append({'test': 'second_start_same_process', 'result': 'passed', 'seconds': elapsed})
        run([str(exe), '--headless', '--diagnostics', str(work / 'live-diagnostics.zip')])
        assert (work / 'live-diagnostics.zip').is_file()
        # Embedded existing model case, explicitly released for storage, unchanged digests.
        case = json.loads((app / '_internal/resources/tests/fixtures/health_period_chain_v1.json').read_text())
        route = '/api/accounting/health-period-chain'
        began = time.perf_counter()
        preview = get_json(route + '/preview', case)
        assert preview['report']['calculated_period_count'] == 2
        stored = get_json(route + '/start', {
            'schema_version': 'ims.health-result-start.v1', 'health_chain_input': case,
            'expected_input_digest': preview['input_digest'],
            'expected_result_digest': preview['result_digest'],
            'idempotency_key': 'ap1-installer-case', 'explicit_storage_release': True,
        })
        result_path = route + '/result/' + stored['result_id']
        with request(result_path) as response:
            etag = response.headers['etag']
        for extension in ('json', 'csv', 'xlsx'):
            with request(result_path + '.' + extension, headers={'If-Match': etag}) as response:
                content = response.read()
            (work / ('Modellfall.' + extension)).write_bytes(content)
            if extension == 'json':
                assert json.loads(content)['result_digest'] == preview['result_digest']
            elif extension == 'csv':
                assert len(list(csv.DictReader(StringIO(content.decode('utf-8'))))) == 2
            else:
                book = load_workbook(BytesIO(content), read_only=True)
                assert len(list(book['Perioden'].values)) == 3
                book.close()
        evidence.append({'test': 'existing_health_case_and_json_csv_xlsx_exports', 'result': 'passed',
                         'seconds': time.perf_counter() - began, 'input_digest': preview['input_digest'],
                         'result_digest': preview['result_digest']})
        # Update while running: setup must shut down old instance before replacing files.
        install(installer, 'update_while_running')
        assert process.wait(timeout=40) == 0
        start('start_after_update')
        assert get_json(result_path)['result_digest'] == stored['result_digest']
        if args.browser_checks:
            began = time.perf_counter()
            repo = Path(__file__).resolve().parents[2]
            node = shutil.which('node')
            if not node:
                raise RuntimeError('Browser harness requires Node in the build/test environment')
            browser_env = {**os.environ, 'IMS_BASE_URL': base + '/'}
            browser_env.pop('IMS_CAPTURE', None)
            subprocess.run([node, str(repo / 'frontend/node_modules/@playwright/test/cli.js'),
                            'test', '--config', str(repo / 'frontend/playwright.config.ts')],
                           cwd=repo / 'frontend', env=browser_env, check=True, timeout=3600,
                           creationflags=subprocess.CREATE_NO_WINDOW)
            evidence.append({'test': 'AP2_real_browser_against_installed_current_frontend',
                             'result': 'passed', 'seconds': time.perf_counter() - began})
        stop()
        before = hashlib.sha256((data / 'metadata.sqlite').read_bytes()).hexdigest()
        with socket.socket() as occupied:
            occupied.bind(('127.0.0.1', port))
            occupied.listen()
            elapsed = run([str(exe), '--headless', '--no-browser', '--port', str(port)], expect=1)
        assert not (data / 'instance.json').exists()
        evidence.append({'test': 'occupied_port_fails_without_foreign_browser', 'result': 'passed', 'seconds': elapsed})
        old = work / '.ims_workbench'
        old.mkdir()
        shutil.copyfile(data / 'metadata.sqlite', old / 'metadata.sqlite')
        run([str(exe), '--headless', '--import-data', str(old)])
        assert list((data / 'backups').glob('*/previous.sqlite'))
        assert hashlib.sha256((old / 'metadata.sqlite').read_bytes()).hexdigest() == before
        evidence.append({'test': 'explicit_adoption_with_source_and_target_backups', 'result': 'passed'})
        run([str(exe), '--headless', '--diagnostics', str(work / 'diagnostics.zip')])
        with zipfile.ZipFile(work / 'diagnostics.zip') as archive:
            assert all('metadata' not in path and 'instance' not in path for path in archive.namelist())
        start('start_before_uninstall')
        elapsed = run([str(app / 'unins000.exe'), '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART'])
        assert process.wait(timeout=40) == 0
        assert not exe.exists() and (data / 'metadata.sqlite').is_file()
        assert not (group / 'IMS Workbench.lnk').exists()
        evidence.append({'test': 'uninstall_while_running_preserves_data', 'result': 'passed', 'seconds': elapsed})
        install(installer, 'reinstall')
        start('restart_after_reinstall')
        assert get_json(result_path)['result_digest'] == stored['result_digest']
        stop()
        evidence.append({'test': 'stored_result_preserved_update_uninstall_reinstall', 'result': 'passed'})
        success = True
    except Exception as exc:
        failure = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        if process is not None and process.poll() is None:
            run([str(exe), '--headless', '--stop'])
            process.wait(timeout=40)
        if (app / 'unins000.exe').exists():
            run([str(app / 'unins000.exe'), '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART'])
        report = {'success': success, 'failure': failure,
                  'environment': 'Windows with developer tools; executable PATH restricted to System32',
                  'clean_windows_acceptance': 'pending', 'work': str(work),
                  'installer_sha256': hashlib.sha256(installer.read_bytes()).hexdigest(),
                  'previous_installer_sha256': hashlib.sha256(previous.read_bytes()).hexdigest(),
                  'previous_application_version': args.previous_version or VERSION,
                  'previous_kind': 'actual_release' if args.previous_version else 'synthetic_same_bundle',
                  'seconds': time.perf_counter() - total, 'tests': evidence}
        (out / 'installer-test-evidence.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
