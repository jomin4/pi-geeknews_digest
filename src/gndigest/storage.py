"""data/ 파일 읽기·쓰기 (ARCH-11, docs/04-data-model.md).

T00에서는 metrics.jsonl 덧붙이기만 있다. JSON 파일의 원자적 저장과
pydantic 검증(DATA-R1, DATA-R2)은 T01에서 이 모듈에 추가한다.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# spec: DATA-R7
def dumps(obj: Any) -> str:
    """한 줄 JSON. 폰에서 한글이 읽히게 ensure_ascii=False."""
    return json.dumps(obj, ensure_ascii=False, separators=(", ", ": "))


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    """JSONL 파일 끝에 한 줄을 덧붙인다. 기존 줄은 건드리지 않는다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = dumps(record)
    if "\n" in line:
        raise ValueError("JSONL 한 줄에 줄바꿈이 들어갈 수 없습니다")
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
