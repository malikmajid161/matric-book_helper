"""Add/update a named student without placing a plaintext code in source or CLI args."""
import argparse
import getpass
import hashlib
import json
from pathlib import Path
import secrets
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('id')
    parser.add_argument('name')
    args = parser.parse_args()
    code = getpass.getpass('Study code (hidden): ')
    salt = secrets.token_bytes(16)
    rows = json.loads(settings.student_profiles_json or '[]')
    rows = [row for row in rows if row['id'] != args.id]
    rows.append({'id': args.id, 'name': args.name, 'salt': salt.hex(),
                 'hash': hashlib.scrypt(code.encode(), salt=salt, n=16384, r=8, p=1).hex()})
    path = Path(__file__).resolve().parents[1] / '.env'
    lines = path.read_text(encoding='utf-8').splitlines() if path.exists() else []
    lines = [line for line in lines if not line.startswith('STUDENT_PROFILES_JSON=')]
    lines.append("STUDENT_PROFILES_JSON='" + json.dumps(rows) + "'")
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('Profile configured. Restart the server to apply it.')


if __name__ == '__main__':
    main()
