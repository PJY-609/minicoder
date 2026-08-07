"""Milestone 01: make one visible LLM call."""

import os
from typing import Any

from dotenv import load_dotenv
from ollama import Client

load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")

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


def ask_llm(client: Any, messages: list[dict[str, str]]) -> str:
    """Send messages and return only the assistant's text."""
    response = client.chat(model=MODEL, messages=messages)
    return response.message.content


def make_client() -> Client:
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    key = os.getenv("OLLAMA_API_KEY", "")
    headers = {"Authorization": f"Bearer {key}"} if key else None
    return Client(host=host, headers=headers)


def main() -> None:
    messages = [
        {"role": "system", "content": "You are a concise reasoning assistant."},
        {"role": "user", "content": WSC_QUESTION},
    ]
    print("UNDERSTAND")
    print(messages[-1]["content"])
    print("OBSERVE")
    print(ask_llm(make_client(), messages))


if __name__ == "__main__":
    main()
