import sys
from pathlib import Path
import re

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path('.').resolve()

patterns = [
    ('Google/Gemini API Key', re.compile(r'AIzaSy[A-Za-z0-9_-]{33}|AQ\.[A-Za-z0-9_-]{40,}')),
    ('Resend API Key', re.compile(r're_[A-Za-z0-9_]{20,}')),
    ('Brevo API Key', re.compile(r'xkeysib-[a-zA-Z0-9_-]+')),
    ('Supabase JWT Token', re.compile(r'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+')),
    ('Supabase URL', re.compile(r'https://[a-zA-Z0-9_-]+\.supabase\.co')),
    ('Postgres Connection URI', re.compile(r'postgres(?:ql)?://[^:]+:[^@]+@[^/]+/[^ \'"\)]+')),
    ('Hardcoded Secret in getenv', re.compile(r'os\.(?:environ\.get|getenv)\(["\'][^"\']+["\'],\s*["\'][^"\']{4,}["\']\)')),
    ('Password or Key Assignment', re.compile(r'(?i)(?:api_key|secret_key|jwt_secret|password|smtp_password)\s*[:=]\s*["\'][^"\']{4,}["\']')),
]

EXCLUDE_DIRS = {'.git', '.pytest_cache', '__pycache__', 'venv', '.venv', 'node_modules', 'archive'}
EXTS = {'.py', '.json', '.yml', '.yaml', '.md', '.env', '.env.example'}

results = []

for p in ROOT.rglob('*'):
    if any(ex in p.parts for ex in EXCLUDE_DIRS):
        continue
    if not p.is_file() or not (p.suffix in EXTS or p.name.startswith('.env')):
        continue
    try:
        content = p.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        continue
    rel = str(p.relative_to(ROOT)).replace('\\', '/')
    for idx, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        # skip purely documentation comments in python or markdown headers
        for name, pat in patterns:
            m = pat.search(line)
            if m:
                results.append((rel, idx, name, stripped, m.group(0)))
                break

print(f"TOTAL_MATCHES: {len(results)}")
for r in results:
    print(f"{r[0]}:{r[1]} | [{r[2]}] | {r[3]}")
