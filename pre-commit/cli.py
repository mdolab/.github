"""Console-script entry points for mdolab's pre-commit hooks.

Each entry point runs a pinned tool from the hook's isolated environment with the shared config bundled in
_config/, or with the consuming repo's own config when one exists at the repo root.
"""

import contextlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from importlib.resources import as_file, files


@contextlib.contextmanager
def _config(name: str):
    """Yield a real filesystem path to a bundled config file."""
    resource = files("mdolab_precommit._config").joinpath(name)
    with as_file(resource) as path:
        yield str(path)


def _tool(name: str) -> str:
    """Absolute path to a tool, preferring the one installed beside this interpreter in the hook environment.

    Falls back to PATH if the tool is not found there.
    """
    bindir = os.path.dirname(sys.executable)
    for candidate in (os.path.join(bindir, name), os.path.join(bindir, name + ".exe")):
        if os.path.isfile(candidate):
            return candidate
    found = shutil.which(name)
    if found:
        return found
    sys.exit(f"mdolab-pre-commit: pinned tool '{name}' missing from the hook environment")


def _run(tool: str, args: list[str]) -> int:
    return subprocess.call([_tool(tool), *args])


def _hook_args() -> list[str]:
    """Arguments from pre-commit: any `args:` set by the consuming repo, followed by the file list."""
    return sys.argv[1:]


def _run_with_local_config(tool: str, config_name: str, flag: str, *extra: str) -> None:
    """Run `tool` with the repo-root `config_name` if present, else the shared one, passed via `flag`.

    `extra` args are inserted after the config and before the hook args.
    """
    local = os.path.join(os.getcwd(), config_name)  # pre-commit cwd == repo root
    if os.path.isfile(local):
        sys.exit(_run(tool, [flag, local, *extra, *_hook_args()]))
    with _config(config_name) as cfg:
        sys.exit(_run(tool, [flag, cfg, *extra, *_hook_args()]))


def _resolve_ruff_config(global_cfg: str) -> tuple[str, bool]:
    """Return (config_path, is_temp) for ruff.

    With no local ruff.toml, the shared config is used. A local ruff.toml is layered on top of the shared one by
    writing a temporary copy with `extend = '<shared path>'` prepended. A local file that already sets its own
    `extend` is used as-is.
    """
    local = os.path.join(os.getcwd(), "ruff.toml")  # pre-commit cwd == repo root
    if not os.path.isfile(local):
        return global_cfg, False

    with open(local, encoding="utf-8") as fh:
        local_text = fh.read()

    if re.search(r"(?m)^\s*extend\s*=", local_text):
        return local, False

    fd, tmp = tempfile.mkstemp(prefix="mdolab-ruff.", suffix=".toml")
    with os.fdopen(fd, "w", encoding="utf-8") as out:
        # single-quoted TOML literal string => no escaping, safe on Windows paths
        out.write(f"extend = '{global_cfg}'\n")
        out.write(local_text)
    return tmp, True


def _ruff(subcommand: str, *extra: str) -> None:
    with _config("ruff.toml") as global_cfg:
        cfg, is_temp = _resolve_ruff_config(global_cfg)
        try:
            # --force-exclude: apply exclude/extend-exclude to the explicit file list pre-commit passes
            rc = _run("ruff", [subcommand, *extra, "--force-exclude", "--config", cfg, *_hook_args()])
        finally:
            if is_temp:
                with contextlib.suppress(FileNotFoundError):
                    os.unlink(cfg)
    sys.exit(rc)


def ruff_check() -> None:
    _ruff("check", "--fix", "--exit-non-zero-on-fix")


def ruff_format() -> None:
    _ruff("format")


def isort() -> None:
    # --filter-files: apply skip/skip_glob to the explicit file list pre-commit passes
    _run_with_local_config("isort", ".isort.cfg", "--settings-path", "--filter-files")


def pylint() -> None:
    _run_with_local_config("pylint", ".pylintrc", "--rcfile")


def clang_format() -> None:
    # clang-format < 14 has no `--style=file:<path>` and only finds a `.clang-format` above each input file, so
    # the shared config is temporarily copied to the repo root unless the repo has its own.
    staged = os.path.join(os.getcwd(), ".clang-format")  # pre-commit cwd == repo root
    if os.path.isfile(staged):
        sys.exit(_run("clang-format", ["-style=file", "-i", *_hook_args()]))
    with _config(".clang-format") as cfg:
        shutil.copyfile(cfg, staged)
        try:
            rc = _run("clang-format", ["-style=file", "-i", *_hook_args()])
        finally:
            with contextlib.suppress(FileNotFoundError):
                os.unlink(staged)
    sys.exit(rc)


def fprettify() -> None:
    _run_with_local_config("fprettify", ".fprettify.rc", "-c")
