"""Final source and Git audit; credentials are compared privately, never printed."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import zipfile

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
WORDS = re.compile(r'TODO|FIXME|DEBUG|print\(|console\.log|temporary|test123|password|secret|token|api_key|NEO4J_PASSWORD', re.I)
SECRETS = {
    'private_key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    'github_token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})\b'),
    'aws_access_key': re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'embedded_url_auth': re.compile(r'\b(?:https?|bolt|neo4j)(?:\+s|\+ssc)?://[^\s/\"\']+:[^\s/@\"\']+@'),
}


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True).stdout


def text_parts(data, name):
    if name.endswith('.docx'):
        with zipfile.ZipFile(io.BytesIO(data)) as package:
            return [(part, package.read(part).decode('utf-8')) for part in package.namelist() if part.endswith(('.xml','.rels'))]
    if name.endswith(('.jpg','.jpeg','.png','.woff','.woff2','.ico')):
        return []
    return [('',data.decode('utf-8',errors='replace'))]


def scan(files, password):
    findings, keywords, paths = [], [], []
    for name,data in files:
        if password and password.encode() in data:
            findings.append({'file':name,'kind':'configured_password'})
        for part,contents in text_parts(data,name):
            if password and password in contents:
                findings.append({'file':name,'part':part,'kind':'configured_password'})
            for kind,pattern in SECRETS.items():
                for match in pattern.finditer(contents):
                    findings.append({'file':name,'part':part,'kind':kind,'line':contents.count('\n',0,match.start())+1})
            if re.search(r'[A-Za-z]:[\\/]+Users[\\/]+Admin',contents,re.I):
                paths.append({'file':name,'part':part,'kind':'machine_path'})
            hits = Counter(m.group(0).lower() for m in WORDS.finditer(contents))
            if hits:
                if name.startswith('app/static/vendor/'):
                    classification='third_party_library'
                elif name.startswith('tests/'):
                    classification='test_assertions_and_fixture_placeholders'
                elif name.startswith('scripts/'):
                    classification='CLI_status_output_or_audit_rules'
                elif name.startswith('docs/') or name in {'.env.example','README.md'}:
                    classification='documentation_placeholder_or_test_evidence'
                else:
                    classification='application_configuration_or_error_handling'
                keywords.append({'file':name,'part':part,'hits':dict(hits),'classification':classification})
    return findings, keywords, paths


def audit(write_report=True):
    cfg = dotenv_values(ROOT/'.env'); password=cfg.get('NEO4J_PASSWORD','')
    candidates = set(filter(None,git('ls-files','--cached','--others','--exclude-standard','-z').decode('utf-8').split('\0')))
    candidate_files = [(name,(ROOT/name).read_bytes()) for name in sorted(candidates)]
    findings,keywords,paths = scan(candidate_files,password)
    staged = list(filter(None,git('diff','--cached','--name-only','-z').decode('utf-8').split('\0')))
    staged_findings,_,_ = scan([(name,git('show',':'+name)) for name in staged],password)
    history = subprocess.run(['git','rev-list','--all'],cwd=ROOT,capture_output=True,text=True)
    revisions=history.stdout.splitlines() if history.returncode==0 else []
    history_findings=[]
    for rev in revisions:
        names=filter(None,git('ls-tree','-r','--name-only','-z',rev).decode('utf-8').split('\0'))
        found,_,_ = scan([(name,git('show',rev+':'+name)) for name in names],password)
        for item in found: item['commit']=rev
        history_findings.extend(found)
    ignored=['.env','.venv/marker','venv/marker','__pycache__/marker.pyc','marker.pyc','.pytest_cache/marker','.DS_Store','Thumbs.db','.qa/marker','local.log']
    for name in ignored:
        assert subprocess.run(['git','check-ignore','-q','--',name],cwd=ROOT).returncode==0, name
    required=['.env.example','README.md','requirements.txt','database/constraints.cypher','database/indexes.cypher','database/seed.cypher','database/demo_queries.cypher','database/validation.cypher','database/shapes.json','database/properties.json','database/conditions.json','database/relationships.json','docs/TONG_QUAN_DU_AN.docx','docs/HUONG_DAN_SU_DUNG.docx']
    assert set(required)<=candidates, 'Required files are excluded or missing'
    forbidden=[name for name in candidates if any(part in {'.qa','.venv','venv','__pycache__','.pytest_cache'} for part in Path(name).parts) or name=='.env']
    assert not forbidden
    status='PASS' if not (findings or staged_findings or history_findings or paths) else 'FAIL'
    result={'status':status,'checked_at':datetime.now(timezone.utc).isoformat(),'candidate_files':len(candidates),'staged_files':len(staged),'history_commits_checked':len(revisions),'gitignore_checks':len(ignored),'required_public_files':len(required),'findings':findings,'staged_findings':staged_findings,'history_findings':history_findings,'machine_paths':paths,'keyword_review':keywords,'history_scope':'All locally available commits; newly initialized repository had no prior local history.','binary_scope':'Known configured password searched in file bytes; DOCX XML and relationship targets scanned; screenshots require visual review.'}
    if write_report:
        (ROOT/'docs/PHASE_7_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['status','candidate_files','staged_files','history_commits_checked','gitignore_checks','findings','staged_findings','history_findings','machine_paths']},ensure_ascii=True))
    assert status=='PASS', 'Audit failed; review filenames, not secret values'


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['audit','database'])
    parser.add_argument('--no-write',action='store_true',help='Audit without changing the saved report or working tree.')
    args=parser.parse_args()
    if args.action=='audit': audit(write_report=not args.no_write)
    else:
        from phase5 import database_check
        database_check('PHASE_7_DB_RESULTS.json')
