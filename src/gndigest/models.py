"""data/ 파일 구조 (docs/04-data-model.md DATA-01~05).

모든 시각은 KST aware datetime으로 바꿔 담는다. 시간대가 없는 시각은 거부한다.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, AwareDatetime, BaseModel, ConfigDict

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
