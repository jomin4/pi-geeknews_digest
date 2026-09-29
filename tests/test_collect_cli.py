import json
import shutil
from datetime import datetime
from pathlib import Path

import httpx
import pytest
import respx

from gndigest import cli
from gndigest.config import KST
from gndigest.rss import FEED_URL

FIXTURE = Path(__file__).parent / "fixtures" / "rss_sample.xml"
REPO_DATA = Path(__file__).parent.parent / "data"
NOW = datetime(2026, 9, 29, 21, 51, 8, tzinfo=KST)


@pytest.fixture
def workdir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """저장소의 초기 data/를 복사한 임시 폴더에서 실행한다."""
    shutil.copytree(REPO_DATA, tmp_path / "data")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "now_kst", lambda: NOW)
    return tmp_path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_sch_r8_collect_dry_run_writes_only_out(workdir: Path) -> None:
    before = (workdir / "data" / "articles.json").read_text(encoding="utf-8")
    assert cli.main(["collect", "--dry-run", "--feed-file", str(FIXTURE)]) == 0

    assert (workdir / "data" / "articles.json").read_text(encoding="utf-8") == before
    assert not (workdir / "data" / "metrics.jsonl").exists()
    items = json.loads((workdir / "out" / "articles.json").read_text(encoding="utf-8"))["items"]
    assert len(items) == 50  # 어제 17:30 이후 글 전부 (가장 오래된 글 9/28 22:59)
    (row,) = read_jsonl(workdir / "out" / "metrics.jsonl")
    assert row["run_id"] == "2026-09-29T21:51-collect"
    assert row["rss_items"] == 50 and row["new_items"] == 50
    assert row["rss_oldest_published"] == "2026-09-28T22:59:58+09:00"


def test_sch_r4_collect_twice_keeps_inbox_and_logs_both_runs(workdir: Path) -> None:
    assert cli.main(["collect", "--feed-file", str(FIXTURE)]) == 0
    assert cli.main(["collect", "--feed-file", str(FIXTURE)]) == 0
    items = json.loads((workdir / "data" / "articles.json").read_text(encoding="utf-8"))["items"]
    assert len(items) == 50
    rows = read_jsonl(workdir / "data" / "metrics.jsonl")
    assert [r["new_items"] for r in rows] == [50, 0]


def test_sch_r4_collect_uses_initial_cutoff_yesterday_1730(workdir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "now_kst", lambda: datetime(2026, 9, 30, 9, 0, tzinfo=KST))
    assert cli.main(["collect", "--dry-run", "--feed-file", str(FIXTURE)]) == 0
    items = json.loads((workdir / "out" / "articles.json").read_text(encoding="utf-8"))["items"]
    assert items and all(i["published"] > "2026-09-29T17:30:00+09:00" for i in items)


@respx.mock
def test_data06_collect_network_failure_is_recorded(workdir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    respx.get(FEED_URL).mock(return_value=httpx.Response(503))
    before = (workdir / "data" / "articles.json").read_text(encoding="utf-8")
    assert cli.main(["collect"]) == 1
    assert (workdir / "data" / "articles.json").read_text(encoding="utf-8") == before
    (row,) = read_jsonl(workdir / "data" / "metrics.jsonl")
    assert row["error"] == "RSS 요청 실패: HTTP 503"
    assert "rss_items" not in row
    assert "503" in capsys.readouterr().err


def test_data_r2_collect_stops_on_broken_inbox(workdir: Path) -> None:
    (workdir / "data" / "articles.json").write_text("{ broken", encoding="utf-8")
    assert cli.main(["collect", "--feed-file", str(FIXTURE)]) == 1
    assert (workdir / "data" / "articles.json").read_text(encoding="utf-8") == "{ broken"
    (row,) = read_jsonl(workdir / "data" / "metrics.jsonl")
    assert "JSON" in row["error"]
