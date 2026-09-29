"""환경변수와 기본 설정 (docs/01-architecture.md §3).

비밀값은 환경변수로만 읽는다. 로컬에서는 `.env`를 `uv run --env-file .env ...`로 넘긴다.
기준선 숫자는 기본값만 여기 두고, 실행 중에는 state.json의 `thresholds`를 읽는다.
"""

from __future__ import annotations

import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")

DATA_DIR = Path("data")
OUT_DIR = Path("out")

DEFAULT_JEV_MODEL = "typesafe/jev-1.13"

# DATA-02 state.json의 thresholds 기본값. 최초 state 생성에만 쓴다.
DEFAULT_THRESHOLDS: dict[str, float] = {
    "top_min_interest": 2.5,
    "maybe_min_interest": 2.0,
    "topic_min_confidence": 0.5,
    "secondary_tag_min_prob": 0.3,
    "excluded_min": 0.7,
    "verify_min": 0.7,
}

SECRET_VARS = ("OPENROUTER_API_KEY", "GEMINI_API_KEY", "DISCORD_BOT_TOKEN")
SETTING_VARS = (
    "DISCORD_REPORT_CHANNEL_ID",
    "DISCORD_FEEDBACK_CHANNEL_ID",
    "DISCORD_OWNER_USER_ID",
    "GEMINI_MODEL",
    "JEV_MODEL",
)
ALL_VARS = SECRET_VARS + SETTING_VARS

DEFAULTS: dict[str, str] = {"JEV_MODEL": DEFAULT_JEV_MODEL}


class ConfigError(RuntimeError):
    """필요한 환경변수가 없을 때. 메시지에 빠진 이름을 모두 담는다."""


@dataclass(frozen=True)
class Settings:
    openrouter_api_key: str | None
    gemini_api_key: str | None
    discord_bot_token: str | None
    discord_report_channel_id: str | None
    discord_feedback_channel_id: str | None
    discord_owner_user_id: str | None
    gemini_model: str | None
    jev_model: str

    def __repr__(self) -> str:
        # 비밀값이 로그·오류 메시지에 찍히지 않게 가린다 (ARCH-S1).
        shown = {
            name: ("***" if name.upper() in SECRET_VARS and value else value)
            for name, value in self.__dict__.items()
        }
        return f"Settings({shown})"


# spec: ARCH-S1
def load_settings(
    require: Iterable[str] = (),
    environ: Mapping[str, str] | None = None,
) -> Settings:
    """환경변수에서 설정을 읽는다.

    `require`에 적은 이름이 비어 있으면 빠진 이름을 모두 모아 ConfigError를 낸다.
    명령마다 필요한 값이 다르므로(collect는 키가 필요 없음) 명령이 require를 정한다.
    """
    env = os.environ if environ is None else environ
    unknown = [name for name in require if name not in ALL_VARS]
    if unknown:
        raise ValueError(f"알 수 없는 설정 이름: {', '.join(unknown)}")

    def get(name: str) -> str | None:
        value = env.get(name, "").strip()
        return value or DEFAULTS.get(name)

    missing = [name for name in require if not get(name)]
    if missing:
        raise ConfigError(
            "필요한 환경변수가 없습니다: "
            + ", ".join(missing)
            + ". 로컬에서는 .env에 넣고 `uv run --env-file .env gndigest ...`로 실행하세요 "
            "(.env.example 참고)."
        )

    return Settings(
        openrouter_api_key=get("OPENROUTER_API_KEY"),
        gemini_api_key=get("GEMINI_API_KEY"),
        discord_bot_token=get("DISCORD_BOT_TOKEN"),
        discord_report_channel_id=get("DISCORD_REPORT_CHANNEL_ID"),
        discord_feedback_channel_id=get("DISCORD_FEEDBACK_CHANNEL_ID"),
        discord_owner_user_id=get("DISCORD_OWNER_USER_ID"),
        gemini_model=get("GEMINI_MODEL"),
        jev_model=get("JEV_MODEL") or DEFAULT_JEV_MODEL,
    )
