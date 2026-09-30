import json
from datetime import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from gndigest.config import DEFAULT_THRESHOLDS, KST
from gndigest.models import PendingProposal, State
from gndigest.storage import DataFileError, read_model, write_model
from gndigest.window import load_state, new_state

NOW = datetime(2026, 9, 28, 23, 0, tzinfo=KST)


def test_data02_new_state_defaults() -> None:
    state = new_state(NOW, "typesafe/jev-1.13")
    assert state.last_cutoff == datetime(2026, 9, 27, 17, 30, tzinfo=KST)
    assert state.last_feedback_msg_id is None
    assert state.jev_model == "typesafe/jev-1.13"
    assert state.thresholds.model_dump() == DEFAULT_THRESHOLDS
    assert state.pending_proposal is None


def test_data02_state_json_matches_document_shape(tmp_path: Path) -> None:
    state = new_state(NOW, "typesafe/jev-1.13").model_copy(update={
        "last_feedback_msg_id": "1290000000000000000",
        "pending_proposal": PendingProposal(
            key="top_min_interest", **{"from": 2.5}, to=2.3,
            reason="좋음 평가 3건이 2.3~2.5 구간", asked_at=datetime(2026, 9, 28, 17, 31, tzinfo=KST),
        ),
    })
    path = tmp_path / "state.json"
    write_model(path, state)
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert set(raw) == {"last_cutoff", "last_feedback_msg_id", "jev_model", "thresholds", "pending_proposal"}
    assert raw["last_cutoff"] == "2026-09-27T17:30:00+09:00"
    assert raw["pending_proposal"]["from"] == 2.5  # 문서의 키 이름 그대로
    assert "from_" not in raw["pending_proposal"]
    assert read_model(path, State) == state


@pytest.mark.parametrize(
    "change",
    [
        {"last_cutoff": "2026-09-27T17:30:00"},
        {"thresholds": {**DEFAULT_THRESHOLDS, "unknown_min": 1.0}},
        {"thresholds": {k: v for k, v in DEFAULT_THRESHOLDS.items() if k != "verify_min"}},
        {"extra_field": 1},
    ],
    ids=["naive-cutoff", "unknown-threshold", "missing-threshold", "unknown-field"],
)
def test_data02_invalid_state_is_rejected(change: dict) -> None:
    raw = json.loads(new_state(NOW, "m").model_dump_json(by_alias=True)) | change
    with pytest.raises(ValidationError):
        State.model_validate(raw)


def test_data02_pending_proposal_key_must_be_threshold() -> None:
    with pytest.raises(ValidationError):
        PendingProposal(key="jev_model", **{"from": 1}, to=2, reason="r", asked_at=NOW)


def test_data02_load_state_creates_file_on_first_run(tmp_path: Path) -> None:
    path = tmp_path / "data" / "state.json"
    state = load_state(path, NOW, "typesafe/jev-1.13", create=True)
    assert path.exists()
    assert read_model(path, State) == state


def test_sch_r8_load_state_dry_run_does_not_create_file(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    state = load_state(path, NOW, "typesafe/jev-1.13", create=False)
    assert not path.exists()
    assert state.last_cutoff == datetime(2026, 9, 27, 17, 30, tzinfo=KST)


def test_data02_load_state_reads_existing_file_unchanged(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    saved = new_state(NOW, "typesafe/jev-1.13").model_copy(
        update={"last_cutoff": datetime(2026, 9, 20, 17, 30, tzinfo=KST)}
    )
    write_model(path, saved)
    before = path.read_text(encoding="utf-8")
    assert load_state(path, NOW, "other-model", create=True) == saved
    assert path.read_text(encoding="utf-8") == before


def test_data_r2_broken_state_stops(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text('{"last_cutoff": "yesterday"}', encoding="utf-8")
    with pytest.raises(DataFileError):
        load_state(path, NOW, "m", create=True)
    assert path.read_text(encoding="utf-8") == '{"last_cutoff": "yesterday"}'
