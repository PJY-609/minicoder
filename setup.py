"""Transactional setup for the Minicoder student workshop."""

import argparse
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parent
ENVIRONMENT = ROOT / ".venv"
TEMP_ENVIRONMENT = ROOT / ".venv.tmp"
BACKUP_ENVIRONMENT = ROOT / ".venv.backup"
REQUIREMENTS = ROOT / "requirements.txt"
ENV_EXAMPLE = ROOT / ".env.example"
ENV_FILE = ROOT / ".env"
MODEL = "qwen3:0.6b"
MIN_FREE_BYTES = 1_000_000_000
IMPORTS = ("dotenv", "httpx", "ollama", "pytest")
TESTS = (
    (ROOT / "step01", "test_agent.py"),
    (ROOT / "step02", "test_agent.py"),
    (ROOT / "step03", "test_agent.py"),
)


class SetupBlocked(RuntimeError):
    """A diagnosed condition that prevents safe setup."""

    def __init__(self, code: str, detail: str, actions: list[str]):
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.actions = actions


def environment_python(environment: Path) -> Path:
    if sys.platform == "win32":
        return environment / "Scripts" / "python.exe"
    return environment / "bin" / "python"


def run(command: list[str], *, cwd: Path = ROOT, timeout: int | None = None) -> None:
    print(f"RUN: {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=cwd, check=True, timeout=timeout)


def check_python() -> None:
    if not (sys.version_info >= (3, 11) and sys.version_info < (3, 13)):
        raise SetupBlocked(
            "UNSUPPORTED_PYTHON",
            f"Python 3.11 or 3.12 is required; found {sys.version.split()[0]}.",
            [
                "Install Python 3.12 from https://www.python.org/downloads/.",
                "Run this file with that interpreter, for example: python3.12 setup.py.",
            ],
        )
    try:
        import ensurepip  # noqa: F401
        import venv  # noqa: F401
    except ImportError as error:
        raise SetupBlocked(
            "VENV_UNAVAILABLE",
            f"This Python installation cannot create virtual environments: {error}",
            ["Install a complete Python 3.11 or 3.12 distribution, then retry."],
        ) from error


def check_disk_space() -> None:
    free = shutil.disk_usage(ROOT).free
    if free < MIN_FREE_BYTES:
        raise SetupBlocked(
            "INSUFFICIENT_DISK_SPACE",
            f"At least 1 GB free is required; found {free / 1_000_000_000:.2f} GB.",
            ["Free at least 1 GB on this drive, then retry."],
        )


def check_pypi() -> None:
    try:
        socket.getaddrinfo("pypi.org", 443)
        request = urllib.request.Request(
            "https://pypi.org/simple/", headers={"User-Agent": "minicoder-setup/1"}
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status != 200:
                raise OSError(f"HTTP status {response.status}")
    except (OSError, urllib.error.URLError) as error:
        raise SetupBlocked(
            "PYPI_UNREACHABLE",
            f"Could not reach https://pypi.org: {error}",
            [
                "Check the laptop's internet, DNS, VPN, and proxy settings.",
                "Confirm https://pypi.org opens in a browser.",
                "Ask the instructor whether the classroom network blocks PyPI.",
            ],
        ) from error


def check_ollama() -> None:
    executable = shutil.which("ollama")
    if executable is None:
        raise SetupBlocked(
            "OLLAMA_NOT_INSTALLED",
            "The ollama command was not found.",
            ["Install Ollama from https://ollama.com/download, start it, and retry."],
        )
    try:
        result = subprocess.run(
            [executable, "list"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        raise SetupBlocked(
            "OLLAMA_UNAVAILABLE",
            f"`ollama list` did not succeed: {error}",
            ["Start the Ollama application or service, then retry."],
        ) from error
    installed = {line.split()[0] for line in result.stdout.splitlines()[1:] if line.split()}
    if MODEL not in installed:
        raise SetupBlocked(
            "OLLAMA_MODEL_MISSING",
            f"Ollama is running, but {MODEL} is not installed.",
            [f"Run `ollama pull {MODEL}` in a terminal, then retry setup."],
        )


def preflight() -> None:
    print("PREFLIGHT: Python", flush=True)
    check_python()
    print("PREFLIGHT: disk space", flush=True)
    check_disk_space()
    print("PREFLIGHT: PyPI connectivity", flush=True)
    check_pypi()
    print("PREFLIGHT: Ollama", flush=True)
    check_ollama()
    print("PREFLIGHT OK", flush=True)


def validate_environment(python: Path) -> None:
    imports = "; ".join(f"import {name}" for name in IMPORTS)
    run([str(python), "-c", imports])
    for directory, test_file in TESTS:
        run([str(python), "-m", "pytest", "-q", test_file], cwd=directory)


def existing_environment_is_valid() -> bool:
    python = environment_python(ENVIRONMENT)
    if not python.is_file():
        return False
    try:
        validate_environment(python)
    except (OSError, subprocess.CalledProcessError):
        return False
    return True


def build_environment() -> None:
    run([sys.executable, "-m", "venv", str(TEMP_ENVIRONMENT)])
    python = environment_python(TEMP_ENVIRONMENT)
    run([str(python), "-m", "pip", "install", "-r", str(REQUIREMENTS)])
    validate_environment(python)


def create_env_file() -> None:
    if ENV_FILE.exists():
        print("KEEP: existing .env", flush=True)
        return
    shutil.copyfile(ENV_EXAMPLE, ENV_FILE)
    print("CREATE: .env from .env.example", flush=True)


def install(*, repair: bool) -> None:
    preflight()
    if ENVIRONMENT.exists():
        if existing_environment_is_valid():
            print("ENVIRONMENT OK: existing .venv", flush=True)
            create_env_file()
            print(f"SETUP COMPLETE: Python {sys.version.split()[0]}", flush=True)
            return
        if not repair:
            raise SetupBlocked(
                "BROKEN_ENVIRONMENT",
                "The existing .venv did not pass validation.",
                ["Run setup again with `python setup.py --repair`."],
            )

    if TEMP_ENVIRONMENT.exists():
        shutil.rmtree(TEMP_ENVIRONMENT)
    if BACKUP_ENVIRONMENT.exists():
        if ENVIRONMENT.exists():
            shutil.rmtree(BACKUP_ENVIRONMENT)
        else:
            BACKUP_ENVIRONMENT.replace(ENVIRONMENT)
    try:
        build_environment()
        if repair and ENVIRONMENT.exists():
            ENVIRONMENT.replace(BACKUP_ENVIRONMENT)
        try:
            TEMP_ENVIRONMENT.replace(ENVIRONMENT)
        except OSError:
            if BACKUP_ENVIRONMENT.exists() and not ENVIRONMENT.exists():
                BACKUP_ENVIRONMENT.replace(ENVIRONMENT)
            raise
        if BACKUP_ENVIRONMENT.exists():
            shutil.rmtree(BACKUP_ENVIRONMENT)
    except Exception:
        if TEMP_ENVIRONMENT.exists():
            shutil.rmtree(TEMP_ENVIRONMENT)
        raise

    create_env_file()
    print(f"SETUP COMPLETE: Python {sys.version.split()[0]}", flush=True)


def print_blocked(error: SetupBlocked) -> None:
    print(f"SETUP BLOCKED: {error.code}")
    print(error.detail)
    print("No new project environment was installed.")
    print("Try:")
    for number, action in enumerate(error.actions, 1):
        print(f"{number}. {action}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="run read-only prerequisite checks only"
    )
    parser.add_argument(
        "--repair", action="store_true", help="replace an existing invalid .venv"
    )
    args = parser.parse_args()
    try:
        if args.check:
            preflight()
            print(f"CHECK COMPLETE: Python {sys.version.split()[0]}")
        else:
            install(repair=args.repair)
    except SetupBlocked as error:
        print_blocked(error)
        return 1
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        if TEMP_ENVIRONMENT.exists():
            shutil.rmtree(TEMP_ENVIRONMENT)
        if BACKUP_ENVIRONMENT.exists() and not ENVIRONMENT.exists():
            BACKUP_ENVIRONMENT.replace(ENVIRONMENT)
        print_blocked(
            SetupBlocked(
                "ENVIRONMENT_BUILD_FAILED",
                f"A setup command failed: {error}",
                ["Review the complete command output above, correct the issue, and retry."],
            )
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
