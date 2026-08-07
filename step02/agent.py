"""Milestone 02: ask a cloud model to answer a Winograd Schema question directly."""

import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "")

SYSTEM_PROMPT = "You are a concise reasoning assistant."

WSC_QUESTION = (
    "Winograd Schema Challenge question "
    "(Hugging Face dataset: winograd_wsc, config wsc273):\n\n"
    "Sentence: The trophy doesn't fit into the brown suitcase "
    "because it is too big.\n\n"
    "Question: What is too big \u2014 the trophy or the suitcase?\n\n"
    "Give your answer and a one-sentence justification. You do "
    "not need to verify whether your answer matches the "
    "dataset's official label."
)


class OpenRouterLLM:
    """Calls a cloud model (e.g. DeepSeek) through OpenRouter's OpenAI-compatible API."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. Add it to your .env file."
            )
        if not OPENROUTER_MODEL:
            raise RuntimeError(
                "OPENROUTER_MODEL is not set. Set it to the exact model slug "
                "shown on https://openrouter.ai/models, e.g. a DeepSeek model id."
            )

    def ask(self, messages: list[dict[str, str]]) -> str:
        response = httpx.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={"model": OPENROUTER_MODEL, "messages": messages},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


def ask_llm(llm: Any, messages: list[dict[str, str]]) -> str:
    """Send messages and return only the assistant's text."""
    return llm.ask(messages)


def main() -> None:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": WSC_QUESTION},
    ]
    print("UNDERSTAND")
    print(messages[-1]["content"])
    print("OBSERVE")
    print(ask_llm(OpenRouterLLM(), messages))


if __name__ == "__main__":
    main()
