import pytest

from agent import OpenRouterLLM, ask_llm


class FakeLLM:
    def ask(self, messages: list[dict[str, str]]) -> str:
        assert messages[-1]["role"] == "user"
        return "The trophy, because the sentence says it doesn't fit due to its own size."


def test_ask_llm_returns_model_text():
    result = ask_llm(FakeLLM(), [{"role": "user", "content": "question"}])
    assert result == "The trophy, because the sentence says it doesn't fit due to its own size."


def test_openrouter_llm_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        OpenRouterLLM()
