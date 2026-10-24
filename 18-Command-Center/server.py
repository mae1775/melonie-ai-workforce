"""Authenticated loopback Command Center with a separate read-only live view."""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
import json
import os
import threading
import engine
from local_security import LocalSecurity
from supabase_reader import SupabaseReader

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'preview.sqlite3'

class Handler(BaseHTTPRequestHandler):
    server_version = 'MWOS/1.3'
    sys_version = ''

    def log_message(self, *args):
        pass

    def send_error(self, code, message=None, explain=None):
        self.reply({'error': 'Request rejected'}, code)

    def reply(self, body, status=200, kind='application/json; charset=utf-8', cookie=None):
        raw = body if isinstance(body, bytes) else json.dumps(body, default=str).encode()
        self.send_response(status)
        headers = {'Content-Type': kind, 'Cache-Control': 'no-store',
                   'Content-Length': str(len(raw)), 'X-Content-Type-Options': 'nosniff',
                   'X-Frame-Options': 'DENY', 'Referrer-Policy': 'no-referrer',
                   'Cross-Origin-Resource-Policy': 'same-origin',
                   'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
                   'Content-Security-Policy': "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"}
        if cookie:
            headers['Set-Cookie'] = cookie
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(raw)

    def guard(self, mutation=False):
        if not self.server.security.trusted(self.headers, mutation):
            self.reply({'error': 'Untrusted request origin or host'}, 403)
            return False
        return True

    def do_GET(self):
        if not self.guard(): return
        path = urlsplit(self.path).path
        if path in ('/', '/app.js'):
            name, kind = ('index.html', 'text/html; charset=utf-8') if path == '/' else ('app.js', 'text/javascript; charset=utf-8')
            return self.reply((ROOT/name).read_bytes(), kind=kind)
        _, session = self.server.security.session(self.headers)
        if not session: return self.reply({'error': 'Local sign-in required'}, 401)
        if path == '/api/session': return self.reply({'csrf': session['csrf']})
        if path == '/api/state':
            try:
                return self.reply(engine.snapshot(self.server.db))
            except Exception:
                return self.reply({'error': 'Local workspace unavailable'}, 503)
        if path == '/api/live/state':
            if urlsplit(self.path).query:
                return self.reply({'error': 'Live scope cannot be supplied by the browser'}, 400)
            if not self.server.live_lock.acquire(blocking=False):
                return self.reply({'error': 'Live refresh already in progress'}, 429)
            try:
                return self.reply(self.server.reader.snapshot())
            finally:
                self.server.live_lock.release()
        return self.reply({'error': 'Not found'}, 404)

    def do_POST(self):
        self.close_connection = True
        if not self.guard(mutation=True): return
        path = urlsplit(self.path).path
        _, session = self.server.security.session(self.headers)
        if path != '/api/login' and not session:
            return self.reply({'error': 'Local sign-in required'}, 401)
        if path != '/api/login' and not self.server.security.csrf_valid(self.headers, session):
            return self.reply({'error': 'CSRF validation failed'}, 403)
        try:
            if self.headers.get('Transfer-Encoding') or len(self.headers.get_all('Content-Length', [])) != 1:
                return self.reply({'error': 'Invalid request framing'}, 400)
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 <= length <= 12000:
                return self.reply({'error': 'Invalid request size'}, 413)
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                return self.reply({'error': 'JSON required'}, 415)
            body = json.loads(self.rfile.read(length) or b'{}')
            if not isinstance(body, dict): raise ValueError('Expected object')
            if path == '/api/login':
                sid = self.server.security.login(body.get('token'))
                if not sid: return self.reply({'error': 'Sign-in failed or rate limited'}, 401)
                return self.reply({'ok': True}, cookie=f'mwos_session={sid}; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800')
            if path == '/api/logout':
                sid, _ = self.server.security.session(self.headers)
                self.server.security.sessions.pop(sid, None)
                return self.reply({'ok': True}, cookie='mwos_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0')
            db = self.server.db
            if path == '/api/projects': result = engine.new_project(db, str(body.get('name','')), str(body.get('business','')))
            elif path == '/api/tasks': result = engine.new_task(db, str(body.get('project_id','')), str(body.get('title','')), str(body.get('agent','')), str(body.get('domain','general')))
            elif path == '/api/acquisition-plan': result = engine.acquisition_plan(db, str(body.get('project_id','')))
            elif path == '/api/approvals': result = engine.draft_approval(db, str(body.get('task_id','')), str(body.get('action','')), body.get('payload',{}))
            elif path == '/api/approvals/decision': result = engine.decide_approval(db, str(body.get('approval_id','')), str(body.get('decision','')))
            elif path == '/api/tasks/transition': result = engine.transition(db, str(body.get('task_id','')), str(body.get('target','')))
            elif path == '/api/pause': result = 'already_paused'
            else: return self.reply({'error': 'Not found'}, 404)
            return self.reply({'ok': True, 'result': result}, 201)
        except (ValueError, TypeError, KeyError, UnicodeError):
            return self.reply({'error': 'Invalid request or offline draft operation'}, 400)
        except Exception:
            return self.reply({'error': 'Local operation unavailable'}, 503)

    def setup(self):
        super().setup()
        self.connection.settimeout(10)


def create_server(port=8765, db=DB, reader=None, token=None):
    httpd = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    httpd.security = LocalSecurity(httpd.server_port, token)
    httpd.db = db
    httpd.reader = reader if reader is not None else SupabaseReader.from_env()
    httpd.live_lock = threading.Lock()
    return httpd

if __name__ == '__main__':
    engine.init(DB)
    httpd = create_server(int(os.environ.get('MWOS_PORT', '8765')))
    print(f'Local Command Center: {httpd.security.origin}', flush=True)
    print(f'Local sign-in token (keep private): {httpd.security.token}', flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
