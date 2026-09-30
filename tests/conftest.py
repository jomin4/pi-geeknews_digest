"""모든 테스트 공통 설정.

REQ-14: 테스트는 인터넷 없이 돈다. 외부 호출은 tests/fixtures/의 가짜 응답을 쓰고,
실수로 실제 네트워크에 나가면 바로 실패하도록 소켓 연결과 이름 조회를 막는다.
"""

from __future__ import annotations

import socket

import pytest

from gndigest.config import ALL_VARS

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


class NetworkBlockedError(RuntimeError):
    """테스트 중 외부 네트워크 접속 시도."""


@pytest.fixture(autouse=True)
def _block_network(monkeypatch: pytest.MonkeyPatch) -> None:
    real_connect = socket.socket.connect
    real_connect_ex = socket.socket.connect_ex
    real_getaddrinfo = socket.getaddrinfo

    def is_internet(sock: socket.socket) -> bool:
        return sock.family in (socket.AF_INET, socket.AF_INET6)

    def guarded_connect(self: socket.socket, address):  # type: ignore[no-untyped-def]
        if is_internet(self) and address[0] not in LOCAL_HOSTS:
            raise NetworkBlockedError(f"테스트에서 네트워크 접속 시도: {address}")
        return real_connect(self, address)

    def guarded_connect_ex(self: socket.socket, address):  # type: ignore[no-untyped-def]
        if is_internet(self) and address[0] not in LOCAL_HOSTS:
            raise NetworkBlockedError(f"테스트에서 네트워크 접속 시도: {address}")
        return real_connect_ex(self, address)

    def guarded_getaddrinfo(host, *args, **kwargs):  # type: ignore[no-untyped-def]
        if host not in LOCAL_HOSTS and host is not None:
            raise NetworkBlockedError(f"테스트에서 이름 조회 시도: {host}")
        return real_getaddrinfo(host, *args, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", guarded_connect_ex)
    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """개발자 셸의 실제 키가 테스트에 섞이지 않게 gndigest 환경변수를 비운다."""
    for name in ALL_VARS:
        monkeypatch.delenv(name, raising=False)
