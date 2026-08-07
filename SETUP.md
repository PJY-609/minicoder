# Minicoder setup

Give GitHub Copilot this instruction:

> Follow `SETUP.md`. Run `python3.12 setup.py` and report its result. Do not
> perform setup or repair commands yourself. Continue only if the program
> prints `SETUP COMPLETE`. If it prints `SETUP BLOCKED`, report the diagnostic
> and stop without opening an exercise.

On Windows, use `py -3.12 setup.py` instead. If neither command exists, install
Python 3.12 from https://www.python.org/downloads/ and retry. Python 3.11 is
also supported; Python 3.10 and 3.13 or newer are not workshop-tested.

## What the setup program does

`setup.py` is the only program that should configure this project. It works in
two phases.

First, it performs read-only preflight checks for:

- Python 3.11 or 3.12 with `venv` and `pip` support;
- at least 1 GB of free disk space;
- DNS and HTTPS access to PyPI;
- an installed and running Ollama service; and
- the local Ollama model `qwen3:0.6b`.

Only after every preflight passes does it:

1. create a temporary root environment named `.venv.tmp`;
2. install the pinned packages in `requirements.txt`;
3. verify all required imports;
4. run the deterministic tests for steps 01, 02, and 03;
5. rename the validated environment to `.venv`; and
6. copy `.env.example` to `.env` if `.env` does not already exist.

If environment creation, installation, imports, or tests fail, `.venv.tmp` is
removed automatically. A partial environment is never promoted to `.venv`.
An existing `.env` is never overwritten.

## Run setup

From the repository root:

```bash
python3.12 setup.py
```

The only successful final message is:

```text
SETUP COMPLETE: Python 3.12.x
```

If setup reports `SETUP BLOCKED`, follow its human-facing recommendation and
then run the same setup command again. Copilot must not improvise a workaround,
install machine-level software, change dependency versions, switch models, or
use a global Python environment.

Common blocked results include:

- `UNSUPPORTED_PYTHON`: install and explicitly run Python 3.12;
- `PYPI_UNREACHABLE`: check internet, DNS, VPN, proxy, or classroom firewall;
- `OLLAMA_NOT_INSTALLED`: install from https://ollama.com/download;
- `OLLAMA_UNAVAILABLE`: start the Ollama application or service;
- `OLLAMA_MODEL_MISSING`: run `ollama pull qwen3:0.6b` yourself, then retry;
- `BROKEN_ENVIRONMENT`: run `python3.12 setup.py --repair` after reviewing the
  report.

## Optional read-only diagnosis

To check prerequisites without creating files or installing packages:

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
terminal output. After `SETUP COMPLETE`, continue with
[step01/README.md](step01/README.md).
