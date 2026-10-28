"""Persistent local media library. Originals are never modified or removed."""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

MEDIA = {'.motionref', '.png', '.jpg', '.jpeg', '.webp', '.mp4', '.mov', '.mkv', '.wav', '.mp3', '.m4a', '.ogg', '.flac'}
IMAGE = {'.png', '.jpg', '.jpeg', '.webp'}

def now(): return datetime.now(timezone.utc).isoformat()
def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()

def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        tmp.replace(path)
    finally: tmp.unlink(missing_ok=True)

def binary(name):
    found = shutil.which(name)
    if found: return found
    root = Path(__file__).resolve().parents[1]
    for p in (root / 'remotion/node_modules/@remotion').glob('compositor-*'):
        for suffix in ('', '.exe'):
            if (p / (name + suffix)).is_file(): return str(p / (name + suffix))
    raise ValueError(f'{name} unavailable; configure PATH with the existing installation')

def run(args):
    return subprocess.run(args, check=True, capture_output=True, timeout=120).stdout

def inspect_media(path):
    if path.suffix.lower() == '.motionref':
        value = json.loads(path.read_text(encoding='utf-8'))
        source = value.get('source', '')
        if value.get('kind') != 'remotion-component' or not source.startswith('remotion/src/') or '..' in source.split('/'):
            raise ValueError('Invalid component reference')
        return dict(width=None, height=None, duration=0, format='remotion-reference', alpha='not-applicable', component=value)
    info = json.loads(run([binary('ffprobe'), '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))
    streams = info.get('streams', [])
    video = next((s for s in streams if s['codec_type'] == 'video'), {})
    audio = next((s for s in streams if s['codec_type'] == 'audio'), {})
    if not video and not audio: raise ValueError('No supported media stream')
    meta = dict(width=video.get('width'), height=video.get('height'),
                duration=float(info.get('format', {}).get('duration', 0)),
                format=info.get('format', {}).get('format_name'), pixel_format=video.get('pix_fmt'),
                codec=video.get('codec_name') or audio.get('codec_name'),
                alpha='unverified-video' if video else 'not-applicable', probe_backend='ffprobe-cpu')
    # Decode the actual alpha, including palette transparency. Do not infer it from a prompt or extension.
    if path.suffix.lower() in IMAGE:
        if meta['width'] * meta['height'] > 20_000_000: raise ValueError('Still exceeds the 20MP inspection limit')
        raw = run([binary('ffmpeg'), '-v', 'error', '-i', str(path), '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-'])
        if len(raw) != meta['width'] * meta['height'] * 4: raise ValueError('Incomplete RGBA decode')
        alpha = raw[3::4]; low, high = min(alpha), max(alpha)
        meta.update(alpha='empty' if high == 0 else 'transparent' if low < 255 else 'opaque', duration=0, alpha_min=low, alpha_max=high,
                    alpha_partial=any(0 < x < 255 for x in alpha), alpha_backend='ffmpeg-rgba-cpu')
    return meta

class Library:
    def __init__(self, root=None):
        self.root = Path(root or os.getenv('MOTION_LIBRARY_ROOT') or Path.home() / 'MotionLibrary').resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.root / 'catalog.sqlite', timeout=30)
        self.db.row_factory = sqlite3.Row
        if self.db.execute('PRAGMA user_version').fetchone()[0] not in (0, 1):
            self.db.close(); raise ValueError('Unsupported catalog version; use a compatible library tool')
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS assets (
          id TEXT PRIMARY KEY, sha256 TEXT UNIQUE NOT NULL, file TEXT UNIQUE NOT NULL,
          description TEXT NOT NULL, category TEXT NOT NULL, tags TEXT NOT NULL,
          metadata TEXT NOT NULL, approval TEXT NOT NULL DEFAULT 'pending',
          license TEXT NOT NULL DEFAULT 'unknown', rights TEXT NOT NULL DEFAULT 'unknown',
          notes TEXT NOT NULL DEFAULT '', thumbnail TEXT, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS sources (
          asset_id TEXT REFERENCES assets(id), original TEXT, metadata TEXT NOT NULL,
          imported TEXT NOT NULL, PRIMARY KEY(asset_id,original));
        CREATE TABLE IF NOT EXISTS variants (
          parent TEXT REFERENCES assets(id), child TEXT REFERENCES assets(id), role TEXT,
          PRIMARY KEY(parent,child,role), CHECK(parent != child));
        CREATE TABLE IF NOT EXISTS usages (
          asset_id TEXT REFERENCES assets(id), project TEXT, scene TEXT, layer TEXT,
          used TEXT NOT NULL, PRIMARY KEY(asset_id,project,scene,layer));
        CREATE TABLE IF NOT EXISTS events (at TEXT, asset_id TEXT, action TEXT, data TEXT);
        CREATE VIRTUAL TABLE IF NOT EXISTS asset_fts USING fts5(id UNINDEXED, description, tags, category);
        PRAGMA user_version=1;
        ''')
    def close(self): self.db.close()
    @contextlib.contextmanager
    def lock(self):
        lock = self.root / 'catalog.lock'
        # Never guess that another operation is stale. Recover only after checking its PID.
        with lock.open('x', encoding='utf-8') as f: f.write(json.dumps(dict(pid=os.getpid(), started=now())))
        try: yield
        finally: lock.unlink(missing_ok=True)
    def event(self, ident, action, data):
        self.db.execute('INSERT INTO events VALUES (?,?,?,?)', (now(), ident, action, json.dumps(data, ensure_ascii=False)))
    def path(self, relative):
        path = (self.root / relative).resolve()
        if not path.is_relative_to(self.root): raise ValueError('Path outside library')
        return path
    def get(self, ident):
        row = self.db.execute('SELECT * FROM assets WHERE id=?', (ident,)).fetchone()
        if not row: raise ValueError('Unknown asset ID')
        result = dict(row); result['metadata'] = json.loads(result['metadata']); result['tags'] = json.loads(result['tags'])
        result['sources'] = [dict(s, metadata=json.loads(s['metadata'])) for s in self.db.execute('SELECT * FROM sources WHERE asset_id=?', (ident,))]
        return result
    def import_file(self, source, metadata=None, category=None):
        source = Path(source).resolve(); metadata = dict(metadata or {})
        if source.suffix.lower() not in MEDIA: raise ValueError('Unsupported media type')
        before = sha(source); ident = 'asset-' + before
        with self.lock():
            old = self.db.execute('SELECT id FROM assets WHERE sha256=?', (before,)).fetchone()
            if old:
                asset = self.get(old['id'])
                if sha(self.path(asset['file'])) != before: raise ValueError('Stored object corrupted; restore backup before importing')
            else:
                # Copy into immutable content storage before catalog publication.
                relative = f'objects/{before[:2]}/{before}{source.suffix.lower()}'
                target = self.path(relative); target.parent.mkdir(parents=True, exist_ok=True)
                tmp = target.with_name(target.name + '.' + uuid.uuid4().hex + '.tmp')
                try:
                    shutil.copyfile(source, tmp)
                    if sha(tmp) != before or sha(source) != before: raise ValueError('Source changed during import')
                    # Probe the copied data using the correct extension.
                    if target.exists() and sha(target) != before: raise ValueError('Existing object corrupted')
                    tmp.replace(target)
                finally: tmp.unlink(missing_ok=True)
                media = inspect_media(target)
                thumb = None
                if source.suffix.lower() in IMAGE or media['width']:
                    thumb = f'thumbnails/{before}.jpg'; dest = self.path(thumb); dest.parent.mkdir(exist_ok=True)
                    run([binary('ffmpeg'), '-v', 'error', '-y', '-i', str(target), '-frames:v', '1', '-vf', 'scale=320:320:force_original_aspect_ratio=decrease', str(dest)])
                kind = category or ('image' if source.suffix.lower() in IMAGE else 'clip' if media['width'] else 'audio')
                tags = sorted(set(metadata.get('tags', [])))
                desc = metadata.get('description', source.stem)
                with self.db:
                    self.db.execute('INSERT INTO assets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (ident, before, relative, desc, kind, json.dumps(tags), json.dumps({**metadata, **media}),
                         'pending', metadata.get('license', 'unknown'), metadata.get('rights', 'unknown'), '', thumb, now()))
                    self.db.execute('INSERT INTO asset_fts VALUES (?,?,?,?)', (ident, desc, ' '.join(tags), kind))
            with self.db:
                self.db.execute('INSERT OR IGNORE INTO sources VALUES (?,?,?,?)', (ident, str(source), json.dumps(metadata), now()))
                self.event(ident, 'import-deduplicated' if old else 'import', {'original': str(source), 'sha256': before})
        return self.get(ident)
    def search(self, query='', category='', approval='', limit=100):
        conditions, values = [], []
        if query.strip():
            # Literal FTS tokens: punctuation and user input cannot become MATCH operators.
            tokens = query.split()
            match = ' AND '.join('"' + t.replace('"', '""') + '"' for t in tokens)
            conditions.append('id IN (SELECT id FROM asset_fts WHERE asset_fts MATCH ?)'); values.append(match)
        for name, value in [('category', category), ('approval', approval)]:
            if value: conditions.append(name + '=?'); values.append(value)
        sql = 'SELECT id FROM assets' + (' WHERE ' + ' AND '.join(conditions) if conditions else '') + ' ORDER BY created DESC LIMIT ?'
        return [self.get(row[0]) for row in self.db.execute(sql, (*values, min(max(int(limit), 1), 1000)))]
    def review(self, ident, approval, license, rights, notes):
        if approval not in ('pending', 'approved', 'rejected'): raise ValueError('Invalid review')
        if approval == 'approved' and (license in ('', 'unknown') or rights in ('', 'unknown') or not notes.strip()):
            raise ValueError('Approval requires license, rights evidence and review notes')
        with self.lock(), self.db:
            self.get(ident)
            self.db.execute('UPDATE assets SET approval=?,license=?,rights=?,notes=? WHERE id=?', (approval, license, rights, notes, ident))
            self.event(ident, 'review', dict(approval=approval, license=license, rights=rights, notes=notes))
    def link(self, parent, child, role):
        if parent == child: raise ValueError('A variant must differ from its parent')
        if role not in ('mask', 'cutout', 'shadow', 'background', 'alternate'): raise ValueError('Invalid variant role')
        with self.lock(), self.db:
            self.get(parent); self.get(child)
            self.db.execute('INSERT OR IGNORE INTO variants VALUES (?,?,?)', (parent, child, role))
            self.event(child, 'variant', dict(parent=parent, role=role))
    def apply(self, ident, project, scene, layer, preview=False):
        import re
        if not all(re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', s) for s in (project, scene, layer)): raise ValueError('Invalid project, scene or layer ID')
        with self.lock():
            asset = self.get(ident)
            if not preview and asset['approval'] != 'approved': raise ValueError('Approve rights and quality before production use; preview is explicit')
            if sha(self.path(asset['file'])) != asset['sha256']: raise ValueError('Object hash mismatch')
            manifest = self.root / 'projects' / project / 'resources.json'
            data = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else dict(project=project, scenes={})
            data['scenes'].setdefault(scene, {})[layer] = dict(asset_id=ident, preview=bool(preview))
            # Manifest is the recoverable source of selection; history records every successful application.
            write_json(manifest, data)
            with self.db:
                self.db.execute('INSERT OR IGNORE INTO usages VALUES (?,?,?,?,?)', (ident, project, scene, layer, now()))
                self.event(ident, 'apply', dict(project=project, scene=scene, layer=layer, preview=preview))
            return data
    def export(self, ident, public, preview=False):
        asset = self.get(ident)
        if not preview and asset['approval'] != 'approved': raise ValueError('Asset not approved')
        source = self.path(asset['file'])
        if sha(source) != asset['sha256']: raise ValueError('Object hash mismatch')
        public = Path(public).resolve()
        relative = 'generated/library/' + source.name
        target = (public / relative).resolve()
        if not target.is_relative_to(public): raise ValueError('Invalid export path')
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and sha(target) != asset['sha256']: raise ValueError('Export collision')
        if not target.exists(): shutil.copyfile(source, target)
        return relative
    def verify(self):
        errors = []
        for row in self.db.execute('SELECT id,file,sha256 FROM assets'):
            try:
                if sha(self.path(row['file'])) != row['sha256']: errors.append(dict(id=row['id'], error='hash mismatch'))
            except OSError: errors.append(dict(id=row['id'], error='missing object'))
        integrity = self.db.execute('PRAGMA integrity_check').fetchone()[0]
        if self.db.execute('PRAGMA foreign_key_check').fetchone(): errors.append(dict(error='foreign key violation'))
        if self.db.execute('SELECT count(*) FROM assets').fetchone()[0] != self.db.execute('SELECT count(*) FROM asset_fts').fetchone()[0]: errors.append(dict(error='FTS index count mismatch'))
        return dict(ok=not errors and integrity == 'ok', integrity=integrity, errors=errors,
                    assets=self.db.execute('SELECT count(*) FROM assets').fetchone()[0])
    def backup(self, destination):
        destination = Path(destination).resolve()
        if destination == self.root or destination.is_relative_to(self.root): raise ValueError('Backup must be outside the live library')
        with self.lock():
            report = self.verify()
            if not report['ok']: raise ValueError('Cannot back up corrupted catalog: ' + json.dumps(report))
            destination.mkdir(parents=True, exist_ok=False)
            try:
                with contextlib.closing(sqlite3.connect(destination / 'catalog.sqlite')) as db: self.db.backup(db)
                paths = {r[0] for r in self.db.execute('SELECT file FROM assets')}
                paths.update(r[0] for r in self.db.execute('SELECT thumbnail FROM assets WHERE thumbnail IS NOT NULL'))
                for p in (self.root / 'projects').rglob('*.json'): paths.add(p.relative_to(self.root).as_posix())
                checksums = {}
                for relative in sorted(paths):
                    dest = destination / relative; dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(self.path(relative), dest); checksums[relative] = sha(dest)
                checksums['catalog.sqlite'] = sha(destination / 'catalog.sqlite')
                write_json(destination / 'backup.json', dict(version=1, created=now(), files=checksums))
            except BaseException:
                # Keep failed snapshot for diagnosis; it has no valid backup.json.
                raise
        return dict(destination=str(destination), files=len(checksums), assets=report['assets'])

def restore(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if destination.exists(): raise ValueError('Restore destination must not exist')
    manifest = json.loads((source / 'backup.json').read_text(encoding='utf-8'))
    if manifest.get('version') != 1 or 'catalog.sqlite' not in manifest['files']: raise ValueError('Invalid backup manifest')
    for relative, checksum in manifest['files'].items():
        p = (source / relative).resolve()
        if not p.is_relative_to(source) or Path(relative).is_absolute() or sha(p) != checksum: raise ValueError('Backup hash/path verification failed')
    destination.mkdir(parents=True)
    for relative in manifest['files']:
        target = destination / relative; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / relative, target)
    library = Library(destination)
    try:
        report = library.verify()
        if not report['ok']: raise ValueError('Restored catalog failed verification')
        return report
    finally: library.close()

def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--root', type=Path)
    sub = p.add_subparsers(dest='command', required=True)
    imp = sub.add_parser('import'); imp.add_argument('sources', nargs='+', type=Path); imp.add_argument('--metadata', type=Path); imp.add_argument('--category')
    search = sub.add_parser('search'); search.add_argument('query', nargs='?', default=''); search.add_argument('--category', default=''); search.add_argument('--approval', default='')
    sub.add_parser('verify')
    b = sub.add_parser('backup'); b.add_argument('destination', type=Path)
    r = sub.add_parser('restore'); r.add_argument('source', type=Path); r.add_argument('destination', type=Path)
    a = sub.add_parser('apply'); a.add_argument('asset_id'); a.add_argument('project'); a.add_argument('scene'); a.add_argument('layer'); a.add_argument('--preview', action='store_true')
    rev = sub.add_parser('review'); rev.add_argument('asset_id'); rev.add_argument('--approval', required=True); rev.add_argument('--license', required=True); rev.add_argument('--rights', required=True); rev.add_argument('--notes', required=True)
    args = p.parse_args()
    if args.command == 'restore': result = restore(args.source, args.destination)
    else:
        lib = Library(args.root)
        try:
            if args.command == 'import':
                meta = json.loads(args.metadata.read_text(encoding='utf-8-sig')) if args.metadata else {}
                paths = []
                for source in args.sources:
                    paths.extend(sorted(s for s in source.rglob('*') if s.is_file() and s.suffix.lower() in MEDIA) if source.is_dir() else [source])
                result = [lib.import_file(source, meta, args.category)['id'] for source in paths]
            elif args.command == 'search': result = lib.search(args.query, args.category, args.approval)
            elif args.command == 'verify': result = lib.verify()
            elif args.command == 'backup': result = lib.backup(args.destination)
            elif args.command == 'apply': result = lib.apply(args.asset_id, args.project, args.scene, args.layer, args.preview)
            elif args.command == 'review': result = lib.review(args.asset_id, args.approval, args.license, args.rights, args.notes)
        finally: lib.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command == 'verify' and not result['ok']: raise SystemExit(1)
if __name__ == '__main__': main()
