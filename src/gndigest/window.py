"""수집 범위 계산 (ARCH-02, docs/02-schedule-and-range.md).

T01에서는 state.json이 없을 때 쓰는 첫 last_cutoff만 있다.
범위 규칙(SCH-R2, R3, R6~R9)과 state 연결은 T02에서 추가한다.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from gndigest.config import KST, REPORT_CUTOFF


# spec: DATA-02
def initial_last_cutoff(now: datetime) -> datetime:
    """state.json이 없는 첫 실행의 last_cutoff: 어제 17:30 KST."""
    if now.tzinfo is None:
        raise ValueError("now에는 시간대가 있어야 합니다")
    yesterday = now.astimezone(KST).date() - timedelta(days=1)
    return datetime.combine(yesterday, REPORT_CUTOFF, tzinfo=KST)
