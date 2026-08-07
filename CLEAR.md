# Clear generated workshop artifacts

Give GitHub Copilot this instruction:

> Follow `CLEAR.md`. Preview the cleanup, report the exact targets, then run
> it and confirm the repository is clean. Do not delete source files or use
> `git clean`, `git reset`, or broad recursive shell commands.

Run from the `minicoder` repository root. First preview the exact allowlisted
targets:

```bash
python3 clear.py --dry-run
```

On Windows, use `py -3 clear.py --dry-run`. Review the list before continuing.
The cleaner may remove only:

- the root `.env` secret file;
- the root `.venv`, any incomplete `.venv.tmp` or `.venv.backup`, and legacy
  step-local environments from older workshop versions;
- Python and pytest caches;
- `step01/llm_output.txt` and `step02/llm_output.txt`;
- `step03/run_output.txt`, `interaction_history.jsonl`, and generated
  `solution.py`.

If the preview names anything else, stop and report it. Otherwise run:

```bash
python3 clear.py
```

Then verify:

```bash
git status --short
```

Expected result: `CLEAR COMPLETE`, followed by no Git status output. Cleanup
does not uninstall Ollama or remove the downloaded model. To repeat the
workshop after cleanup, begin again with [SETUP.md](SETUP.md).
