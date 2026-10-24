"""Process-local owner sessions. Restart revokes all sessions."""
import secrets
import time
from http.cookies import SimpleCookie, CookieError

class LocalSecurity:
    def __init__(self, port, token=None):
        self.host = f'127.0.0.1:{port}'
        self.origin = f'http://{self.host}'
        self.token = token or secrets.token_urlsafe(32)
        self.sessions = {}
        self.failures = []

    def trusted(self, headers, mutation=False):
        if headers.get_all('Host', []) != [self.host]:
            return False
        origins = headers.get_all('Origin', [])
        if origins and origins != [self.origin]:
            return False
        if mutation and origins != [self.origin]:
            return False
        return headers.get('Sec-Fetch-Site') not in ('cross-site', 'same-site')

    def login(self, token):
        now = time.monotonic()
        self.failures = [t for t in self.failures if now-t < 60]
        if len(self.failures) >= 5:
            return None
        if not isinstance(token, str) or not secrets.compare_digest(token.encode(), self.token.encode()):
            self.failures.append(now)
            return None
        self.sessions = {k:v for k,v in self.sessions.items() if v['expires'] > now}
        if len(self.sessions) >= 16:
            self.sessions.clear()
        sid = secrets.token_urlsafe(32)
        self.sessions[sid] = {'csrf': secrets.token_urlsafe(32), 'expires': now+28800}
        return sid

    def session(self, headers):
        try:
            cookies = SimpleCookie(headers.get('Cookie', ''))
            sid = cookies['mwos_session'].value if 'mwos_session' in cookies else ''
        except CookieError:
            return None, None
        session = self.sessions.get(sid)
        if session and session['expires'] > time.monotonic():
            return sid, session
        return None, None

    @staticmethod
    def csrf_valid(headers, session):
        return secrets.compare_digest(headers.get('X-CSRF-Token', '').encode(), session['csrf'].encode())
