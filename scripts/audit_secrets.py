"""Comprehensive Secret Scanner for LumiChart Codebase."""

import re
from pathlib import Path

ROOT = Path(".").resolve()

PATTERNS = [
    (r'(?i)(api[_-]?key|secret[_-]?key|token|password|passwd|auth[_-]?token|access[_-]?token|service[_-]?role|anon[_-]?key)\s*[:=]\s*[\'"][^\'"]+[\'"]', 'Assigned secret key or token'),
    (r'(?i)os\.(?:environ\.get|getenv)\([\'"][^\'"]+[\'"],\s*[\'"][^\'"]+[\'"]\)', 'os.getenv with default fallback value'),
    (r'AIzaSy[A-Za-z0-9_-]{33}', 'Google / Gemini API Key pattern'),
    (r'eyJh[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', 'JWT Token pattern'),
    (r're_[A-Za-z0-9_]{20,}', 'Resend API Key pattern'),
    (r'sk-[A-Za-z0-9]{20,}', 'OpenAI / Secret Key pattern'),
    (r'https?://[a-zA-Z0-9_-]+\.supabase\.co', 'Supabase Project URL'),
    (r'postgres(?:ql)?://[^:]+:[^@]+@[^/]+/[^ \'"\)]+', 'PostgreSQL Connection URI with credentials'),
    (r'(?i)cinetpay[_-]?(?:api[_-]?key|site[_-]?id|secret)\s*[:=]\s*[\'"][^\'"]+[\'"]', 'CinetPay Credential')
]

EXCLUDE_DIRS = {'.git', '.pytest_cache', '__pycache__', 'venv', '.venv', 'node_modules', 'archive'}
EXTS = {'.py', '.json', '.yml', '.yaml', '.md', '.env', '.env.example', '.env.local', '.env.production', '.env.staging'}

findings = []

for p in ROOT.rglob('*'):
    if any(ex in p.parts for ex in EXCLUDE_DIRS):
        continue
    if p.is_file() and (p.suffix in EXTS or p.name.startswith('.env')):
        try:
            content = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            # Ignore comments in markdown or python that are just generic documentation
            if stripped.startswith('#') and not p.name.startswith('.env'):
                continue
            for pat, desc in PATTERNS:
                m = re.search(pat, line)
                if m:
                    val = m.group(0)
                    findings.append({
                        'file': str(p.relative_to(ROOT)).replace('\\', '/'),
                        'line': idx,
                        'type': desc,
                        'snippet': stripped,
                        'matched': val
                    })
                    break

print(f"TOTAL_FINDINGS: {len(findings)}")
for f in findings:
    print(f"FINDING::{f['file']}::{f['line']}::{f['type']}::{f['snippet']}")
