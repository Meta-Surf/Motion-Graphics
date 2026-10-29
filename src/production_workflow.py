"""Offline request planning and delivery evidence. Never calls a paid provider."""
from __future__ import annotations

import re
import subprocess
from datetime import datetime
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from video_contract import ROOT, digest, file_digest, probe, read_json

KINDS = ('creation', 'edit', 'cut', 'motion', 'review', 'update')
HF_TEMPLATES = {'photo_essay', 'layers'}
REMOTION_TEMPLATES = HF_TEMPLATES | {'object3d', 'dataflow', 'cutaway', 'scale', 'compare'}
EDIT_KINDS = {'edit', 'cut', 'update'}


def classify(request: str) -> str:
    """Suggested class only; explicit manifest kind always wins."""
    for kind, expression in (
        ('review', r'\b(revis[aã]o|revisar|review|auditar)\b'),
        ('update', r'\b(atualizar|atualiza[çc][aã]o|update)\b'),
        ('cut', r'\b(cortar|cortes?|cut|clips?)\b'),
        ('edit', r'\b(editar|edi[çc][aã]o|edit)\b'),
        ('motion', r'\b(motion|anima[çc][aã]o|animar)\b'),
    ):
        if re.search(expression, request, re.I):
            return kind
    return 'creation'


def validate_request(value: dict) -> None:
    schema = read_json(ROOT / 'schemas/production-request.schema.json')
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value), key=lambda e: e.json_path)
    if errors:
        raise ValueError('; '.join(f'{e.json_path}: {e.message}' for e in errors[:8]))
    assets = {a['id']: a for a in value['assets']}
    scenes = value['scenes']
    if len(assets) != len(value['assets']) or len({s['id'] for s in scenes}) != len(scenes):
        raise ValueError('Asset and scene IDs must be unique')
    for scene in scenes:
        if not set(scene['assets']) <= assets.keys():
            raise ValueError(f"Unknown asset in scene {scene['id']}")
        if not scene['assets'] and not scene['new_asset_reason']:
            raise ValueError(f"{scene['id']}: explain why new assets are needed")
    fmt = value['brief']['format']
    if fmt:
        try:
            if not 0 < Fraction(fmt['fps']) <= 240:
                raise ValueError('FPS outside 0–240')
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError('Use a positive rational FPS, e.g. 30000/1001') from exc
    external = value['brief']['external']
    if external and external['allowed'] and not external['providers']:
        raise ValueError('External authorization must name providers')
    card = value['approvals']['editonny_card']
    if card:
        if datetime.fromisoformat(card['replied_at'].replace('Z', '+00:00')) <= datetime.fromisoformat(card['shown_at'].replace('Z', '+00:00')):
            raise ValueError('Editonny needs a subsequent explicit reply, after the settings card')
    for name, review in value['reviews'].items():
        if review['status'] != 'pending' and (not review['reviewer'] or not review['evidence']):
            raise ValueError(f'{name}: reviewer and evidence required, including justified not_applicable')


def approval_fingerprint(value: dict) -> str:
    return digest({key:val for key,val in value.items() if key not in ('approvals','reviews')})


def new_request(request: str, project_id: str, kind: str | None = None) -> dict:
    """Create a draft without inventing production choices or approvals."""
    value = read_json(ROOT / 'examples/production-request.synthetic.json')
    value.update(request=request, project_id=project_id, kind=kind or classify(request))
    value['brief'] = {key: [] if key == 'references' else None for key in value['brief']}
    value['scenes'] = []
    validate_request(value)
    return value


def plan_request(value: dict, capabilities: dict) -> dict:
    """Capabilities are current local observations, never inferred from README claims."""
    validate_request(value)
    brief = value['brief']
    questions = [key for key, answer in brief.items() if answer is None and (key != 'existing_renderer' or value['kind'] == 'update')]
    voice = brief['voice']
    if voice and voice['mode'] == 'narration' and (not voice['authorized'] or not voice['profile_id']):
        questions.append('voice.authorized_profile')
    if value['kind'] in EDIT_KINDS | {'review'} and not brief['sources']:
        questions.append('sources.selected_media')
    gates, routes = [], []

    def available(tool):
        observed = capabilities.get(tool, {})
        return observed.get('state') in ('functional', 'sampled', 'production') and bool(observed.get('evidence'))

    def route(stage, tool, reason, blocked=False):
        routes.append(dict(stage=stage, tool=tool, reason=reason, blocked=blocked))
        if blocked:
            gates.append(f'{stage}: {reason}')

    if not value['scenes'] and value['kind'] in {'creation', 'motion'}:
        gates.append('Prepare script, scene map, sources and asset/audio plan')
    current = approval_fingerprint(value)
    if not value['approvals']['plan'] or value['approvals']['plan']['request_sha256'] != current:
        gates.append('Record approval of the script, scenes, sources, tools and criteria before full production')
    if not value['approvals']['sample'] or value['approvals']['sample']['request_sha256'] != current:
        gates.append('Measure and review a representative sample before full production')
    if value['kind'] in EDIT_KINDS | {'review'}:
        route('editorial', 'editonny', 'Inspect sources and use the installed package quality controls', not available('editonny'))
        card = value['approvals']['editonny_card']
        if value['kind'] in EDIT_KINDS and (not card or card.get('request_sha256') != current):
            gates.append('Editonny: inspect → settings card → subsequent explicit reply → workspace init')
    for scene in value['scenes']:
        selected = [a for a in value['assets'] if a['id'] in scene['assets']]
        if selected:
            route('assets:' + scene['id'], 'reuse', 'Use selected original/approved assets; verify bytes and rights', any(not a['approved'] for a in selected))
        elif scene['asset_strategy'] == 'synthetic':
            route('assets:' + scene['id'], 'synthetic', 'Local authored fixtures: ' + scene['new_asset_reason'])
        elif scene['asset_strategy'] == 'local-gpu':
            route('assets:' + scene['id'], 'local-gpu', 'Measure a representative generation and review license/matte before approval', not available('local-generation'))
        elif scene['asset_strategy'] == 'external':
            auth = brief['external']
            permitted = bool(auth and auth['allowed'] and scene['provider'] in auth['providers'] and auth['max_cost'] > 0)
            route('assets:' + scene['id'], scene['provider'], 'Named provider needs budget, license/privacy review and a costed sample', not permitted)
        else:
            route('assets:' + scene['id'], 'decision', 'Select existing assets before production', True)
    if voice and voice['mode'] == 'narration':
        supported_language = (brief['language'] or '').lower() in ('pt', 'pt-br')
        route('narration', 'voicestudio',
              'Current adapter requires Portuguese, approved profile and live AMD GPU; speed=1; another language needs a tested route',
              not available('voicestudio') or not supported_language)
    else:
        route('audio', 'reuse', 'Preserve original audio or explicitly silent output; music/effects only when requested')
    if value['kind'] in {'creation', 'motion', 'update'} and value['scenes']:
        templates = {s['template_id'] for s in value['scenes']}
        fmt = brief['format']
        duration = brief['duration_seconds']
        supported_format = bool(fmt and duration is not None and Fraction(fmt['fps']) in (24, 25, 30, 60) and (
            (fmt['width'], fmt['height']) == (1080, 1920) and 15 <= duration <= 180 or
            (fmt['width'], fmt['height']) == (1920, 1080) and 480 <= duration <= 1800))
        previous = brief.get('existing_renderer')
        if not supported_format:
            route('motion', 'decision', 'Current AiVideo bridge does not support the requested format/duration; select a tested editing or native composition route', True)
        elif value['kind'] == 'update' and previous is None:
            route('motion', 'decision', 'Inspect the existing editable project and identify its renderer before updating', True)
        elif templates <= HF_TEMPLATES and available('hyperframes') and (value['kind'] != 'update' or previous == 'hyperframes'):
            route('motion', 'hyperframes', 'Preferred for supported photo_essay/layers; run official check and sample')
        elif templates <= REMOTION_TEMPLATES and available('remotion') and (value['kind'] != 'update' or previous == 'remotion'):
            reason = ('Preserve existing Remotion composition for this update' if value['kind'] == 'update' else 'HyperFrames bridge lacks these templates' if not templates <= HF_TEMPLATES else 'HyperFrames unavailable in current observations')
            route('motion', 'remotion', reason + '; preserve existing composition and sample before full render')
        else:
            route('motion', 'decision', 'No tested renderer binding for these templates; catalog/Gemini IDs are planning recipes', True)
    if brief['delivery'] and brief['delivery']['editable']:
        concat_tested = capabilities.get('concat', {}).get('state') in ('sampled', 'production') and available('concat')
        route('timeline', 'concat' if concat_tested else 'native-project',
              'Use Concat only with tested import/reopen evidence; retain native source and assets otherwise')
    return dict(project_id=value['project_id'],kind=value['kind'],suggested_kind=classify(value['request']),
                request_sha256=current,questions=questions,routes=routes,gates=gates,
                status='needs_decisions' if questions or gates else 'ready_for_full_production',
                external_authorization=brief['external'],
                note='This planner executes no generation, editing or paid requests. Evidence never approves itself.')


def delivery_report(media: Path, request: dict, *, ffprobe='ffprobe', ffmpeg='ffmpeg') -> dict:
    validate_request(request)
    fmt = request['brief']['format']
    duration = request['brief']['duration_seconds']
    if not fmt or duration is None:
        raise ValueError('Delivery requires explicit format and duration')
    meta = probe(media, ffprobe)
    videos = [s for s in meta['streams'] if s.get('codec_type') == 'video']
    audios = [s for s in meta['streams'] if s.get('codec_type') == 'audio']
    failures = []
    if len(videos) != 1:
        failures.append('Expected one video stream')
    else:
        video = videos[0]
        for key, expected in [('width',fmt['width']),('height',fmt['height']),('codec_name',fmt['video_codec']),('pix_fmt',fmt['pixel_format'])]:
            if video.get(key) != expected:
                failures.append(f'Video {key} differs from brief')
        if Fraction(video.get('avg_frame_rate','0/1')) != Fraction(fmt['fps']):
            failures.append('FPS differs from brief')
        if abs(float(video.get('duration',meta['format']['duration']))-duration) > 1/float(Fraction(fmt['fps']))+.001:
            failures.append('Video duration differs from brief')
    if fmt['audio_codec']:
        if len(audios) != 1 or audios[0].get('codec_name') != fmt['audio_codec']:
            failures.append('Audio codec/stream count differs from brief')
        elif abs(float(audios[0].get('duration',0))-duration) > .05:
            failures.append('Audio duration/sync differs from brief')
    elif audios:
        failures.append('Unexpected audio in explicitly silent delivery')
    decoded = subprocess.run([ffmpeg,'-nostdin','-v','error','-xerror','-i',str(media),'-f','null','-'],capture_output=True,timeout=300)
    if decoded.returncode:
        failures.append('Full decode failed')
    reviews = request['reviews']
    actual_hash=file_digest(media)
    pending = [name for name, review in reviews.items() if review['status']=='pending' or review['media_sha256']!=actual_hash]
    return dict(media=str(media.resolve()),sha256=actual_hash,bytes=media.stat().st_size,
                technical='failed' if failures else 'passed',failures=failures,reviews=reviews,
                pending=pending,delivery='blocked' if failures or pending else 'approved',
                note='Stream durations do not prove lip sync, caption accuracy, listening or appearance; record those reviews separately.')
