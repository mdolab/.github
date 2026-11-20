"""Console-script entry points for mdolab's pre-commit hooks.

Each entry point runs a pinned tool from the hook's isolated environment (first on PATH under pre-commit) with the
shared config bundled in _config/, or with the consuming repo's own config when one exists at the repo root.
pre-commit runs hooks from the repo root and passes any `args:` followed by the file list as argv.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from importlib.resources import files


def _config(name: str) -> str:
    """Path to a bundled shared config file."""
    return str(files("mdolab_precommit._config") / name)


def _run(tool: str, *args: str) -> None:
    sys.exit(subprocess.call([tool, *args, *sys.argv[1:]]))


def _run_with_config(tool: str, config_name: str, flag: str, *extra: str) -> None:
    """Run `tool` with the repo-root `config_name` if present, else the shared one, passed via `flag`."""
    config = config_name if os.path.isfile(config_name) else _config(config_name)
    _run(tool, flag, config, *extra)


def _ruff_config(tmpdir: str) -> str:
    """Path to the ruff config: the shared one, or a local ruff.toml layered on top of it via `extend`.

    A local ruff.toml that already sets its own `extend` is used as-is.
    """
    if not os.path.isfile("ruff.toml"):
        return _config("ruff.toml")
    with open("ruff.toml", encoding="utf-8") as fh:
        local = fh.read()
    if re.search(r"(?m)^\s*extend\s*=", local):
        return "ruff.toml"
    merged = os.path.join(tmpdir, "ruff.toml")
    with open(merged, "w", encoding="utf-8") as fh:
        # single-quoted TOML literal string, so Windows paths need no escaping
        fh.write(f"extend = '{_config('ruff.toml')}'\n{local}")
    return merged


def _ruff(subcommand: str, *extra: str) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        # --force-exclude: apply exclude/extend-exclude to the explicit file list pre-commit passes
        _run("ruff", subcommand, *extra, "--force-exclude", "--config", _ruff_config(tmpdir))


def ruff_check() -> None:
    _ruff("check", "--fix", "--exit-non-zero-on-fix")


def ruff_format() -> None:
    _ruff("format")


def isort() -> None:
    # --filter-files: apply skip/skip_glob to the explicit file list pre-commit passes
    _run_with_config("isort", ".isort.cfg", "--settings-path", "--filter-files")


def pylint() -> None:
    _run_with_config("pylint", ".pylintrc", "--rcfile")


def clang_format() -> None:
    # clang-format < 14 has no `--style=file:<path>` and only finds a `.clang-format` above each input file, so
    # the shared config is temporarily copied to the repo root unless the repo has its own.
    staged = not os.path.isfile(".clang-format")
    if staged:
        shutil.copyfile(_config(".clang-format"), ".clang-format")
    try:
        _run("clang-format", "-style=file", "-i")
    finally:
        if staged:
            os.remove(".clang-format")


def fprettify() -> None:
    _run_with_config("fprettify", ".fprettify.rc", "-c")
