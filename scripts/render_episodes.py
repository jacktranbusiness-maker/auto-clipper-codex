#!/usr/bin/env python3
"""Validate a full-coverage editorial cutlist and render separate episodes."""
import argparse
import csv
import json
import math
from pathlib import Path
import subprocess
import sys


def probe(path):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)
    ], text=True))


def read_plan(path, duration):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError('Empty cutlist')
    cursor = 0.0
    names = set()
    for index, row in enumerate(rows, 1):
        start, end = float(row['start_seconds']), float(row['end_seconds'])
        name = row['filename']
        if int(row['episode']) != index:
            raise ValueError('Episodes must be sequential, starting at 1')
        if not all(math.isfinite(t) for t in (start, end)) or start < 0 or end <= start:
            raise ValueError(f'Ep {index}: invalid times')
        if abs(start - cursor) > 0.0011:
            raise ValueError(f'Ep {index}: gap/overlap at {cursor}')
        if end > duration + 0.002:
            raise ValueError(f'Ep {index}: beyond source duration')
        if (not name or Path(name).name != name or '/' in name or '\\' in name
                or not name.lower().endswith('.mp4') or name.casefold() in names):
            raise ValueError(f'Ep {index}: unsafe or duplicate filename')
        names.add(name.casefold())
        row.update(start=start, end=end, duration=end-start)
        cursor = end
    if abs(cursor - duration) > 0.002:
        raise ValueError(f'Cutlist must cover source end {duration:.6f}; got {cursor}')
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--cutlist', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--crf', type=int, default=19, choices=range(0, 52), metavar='0..51')
    parser.add_argument('--preset', default='veryfast', choices=[
        'ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow'])
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    info = probe(source)
    video = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
    if not video:
        raise ValueError('No video stream')
    audio = any(s['codec_type'] == 'audio' for s in info['streams'])
    duration = float(info['format']['duration'])
    rows = read_plan(args.cutlist, duration)
    print(f'Validated {len(rows)} episodes; source {duration:.3f}s', flush=True)
    if args.check_only:
        return
    if video['width'] % 2 or video['height'] % 2:
        raise ValueError('Odd dimensions require an explicit encode choice')
    if video.get('color_transfer') in ('smpte2084', 'arib-std-b67'):
        raise ValueError('HDR input requires an explicit color pipeline')
    output = args.output.resolve()
    report_path = output / 'render_report.json'
    targets = [output / r['filename'] for r in rows]
    partials = [p.with_name(p.stem + '.partial.mp4') for p in targets]
    all_paths = targets + partials + [report_path]
    if len(set(all_paths)) != len(all_paths) or any(p.exists() for p in all_paths):
        raise ValueError('Output files already exist or collide; use a fresh folder')
    if source in all_paths:
        raise ValueError('Output would replace source')
    output.mkdir(parents=True, exist_ok=True)
    report = {'source': str(source), 'cutlist': str(args.cutlist.resolve()),
              'source_duration': duration, 'status': 'running', 'episodes': []}
    def save():
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    save()
    try:
        for row, target, partial in zip(rows, targets, partials):
            subprocess.run([
                'ffmpeg', '-hide_banner', '-loglevel', 'error', '-n',
                '-ss', f"{row['start']:.6f}", '-i', str(source),
                '-t', f"{row['duration']:.6f}", '-map', '0:v:0', '-map', '0:a:0?',
                '-c:v', 'libx264', '-preset', args.preset, '-crf', str(args.crf),
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                '-movflags', '+faststart', str(partial)
            ], check=True)
            result = probe(partial)
            actual = float(result['format']['duration'])
            out_video = next(s for s in result['streams'] if s['codec_type'] == 'video')
            out_audio = any(s['codec_type'] == 'audio' for s in result['streams'])
            if abs(actual - row['duration']) > 0.25 or out_audio != audio:
                raise ValueError(f"{target.name}: duration/audio validation failed")
            if (out_video['width'], out_video['height']) != (video['width'], video['height']):
                raise ValueError('Dimensions changed; inspect source rotation/display transform')
            subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(partial),
                            '-f', 'null', '-'], check=True)
            partial.rename(target)
            report['episodes'].append({'episode': int(row['episode']), 'file': target.name,
                'expected_duration': row['duration'], 'actual_duration': actual,
                'decode_ok': True})
            save()
            print(f"Ep {row['episode']}: {target.name} ({actual:.3f}s)", flush=True)
        report['status'] = 'complete'
        save()
    except BaseException as exc:
        report.update(status='failed', error=str(exc))
        save()
        raise


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
