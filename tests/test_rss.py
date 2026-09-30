from datetime import datetime
from pathlib import Path

import httpx
import pytest
import respx

from gndigest.config import KST
from gndigest.models import Article
from gndigest.rss import (
    FEED_URL,
    RssError,
    article_type,
    collect,
    fetch_feed,
    html_to_text,
    parse_feed,
    select_new,
)

FIXTURE = Path(__file__).parent / "fixtures" / "rss_sample.xml"
COLLECTED_AT = datetime(2026, 9, 29, 21, 51, 8, tzinfo=KST)


def atom(*entries: str) -> bytes:
    return (
        "<?xml version='1.0' encoding='UTF-8'?>"
        "<feed xmlns='http://www.w3.org/2005/Atom'><title>GeekNews</title>"
        + "".join(entries)
        + "</feed>"
    ).encode()


def entry(
    topic: int | None = 1,
    title: str = "제목",
    published: str = "2026-09-29T10:00:00+09:00",
    content: str = "<p>본문</p>",
) -> str:
    href = f"https://news.hada.io/topic?id={topic}" if topic is not None else "https://news.hada.io/"
    return (
        f"<entry><title><![CDATA[{title}]]></title>"
        f"<link rel='alternate' type='text/html' href='{href}' />"
        f"<id>{href}</id><updated>{published}</updated><published>{published}</published>"
        "<author><name>neo</name></author>"
        f"<content type='html'><![CDATA[{content}]]></content></entry>"
    )


def article(topic: int, published: datetime) -> Article:
    return Article(
        id=topic, title="t", link=f"https://news.hada.io/topic?id={topic}", published=published,
        author="a", type="news", summary="s", collected_at=COLLECTED_AT,
    )


# ---- 실제 피드 저장본 (2026-09-29 21:51 KST 수집) ----------------------------


def test_data01_fixture_parses_all_entries() -> None:
    items = parse_feed(FIXTURE.read_bytes(), COLLECTED_AT)
    assert len(items) == 50
    first = items[0]
    assert first.id == 34489
    assert first.link == "https://news.hada.io/topic?id=34489"
    assert first.author == "neo"
    assert first.published == datetime(2026, 9, 29, 21, 32, 57, tzinfo=KST)
    assert first.collected_at == COLLECTED_AT


def test_data01_fixture_ids_are_unique_and_positive() -> None:
    ids = [item.id for item in parse_feed(FIXTURE.read_bytes(), COLLECTED_AT)]
    assert len(set(ids)) == len(ids)
    assert all(i > 0 for i in ids)


def test_data01_fixture_summaries_have_no_html() -> None:
    for item in parse_feed(FIXTURE.read_bytes(), COLLECTED_AT):
        assert "<" not in item.summary and ">" not in item.summary
        assert "  " not in item.summary
        assert item.summary == item.summary.strip()


def test_data01_fixture_title_entities_are_unescaped() -> None:
    titles = [item.title for item in parse_feed(FIXTURE.read_bytes(), COLLECTED_AT)]
    assert "Regression Testing: Techniques, Tools & Best Practices" in titles
    assert not any("&amp;" in t for t in titles)


def test_data01_fixture_show_gn_detected() -> None:
    items = parse_feed(FIXTURE.read_bytes(), COLLECTED_AT)
    shows = [item for item in items if item.type == "show"]
    assert {item.title for item in shows} == {
        "Show GN: Relio ERD - 브라우저에서 테이블과 관계를 설계하는 ERD 편집기",
        "Show GN: OVERFIT - 딥러닝 기반 2D 횡스크롤 소울라이크",
    }


# ---- 규칙별 ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("Show GN: 새 도구", "show"),
        ("Ask GN: 질문 있어요", "ask"),
        ("Rust 1.90 출시", "news"),
        ("show gn: 소문자는 뉴스", "news"),
        ("요약: Show GN: 앞에 다른 말", "news"),
    ],
)
def test_data01_type_from_title_prefix(title: str, expected: str) -> None:
    assert article_type(title) == expected


def test_data01_ask_gn_in_feed() -> None:
    (item,) = parse_feed(atom(entry(title="Ask GN: 어떤 IDE 쓰세요?")), COLLECTED_AT)
    assert item.type == "ask"


def test_data01_html_removed_and_whitespace_normalized() -> None:
    text = html_to_text("<ul>\n<li>첫째 <strong>강조</strong></li><li>둘째&nbsp;&amp; 셋째</li></ul>\n<p>끝...</p>")
    assert text == "첫째 강조 둘째 & 셋째 끝..."


def test_data01_block_tags_do_not_glue_words() -> None:
    assert html_to_text("<li>a</li><li>b</li>") == "a b"
    assert html_to_text("줄1<br>줄2") == "줄1 줄2"


def test_data01_entry_without_topic_id_is_skipped() -> None:
    items = parse_feed(atom(entry(topic=None), entry(topic=7)), COLLECTED_AT)
    assert [item.id for item in items] == [7]


@pytest.mark.parametrize(
    "published",
    ["2026-09-29T08:30:00Z", "2026-09-29T08:30:00+00:00", "2026-09-29T17:30:00+09:00"],
)
def test_sch_r1_published_converted_to_kst(published: str) -> None:
    (item,) = parse_feed(atom(entry(published=published)), COLLECTED_AT)
    assert item.published == datetime(2026, 9, 29, 17, 30, tzinfo=KST)
    assert item.published.utcoffset().total_seconds() == 9 * 3600


def test_sch_r1_rfc822_published_falls_back_to_parsed_time() -> None:
    (item,) = parse_feed(atom(entry(published="Tue, 29 Sep 2026 08:30:00 GMT")), COLLECTED_AT)
    assert item.published == datetime(2026, 9, 29, 17, 30, tzinfo=KST)


@pytest.mark.parametrize(
    "raw",
    [
        b"<html>Just a moment...</html",
        b"<!DOCTYPE html><html><head><title>Just a moment...</title></head><body></body></html>",
        atom(),
    ],
    ids=["broken-html", "valid-html-page", "empty-feed"],
)
def test_rss_non_feed_or_empty_response_raises(raw: bytes) -> None:
    with pytest.raises(RssError, match="RSS를 읽지 못했습니다"):
        parse_feed(raw, COLLECTED_AT)


CUTOFF = datetime(2026, 9, 28, 17, 30, tzinfo=KST)


def test_sch_r4_published_at_cutoff_is_not_new() -> None:
    at = article(1, CUTOFF)
    after = article(2, datetime(2026, 9, 28, 17, 30, 1, tzinfo=KST))
    before = article(3, datetime(2026, 9, 28, 17, 29, 59, tzinfo=KST))
    assert [a.id for a in select_new([at, after, before], [], CUTOFF)] == [2]


def test_sch_r4_ids_already_in_inbox_are_skipped() -> None:
    late = datetime(2026, 9, 29, 9, 0, tzinfo=KST)
    inbox = [article(1, late)]
    assert [a.id for a in select_new([article(1, late), article(2, late)], inbox, CUTOFF)] == [2]


def test_sch_r4_duplicate_ids_in_feed_kept_once() -> None:
    late = datetime(2026, 9, 29, 9, 0, tzinfo=KST)
    assert [a.id for a in select_new([article(5, late), article(5, late)], [], CUTOFF)] == [5]


def test_sch_r4_same_feed_collected_twice_adds_nothing() -> None:
    raw = FIXTURE.read_bytes()
    first = collect(raw, [], CUTOFF, COLLECTED_AT)
    second = collect(raw, first.inbox, CUTOFF, COLLECTED_AT)
    assert len(first.new_items) == 50
    assert second.new_items == []
    assert second.inbox == first.inbox


def test_data06_collect_metric_fields() -> None:
    result = collect(FIXTURE.read_bytes(), [], datetime(2026, 9, 29, 12, 0, tzinfo=KST), COLLECTED_AT)
    fields = result.metric_fields()
    assert fields["rss_items"] == 50
    assert fields["new_items"] == len(result.new_items) < 50
    assert fields["rss_oldest_published"] == datetime(2026, 9, 28, 22, 59, 58, tzinfo=KST)
    assert fields["rss_newest_published"] == datetime(2026, 9, 29, 21, 32, 57, tzinfo=KST)


# ---- 외부 호출 (가짜 응답) -----------------------------------------------------


@respx.mock
def test_fetch_feed_returns_body() -> None:
    respx.get(FEED_URL).mock(return_value=httpx.Response(200, content=b"<feed/>"))
    assert fetch_feed() == b"<feed/>"


@respx.mock
def test_fetch_feed_sends_user_agent() -> None:
    route = respx.get(FEED_URL).mock(return_value=httpx.Response(200, content=b"<feed/>"))
    fetch_feed()
    assert route.calls.last.request.headers["User-Agent"].startswith("gndigest/")


@respx.mock
@pytest.mark.parametrize("status", [403, 500, 503])
def test_fetch_feed_http_error_raises(status: int) -> None:
    respx.get(FEED_URL).mock(return_value=httpx.Response(status))
    with pytest.raises(RssError, match=str(status)):
        fetch_feed()


@respx.mock
def test_fetch_feed_timeout_raises() -> None:
    respx.get(FEED_URL).mock(side_effect=httpx.ConnectTimeout("timeout"))
    with pytest.raises(RssError, match="ConnectTimeout"):
        fetch_feed()
