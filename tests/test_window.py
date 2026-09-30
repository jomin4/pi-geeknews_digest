"""docs/02-schedule-and-range.md §2의 경계 사례·마감 시각 사례·전송·중복 사례 (범위·상태 부분)."""

from datetime import UTC, datetime

import pytest

from gndigest.config import KST
from gndigest.models import Article
from gndigest.rss import parse_feed, select_new
from gndigest.window import (
    advance_after_send,
    already_sent,
    in_range,
    initial_last_cutoff,
    new_state,
    report_cutoff,
    split_inbox,
)


def kst(*args: int) -> datetime:
    return datetime(*args, tzinfo=KST)


YESTERDAY = kst(2026, 9, 27, 17, 30)
TODAY = kst(2026, 9, 28, 17, 30)
DAY_BEFORE = kst(2026, 9, 26, 17, 30)


def article(topic: int, published: datetime) -> Article:
    return Article(
        id=topic, title=f"글 {topic}", link=f"https://news.hada.io/topic?id={topic}",
        published=published, author="neo", type="news", summary="요약",
        collected_at=kst(2026, 9, 28, 17, 45),
    )


def state_at(last_cutoff: datetime):
    return new_state(kst(2026, 9, 28, 9, 0), "typesafe/jev-1.13").model_copy(update={"last_cutoff": last_cutoff})


# ---- 경계 사례 6개 (02 §2) ----------------------------------------------------


def test_sch_r2_case1_published_exactly_yesterday_1730_is_not_today() -> None:
    assert not in_range(kst(2026, 9, 27, 17, 30, 0), YESTERDAY, TODAY)


def test_sch_r2_case2_published_exactly_today_1730_is_today() -> None:
    assert in_range(kst(2026, 9, 28, 17, 30, 0), YESTERDAY, TODAY)


def test_sch_r7_case3_published_after_cutoff_stays_in_inbox() -> None:
    late = article(2, kst(2026, 9, 28, 17, 30, 1))  # 17:45 실행 때 수집됨
    on_time = article(1, kst(2026, 9, 28, 12, 0))
    selected, rest = split_inbox([on_time, late], YESTERDAY, TODAY)
    assert [a.id for a in selected] == [1]
    assert [a.id for a in rest] == [2]
    # 내일 리포트에서는 범위 안
    tomorrow = kst(2026, 9, 29, 17, 30)
    assert in_range(late.published, TODAY, tomorrow)


def test_sch_r6_case4_failed_send_yesterday_gives_two_days_today() -> None:
    # 어제 전송 실패 → advance_after_send를 부르지 않아 last_cutoff가 그제 17:30 그대로
    state = state_at(DAY_BEFORE)
    inbox = [article(1, kst(2026, 9, 27, 9, 0)), article(2, kst(2026, 9, 28, 9, 0))]
    selected, _ = split_inbox(inbox, state.last_cutoff, report_cutoff(kst(2026, 9, 28, 17, 30)))
    assert [a.id for a in selected] == [1, 2]


def test_sch_r4_case5_same_article_in_collect1_and_collect2_saved_once() -> None:
    first = article(7, kst(2026, 9, 27, 22, 0))
    inbox = select_new([first], [], YESTERDAY)  # 수집 1 (23:00)
    inbox += select_new([first, article(8, kst(2026, 9, 28, 8, 0))], inbox, YESTERDAY)  # 수집 2 (09:00)
    assert [a.id for a in inbox] == [7, 8]


def test_sch_r1_case6_utc_and_kst_notation_compared_in_kst() -> None:
    feed = (
        "<?xml version='1.0' encoding='UTF-8'?><feed xmlns='http://www.w3.org/2005/Atom'>"
        + "".join(
            f"<entry><title>t{i}</title><link href='https://news.hada.io/topic?id={i}'/>"
            f"<published>{p}</published><content type='html'>c</content></entry>"
            for i, p in [
                (1, "2026-09-28T08:30:00Z"),  # = 17:30 KST → 오늘
                (2, "2026-09-28T08:30:01Z"),  # = 17:30:01 KST → 내일
                (3, "2026-09-28T17:30:00+09:00"),  # → 오늘
                (4, "2026-09-27T08:30:00+00:00"),  # = 어제 17:30 KST → 어제분
            ]
        )
        + "</feed>"
    ).encode()
    items = parse_feed(feed, kst(2026, 9, 28, 17, 45))
    assert [a.id for a in items if in_range(a.published, YESTERDAY, TODAY)] == [1, 3]


# ---- 마감 시각 사례 (SCH-R3) ------------------------------------------------------


@pytest.mark.parametrize(
    ("started", "expected"),
    [
        (kst(2026, 9, 28, 17, 30, 0), TODAY),
        (kst(2026, 9, 28, 17, 50), TODAY),
        (kst(2026, 9, 28, 17, 29, 59), YESTERDAY),
        (kst(2026, 9, 28, 10, 0), YESTERDAY),
        (kst(2026, 9, 29, 0, 10), TODAY),
    ],
    ids=["1730", "1750-backup", "1729-59", "1000-manual", "0010-after-midnight"],
)
def test_sch_r3_cutoff_is_latest_1730_not_after_start(started: datetime, expected: datetime) -> None:
    assert report_cutoff(started) == expected


def test_sch_r3_cutoff_from_utc_start_time() -> None:
    assert report_cutoff(datetime(2026, 9, 28, 8, 50, tzinfo=UTC)) == TODAY  # 17:50 KST


def test_sch_r3_naive_time_is_rejected() -> None:
    with pytest.raises(ValueError):
        report_cutoff(datetime(2026, 9, 28, 17, 50))


# ---- 전송·중복 사례 중 범위·상태 부분 (SCH-R6, SCH-R9) -------------------------------


def test_sch_r6_advance_moves_cutoff_and_keeps_only_later_articles() -> None:
    state = state_at(YESTERDAY)
    inbox = [article(1, kst(2026, 9, 28, 9, 0)), article(2, kst(2026, 9, 28, 17, 40))]
    new, remaining = advance_after_send(state, inbox, TODAY)
    assert new.last_cutoff == TODAY
    assert [a.id for a in remaining] == [2]
    assert state.last_cutoff == YESTERDAY  # 원래 state는 그대로


def test_sch_r6_advance_refuses_cutoff_not_after_last_cutoff() -> None:
    with pytest.raises(ValueError):
        advance_after_send(state_at(TODAY), [], TODAY)


def test_sch_r9_primary_1730_not_yet_sent() -> None:
    assert not already_sent(state_at(YESTERDAY), report_cutoff(kst(2026, 9, 28, 17, 31)))


def test_sch_r9_backup_1750_skips_after_primary_sent() -> None:
    state, _ = advance_after_send(state_at(YESTERDAY), [], report_cutoff(kst(2026, 9, 28, 17, 33)))
    assert already_sent(state, report_cutoff(kst(2026, 9, 28, 17, 52)))


def test_sch_r9_backup_1750_sends_when_primary_missed() -> None:
    assert not already_sent(state_at(YESTERDAY), report_cutoff(kst(2026, 9, 28, 17, 52)))


def test_sch_r9_late_primary_skips_after_backup_sent() -> None:
    state, _ = advance_after_send(state_at(YESTERDAY), [], report_cutoff(kst(2026, 9, 28, 17, 52)))
    assert already_sent(state, report_cutoff(kst(2026, 9, 28, 17, 55)))


def test_sch_r9_manual_morning_run_after_yesterday_sent_is_skipped() -> None:
    assert already_sent(state_at(YESTERDAY), report_cutoff(kst(2026, 9, 28, 10, 0)))


def test_data02_initial_last_cutoff_is_yesterday_1730() -> None:
    assert initial_last_cutoff(kst(2026, 9, 28, 23, 0)) == YESTERDAY
    assert initial_last_cutoff(kst(2026, 9, 29, 0, 5)) == TODAY
