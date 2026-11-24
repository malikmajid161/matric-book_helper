"""Check a configured key without printing it or a provider error body."""
import argparse
import getpass
import sys
from pathlib import Path
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import settings

parser = argparse.ArgumentParser()
parser.add_argument('--stdin', action='store_true')
parser.add_argument('--save', action='store_true', help='Save a valid key to the ignored backend .env')
args = parser.parse_args()
if args.stdin:
    print('Ready for key on stdin (key is not echoed).', flush=True)
key = (getpass.getpass('Gemini key: ') if sys.stdin.isatty() else sys.stdin.readline().strip()) if args.stdin else settings.gemini_api_key
if not key:
    raise SystemExit('No Gemini key configured.')
try:
    response = httpx.get('https://generativelanguage.googleapis.com/v1beta/models', headers={'x-goog-api-key': key}, timeout=20)
    print('Gemini model access HTTP status:', response.status_code)
    if response.is_success:
        names = [row['name'].removeprefix('models/') for row in response.json().get('models', [])]
        print('Configured model accessible:', settings.gemini_model in names)
        if args.save:
            path = Path(__file__).resolve().parents[1] / '.env'
            lines = path.read_text(encoding='utf-8').splitlines() if path.exists() else []
            lines = [line for line in lines if not line.startswith('GEMINI_API_KEY=')]
            lines.append('GEMINI_API_KEY=' + key)
            path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
            print('Valid key saved to the ignored server environment file. Restart the backend.')
    else:
        print('Provider rejected this key or request. No key or provider error body was logged.')
except httpx.HTTPError:
    print('Provider connection failed; key status is unknown.')
