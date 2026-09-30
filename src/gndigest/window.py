"""수집 범위와 실행 상태 (ARCH-02, docs/02-schedule-and-range.md, DATA-02).

범위 계산은 파일을 건드리지 않는 순수 함수로 두고, state.json 읽기·만들기만 storage를 거친다.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta
from pathlib import Path

from gndigest import storage
from gndigest.config import DEFAULT_THRESHOLDS, KST, REPORT_CUTOFF
from gndigest.models import Article, State, Thresholds


def _require_aware(value: datetime, name: str) -> datetime:
    if value.tzinfo is None:
        raise ValueError(f"{name}에는 시간대가 있어야 합니다")
    return value.astimezone(KST)


# spec: SCH-R3
def report_cutoff(now: datetime) -> datetime:
    """실행 시각 이전의 가장 최근 17:30 KST.

    17:50에 시작해도 오늘 17:30, 17:30 전이나 자정 넘어 시작하면 전날 17:30이다.
    """
    now = _require_aware(now, "now")
    today = datetime.combine(now.date(), REPORT_CUTOFF, tzinfo=KST)
    return today if now >= today else today - timedelta(days=1)


# spec: DATA-02
def initial_last_cutoff(now: datetime) -> datetime:
    """state.json이 없는 첫 실행의 last_cutoff: 어제 17:30 KST."""
    now = _require_aware(now, "now")
    return datetime.combine(now.date() - timedelta(days=1), REPORT_CUTOFF, tzinfo=KST)


# spec: SCH-R1, SCH-R2
def in_range(published: datetime, last_cutoff: datetime, cutoff: datetime) -> bool:
    """오늘 리포트 범위: last_cutoff **초과** ~ cutoff **이하** (KST로 비교)."""
    published = _require_aware(published, "published")
    return last_cutoff < published <= cutoff


# spec: SCH-R2, SCH-R7
def split_inbox(
    items: Iterable[Article], last_cutoff: datetime, cutoff: datetime
) -> tuple[list[Article], list[Article]]:
    """수집함을 (이번 리포트 범위, 수집함에 남길 글)로 나눈다. 순서는 유지한다.

    마감 이후 게시된 글은 남겨 다음 리포트로 넘긴다 (SCH-R7).
    """
    selected: list[Article] = []
    rest: list[Article] = []
    for item in items:
        (selected if in_range(item.published, last_cutoff, cutoff) else rest).append(item)
    return selected, rest


# spec: SCH-R9
def already_sent(state: State, cutoff: datetime) -> bool:
    """이 마감의 리포트를 이미 보냈는지. 보냈으면 리포트 실행은 아무것도 보내지 않는다."""
    return state.last_cutoff >= cutoff


# spec: SCH-R6
def advance_after_send(
    state: State, inbox: Iterable[Article], cutoff: datetime
) -> tuple[State, list[Article]]:
    """리포트 전송이 **성공한 뒤에만** 부른다 (메시지 1 성공, DSC-10).

    last_cutoff를 cutoff로 옮기고, 범위 안 글을 뺀 수집함을 돌려준다.
    전송이 실패하면 부르지 않는다 → last_cutoff와 수집함이 그대로 남아 다음 날 이틀치를 보낸다.
    """
    if cutoff <= state.last_cutoff:
        raise ValueError(f"마감 {cutoff.isoformat()}이 last_cutoff {state.last_cutoff.isoformat()}보다 늦지 않습니다")
    _, rest = split_inbox(inbox, state.last_cutoff, cutoff)
    return state.model_copy(update={"last_cutoff": cutoff}), rest


# spec: DATA-02
def new_state(now: datetime, jev_model: str) -> State:
    """첫 실행용 state. last_cutoff는 어제 17:30, 기준선은 기본값."""
    return State(
        last_cutoff=initial_last_cutoff(now),
        jev_model=jev_model,
        thresholds=Thresholds(**DEFAULT_THRESHOLDS),
    )


# spec: DATA-02, SCH-R8
def load_state(path: Path, now: datetime, jev_model: str, *, create: bool) -> State:
    """state.json을 읽는다. 없으면 새로 만들고, create=True일 때만 파일로 저장한다.

    dry-run은 create=False로 불러 state.json을 만들지도 바꾸지도 않는다 (SCH-R8).
    깨진 파일은 덮어쓰지 않고 멈춘다 (DATA-R2).
    """
    if path.exists():
        return storage.read_model(path, State)
    state = new_state(now, jev_model)
    if create:
        storage.write_model(path, state)
    return state
