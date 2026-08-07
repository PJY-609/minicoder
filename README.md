# Minicoder

Build a tiny coding agent in three steps, moving from a single LLM call to a
verify-and-revise agent loop.

## Steps

| Step | New capability | Backend |
| --- | --- | --- |
| [step01](step01/README.md) | Call an LLM | local Ollama (`qwen3:0.6b`) |
| [step02](step02/README.md) | Ask a cloud model directly | OpenRouter (cloud) |
| [step03](step03/README.md) | Search, plan, and verify-and-revise until tests pass | OpenRouter (cloud) |

Start with [SETUP.md](SETUP.md) before opening `step01/README.md`.

## Configuration

All three steps read a single shared `.env` file at the repository root (created
during step01 setup from [.env.example](.env.example)). It governs the whole
project:

```dotenv
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:0.6b
OLLAMA_API_KEY=

OPENROUTER_API_KEY=
OPENROUTER_MODEL=
```

- step01 uses only the `OLLAMA_*` values (local, no API key needed).
- step02 and step03 use only the `OPENROUTER_*` values. Get a key at
  https://openrouter.ai/keys and the exact model slug at
  https://openrouter.ai/models.

Never commit `.env` or paste an API key into chat or source code.

## Virtual environments

Each step keeps its own independent `.venv` (see each step's README). Do not
share one virtual environment across steps.

## Ground rules

- Read the code before asking a coding assistant to change it.
- Run the deterministic test before trying a live model.
- Never paste an API key into source code or a prompt.
