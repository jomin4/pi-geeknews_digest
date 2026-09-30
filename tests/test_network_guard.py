import socket

import pytest

from conftest import NetworkBlockedError


def test_req14_tcp_connect_is_blocked() -> None:
    with pytest.raises(NetworkBlockedError):
        socket.create_connection(("93.184.216.34", 443), timeout=1)


def test_req14_dns_lookup_is_blocked() -> None:
    with pytest.raises(NetworkBlockedError):
        socket.getaddrinfo("news.hada.io", 443)
