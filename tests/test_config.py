import pytest

from gndigest.config import (
    DEFAULT_JEV_MODEL,
    DEFAULT_THRESHOLDS,
    KST,
    ConfigError,
    load_settings,
)


def test_arch_s1_missing_required_env_lists_all_names() -> None:
    with pytest.raises(ConfigError) as exc:
        load_settings(require=["OPENROUTER_API_KEY", "DISCORD_BOT_TOKEN"], environ={})
    message = str(exc.value)
    assert "OPENROUTER_API_KEY" in message
    assert "DISCORD_BOT_TOKEN" in message
    assert ".env.example" in message


def test_arch_s1_blank_value_counts_as_missing() -> None:
    with pytest.raises(ConfigError, match="GEMINI_API_KEY"):
        load_settings(require=["GEMINI_API_KEY"], environ={"GEMINI_API_KEY": "  "})


def test_arch_s1_reads_values_from_env() -> None:
    settings = load_settings(
        require=["GEMINI_API_KEY", "GEMINI_MODEL"],
        environ={"GEMINI_API_KEY": "g-key", "GEMINI_MODEL": "flash-x", "DISCORD_OWNER_USER_ID": "42"},
    )
    assert settings.gemini_api_key == "g-key"
    assert settings.gemini_model == "flash-x"
    assert settings.discord_owner_user_id == "42"
    assert settings.openrouter_api_key is None


def test_arch_s1_reads_process_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "bot-token")
    assert load_settings(require=["DISCORD_BOT_TOKEN"]).discord_bot_token == "bot-token"


def test_arch_s1_repr_hides_secrets() -> None:
    settings = load_settings(environ={"OPENROUTER_API_KEY": "sk-secret", "DISCORD_OWNER_USER_ID": "42"})
    text = repr(settings)
    assert "sk-secret" not in text
    assert "42" in text


def test_arch_s1_collect_needs_no_env() -> None:
    settings = load_settings(environ={})
    assert settings.openrouter_api_key is None


def test_arch_s1_unknown_require_name_is_programming_error() -> None:
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        load_settings(require=["OPENAI_API_KEY"], environ={})


def test_jev_c2_default_model_is_pinned_version() -> None:
    assert DEFAULT_JEV_MODEL == "typesafe/jev-1.13"
    assert load_settings(environ={}).jev_model == "typesafe/jev-1.13"
    assert load_settings(environ={"JEV_MODEL": "typesafe/jev-1.14"}).jev_model == "typesafe/jev-1.14"


def test_data02_default_thresholds_match_document() -> None:
    assert DEFAULT_THRESHOLDS == {
        "top_min_interest": 2.5,
        "maybe_min_interest": 2.0,
        "topic_min_confidence": 0.5,
        "secondary_tag_min_prob": 0.3,
        "excluded_min": 0.7,
        "verify_min": 0.7,
    }


def test_kst_is_asia_seoul() -> None:
    assert str(KST) == "Asia/Seoul"
