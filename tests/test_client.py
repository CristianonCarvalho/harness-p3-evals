import json
import pytest
import httpx
from evals.client import OpenRouterClient, ClientError


def make(handler):
    return OpenRouterClient("k", transport=httpx.MockTransport(handler))


def test_chat_sends_body_and_auth():
    seen = {}

    def h(req):
        seen["auth"] = req.headers["authorization"]
        seen["body"] = json.loads(req.content)
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "oi"}, "finish_reason": "stop"}],
                "usage": {},
            },
        )

    r = make(h).chat([{"role": "user", "content": "x"}], model="m/a")
    assert seen["auth"] == "Bearer k"
    assert seen["body"]["usage"] == {"include": True} and seen["body"]["model"] == "m/a"
    assert "tools" not in seen["body"]
    assert r["choices"][0]["message"]["content"] == "oi"


def test_chat_sends_max_tokens():
    seen = {}

    def h(req):
        seen["body"] = json.loads(req.content)
        return httpx.Response(200, json={"choices": [{"message": {"content": "oi"}, "finish_reason": "stop"}], "usage": {}})

    make(h).chat([{"role": "user", "content": "x"}], model="m")
    assert seen["body"]["max_tokens"] == 4096


def test_chat_without_max_tokens():
    seen = {}

    def h(req):
        seen["body"] = json.loads(req.content)
        return httpx.Response(200, json={"choices": [{"message": {"content": "oi"}, "finish_reason": "stop"}], "usage": {}})

    OpenRouterClient("k", transport=httpx.MockTransport(h), max_tokens=None).chat([{"role": "user", "content": "x"}], model="m")
    assert "max_tokens" not in seen["body"]


def test_error_payload_with_200_raises():
    with pytest.raises(ClientError):
        make(lambda req: httpx.Response(200, json={"error": {"code": 400, "message": "bad"}})).chat([], model="m")


def test_http_error_raises():
    with pytest.raises(ClientError):
        make(lambda req: httpx.Response(401, json={})).chat([], model="m")


def test_chat_sends_tools():
    seen = {}

    def h(req):
        seen["body"] = json.loads(req.content)
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "oi"}, "finish_reason": "stop"}],
                "usage": {},
            },
        )

    tools = [{"type": "function", "function": {"name": "test_func", "parameters": {}}}]
    r = make(h).chat([{"role": "user", "content": "x"}], model="m/a", tools=tools)
    assert seen["body"]["tools"] == tools
    assert r["choices"][0]["message"]["content"] == "oi"


def test_models_returns_data():
    sample_models = [
        {"id": "deepseek/deepseek-v4-flash-0731", "pricing": {"prompt": "0.0000001", "completion": "0.0000002"}},
        {"id": "openai/gpt-4o", "pricing": {"prompt": "0.0000025", "completion": "0.00001"}},
    ]

    def h(req):
        assert req.headers["authorization"] == "Bearer k"
        assert req.url.path == "/api/v1/models"
        return httpx.Response(200, json={"data": sample_models})

    res = make(h).models()
    assert res == sample_models


def test_models_error_raises():
    with pytest.raises(ClientError):
        make(lambda req: httpx.Response(500, json={"error": {"message": "Server error"}})).models()


def test_chat_missing_choices_raises():
    with pytest.raises(ClientError):
        make(lambda req: httpx.Response(200, json={"id": "gen-1"})).chat([], model="m")


def test_chat_empty_choices_raises():
    client = OpenRouterClient("k", transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"choices": []})))
    with pytest.raises(ClientError):
        client.chat([{"role": "user", "content": "x"}], model="m")


def test_models_missing_data_raises():
    with pytest.raises(ClientError):
        make(lambda req: httpx.Response(200, json={"object": "list"})).models()


def test_client_context_manager():
    with make(lambda req: httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})) as client:
        r = client.chat([], model="m")
        assert r["choices"][0]["message"]["content"] == "ok"
