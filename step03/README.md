# 09 - Final: Solve a HumanEval Task

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

## Virtual Environment Setup (required)

Create a dedicated virtual environment for this task in `minicoder/step03`.
Prefer one independent `.venv` per step folder so each task keeps its own
dependencies isolated.

Run from this folder: `minicoder/step03`.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Testing

Run the deterministic agent tests first (fake LLM, no live model call):

```bash
.venv/bin/python -m pytest -q test_agent.py
```

## Run The Milestone Script

Configure the OpenRouter backend in the shared `.env` file (created in step01,
located at `minicoder/.env`):

- `OPENROUTER_API_KEY=<your key>`
- `OPENROUTER_MODEL=<exact model slug from openrouter.ai/models>`

Then run the live agent from this directory:

```bash
.venv/bin/python agent.py
```

If your sandbox shell injects proxy variables, run with proxies unset:

```bash
env -u ALL_PROXY -u all_proxy -u HTTPS_PROXY -u https_proxy -u HTTP_PROXY -u http_proxy .venv/bin/python agent.py
```
