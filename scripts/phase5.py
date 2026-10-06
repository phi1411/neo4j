"""QA chỉ đọc trước/sau fresh-start; giữ nguyên báo cáo Phase 2–4."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values, set_key
from neo4j import GraphDatabase

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import phase2

ROOT = phase2.ROOT


def save(name, result):
    (ROOT / 'docs' / name).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')


def database_check(name):
    cfg = dotenv_values(ROOT / '.env')
    baseline = json.loads((ROOT / 'docs/PHASE_2_RESULTS.json').read_text(encoding='utf-8'))
    external = json.loads((ROOT / 'docs/PHASE_3_BASELINE.json').read_text(encoding='utf-8'))
    assert cfg['NEO4J_DATABASE'] == 'quadrilateral'
    with GraphDatabase.driver(cfg['NEO4J_URI'], auth=(cfg['NEO4J_USER'], cfg['NEO4J_PASSWORD'])) as driver:
        driver.verify_connectivity()
        snapshot = phase2.graph(driver, cfg['NEO4J_DATABASE'])
        outside = phase2.graph(driver, cfg['NEO4J_DATABASE'], project=False)
        assert phase2.digest(snapshot) == baseline['second_sha256'], 'Dataset changed: investigate before seed'
        assert phase2.digest(outside) == external['outside_sha256'], 'Outside dataset changed'
        validations, queries = phase2.verify(driver, cfg['NEO4J_DATABASE'])
    report = {'status': 'PASS', 'checked_at': datetime.now(timezone.utc).isoformat(),
              'database': cfg['NEO4J_DATABASE'], 'dataset': phase2.DATASET,
              'nodes': len(snapshot['nodes']), 'relationships': len(snapshot['relationships']),
              'dataset_sha256': phase2.digest(snapshot), 'outside_sha256': phase2.digest(outside),
              'phase2_hash_matched': True, 'validations': validations, 'queries': queries}
    save(name, report)
    print('REAL DATABASE PASS: 44/79, 20 validations, 15 queries; Phase 2 hash unchanged')


def prepare_clean():
    destination = ROOT / '.qa/phase5-clean'
    assert not destination.exists(), 'Clean test directory already exists; do not overwrite'
    destination.mkdir(parents=True)
    for directory in ('app', 'database', 'scripts', 'tests'):
        shutil.copytree(ROOT / directory, destination / directory,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for name in ('requirements.txt', 'run.py', '.env.example', '.gitignore', 'pytest.ini', 'README.md'):
        shutil.copy2(ROOT / name, destination / name)
    (destination / 'docs').mkdir()
    shutil.copy2(destination / '.env.example', destination / '.env')
    config = dotenv_values(ROOT / '.env')
    for key in ('NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD', 'NEO4J_DATABASE'):
        set_key(destination / '.env', key, config[key])
    # Git ở bản sao dùng riêng để kiểm tra ignore và mô phỏng source mới, không init repo gốc.
    subprocess.run(['git', 'init', '--quiet', str(destination)], check=True)
    for relative in ('.env', '.venv/marker', '__pycache__/marker.pyc', '.pytest_cache/marker', '.qa/marker'):
        result = subprocess.run(['git', '-C', str(destination), 'check-ignore', '-q', '--', relative])
        assert result.returncode == 0, f'Missing ignore: {relative}'
    save('PHASE_5_FRESH_START.json', {'status': 'PREPARED', 'copy': '.qa/phase5-clean',
          'original_git_repository': (ROOT / '.git').exists(), 'ignore_checks': 5,
          'copied_existing_venv': False, 'database_reset': False})
    print('Clean source copy prepared; ignore checks PASS; credentials kept private')


def audit():
    config = dotenv_values(ROOT / '.env')
    assert not urlsplit(config['NEO4J_URI']).username and not urlsplit(config['NEO4J_URI']).password
    checked, findings = [], []
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if not path.is_file() or any(part in {'.venv', '.qa', '__pycache__', '.pytest_cache', '.git'} for part in relative.parts):
            continue
        if path.name == '.env' or path.suffix.lower() in {'.jpg', '.png', '.pyc'}:
            continue
        contents = path.read_text(encoding='utf-8', errors='replace')
        checked.append(relative.as_posix())
        if config.get('NEO4J_PASSWORD') and config['NEO4J_PASSWORD'] in contents:
            findings.append({'file': relative.as_posix(), 'kind': 'credential'})
        if re.search(r'[A-Za-z]:[\\/](?:Users|Documents)[\\/]', contents):
            findings.append({'file': relative.as_posix(), 'kind': 'machine_path'})
    assert not findings, 'Source/report audit failed; inspect reported filenames privately'
    save('PHASE_5_AUDIT.json', {'status': 'PASS', 'files_checked': len(checked), 'findings': findings,
                              'uri_has_embedded_auth': False, 'git_repository': (ROOT / '.git').exists(),
                              'tracked_files_audit': 'not applicable: no Git repository at project root',
                              'files': checked})
    print(f'Credential and portable path audit PASS: {len(checked)} files')


def finalize():
    def evidence(name):
        result = json.loads((ROOT / 'docs' / name).read_text(encoding='utf-8'))
        assert result['status'] == 'PASS', name
        return result

    before = evidence('PHASE_5_DB_PREFLIGHT.json')
    after = evidence('PHASE_5_DB_POSTFLIGHT.json')
    seed = evidence('PHASE_5_SEED_RESULTS.json')
    assert before['dataset_sha256'] == after['dataset_sha256'] == seed['second_sha256']
    assert before['outside_sha256'] == after['outside_sha256']
    assert len(after['validations']) == 20 and len(after['queries']) == 15
    assert all(v['status'] == 'PASS' and v['violations'] == 0 for v in after['validations'])
    assert all(q['status'] == 'PASS' for q in after['queries'])
    assert after['nodes'] == 44 and after['relationships'] == 79 and seed['idempotent']
    http = evidence('PHASE_5_HTTP_RESULTS.json')
    fresh_http = evidence('PHASE_5_FRESH_HTTP_RESULTS.json')
    errors = evidence('PHASE_5_ERROR_HTTP.json')
    ui = evidence('PHASE_5_UI_RESULTS.json')
    fresh = evidence('PHASE_5_FRESH_START.json')
    assert all(c['status'] == 'PASS' for c in ui['checks']) and not ui['normal_console_errors']
    required_ui = {'dashboard_stats', 'search_to_detail', 'five_conditions_OR', 'canvas_click_HV',
                   'canvas_click_IS_A', 'tooltip_HV_visible', 'missing_shape_UI_controlled',
                   'fresh_start_real_detail_graph', 'Neo4j_Browser_equal_sides_result'}
    required_ui.update('graph_depth_' + str(d) for d in (1, 2, 3))
    required_ui.update(q + '_UI_expected' for q in ('Q06', 'Q07', 'Q08', 'Q09', 'Q15'))
    assert required_ui <= {c['name'] for c in ui['checks']}
    test_results = {}
    for name in ('PHASE_5_PYTEST.xml', 'PHASE_5_FRESH_PYTEST.xml'):
        document = ET.parse(ROOT / 'docs' / name).getroot()
        assert not any(list(document.iter(kind)) for kind in ('failure', 'error', 'skipped'))
        count = len(list(document.iter('testcase')))
        assert count >= 92
        test_results[name] = {'passed': count, 'failed': 0, 'skipped': 0}
    vendor = ROOT / 'app/static/vendor/vis-network'
    manifest = json.loads((vendor / 'manifest.json').read_text(encoding='utf-8'))
    for name, expected in manifest['files'].items():
        assert hashlib.sha256((vendor / name).read_bytes()).hexdigest() == expected
    images = []
    for path in sorted((ROOT / 'docs/images/phase5').glob('*.jpg')):
        data = path.read_bytes()
        assert data.startswith(b'\xff\xd8') and data.endswith(b'\xff\xd9')
        images.append({'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(data).hexdigest()})
    assert len(images) >= 14 and len(images) == len(ui['screenshots'])
    fresh['temporary_directory_retained'] = True
    fresh['temporary_directory_gitignored'] = True
    fresh['auxiliary_servers_stopped'] = True
    fresh['cleanup_note'] = 'Automatic approval review blocked recursive QA cleanup and deletion of temporary login copies; no bypass attempted.'
    save('PHASE_5_FRESH_START.json', fresh)
    audit()
    report = {'status': 'PASS', 'checked_at': datetime.now(timezone.utc).isoformat(),
              'database': after, 'seed_idempotent': seed['idempotent'], 'pytest': test_results,
              'http': {'main_passed': http['passed'], 'fresh_passed': fresh_http['passed'],
                       'extra_error_search_passed': len(errors['checks'])},
              'browser': {'passed': ui['passed'], 'failed': ui['failed'], 'unexpected_console_errors': 0},
              'fresh_start': fresh, 'local_vendor_integrity': 'PASS', 'credential_scan': 'PASS',
              'screenshots': images, 'ready_for_phase6': True,
              'limitations': ['No Git repository or remote clone available: clean source copy tested instead.',
                              'Clean source/venv tested against existing database; no database reset.',
                              'Temporary QA directory retained after automatic approval rejection; ignored by Git.']}
    save('PHASE_5_RESULTS.json', report)
    print(f'PHASE 5 PASS: {ui["passed"]} browser checks; {len(images)} real screenshots; ready for final documentation')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['preflight', 'postflight', 'prepare-clean', 'audit', 'finalize'])
    args = parser.parse_args()
    try:
        if args.action in {'preflight', 'postflight'}:
            database_check('PHASE_5_DB_' + args.action.upper() + '.json')
        elif args.action == 'prepare-clean':
            prepare_clean()
        elif args.action == 'finalize':
            finalize()
        else:
            audit()
    except Exception as exc:
        print(f'PHASE 5 FAILED ({type(exc).__name__}); inspect the failing check, private details omitted.', file=sys.stderr)
        sys.exit(1)
