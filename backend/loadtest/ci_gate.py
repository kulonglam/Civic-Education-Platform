"""Headless Locust smoke gate for CI.

Runs a short read-heavy scenario and fails when the aggregate failure ratio
or p95 response time exceeds configured thresholds.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]


def _parse_stats(stats_path: Path) -> tuple[float, float, int, int]:
    """Return fail_ratio, p95_ms, failures, requests from Locust CSV stats."""
    with stats_path.open(newline='', encoding='utf-8') as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise RuntimeError(f'No stats rows in {stats_path}')

    aggregated = None
    for row in rows:
        name = (row.get('Name') or row.get('name') or '').strip()
        if name == 'Aggregated':
            aggregated = row
            break
    if aggregated is None:
        aggregated = rows[-1]

    def num(key: str, default: float = 0.0) -> float:
        raw = aggregated.get(key) or aggregated.get(key.lower()) or default
        try:
            return float(raw)
        except (TypeError, ValueError):
            return float(default)

    requests = int(num('Request Count') or num('# requests') or 0)
    failures = int(num('Failure Count') or num('# failures') or 0)
    p95 = num('95%') or num('95%ile') or 0.0
    if requests <= 0:
        raise RuntimeError('Locust reported zero requests.')
    return failures / requests, p95, failures, requests


def main() -> int:
    parser = argparse.ArgumentParser(description='Run Locust CI smoke gate')
    parser.add_argument('--host', default='http://127.0.0.1:8000')
    parser.add_argument('--users', type=int, default=10)
    parser.add_argument('--spawn-rate', type=int, default=2)
    parser.add_argument('--run-time', default='30s')
    parser.add_argument('--max-fail-ratio', type=float, default=0.05)
    parser.add_argument('--max-p95-ms', type=float, default=2000.0)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix='cep-locust-') as tmp:
        prefix = str(Path(tmp) / 'stats')
        cmd = [
            sys.executable,
            '-m',
            'locust',
            '-f',
            'loadtest/ci_locustfile.py',
            '--host',
            args.host,
            '--headless',
            '--users',
            str(args.users),
            '--spawn-rate',
            str(args.spawn_rate),
            '--run-time',
            args.run_time,
            '--csv',
            prefix,
            '--only-summary',
            '--exit-code-on-error',
            '1',
        ]
        completed = subprocess.run(cmd, cwd=BACKEND_DIR, check=False)
        stats_path = Path(f'{prefix}_stats.csv')
        if not stats_path.is_file():
            print(f'Locust stats missing at {stats_path}', file=sys.stderr)
            return completed.returncode or 1

        try:
            fail_ratio, p95, failures, requests = _parse_stats(stats_path)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print(
            f'Locust summary: requests={requests} failures={failures} '
            f'fail_ratio={fail_ratio:.3%} p95={p95:.0f}ms'
        )

        if completed.returncode != 0:
            print(f'Locust exited with code {completed.returncode}', file=sys.stderr)
            return completed.returncode

        if fail_ratio > args.max_fail_ratio:
            print(
                f'Fail ratio {fail_ratio:.3%} exceeds max {args.max_fail_ratio:.3%}',
                file=sys.stderr,
            )
            return 1
        if p95 > args.max_p95_ms:
            print(
                f'p95 latency {p95:.0f}ms exceeds max {args.max_p95_ms:.0f}ms',
                file=sys.stderr,
            )
            return 1

    print('Locust CI gate passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
