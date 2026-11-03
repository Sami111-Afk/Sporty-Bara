import pytest

from sportybara.http import get_json


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append({"url": url, "params": params, "headers": headers, "timeout": timeout})
        return self.response


def test_get_json_trimite_parametrii_si_intoarce_json():
    session = FakeSession(FakeResponse({"response": [1, 2]}))
    data = get_json(session, "https://example.test/x", params={"league": 140}, headers={"k": "v"})
    assert data == {"response": [1, 2]}
    assert session.calls == [{
        "url": "https://example.test/x",
        "params": {"league": 140},
        "headers": {"k": "v"},
        "timeout": 15,
    }]


def test_get_json_ridica_la_eroare_http():
    session = FakeSession(FakeResponse({"message": "limit"}, status=429))
    with pytest.raises(RuntimeError, match="HTTP 429"):
        get_json(session, "https://example.test/x")
