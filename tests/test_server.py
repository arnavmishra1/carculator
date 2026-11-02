import json
import threading
import urllib.error
import urllib.request

import pytest

from calculator.server import HOST, MAX_BODY_BYTES, CalculatorServer


@pytest.fixture
def base_url(tmp_path):
    (tmp_path / "index.html").write_text("<h1>Calculator</h1>")
    server = CalculatorServer((HOST, 0), tmp_path)
    thread = threading.Thread(
        target=server.serve_forever, args=(0.01,), daemon=True
    )
    thread.start()
    yield f"http://{HOST}:{server.server_address[1]}"
    server.shutdown()
    server.server_close()
    thread.join()


def request(url, method="GET", body=None, content_type="application/json"):
    data = body if isinstance(body, bytes) or body is None else json.dumps(body).encode()
    headers = {"Content-Type": content_type} if data is not None else {}
    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, data=data, method=method, headers=headers)
        ) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


def calculate(base_url, expression):
    status, body = request(
        f"{base_url}/api/calculate", "POST", {"expression": expression}
    )
    return status, json.loads(body)


def test_calculate_returns_result_fact_and_history(base_url):
    status, body = calculate(base_url, "100+81")
    assert status == 200
    assert body["result"] == "181"
    assert "181 horsepower" in body["fact"]
    assert body["history"] == [{"expression": "100+81", "result": "181"}]


def test_fact_is_null_when_nothing_matches(base_url):
    status, body = calculate(base_url, "0.1+0.2")
    assert status == 200
    assert body["result"] == "0.3"
    assert body["fact"] is None


def test_calculation_errors_are_reported_and_not_recorded(base_url):
    status, body = calculate(base_url, "1÷0")
    assert status == 422
    assert body == {"error": "Can't divide by zero"}
    assert json.loads(request(f"{base_url}/api/history")[1]) == {"history": []}


def test_history_can_be_read_and_cleared(base_url):
    calculate(base_url, "1+1")
    calculate(base_url, "2+2")
    history = json.loads(request(f"{base_url}/api/history")[1])["history"]
    assert [entry["expression"] for entry in history] == ["2+2", "1+1"]

    status, _ = request(f"{base_url}/api/history", "DELETE")
    assert status == 200
    assert json.loads(request(f"{base_url}/api/history")[1]) == {"history": []}


@pytest.mark.parametrize(
    "body",
    [
        b"not json",
        b"[]",
        b"{}",
        b'{"expression": 5}',
        b"x" * (MAX_BODY_BYTES + 1),
    ],
)
def test_malformed_requests_are_rejected(base_url, body):
    status, response = request(f"{base_url}/api/calculate", "POST", body)
    assert status == 400
    assert json.loads(response) == {"error": "Invalid request"}


def test_non_json_requests_are_rejected(base_url):
    status, _ = request(
        f"{base_url}/api/calculate",
        "POST",
        {"expression": "1+1"},
        content_type="text/plain",
    )
    assert status == 415


def test_frontend_is_served(base_url):
    status, body = request(f"{base_url}/")
    assert status == 200
    assert b"Calculator" in body
