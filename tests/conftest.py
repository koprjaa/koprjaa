import socket

import pytest


@pytest.fixture(autouse=True)
def _bez_site(monkeypatch):
    def zakazano(*args, **kwargs):
        raise RuntimeError("testy nesmí na síť")

    monkeypatch.setattr(socket.socket, "connect", zakazano)
