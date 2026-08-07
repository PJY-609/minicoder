import os

import pytest

from agent import ask_llm, make_client


class FakeResponse:
    class Message:
        content = "A unit test checks one behavior."

    message = Message()


class FakeClient:
    def chat(self, *, model, messages):
        assert model
        assert messages[-1]["role"] == "user"
        return FakeResponse()


def test_ask_llm_returns_message_content():
    result = ask_llm(FakeClient(), [{"role": "user", "content": "What is a test?"}])
    assert result == "A unit test checks one behavior."


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_OLLAMA_TEST") != "1",
    reason="Set RUN_LIVE_OLLAMA_TEST=1 to run the live local-Ollama test.",
)
def test_ask_llm_live_returns_non_empty_response():
    messages = [
        {"role": "system", "content": "You are a concise reasoning assistant."},
        {
            "role": "user",
            "content": (
                "Winograd Schema Challenge question: The trophy doesn't fit "
                "into the brown suitcase because it is too big. What is too "
                "big \u2014 the trophy or the suitcase?"
            ),
        },
    ]
    result = ask_llm(make_client(), messages)
    assert isinstance(result, str)
    assert result.strip()
