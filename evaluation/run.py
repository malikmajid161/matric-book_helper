"""Collect real-book answers and timings for manual ground-truth review."""
import getpass
import json
import os
from pathlib import Path
import time
import httpx

base = os.getenv('PTB_API_URL', 'http://localhost:8000').rstrip('/')
profile = input('Profile ID: ').strip()
response = httpx.post(base + '/login', json={'profile_id': profile, 'code': getpass.getpass('Study code: ')}, timeout=15)
response.raise_for_status()
headers = {'Authorization': 'Bearer ' + response.json()['token']}
cases = json.loads(Path(__file__).with_name('cases.json').read_text(encoding='utf-8'))['cases']
if not cases:
    raise SystemExit('No teacher-reviewed real-book cases are configured. Evaluation cannot pass.')
results = []
for case in cases:
    start = time.monotonic()
    response = httpx.post(base + '/ask', headers=headers, json={key: case[key] for key in ('question', 'book', 'chapter')}, timeout=60)
    results.append({'case': case, 'status': response.status_code, 'seconds': round(time.monotonic() - start, 3),
                    'response': response.json(), 'manual_review': 'pending'})
Path(__file__).with_name('results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
print('Results collected. Teacher review is required; this script does not certify correctness.')
