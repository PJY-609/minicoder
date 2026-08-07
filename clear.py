"""Remove only generated Minicoder workshop artifacts."""

import argparse
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent
EXACT_TARGETS = [
    ROOT / ".env",
    ROOT / ".venv",
    ROOT / ".venv.tmp",
    ROOT / ".venv.backup",
    ROOT / ".pytest_cache",
    # Remove legacy per-step environments created by older workshop versions.
    ROOT / "step01" / ".venv",
    ROOT / "step01" / "llm_output.txt",
    ROOT / "step02" / ".venv",
    ROOT / "step02" / "llm_output.txt",
    ROOT / "step03" / ".venv",
    ROOT / "step03" / "run_output.txt",
    ROOT / "step03" / "interaction_history.jsonl",
    ROOT / "step03" / "solution.py",
]
CACHE_NAMES = {"__pycache__", ".pytest_cache"}


def targets() -> list[Path]:
    found = {path for path in EXACT_TARGETS if path.exists() or path.is_symlink()}
    covered_directories = {path for path in found if path.is_dir()}
    for path in ROOT.rglob("*"):
        if any(path.is_relative_to(parent) for parent in covered_directories):
            continue
        if path.is_dir() and path.name in CACHE_NAMES:
            found.add(path)
    return sorted(found, key=lambda path: (len(path.parts), str(path)), reverse=True)


def remove(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true", help="list targets without removing them"
    )
    args = parser.parse_args()
    selected = targets()

    if not selected:
        print("Nothing to clear.")
        return

    for path in selected:
        relative = path.relative_to(ROOT)
        print(f"{'WOULD REMOVE' if args.dry_run else 'REMOVE'}: {relative}")
        if not args.dry_run:
            remove(path)

    print("Dry run complete; nothing removed." if args.dry_run else "CLEAR COMPLETE")


if __name__ == "__main__":
    main()
