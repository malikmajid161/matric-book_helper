import hashlib
import hmac
import json
import secrets
import time
from fastapi import HTTPException, Request
from config import settings

sessions: dict[str, dict] = {}
attempts: dict[str, list[float]] = {}


def profiles():
    return json.loads(settings.student_profiles_json) if settings.student_profiles_json else []


def profile_list():
    return [{'id': row['id'], 'name': row['name']} for row in profiles()]


def login(identifier: str, code: str, address: str):
    now = time.time()
    attempts[address] = [stamp for stamp in attempts.get(address, []) if stamp > now - 300]
    if len(attempts[address]) >= 10:
        raise HTTPException(429, 'Too many sign-in attempts. Try again in five minutes.')
    attempts[address].append(now)
    profile = next((row for row in profiles() if row['id'] == identifier), None)
    if profile is None:
        raise HTTPException(401, 'Incorrect name or study code.')
    actual = hashlib.scrypt(code.encode(), salt=bytes.fromhex(profile['salt']), n=16384, r=8, p=1).hex()
    if not hmac.compare_digest(actual, profile['hash']):
        raise HTTPException(401, 'Incorrect name or study code.')
    token = secrets.token_urlsafe(32)
    for key in list(sessions):
        if sessions[key]['expires'] < now:
            del sessions[key]
    sessions[token] = {'id': identifier, 'name': profile['name'], 'expires': now + 604800}
    return {'token': token, 'profile': {'id': identifier, 'name': profile['name']}, 'expires_at': int(now + 604800)}


def check_session(request: Request):
    if not profiles():
        return
    token = request.headers.get('Authorization', '').removeprefix('Bearer ')
    session = sessions.get(token)
    if session is None or session['expires'] < time.time():
        raise HTTPException(401, 'Sign in with your name and study code. Downloaded books remain available offline.')
