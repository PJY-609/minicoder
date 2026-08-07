"""Create and validate the three isolated workshop environments."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
STEPS = {
    "step01": ("dotenv", "ollama", "pytest"),
    "step02": ("dotenv", "httpx", "pytest"),
    "step03": ("dotenv", "httpx", "pytest"),
}


def environment_python(environment: Path) -> Path:
    if sys.platform == "win32":
        return environment / "Scripts" / "python.exe"
    return environment / "bin" / "python"


def run(command: list[str], *, cwd: Path) -> None:
    print(f"RUN ({cwd.name}): {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def main() -> None:
    if sys.version_info < (3, 10):
        raise SystemExit(
            f"STOP: Python 3.10 or newer is required; found {sys.version.split()[0]}"
        )

    print(f"Bootstrap Python: {sys.version.split()[0]}", flush=True)
    for step, imports in STEPS.items():
        step_dir = ROOT / step
        environment = step_dir / ".venv"
        requirements = step_dir / "requirements.txt"

        run([sys.executable, "-m", "venv", str(environment)], cwd=step_dir)
        python = environment_python(environment)
        run(
            [str(python), "-m", "pip", "install", "-r", str(requirements)],
            cwd=step_dir,
        )
        import_statement = "; ".join(f"import {name}" for name in imports)
        run(
            [
                str(python),
                "-c",
                f"{import_statement}; import sys; print(sys.version.split()[0])",
            ],
            cwd=step_dir,
        )
        print(f"{step}: READY", flush=True)

    print("SETUP OK", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"STOP: environment setup failed: {error}") from error
