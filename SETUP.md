# Minicoder setup

Give GitHub Copilot this instruction:

> Set up this project by following `SETUP.md`. Use a supported Python interpreter
> and keep all work project-local. Diagnose failures and try safe recovery rather
> than stopping after the first failed command. Preserve the classroom invariants
> below. When `setup.py` confirms `SETUP COMPLETE`, report the setup result and
> stop. Do not open, inspect, or run step01 until the user explicitly asks you to
> begin step01. Ask for help only when the remaining setup action needs human or
> system access.

Use any available command that launches Python 3.11 or 3.12, such as
`python3.12`, `python3.11`, or Windows' `py -3.12`. Python 3.10 and 3.13 or
newer are not workshop-supported. If no supported interpreter is installed,
that is a human-action blocker.

## Classroom invariants

The setup method may adapt to the laptop, but the finished environment must be
the same for every learner:

- use only Python 3.11 or 3.12;
- keep the environment project-local at `.venv`;
- install the exact versions pinned in `requirements.txt`;
- use the required local Ollama model `qwen3:0.6b`;
- preserve an existing `.env` and never print or paste its secrets; and
- pass the required imports and deterministic tests for steps 01, 02, and 03.

Do not use global packages, change dependency versions, switch models, bypass
tests, or modify exercise code to make setup pass. Those constraints—not a
particular shell command—provide classroom consistency.

## What the setup program does

`setup.py` is the preferred transactional setup and the final acceptance check.
An agent may choose equivalent standard Python environment commands while
diagnosing or recovering, provided they preserve every classroom invariant.
It must finish by rerunning `setup.py`. When that program prints
`SETUP COMPLETE`, setup is finished: report the result and pause. Setup does
not authorize opening, inspecting, or running an exercise. Wait for an explicit
user request before accessing `step01/README.md` or doing any step01 work.

The setup program works in two phases.

First, it performs local preflight checks for:

- Python 3.11 or 3.12 with `venv` and `pip` support;
- at least 1 GB of free disk space;
- an installed and running Ollama service; and
- the local Ollama model `qwen3:0.6b`.

Only after every preflight passes does it:

1. create a temporary root environment named `.venv.tmp`;
2. install the pinned packages in `requirements.txt`;
3. verify all required imports;
4. run the deterministic tests for steps 01, 02, and 03;
5. rename the validated environment to `.venv`; and
6. copy `.env.example` to `.env` if `.env` does not already exist.

If an existing `.venv` is invalid, setup rebuilds it automatically. If
environment creation, installation, imports, or tests fail, `.venv.tmp` is
removed automatically and the previous `.venv` is preserved. A partial
environment is never promoted, and an existing `.env` is never overwritten.

Setup does not reject the network based on a separate connectivity probe.
When packages are needed, `pip` makes the authoritative attempt and reports
the actual index, certificate, proxy, or connectivity error. This also lets an
already-valid environment work while offline.

## Run setup

From the repository root:

```bash
python3.12 setup.py  # or another supported Python 3.11/3.12 launcher
```

The only successful final message is:

```text
SETUP COMPLETE: Python 3.12.x
```

The agent should inspect complete command output, make safe project-local
corrections, and retry when appropriate. It may choose how to create or repair
`.venv`; no particular repair command is required. Running `setup.py` again is
normally enough because it rebuilds invalid environments transactionally.

Stop and request human action only when the remaining fix is outside the
project—for example installing Python or Ollama, starting a desktop service,
changing VPN/proxy/firewall settings, downloading a missing Ollama model, or
entering an API key. Report the exact diagnostic and do not open an exercise.

Common blocked results include:

- `UNSUPPORTED_PYTHON`: install and explicitly run Python 3.12;
- `OLLAMA_NOT_INSTALLED`: install from https://ollama.com/download;
- `OLLAMA_UNAVAILABLE`: start the Ollama application or service;
- `OLLAMA_MODEL_MISSING`: run `ollama pull qwen3:0.6b` yourself, then retry;
- `ENVIRONMENT_BUILD_FAILED`: inspect the preceding `pip`, import, or test
  output; retry transient failures, otherwise report the exact failing command.

## Optional read-only diagnosis

To check prerequisites, including direct PyPI connectivity, without creating
files or installing packages:

```bash
python3.12 setup.py --check
```

## Secrets

The generated root `.env` already contains the local Ollama defaults. Leave
them unchanged for step01. Before step02, enter your own OpenRouter key and
model slug directly in `.env`:

```dotenv
OPENROUTER_API_KEY=
OPENROUTER_MODEL=
```

Never paste `.env` contents or an API key into Copilot, chat, source code, or
terminal output. After `SETUP COMPLETE`, report success and stop. When the user
later explicitly asks to begin step01, follow
[step01/README.md](step01/README.md).
