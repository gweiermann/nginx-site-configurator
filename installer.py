"""Helpers for installing and uninstalling the nginx-cli binary."""

from __future__ import annotations

import importlib
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Iterable


INSTALL_DIR = Path.home() / ".local" / "bin"
INSTALL_PATH = INSTALL_DIR / "nginx-cli"
BASHRC_PATH = Path.home() / ".bashrc"

ALIAS_BLOCK_START = "# >>> nginx-cli alias (managed)"
ALIAS_BLOCK_END = "# <<< nginx-cli alias (managed)"
COMPLETION_BLOCK_START = "# >>> nginx-cli completion (managed)"
COMPLETION_BLOCK_END = "# <<< nginx-cli completion (managed)"


def _load_bashrc_lines() -> list[str]:
    if not BASHRC_PATH.exists():
        return []
    return BASHRC_PATH.read_text(encoding="utf-8").splitlines(keepends=True)


def _write_bashrc_lines(lines: Iterable[str]) -> None:
    BASHRC_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASHRC_PATH.write_text("".join(lines), encoding="utf-8")


def _remove_block(lines: list[str], start_marker: str, end_marker: str) -> list[str]:
    updated: list[str] = []
    skip = False
    for line in lines:
        stripped = line.rstrip("\n")
        if not skip and stripped == start_marker:
            skip = True
            continue
        if skip and stripped == end_marker:
            skip = False
            continue
        if skip:
            continue
        updated.append(line)
    return updated


def _append_block(lines: list[str], block_lines: Iterable[str]) -> list[str]:
    if lines and not lines[-1].endswith("\n"):
        lines[-1] = lines[-1] + "\n"
    if lines and lines[-1] != "\n":
        lines.append("\n")
    for line in block_lines:
        lines.append(line if line.endswith("\n") else f"{line}\n")
    if not lines[-1].endswith("\n"):
        lines[-1] = lines[-1] + "\n"
    return lines


def _ensure_argcomplete_available() -> bool:
    try:
        importlib.import_module("argcomplete")
        return True
    except ModuleNotFoundError:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--user", "argcomplete"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("warning: argcomplete not available; tab completion will be disabled.", file=sys.stderr)
            return False

        importlib.invalidate_caches()
        try:
            importlib.import_module("argcomplete")
            return True
        except ModuleNotFoundError:
            print("warning: argcomplete installation failed; tab completion will be disabled.", file=sys.stderr)
            return False


def _generate_completion_block() -> list[str]:
    return [
        COMPLETION_BLOCK_START,
        "if command -v register-python-argcomplete >/dev/null 2>&1; then",
        "    eval \"$(register-python-argcomplete nginx-cli)\"",
        "elif command -v python3 >/dev/null 2>&1; then",
        "    eval \"$(python3 -m argcomplete nginx-cli 2>/dev/null)\"",
        "fi",
        COMPLETION_BLOCK_END,
    ]


def _ensure_executable(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def install_cli(source: Path) -> None:
    if not source.exists():
        raise SystemExit("Unable to locate nginx-cli executable for installation.")

    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, INSTALL_PATH)
    _ensure_executable(INSTALL_PATH)

    lines = _load_bashrc_lines()
    lines = _remove_block(lines, ALIAS_BLOCK_START, ALIAS_BLOCK_END)
    alias_block = [
        ALIAS_BLOCK_START,
        "alias nginx-cli='$HOME/.local/bin/nginx-cli'",
        ALIAS_BLOCK_END,
    ]
    lines = _append_block(lines, alias_block)

    argcomplete_available = _ensure_argcomplete_available()
    lines = _remove_block(lines, COMPLETION_BLOCK_START, COMPLETION_BLOCK_END)
    if argcomplete_available:
        lines = _append_block(lines, _generate_completion_block())

    _write_bashrc_lines(lines)
    print("nginx-cli installed. Restart your shell or run 'source ~/.bashrc'.")


def uninstall_cli(current: Path | None = None) -> None:
    lines = _load_bashrc_lines()
    lines = _remove_block(lines, ALIAS_BLOCK_START, ALIAS_BLOCK_END)
    lines = _remove_block(lines, COMPLETION_BLOCK_START, COMPLETION_BLOCK_END)
    _write_bashrc_lines(lines)

    if INSTALL_PATH.exists():
        try:
            INSTALL_PATH.unlink()
        except PermissionError:
            pass

    if current:
        resolved = current.resolve()
        if resolved.exists() and resolved != INSTALL_PATH:
            try:
                resolved.unlink()
            except PermissionError:
                pass

    print("nginx-cli successfully uninstalled.")


