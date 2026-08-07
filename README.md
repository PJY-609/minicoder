# Minicoder

Build a tiny coding agent in three steps, moving from a single LLM call to a
verify-and-revise agent loop.

## Steps

| Step | New capability | Backend |
| --- | --- | --- |
| [step01](step01/README.md) | Call an LLM | local Ollama (`qwen3:0.6b`) |
| [step02](step02/README.md) | Ask a cloud model directly | OpenRouter (cloud) |
| [step03](step03/README.md) | Search, plan, and verify-and-revise until tests pass | OpenRouter (cloud) |

Start with [SETUP.md](SETUP.md). Completing setup is a stopping point: report
the result and wait. Do not open, inspect, or run `step01` until the user
explicitly asks to begin it.

The intended GitHub Copilot workflow is:

1. Ask Copilot to follow `SETUP.md`. Do not start an exercise unless setup
   reports that every prerequisite passed.
2. Ask Copilot to follow one step's `README.md`, complete its required job,
   and report the saved evidence file.
3. When the workshop is over, ask Copilot to follow [CLEAR.md](CLEAR.md).

Each document contains explicit stop conditions. If a prerequisite or live
model call fails, Copilot should report the exact command and error and stop;
it should not replace the required tool, model, or environment.

## Configuration

All three steps read a single shared `.env` file at the repository root (created
by `setup.py` from [.env.example](.env.example)). It governs the whole
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

The repository uses one root `.venv` containing the pinned dependencies shared
by all three steps. `SETUP.md` creates it transactionally and validates every
exercise before the workshop begins.

## Ground rules

- Read the code before asking a coding assistant to change it.
- Run the deterministic test before trying a live model.
- Never paste an API key into source code or a prompt.
- Do not commit generated output, transcripts, solutions, or `.env`.
