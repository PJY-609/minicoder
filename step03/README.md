# 03 — Build a Verify-and-Revise Coding Agent

## Copilot job

Give GitHub Copilot this instruction:

> Follow `step03/README.md`, complete the required job, and report the result
> plus the LLM/environment interaction history saved in
> `step03/interaction_history.jsonl`.

Copilot must run the existing agent rather than solve `task.py` itself. It must
not create `solution.py` by hand, weaken tests, reveal the API key, or claim
success without a passing verification. If a required command fails, it must
stop and report the command and sanitized error.

This final exercise uses **HumanEval/20**, `find_closest_elements`. The task is
moderately challenging: a correct implementation must compare the whole list,
handle duplicate values, and return its result in sorted order.

The teaching materials were extracted from the Hugging Face dataset with:

```python
from datasets import load_dataset

dataset = load_dataset("openai/openai_humaneval")
problem = dataset["test"][20]
print(problem["prompt"])
print(problem["test"])
print(problem["entry_point"])
```

The resulting artifacts are deliberately separate:

- `task.py` contains the HumanEval prompt and required function signature.
- `tests.py` contains the dataset's test assertions, adapted only to import
  `find_closest_elements` from the generated `solution.py` file.
- `agent.py` supplies the iterative coding-agent loop.

## Agent Loop

```text
Read task.py
      ↓
Generate implementation
      ↓
verify(code) saves solution.py
      ↓
Run tests.py
      ↓
Observe failures
      ↓
Revise implementation
      ↓
Repeat until all tests pass
```

The model sends one JSON action per turn. `verify(code)` is the key final
action: it saves the complete proposed `solution.py`, runs `tests.py` in a
subprocess, and returns stdout, stderr, and the exit code to the next model
turn. The model may make at most four verification attempts and cannot finish
until the test result passes.

This step always uses a cloud model (e.g. DeepSeek) through OpenRouter — the
same backend as step02 — since the agent loop needs a stronger model than a
tiny local one to reliably converge on a passing solution.

## Prerequisite check

Complete [../SETUP.md](../SETUP.md) and the OpenRouter configuration described
in step02. Then run from `minicoder/step03`:

```bash
.venv/bin/python --version
.venv/bin/python -c "from pathlib import Path; from dotenv import dotenv_values; c=dotenv_values(Path('..')/'.env'); assert c.get('OPENROUTER_API_KEY'), 'OPENROUTER_API_KEY is blank'; assert c.get('OPENROUTER_MODEL'), 'OPENROUTER_MODEL is blank'; print('OpenRouter configuration present')"
```

On Windows, replace `.venv/bin/python` with `.venv\Scripts\python.exe`.
The configuration check must never print either value. Stop if a check fails.

## Testing

Run the deterministic agent tests first (fake LLM, no live model call):

```bash
.venv/bin/python -m pytest -q test_agent.py
```

## Required job and evidence

Run the live agent and save its console output. The agent automatically
replaces `interaction_history.jsonl` with a fresh structured transcript:

```bash
.venv/bin/python agent.py > run_output.txt
```

On macOS or Linux, if your sandbox shell injects proxy variables, run with
proxies unset:

```bash
env -u ALL_PROXY -u all_proxy -u HTTPS_PROXY -u https_proxy -u HTTP_PROXY -u http_proxy .venv/bin/python agent.py > run_output.txt
```

Inspect, but do not edit, these generated files:

- `run_output.txt`: human-readable actions and observations;
- `interaction_history.jsonl`: one JSON record per model/environment event;
- `solution.py`: code proposed by the model through `verify(code)`.

Confirm that the last transcript record has `status` equal to `passed`, then
run `.venv/bin/python tests.py` once independently. If the agent ends with
`failed`, `model_error`, or `budget_exhausted`, report that status and the last
sanitized observation; do not repair the solution manually.

Completion means:

- the deterministic agent tests passed;
- the live agent finished with transcript status `passed`;
- the independent `tests.py` run passed; and
- all three evidence files exist.

Report the model slug, final status, verification-attempt count, final test
output, and a concise round-by-round summary from the transcript. Never report
the API key.
