"""명령행 진입점: gndigest collect | report | tune | show-profile.

T00에서는 명령과 인자만 있고, 각 명령의 동작은 해당 작업에서 채운다.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from gndigest import __version__, metrics, rss, storage, window
from gndigest.config import DATA_DIR, KST, OUT_DIR, load_settings
from gndigest.models import ArticlesFile

# 명령 → 동작을 구현할 작업 (docs/08-implementation-plan.md)
PENDING_TASK = {
    "report": "T02~T07",
    "tune": "T09",
    "show-profile": "T09",
}


# spec: SCH-R8
def parse_cutoff(text: str) -> datetime:
    """--cutoff 값을 KST aware datetime으로 바꾼다. 시간대가 없으면 거부한다."""
    try:
        value = datetime.fromisoformat(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"ISO 8601 형식이 아닙니다: {text} (예: 2026-09-28T17:30:00+09:00)"
        ) from exc
    if value.tzinfo is None:
        raise argparse.ArgumentTypeError(
            f"시간대가 없습니다: {text} (예: 2026-09-28T17:30:00+09:00)"
        )
    return value.astimezone(KST)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gndigest",
        description="GeekNews RSS를 Jev·Gemini로 골라 요약해 Discord로 보내는 리포트 봇",
    )
    parser.add_argument("--version", action="version", version=f"gndigest {__version__}")
    sub = parser.add_subparsers(dest="command", required=True, metavar="명령")

    def add(name: str, help_text: str) -> argparse.ArgumentParser:
        cmd = sub.add_parser(name, help=help_text, description=help_text)
        cmd.add_argument(
            "--dry-run",
            action="store_true",
            help="data/와 Discord를 바꾸지 않고 결과를 out/에만 쓴다",
        )
        return cmd

    collect = add("collect", "RSS를 읽어 새 글을 수집함(articles.json)에 쌓는다")
    collect.add_argument(
        "--feed-file",
        type=Path,
        metavar="파일",
        help="RSS를 요청하지 않고 저장해 둔 피드 파일을 쓴다 (예: tests/fixtures/rss_sample.xml)",
    )
    report = add("report", "최종 수집 → 피드백 해석 → 판단 → 요약 → Discord 전송")
    report.add_argument(
        "--cutoff",
        type=parse_cutoff,
        metavar="ISO시각",
        help="마감 시각 지정 (기본: 오늘 17:30 KST). 예: 2026-09-28T17:30:00+09:00",
    )
    add("tune", "최근 4주 평가로 기준선 변경을 제안한다 (주간 보정)")
    add("show-profile", "현재 취향 프로필을 보여준다")
    return parser


def now_kst() -> datetime:
    """현재 KST 시각 (초 단위, DATA-01·DATA-06 예시 형식)."""
    return datetime.now(KST).replace(microsecond=0)


# spec: SCH-R4, DATA-06
def run_collect(args: argparse.Namespace) -> int:
    """RSS 수집. --dry-run이면 data/는 그대로 두고 결과를 out/에만 쓴다 (SCH-R8)."""
    started = now_kst()
    articles_path = DATA_DIR / "articles.json"
    target = OUT_DIR / "articles.json" if args.dry_run else articles_path
    metrics_path = OUT_DIR / "metrics.jsonl" if args.dry_run else metrics.METRICS_FILE
    run_id = metrics.make_run_id("collect", started)

    try:
        inbox = storage.read_model(articles_path, ArticlesFile, ArticlesFile())
        state = window.load_state(
            DATA_DIR / "state.json", started, load_settings().jev_model, create=not args.dry_run
        )
        raw = args.feed_file.read_bytes() if args.feed_file else rss.fetch_feed()
        result = rss.collect(raw, inbox.items, state.last_cutoff, started)
        storage.write_model(target, ArticlesFile(items=result.inbox))
    except (rss.RssError, storage.DataFileError, OSError) as exc:
        metrics.record_run(
            metrics.RunMetric(
                run_id=run_id, kind="collect", started_at=started, finished_at=now_kst(),
                error=str(exc).splitlines()[0][:200],
            ),
            metrics_path,
        )
        print(f"gndigest collect 실패: {exc}", file=sys.stderr)
        return 1

    metrics.record_run(
        metrics.RunMetric(
            run_id=run_id, kind="collect", started_at=started, finished_at=now_kst(),
            **result.metric_fields(),
        ),
        metrics_path,
    )
    print(
        f"RSS {result.rss_items}건 · 새 글 {len(result.new_items)}건 · "
        f"수집함 {len(result.inbox)}건 → {target}"
    )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "collect":
        return run_collect(args)
    task = PENDING_TASK[args.command]
    print(f"gndigest {args.command}: 아직 구현되지 않았습니다 ({task}에서 구현)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
