# 02 — Ask a Cloud Model Directly

## Discover

There is no agent loop here, and no file to read. The same Winograd Schema
Challenge question used in step01 (`WSC_QUESTION` in `agent.py`) is embedded
directly in the prompt — the model is never asked to propose a "read"
action. It simply sees the question and reports its answer.

The task is:

1. Send the embedded Winograd Schema Challenge question (Hugging Face
   dataset: `winograd_wsc`, config `wsc273`) to a cloud model (DeepSeek v4
   Flash) via OpenRouter.
2. Print the model's answer.

You do not need to verify whether the model's answer matches the dataset's
official label — the goal is to see a cloud model reason over the same
question as step01, but through a cloud API instead of a local model.

## Virtual Environment Setup (required)

Create a dedicated virtual environment for this task in `minicoder/step02`.
Prefer one independent `.venv` per step folder so each task keeps its own
dependencies isolated.

Run from this folder: `minicoder/step02`.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Testing

Deterministic unit tests (fake LLM, no live model call):

```bash
.venv/bin/python -m pytest -q test_agent.py
```

## Run The Milestone Script

Configure the OpenRouter backend in the shared `.env` file (created in step01,
located at `minicoder/.env`):

- `OPENROUTER_API_KEY=<your key>`
- `OPENROUTER_MODEL=<exact DeepSeek v4 Flash model slug from openrouter.ai/models>`

Get a key at https://openrouter.ai/keys and the exact model slug at
https://openrouter.ai/models.

```bash
.venv/bin/python agent.py
```

The script prints the question and the model's answer.

If your sandbox shell injects proxy variables, run with proxies unset:

```bash
env -u ALL_PROXY -u all_proxy -u HTTPS_PROXY -u https_proxy -u HTTP_PROXY -u http_proxy .venv/bin/python agent.py
```

Reflection: what changes for the model (and for you as the developer) when the
question is embedded directly in the prompt instead of being fetched through a
proposed "read" action?
