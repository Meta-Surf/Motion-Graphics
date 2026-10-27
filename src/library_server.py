"""Loopback gallery: search, inspect alpha, select and apply an asset to a scene."""
import argparse
import hmac
import json
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from asset_library import Library


def server(root=None, port=8770):
    token = secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass
        def send(self, status, body, mime='application/json; charset=utf-8'):
            if not isinstance(body, bytes): body = json.dumps(body, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', mime); self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store'); self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; img-src 'self'; media-src 'self'; style-src 'unsafe-inline'; script-src 'nonce-" + token + "'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers(); self.wfile.write(body)
        def local(self):
            hosts = (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}')
            host = self.headers.get('Host', '')
            origin = self.headers.get('Origin')
            if host not in hosts or (origin and origin != 'http://' + host):
                self.send(403, dict(error='Local origin required')); return False
            return True
        def do_GET(self):
            if not self.local(): return
            lib = Library(root)
            try:
                url = urlsplit(self.path); q = parse_qs(url.query)
                if url.path == '/':
                    html = (Path(__file__).parent / 'library_ui/index.html').read_text(encoding='utf-8').replace('__TOKEN__', token)
                    self.send(200, html.encode(), 'text/html; charset=utf-8')
                elif url.path == '/api/assets':
                    self.send(200, lib.search(q.get('q', [''])[0], q.get('category', [''])[0], q.get('approval', [''])[0]))
                elif url.path.startswith('/media/'):
                    parts = url.path.split('/')
                    if len(parts) != 4 or parts[3] not in ('thumbnail', 'original'): raise ValueError('Invalid media path')
                    asset = lib.get(parts[2]); relative = asset['thumbnail'] if parts[3] == 'thumbnail' else asset['file']
                    if not relative: self.send(404, dict(error='No thumbnail')); return
                    path = lib.path(relative)
                    # Large clips use download/CLI; never buffer an unbounded video in the gallery.
                    if path.stat().st_size > 32 * 1024 * 1024: raise ValueError('Use the local file for media over 32MiB')
                    import mimetypes
                    self.send(200, path.read_bytes(), mimetypes.guess_type(str(path))[0] or 'application/octet-stream')
                else: self.send(404, dict(error='Not found'))
            except (ValueError, OSError) as e: self.send(400, dict(error=str(e)))
            finally: lib.close()
        def do_POST(self):
            if not self.local(): return
            if not hmac.compare_digest(self.headers.get('X-Motion-Token', ''), token): self.send(403, dict(error='Page token required')); return
            lib = Library(root)
            try:
                size = int(self.headers.get('Content-Length', 0))
                if not 0 < size <= 16384 or self.headers.get('Content-Type') != 'application/json': raise ValueError('Small JSON body required')
                body = json.loads(self.rfile.read(size))
                if urlsplit(self.path).path != '/api/apply': self.send(404, dict(error='Not found')); return
                if type(body.get('preview', False)) is not bool: raise ValueError('Preview must be boolean')
                result = lib.apply(body['asset_id'], body['project'], body['scene'], body['layer'], body.get('preview', False))
                self.send(200, result)
            except (ValueError, KeyError, TypeError, OSError) as e: self.send(400, dict(error=str(e)))
            finally: lib.close()
    return HTTPServer(('127.0.0.1', port), Handler)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--root', type=Path); p.add_argument('--port', type=int, default=8770); a = p.parse_args()
    service = server(a.root, a.port)
    print(f'Library gallery: http://127.0.0.1:{service.server_port}', flush=True)
    try: service.serve_forever()
    except KeyboardInterrupt: pass
    finally: service.server_close()
