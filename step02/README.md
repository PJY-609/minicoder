# 02 — Ask a Cloud Model Directly

## Copilot job

Give GitHub Copilot this instruction:

> Follow `step02/README.md`, complete the required job, and report the LLM's
> output saved in `step02/llm_output.txt`.

Copilot must use the existing `agent.py` and the configured OpenRouter model.
It must never print, read aloud, or paste the API key into chat. If a required
command fails, it must stop and report the command and sanitized error.

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

## Prerequisite check

Complete [../SETUP.md](../SETUP.md) first. Configure these two values in the
root `.env` without showing them in chat:

- `OPENROUTER_API_KEY=<your key>`
- `OPENROUTER_MODEL=<exact model slug from openrouter.ai/models>`

Then run from `minicoder/step02`:

```bash
.venv/bin/python --version
.venv/bin/python -c "from pathlib import Path; from dotenv import dotenv_values; c=dotenv_values(Path('..')/'.env'); assert c.get('OPENROUTER_API_KEY'), 'OPENROUTER_API_KEY is blank'; assert c.get('OPENROUTER_MODEL'), 'OPENROUTER_MODEL is blank'; print('OpenRouter configuration present')"
```

On Windows, replace `.venv/bin/python` with `.venv\Scripts\python.exe`.
This check reports only whether values exist; it must never print them. Stop if
either check fails.

## Testing

Deterministic unit tests (fake LLM, no live model call):

```bash
.venv/bin/python -m pytest -q test_agent.py
```

## Required job and evidence

Get a key at https://openrouter.ai/keys and an exact supported model slug at
https://openrouter.ai/models. Run the live script and save its complete stdout:

```bash
.venv/bin/python agent.py > llm_output.txt
```

The script prints the question and the model's answer.

On macOS or Linux, if your sandbox shell injects proxy variables, run with
proxies unset:

```bash
env -u ALL_PROXY -u all_proxy -u HTTPS_PROXY -u https_proxy -u HTTP_PROXY -u http_proxy .venv/bin/python agent.py > llm_output.txt
```

Open `llm_output.txt` and confirm that it contains `UNDERSTAND`, the question,
`OBSERVE`, and a non-empty cloud-model response. Do not invent or manually
edit the response.

Completion means:

- the deterministic tests passed;
- the live OpenRouter call succeeded; and
- `step02/llm_output.txt` contains the captured output.

Report those checks, the configured model slug (never the key), and quote the
model response from the saved file.

Reflection: what changes for the model (and for you as the developer) when the
question is embedded directly in the prompt instead of being fetched through a
proposed "read" action?
