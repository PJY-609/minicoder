"""Final milestone: an agent loops until the selected HumanEval tests pass."""

import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Optional

from dotenv import load_dotenv
import httpx

load_dotenv()
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "")
MAX_ACTIONS = int(os.getenv("MAX_ACTIONS", "16"))
MAX_VERIFICATIONS = 4
MAX_FILE_CHARS = 20_000
MAX_OBSERVATION_CHARS = 4_000
TEST_TIMEOUT = 10
EXCLUDED_PARTS = {".git", ".env", "__pycache__", ".pytest_cache"}

SYSTEM_PROMPT = """Reply with exactly one JSON object and no markdown fences.
You are solving one HumanEval task. Work in this order:
1. read task.py
2. make a short visible plan
3. call verify(code) with the complete source code for solution.py
4. inspect test evidence and revise with another verify(code) when tests fail
5. finish only after a passing verification.

Available actions: list_files, search_text(query), read_file(path), plan(steps),
verify(code), finish(summary).
Examples:
{"action":"read_file","path":"task.py"}
{"action":"plan","steps":["Read the task","Implement the function","Verify it"]}
{"action":"verify","code":"from typing import List, Tuple\\n..."}
{"action":"finish","summary":"All tests pass."}
The verify action saves code as solution.py and runs tests.py. Return source code,
not an explanation, in the code field. Test failures are feedback for the next turn.
"""

TASK_PROMPT = "Solve the implementation task in task.py. Use verify(code) until tests.py passes."


class ScriptedLLM:
    def __init__(self, replies: list[str]):
        self.replies = iter(replies)
        self.seen_messages: list[list[dict[str, str]]] = []

    def ask(self, messages: list[dict[str, str]]) -> str:
        self.seen_messages.append([message.copy() for message in messages])
        return next(self.replies)


class OpenRouterLLM:
    """Calls a cloud model (e.g. DeepSeek) through OpenRouter's OpenAI-compatible API."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. Add it to your .env file."
            )
        if not OPENROUTER_MODEL:
            raise RuntimeError(
                "OPENROUTER_MODEL is not set. Set it to the exact model slug "
                "shown on https://openrouter.ai/models, e.g. a DeepSeek model id."
            )

    def ask(self, messages: list[dict[str, str]]) -> str:
        response = httpx.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={"model": OPENROUTER_MODEL, "messages": messages},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


def build_llm() -> Any:
    return OpenRouterLLM()


def parse_action(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        if start < 0:
            raise ValueError("reply must be a JSON object with an action") from None
        value, _ = json.JSONDecoder().raw_decode(cleaned[start:])
    if not isinstance(value, dict) or not isinstance(value.get("action"), str):
        raise ValueError("reply must be a JSON object with an action")
    return value


def safe_path(repo_root: Path, requested: str) -> Path:
    root = repo_root.resolve()
    candidate = Path(requested)
    if candidate.is_absolute():
        raise ValueError("absolute paths are not allowed")
    resolved = (root / candidate).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("path leaves the repository")
    if any(part in EXCLUDED_PARTS or part.startswith(".env") for part in resolved.relative_to(root).parts):
        raise ValueError("path is excluded")
    return resolved


def visible_files(repo_root: Path) -> list[Path]:
    root = repo_root.resolve()
    return [
        path for path in root.rglob("*")
        if path.is_file() and path.resolve().is_relative_to(root)
        and not any(part in EXCLUDED_PARTS or part.startswith(".env") for part in path.relative_to(root).parts)
    ]


def search_text(repo_root: Path, query: str) -> str:
    if not query:
        raise ValueError("query must be non-empty")
    root = repo_root.resolve()
    matches: list[str] = []
    for path in visible_files(root):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(lines, 1):
            if query in line:
                matches.append(f"{path.relative_to(root)}:{number}: {line.strip()}")
                if len(matches) == 20:
                    return "\n".join(matches)
    return "\n".join(matches) if matches else "no matches"


def run_tests(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            [sys.executable, "tests.py"],
            cwd=repo_root,
            shell=False,
            capture_output=True,
            text=True,
            timeout=TEST_TIMEOUT,
            check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
    except subprocess.TimeoutExpired:
        return f"tests timed out after {TEST_TIMEOUT} seconds"
    return f"exit_code: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"[:MAX_OBSERVATION_CHARS]


def record_verification(state: dict[str, Any], observation: str) -> None:
    state["attempts"] += 1
    state["last_test"] = observation
    state["tests_passed"] = observation.startswith("exit_code: 0")
    if not state["tests_passed"] and state["attempts"] >= MAX_VERIFICATIONS:
        state["status"] = "failed"


def execute_action(action: dict[str, Any], repo_root: Path, state: dict[str, Any]) -> tuple[str, bool]:
    name = action["action"]
    if name == "list_files":
        root = repo_root.resolve()
        return "\n".join(sorted(str(path.relative_to(root)) for path in visible_files(root))[:20]), False
    if name == "search_text":
        query = action.get("query")
        if not isinstance(query, str):
            raise ValueError("query must be a string")
        return search_text(repo_root, query), False
    if name == "read_file":
        return safe_path(repo_root, action.get("path", "")).read_text(encoding="utf-8")[:MAX_FILE_CHARS], False
    if name == "plan":
        steps = action.get("steps")
        if not isinstance(steps, list) or not 1 <= len(steps) <= 5 or not all(isinstance(step, str) and step.strip() for step in steps):
            raise ValueError("plan needs 1-5 non-empty steps")
        state["plan"] = steps
        return "\n".join(steps), False
    if name == "verify":
        if not state.get("plan"):
            raise ValueError("make a visible plan before verification")
        if state["attempts"] >= MAX_VERIFICATIONS:
            raise ValueError("verification budget exhausted")
        code = action.get("code")
        if not isinstance(code, str) or not code.strip() or len(code) > MAX_FILE_CHARS:
            raise ValueError("code must be a non-empty, reasonably sized string")
        (repo_root / "solution.py").write_text(code, encoding="utf-8")
        observation = run_tests(repo_root)
        record_verification(state, observation)
        return observation, False
    if name == "finish":
        if not state.get("tests_passed"):
            raise ValueError("tests must pass before finish")
        return str(action.get("summary", "finished")), True
    raise ValueError(f"unknown action: {name}")


def initial_state(task: str) -> dict[str, Any]:
    return {"task": task, "plan": [], "attempts": 0, "last_test": None, "tests_passed": False, "status": "running"}


def record_interaction(path: Optional[Path], record: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as transcript:
        transcript.write(json.dumps(record) + "\n")


def run_agent(task: str, llm: Any, repo_root: Path, transcript_path: Optional[Path] = None) -> dict[str, Any]:
    state = initial_state(task)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": task}]
    print("UNDERSTAND", task)
    record_interaction(transcript_path, {"event": "start", "task": task, "max_actions": MAX_ACTIONS})
    for round_number in range(1, MAX_ACTIONS + 1):
        try:
            raw = llm.ask(messages)
        except Exception as error:
            state["status"] = "model_error"
            observation = f"model error: {error}"
            print(f"ROUND {round_number} MODEL ERROR", observation)
            record_interaction(transcript_path, {
                "event": "model_error",
                "round": round_number,
                "observation": observation,
                "state": state,
            })
            return state
        try:
            action = parse_action(raw)
            observation, finished = execute_action(action, repo_root, state)
        except (ValueError, OSError) as error:
            action = {"action": "invalid"}
            observation, finished = f"action error: {error}", False
        print(f"ROUND {round_number} ACT", action["action"])
        print("VERIFY" if action["action"] == "verify" else "OBSERVE", observation[:MAX_OBSERVATION_CHARS])
        record_interaction(transcript_path, {
            "event": "round",
            "round": round_number,
            "model_reply": raw,
            "action": action,
            "observation": observation,
            "state": state.copy(),
        })
        if finished:
            state["status"] = "passed"
            record_interaction(transcript_path, {"event": "finish", "state": state})
            return state
        if state["status"] == "failed":
            record_interaction(transcript_path, {"event": "finish", "state": state})
            return state
        if action["action"] == "verify" and not state["tests_passed"]:
            observation = f"Tests failed. Inspect this evidence and revise solution.py with verify(code):\n{observation}"
        messages.extend([{"role": "assistant", "content": raw}, {"role": "user", "content": observation[:MAX_OBSERVATION_CHARS]}])
    state["status"] = "budget_exhausted"
    record_interaction(transcript_path, {"event": "finish", "state": state})
    return state


def main() -> None:
    transcript = os.getenv("TRANSCRIPT_PATH")
    run_agent(TASK_PROMPT, build_llm(), Path(__file__).parent, Path(transcript) if transcript else None)



if __name__ == "__main__":
    main()