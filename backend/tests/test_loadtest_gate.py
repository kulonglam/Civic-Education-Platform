"""Unit tests for Locust CI gate stats parsing (no live Locust run)."""

from pathlib import Path

from loadtest.ci_gate import _parse_stats


def test_parse_stats_aggregated(tmp_path: Path):
    stats = tmp_path / 'stats_stats.csv'
    stats.write_text(
        'Type,Name,Request Count,Failure Count,Median Response Time,Average Response Time,'
        'Min Response Time,Max Response Time,Average Content Size,Requests/s,Failures/s,'
        '50%,66%,75%,80%,90%,95%,98%,99%,99.9%,99.99%,100%\n'
        'GET,/api/health/,10,0,12,15,5,40,20,1,0,10,12,14,15,18,22,30,35,38,39,40\n'
        ',Aggregated,10,1,12,15,5,40,20,1,0.1,10,12,14,15,18,22,30,35,38,39,40\n',
        encoding='utf-8',
    )
    fail_ratio, p95, failures, requests = _parse_stats(stats)
    assert requests == 10
    assert failures == 1
    assert fail_ratio == 0.1
    assert p95 == 22.0
