from datetime import datetime

import pytest

from gndigest.cli import build_parser, main
from gndigest.config import KST


def test_cli_help_lists_all_commands(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    for command in ("collect", "report", "tune", "show-profile"):
        assert command in out


@pytest.mark.parametrize("command", ["collect", "report", "tune", "show-profile"])
@pytest.mark.parametrize("dry_run", [[], ["--dry-run"]])
def test_cli_commands_exist_and_run(command: str, dry_run: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    assert main([command, *dry_run]) == 0
    assert "아직 구현되지 않았습니다" in capsys.readouterr().err


def test_cli_requires_a_command() -> None:
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


def test_sch_r8_cutoff_is_converted_to_kst() -> None:
    args = build_parser().parse_args(["report", "--dry-run", "--cutoff", "2026-09-28T08:30:00Z"])
    assert args.cutoff == datetime(2026, 9, 28, 17, 30, tzinfo=KST)
    assert args.cutoff.utcoffset().total_seconds() == 9 * 3600


def test_sch_r8_cutoff_keeps_kst_input() -> None:
    args = build_parser().parse_args(["report", "--cutoff", "2026-09-28T17:30:00+09:00"])
    assert args.cutoff == datetime(2026, 9, 28, 17, 30, tzinfo=KST)
    assert args.dry_run is False


@pytest.mark.parametrize("value", ["2026-09-28T17:30:00", "어제 17시 반"])
def test_sch_r8_cutoff_rejects_naive_or_invalid(value: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["report", "--cutoff", value])
    assert exc.value.code == 2
    assert "2026-09-28T17:30:00+09:00" in capsys.readouterr().err


def test_sch_r8_cutoff_only_on_report() -> None:
    with pytest.raises(SystemExit):
        main(["collect", "--cutoff", "2026-09-28T17:30:00+09:00"])
