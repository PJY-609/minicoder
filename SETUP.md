# Minicoder setup

Follow this once, in order, before opening `step01/README.md`. Steps 1–2
(Ollama) only need to succeed one time — step02 and step03 never use Ollama.

## 1. Check Ollama is installed

```bash
command -v ollama
```

- If this prints a path → continue to step 2.
- If this prints nothing / "command not found" → **stop here**. Install
  Ollama from https://ollama.com/download, then re-run this command. Do not
  continue to any other setup step (do not create venvs, do not edit `.env`,
  do not open step01) until `ollama` is found.

Confirm the Ollama service responds:

```bash
ollama list
```

If this errors with a connection failure, start the Ollama app (or run
`ollama serve` in a separate terminal) and retry before continuing.

## 2. Check the `qwen3:0.6b` model is available

```bash
ollama list | grep qwen3:0.6b
```

- If it's listed → skip to [3. Create the shared `.env` file](#3-create-the-shared-env-file).
- If it's not listed, pull it:

  ```bash
  ollama pull qwen3:0.6b
  ```

`qwen3:0.6b` is a small model (a few hundred MB) and should fit on nearly any
laptop. **If the pull fails** (no disk space, no network, or another device
constraint) → **stop here**. Do not substitute a different model, do not
change `OLLAMA_MODEL` in `.env`, and do not continue to step01. Report the
exact error instead.

> **Strict rule:** perform steps 1–2 exactly once, before step01. Never
> repeat, skip silently, or work around them — a missing Ollama install or a
> failed model pull is a hard stop, not something to route around.

## 3. Create the shared `.env` file

Run from the repository root (`minicoder/`):

```bash
cp .env.example .env
```

This single `.env` file governs all three steps — do not create per-step
`.env` files.

- Leave the `OLLAMA_*` values as-is; they already match step01
  (`OLLAMA_HOST=http://localhost:11434`, `OLLAMA_MODEL=qwen3:0.6b`).
- Leave `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` blank for now — you'll
  set those when you reach step02 (create a key at
  https://openrouter.ai/keys and copy the exact model slug from
  https://openrouter.ai/models).

Never commit `.env` or paste its contents into chat.

## 4. Set up each step's virtual environment

Each step (`step01`, `step02`, `step03`) keeps its own independent `.venv`.
Follow the "Virtual Environment Setup" section in that step's own README —
do not share one `.venv` across steps.

Now open [step01/README.md](step01/README.md).
