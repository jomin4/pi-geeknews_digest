"""GeekNews RSS 수집기 (ARCH-02, docs/02-schedule-and-range.md, DATA-01).

외부 호출(RSS 요청)은 fetch_feed 한 곳에서만 한다. 테스트는 저장본(tests/fixtures)이나
respx 가짜 응답을 쓴다.
"""

from __future__ import annotations

import html
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser

import feedparser
import httpx

from gndigest import __version__
from gndigest.config import KST
from gndigest.models import Article, ArticleType

FEED_URL = "https://news.hada.io/rss/news"
USER_AGENT = f"gndigest/{__version__} (+https://github.com/jomin4/pi-geeknews_digest)"
TIMEOUT_SECONDS = 20.0

_TOPIC_ID = re.compile(r"[?&]id=(\d+)")
_BLOCK_TAGS = {"p", "br", "li", "ul", "ol", "div", "blockquote", "pre", "h1", "h2", "h3", "h4", "h5", "h6", "tr"}


class RssError(RuntimeError):
    """RSS를 받거나 읽지 못했을 때."""


def fetch_feed(client: httpx.Client | None = None) -> bytes:
    """GeekNews RSS 원문을 받는다."""
    own = client is None
    client = client or httpx.Client(timeout=TIMEOUT_SECONDS, headers={"User-Agent": USER_AGENT})
    try:
        response = client.get(FEED_URL)
        response.raise_for_status()
        return response.content
    except httpx.HTTPStatusError as exc:
        raise RssError(f"RSS 요청 실패: HTTP {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise RssError(f"RSS 요청 실패: {type(exc).__name__}") from exc
    finally:
        if own:
            client.close()


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _BLOCK_TAGS:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in _BLOCK_TAGS:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


# spec: DATA-01
def html_to_text(value: str) -> str:
    """HTML 태그를 없애고 엔터티를 풀고 공백을 한 칸으로 정리한다.

    블록 태그(<li>, <p> 등) 경계는 공백으로 바꿔 앞뒤 단어가 붙지 않게 한다.
    """
    parser = _TextExtractor()
    parser.feed(value)
    parser.close()
    return " ".join("".join(parser.parts).split())


# spec: DATA-01
def article_type(title: str) -> ArticleType:
    if title.startswith("Show GN:"):
        return "show"
    if title.startswith("Ask GN:"):
        return "ask"
    return "news"


def topic_id(link: str) -> int | None:
    match = _TOPIC_ID.search(link)
    return int(match.group(1)) if match else None


# spec: SCH-R1
def parse_published(entry: feedparser.FeedParserDict) -> datetime:
    """RSS 시각(ISO 8601, UTC·+09:00 등)을 KST aware datetime으로.

    ISO 형식이 아니면 feedparser가 UTC로 풀어 둔 published_parsed를 쓴다.
    """
    value = entry["published"]
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        if not entry.get("published_parsed"):
            raise RssError(f"published를 읽지 못했습니다: {value}") from None
        parsed = datetime(*entry["published_parsed"][:6], tzinfo=UTC)
    if parsed.tzinfo is None:
        raise RssError(f"published에 시간대가 없습니다: {value}")
    return parsed.astimezone(KST)


# spec: DATA-01, SCH-R1
def parse_feed(raw: bytes, collected_at: datetime) -> list[Article]:
    """Atom 피드를 Article 목록으로 바꾼다 (피드 순서 유지).

    topic id가 없는 글은 가리킬 수 없으므로 건너뛴다.
    """
    feed = feedparser.parse(raw)
    if not feed.entries:
        # 봇 확인 화면·점검 페이지처럼 피드가 아닌 응답을 "0건 수집"으로 넘기지 않는다
        reason = feed.get("bozo_exception") if feed.bozo else "항목이 없습니다"
        raise RssError(f"RSS를 읽지 못했습니다: {reason}")
    articles: list[Article] = []
    for entry in feed.entries:
        link = entry.get("link", "")
        article_id = topic_id(link)
        if article_id is None or "published" not in entry:
            continue
        # GeekNews 제목은 CDATA 안에 엔터티(&amp; 등)가 한 번 더 들어 있다 (L-20260929-2)
        title = html.unescape(entry.get("title", "")).strip()
        content = entry.get("content") or [{}]
        body = content[0].get("value") or entry.get("summary", "")
        articles.append(
            Article(
                id=article_id,
                title=title,
                link=link,
                published=parse_published(entry),
                author=entry.get("author", ""),
                type=article_type(title),
                summary=html_to_text(body),
                collected_at=collected_at,
            )
        )
    return articles


@dataclass(frozen=True)
class CollectResult:
    """수집 1번의 결과와 DATA-06 지표 (P1 증거)."""

    inbox: list[Article]
    new_items: list[Article]
    rss_items: int
    rss_oldest_published: datetime | None
    rss_newest_published: datetime | None

    def metric_fields(self) -> dict[str, object]:
        return {
            "rss_items": self.rss_items,
            "new_items": len(self.new_items),
            "rss_oldest_published": self.rss_oldest_published,
            "rss_newest_published": self.rss_newest_published,
        }


# spec: SCH-R4
def select_new(
    feed_items: Iterable[Article], inbox: Iterable[Article], last_cutoff: datetime
) -> list[Article]:
    """`published > last_cutoff`이고 수집함에 같은 id가 없는 글만 고른다."""
    seen = {item.id for item in inbox}
    fresh: list[Article] = []
    for item in feed_items:
        if item.published > last_cutoff and item.id not in seen:
            fresh.append(item)
            seen.add(item.id)
    return fresh


def collect(
    raw: bytes, inbox: list[Article], last_cutoff: datetime, collected_at: datetime
) -> CollectResult:
    """피드 원문과 현재 수집함으로 새 수집함을 만든다. 파일은 건드리지 않는다."""
    feed_items = parse_feed(raw, collected_at)
    new_items = select_new(feed_items, inbox, last_cutoff)
    published = [item.published for item in feed_items]
    return CollectResult(
        inbox=[*inbox, *new_items],
        new_items=new_items,
        rss_items=len(feed_items),
        rss_oldest_published=min(published) if published else None,
        rss_newest_published=max(published) if published else None,
    )
