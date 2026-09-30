"""data/ 파일 구조 (docs/04-data-model.md DATA-01~05).

모든 시각은 KST aware datetime으로 바꿔 담는다. 시간대가 없는 시각은 거부한다.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, AwareDatetime, BaseModel, ConfigDict, Field

from gndigest.config import KST


def _to_kst(value: datetime) -> datetime:
    return value.astimezone(KST)


KstDatetime = Annotated[AwareDatetime, AfterValidator(_to_kst)]

ArticleType = Literal["news", "show", "ask"]


class Article(BaseModel):
    """DATA-01 수집함의 글 하나."""

    model_config = ConfigDict(extra="forbid")

    id: int
    title: str
    link: str
    published: KstDatetime
    author: str
    type: ArticleType
    summary: str
    collected_at: KstDatetime


class ArticlesFile(BaseModel):
    """DATA-01 articles.json."""

    model_config = ConfigDict(extra="forbid")

    items: list[Article] = []


ThresholdKey = Literal[
    "top_min_interest",
    "maybe_min_interest",
    "topic_min_confidence",
    "secondary_tag_min_prob",
    "excluded_min",
    "verify_min",
]


class Thresholds(BaseModel):
    """DATA-02 기준선. 기본값은 config.DEFAULT_THRESHOLDS, 실행 중에는 state.json 값을 쓴다."""

    model_config = ConfigDict(extra="forbid")

    top_min_interest: float
    maybe_min_interest: float
    topic_min_confidence: float
    secondary_tag_min_prob: float
    excluded_min: float
    verify_min: float


class PendingProposal(BaseModel):
    """DATA-02 주간 보정 제안 (FB-24). JSON 키 `from`은 파이썬 예약어라 from_로 받는다."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    key: ThresholdKey
    from_: float = Field(alias="from")
    to: float
    reason: str
    asked_at: KstDatetime


class State(BaseModel):
    """DATA-02 state.json 실행 상태."""

    model_config = ConfigDict(extra="forbid")

    last_cutoff: KstDatetime
    last_feedback_msg_id: str | None = None
    jev_model: str
    thresholds: Thresholds
    pending_proposal: PendingProposal | None = None
