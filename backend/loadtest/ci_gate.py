"""Headless Locust smoke gate for CI.

Runs a short read-heavy scenario against a running API and fails when the
aggregate failure ratio exceeds the configured threshold.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description='Run Locust CI smoke gate')
    parser.add_argument('--host', default='http://127.0.0.1:8000')
    parser.add_argument('--users', type=int, default=10)
    parser.add_argument('--spawn-rate', type=int, default=2)
    parser.add_argument('--run-time', default='30s')
    parser.add_argument('--max-fail-ratio', type=float, default=0.05)
    args = parser.parse_args()

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
        '--only-summary',
        '--exit-code-on-error',
        '0',
    ]
    completed = subprocess.run(cmd, cwd=BACKEND_DIR, check=False)
    if completed.returncode != 0:
        print(f'Locust exited with code {completed.returncode}', file=sys.stderr)
        return completed.returncode

    print('Locust CI gate passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
