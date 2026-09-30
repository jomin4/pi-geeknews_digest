import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from gndigest.config import KST
from gndigest.metrics import RunMetric, make_run_id, record_run


def _metric(**extra: object) -> RunMetric:
    return RunMetric(
        run_id="2026-09-28T17:30-report",
        kind="report",
        scheduled_at=datetime(2026, 9, 28, 17, 30, tzinfo=KST),
        started_at=datetime(2026, 9, 28, 17, 34, 12, tzinfo=KST),
        **extra,
    )


def test_data06_record_run_writes_one_json_line(tmp_path: Path) -> None:
    path = tmp_path / "data" / "metrics.jsonl"
    record_run(_metric(rss_items=50, new_items=6), path)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["run_id"] == "2026-09-28T17:30-report"
    assert row["kind"] == "report"
    assert row["started_at"] == "2026-09-28T17:34:12+09:00"
    assert row["rss_items"] == 50
    assert "error" not in row  # 값이 없는 필드는 쓰지 않는다


def test_data06_only_appends(tmp_path: Path) -> None:
    path = tmp_path / "metrics.jsonl"
    path.write_text('{"run_id": "old"}\n', encoding="utf-8")
    record_run(_metric(), path)
    record_run(_metric(skipped="already_sent"), path)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == '{"run_id": "old"}'
    assert len(lines) == 3
    assert json.loads(lines[2])["skipped"] == "already_sent"


def test_data_r7_korean_is_not_escaped(tmp_path: Path) -> None:
    path = tmp_path / "metrics.jsonl"
    record_run(_metric(error="요약 단계 429 재시도 초과"), path)
    assert "요약 단계 429 재시도 초과" in path.read_text(encoding="utf-8")


def test_data06_times_are_stored_in_kst(tmp_path: Path) -> None:
    path = tmp_path / "metrics.jsonl"
    metric = RunMetric(
        run_id="x", kind="collect", started_at=datetime(2026, 9, 28, 0, 0, 5, tzinfo=UTC)
    )
    record_run(metric, path)
    assert json.loads(path.read_text(encoding="utf-8"))["started_at"] == "2026-09-28T09:00:05+09:00"


def test_data06_naive_datetime_is_rejected() -> None:
    with pytest.raises(ValidationError):
        RunMetric(run_id="x", kind="collect", started_at=datetime(2026, 9, 28, 9, 0))


def test_data06_unknown_kind_is_rejected() -> None:
    with pytest.raises(ValidationError):
        RunMetric(run_id="x", kind="tune", started_at=datetime(2026, 9, 28, 9, 0, tzinfo=KST))


def test_data06_run_id_format() -> None:
    assert make_run_id("report", datetime(2026, 9, 28, 17, 30, tzinfo=KST)) == "2026-09-28T17:30-report"
    assert make_run_id("collect", datetime(2026, 9, 28, 0, 0, tzinfo=UTC)) == "2026-09-28T09:00-collect"
    with pytest.raises(ValueError):
        make_run_id("collect", datetime(2026, 9, 28, 9, 0))
