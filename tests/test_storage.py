import json
import os
from datetime import datetime
from pathlib import Path

import pytest

from gndigest.config import KST
from gndigest.models import Article, ArticlesFile
from gndigest.storage import DataFileError, read_model, write_model


def sample() -> ArticlesFile:
    return ArticlesFile(items=[Article(
        id=34388, title="브라질, 온라인 베팅 금지", link="https://news.hada.io/topic?id=34388",
        published=datetime(2026, 9, 28, 7, 45, 59, tzinfo=KST), author="neo", type="news",
        summary="브라질 대통령이…", collected_at=datetime(2026, 9, 28, 9, 0, 12, tzinfo=KST),
    )])


def test_data_r1_write_then_read_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "data" / "articles.json"
    write_model(path, sample())
    assert read_model(path, ArticlesFile) == sample()


def test_data_r1_failed_write_keeps_old_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "articles.json"
    write_model(path, ArticlesFile())
    before = path.read_text(encoding="utf-8")

    def boom(src: object, dst: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError, match="disk full"):
        write_model(path, sample())
    assert path.read_text(encoding="utf-8") == before
    assert [p.name for p in tmp_path.iterdir()] == ["articles.json"]  # 임시 파일 남지 않음


def test_data_r7_format_utf8_indent2_kst(tmp_path: Path) -> None:
    path = tmp_path / "articles.json"
    write_model(path, sample())
    text = path.read_text(encoding="utf-8")
    assert "브라질, 온라인 베팅 금지" in text  # ensure_ascii=False
    assert text.startswith('{\n  "items": [\n    {')  # 들여쓰기 2칸
    assert text.endswith("\n")
    assert '"published": "2026-09-28T07:45:59+09:00"' in text


def test_data_r2_missing_file_returns_default(tmp_path: Path) -> None:
    assert read_model(tmp_path / "none.json", ArticlesFile, ArticlesFile()) == ArticlesFile()


def test_data_r2_missing_file_without_default_raises(tmp_path: Path) -> None:
    with pytest.raises(DataFileError, match="없습니다"):
        read_model(tmp_path / "none.json", ArticlesFile)


@pytest.mark.parametrize(
    "content",
    [
        "{ broken",
        json.dumps({"items": [{"id": "not-int"}]}),
        json.dumps({"items": [], "unknown": 1}),
        json.dumps({"items": [{**json.loads(sample().model_dump_json())["items"][0], "published": "2026-09-28T07:45:59"}]}),
    ],
    ids=["invalid-json", "wrong-type", "unknown-field", "naive-datetime"],
)
def test_data_r2_broken_file_stops_and_is_not_overwritten(tmp_path: Path, content: str) -> None:
    path = tmp_path / "articles.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(DataFileError):
        read_model(path, ArticlesFile, ArticlesFile())
    assert path.read_text(encoding="utf-8") == content


def test_repo_initial_data_files_are_valid() -> None:
    root = Path(__file__).parent.parent
    assert read_model(root / "data" / "articles.json", ArticlesFile).items == []
