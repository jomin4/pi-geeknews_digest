"""실행 지표 기록기 (ARCH-12, DATA-06).

실행 1번 = metrics.jsonl 한 줄. 포트폴리오 결과 수치의 원본이므로 덧붙이기만 한다.
작업별 지표 필드(rss_items, jev_calls …)는 각 작업(T01~T11)에서 채운다.
비밀값과 API 원문 응답은 넣지 않는다.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, field_validator

from gndigest import storage
from gndigest.config import DATA_DIR, KST

METRICS_FILE = DATA_DIR / "metrics.jsonl"

RunKind = Literal["collect", "report"]


class RunMetric(BaseModel):
    """DATA-06 한 줄. 공통 필드만 고정하고, 작업별 필드는 extra로 받는다."""

    model_config = ConfigDict(extra="allow")

    run_id: str
    kind: RunKind
    scheduled_at: datetime | None = None
    started_at: datetime
    finished_at: datetime | None = None
    skipped: str | None = None
    error: str | None = None
    report: dict[str, Any] | None = None

    @field_validator("scheduled_at", "started_at", "finished_at")
    @classmethod
    def _aware_kst(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("시각에는 시간대가 있어야 합니다 (KST aware datetime)")
        return value.astimezone(KST)


def make_run_id(kind: RunKind, scheduled_at: datetime) -> str:
    """예: 2026-09-28T17:30-report (DATA-06 예시 형식)."""
    if scheduled_at.tzinfo is None:
        raise ValueError("scheduled_at에는 시간대가 있어야 합니다")
    return f"{scheduled_at.astimezone(KST):%Y-%m-%dT%H:%M}-{kind}"


# spec: DATA-06
def record_run(metric: RunMetric, path: Path = METRICS_FILE) -> None:
    """지표 한 줄을 덧붙인다. 값이 없는 필드는 쓰지 않는다."""
    storage.append_jsonl(path, metric.model_dump(mode="json", exclude_none=True))
