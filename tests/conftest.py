#
# Project: koprjaa
# File:    conftest.py
#
# Description:
# Provides a fixture that prevents network access during testing.
#
# Author:
# Jan Alexandr Kopřiva
# jan.alexandr.kopriva@gmail.com
#
# License: MIT
#

import socket

import pytest


@pytest.fixture(autouse=True)
def _bez_site(monkeypatch):
    def zakazano(*args, **kwargs):
        raise RuntimeError("testy nesmí na síť")

    monkeypatch.setattr(socket.socket, "connect", zakazano)
