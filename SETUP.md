# Minicoder setup

Give GitHub Copilot this instruction:

> Follow `SETUP.md` exactly. Run every check in order. If any command fails,
> stop immediately and report the command and its complete error. Do not
> substitute tools, skip checks, edit source code, or continue to an exercise.

Run this setup once from the repository root before opening
`step01/README.md`. A successful setup ends with three usable virtual
environments and a working local Ollama model.

## 1. Validate Python and build all environments

Python 3.10 or newer is required. First check it:

```bash
python3 --version
```

Then run the repository's cross-platform bootstrap program:

```bash
python3 bootstrap.py
```

On Windows, use `py -3 bootstrap.py` if `python3` is not available.

The bootstrap program creates `step01/.venv`, `step02/.venv`, and
`step03/.venv`, installs each step's `requirements.txt`, and verifies that
each environment can import its dependencies. A final `SETUP OK` means the
laptop can support the Python portion of the workshop.

If Python is missing, is older than 3.10, cannot create a virtual environment,
cannot install a dependency, or cannot pass an import check, **stop**. Report
the failing step and full error. Do not use a global environment, merge the
three environments, change package requirements, or proceed to Ollama.

## 2. Check Ollama is installed

```bash
command -v ollama
```

On Windows, run `where ollama` instead.

- If this prints a path → continue.
- If this prints nothing / "command not found" → **stop here**. Install
  Ollama from https://ollama.com/download, then re-run this command. Do not
  continue to any other setup step (do not edit `.env` or open step01) until
  `ollama` is found. The environments already created by step 1 may remain.

Confirm the Ollama service responds:

```bash
ollama list
```

If this errors with a connection failure, start the Ollama app (or run
`ollama serve` in a separate terminal) and retry before continuing.

## 3. Check the `qwen3:0.6b` model is available

```bash
ollama list | grep qwen3:0.6b
```

On Windows PowerShell, run `ollama list | Select-String 'qwen3:0.6b'`.

- If it's listed → continue to step 4.
- If it's not listed, pull it:

  ```bash
  ollama pull qwen3:0.6b
  ```

`qwen3:0.6b` is a small model (a few hundred MB) and should fit on nearly any
laptop. **If the pull fails** (no disk space, no network, or another device
constraint) → **stop here**. Do not substitute a different model, do not
change `OLLAMA_MODEL` in `.env`, and do not continue to step01. Report the
exact error instead.

> **Strict rule:** perform the Ollama checks exactly once, before step01. Never
> repeat, skip silently, or work around them — a missing Ollama install or a
> failed model pull is a hard stop, not something to route around.

## 4. Create the shared `.env` file

Run from the repository root (`minicoder/`):

```bash
cp .env.example .env
```

On Windows PowerShell, run `Copy-Item .env.example .env`.

This single `.env` file governs all three steps — do not create per-step
`.env` files.

- Leave the `OLLAMA_*` values as-is; they already match step01
  (`OLLAMA_HOST=http://localhost:11434`, `OLLAMA_MODEL=qwen3:0.6b`).
- Leave `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` blank for now — you'll
  set those when you reach step02 (create a key at
  https://openrouter.ai/keys and copy the exact model slug from
  https://openrouter.ai/models).

Never commit `.env` or paste its contents into chat.

## 5. Confirm setup is complete

Confirm all of these are true:

- `bootstrap.py` ended with `SETUP OK`.
- `ollama list` succeeded and lists `qwen3:0.6b`.
- The repository root contains `.env`; its OpenRouter values may remain blank
  until step02.

Report `SETUP COMPLETE` and the three Python versions shown by
`bootstrap.py`. Do not include `.env` contents or any API key in the report.

Now open [step01/README.md](step01/README.md).
