"""data/ 파일 읽기·쓰기 (ARCH-11, docs/04-data-model.md §1).

data/의 JSON은 이 모듈로만 읽고 쓴다.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

M = TypeVar("M", bound=BaseModel)


class DataFileError(RuntimeError):
    """data 파일이 깨졌거나 구조가 맞지 않을 때. 실행을 멈춘다 (DATA-R2)."""


# spec: DATA-R7
def dumps(obj: Any) -> str:
    """한 줄 JSON. 폰에서 한글이 읽히게 ensure_ascii=False."""
    return json.dumps(obj, ensure_ascii=False, separators=(", ", ": "))


# spec: DATA-R2
def read_model(path: Path, model: type[M], default: M | None = None) -> M:
    """JSON 파일을 읽어 pydantic으로 검증한다.

    파일이 없으면 default를 돌려준다 (default가 없으면 오류).
    깨진 파일은 고치거나 덮어쓰지 않고 DataFileError로 멈춘다.
    """
    if not path.exists():
        if default is None:
            raise DataFileError(f"{path} 파일이 없습니다")
        return default
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise DataFileError(f"{path} 파일이 올바른 JSON이 아닙니다: {exc}") from exc
    try:
        return model.model_validate(raw)
    except ValidationError as exc:
        raise DataFileError(f"{path} 파일 구조가 맞지 않습니다: {exc}") from exc


# spec: DATA-R1, DATA-R7
def write_model(path: Path, obj: BaseModel) -> None:
    """임시 파일에 쓴 뒤 이름을 바꿔 원자적으로 저장한다. 들여쓰기 2칸, UTF-8."""
    text = json.dumps(obj.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    """JSONL 파일 끝에 한 줄을 덧붙인다. 기존 줄은 건드리지 않는다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = dumps(record)
    if "\n" in line:
        raise ValueError("JSONL 한 줄에 줄바꿈이 들어갈 수 없습니다")
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
