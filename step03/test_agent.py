import json
from pathlib import Path

import pytest

from agent import ScriptedLLM, execute_action, initial_state, run_agent, run_tests


def copy_materials(destination: Path) -> None:
    source = Path(__file__).parent
    for name in ("task.py", "tests.py"):
        (destination / name).write_text((source / name).read_text(encoding="utf-8"), encoding="utf-8")


def working_solution() -> str:
    return """from typing import List, Tuple


def find_closest_elements(numbers: List[float]) -> Tuple[float, float]:
    ordered = sorted(numbers)
    return min(zip(ordered, ordered[1:]), key=lambda pair: pair[1] - pair[0])
"""


def test_extracted_humaneval_suite_accepts_a_correct_solution(tmp_path):
    copy_materials(tmp_path)
    (tmp_path / "solution.py").write_text(working_solution(), encoding="utf-8")
    assert "exit_code: 0" in run_tests(tmp_path)


def test_verify_returns_failure_then_allows_a_revision(tmp_path):
    copy_materials(tmp_path)
    wrong = "def find_closest_elements(numbers):\n    return (numbers[0], numbers[1])\n"
    llm = ScriptedLLM([
        json.dumps({"action": "read_file", "path": "task.py"}),
        json.dumps({"action": "plan", "steps": ["Read the task", "Implement it", "Verify it"]}),
        json.dumps({"action": "verify", "code": wrong}),
        json.dumps({"action": "verify", "code": working_solution()}),
        json.dumps({"action": "finish", "summary": "all checks pass"}),
    ])
    state = run_agent("Solve task.py", llm, tmp_path)
    assert state["status"] == "passed"
    assert state["attempts"] == 2
    assert any("Tests failed" in message["content"] for message in llm.seen_messages[3])


def test_finish_requires_a_passing_verification(tmp_path):
    state = initial_state("solve task")
    with pytest.raises(ValueError, match="tests must pass"):
        execute_action({"action": "finish"}, tmp_path, state)