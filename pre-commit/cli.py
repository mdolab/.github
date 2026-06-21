"""Console-script entry points for mdolab's repackaged pre-commit hooks.

Each entry point:
  1. locates its bundled config, shipped as package data (importlib.resources),
  2. locates the pinned tool installed in the SAME isolated environment that pre-commit built
  3. execs the tool against the files pre-commit passes as argv.

Nothing here relies on a globally installed tool or on PATH ordering.
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
    resource = files("_config").joinpath(name)
    with as_file(resource) as path:
        yield str(path)


def _tool(name: str) -> str:
    """Absolute path to a pinned tool installed beside this interpreter.

    pre-commit's venv puts the interpreter and the tool console scripts in the
    same bin/ directory, so resolving relative to sys.executable is exact and
    PATH-independent. Falls back to PATH only as a courtesy.
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


def _argv_files() -> list[str]:
    return sys.argv[1:]


# --------------------------------------------------------------------------- #
# ruff: shared base config, optionally extended by a local ./ruff.toml
# --------------------------------------------------------------------------- #


def _resolve_ruff_config(global_cfg: str) -> tuple[str, bool]:
    """Return (config_path, is_temp).

    - No local ./ruff.toml          -> use the shared base directly.
    - Local ./ruff.toml present     -> synthesize a temp config:
          extend = '<base>'
          <local overrides>
      so the shared base is inherited and the local file layers on top. Ruff
      does not merge configs implicitly; `extend` is the supported mechanism,
      and an absolute path sidesteps the unknown pre-commit cache location.
    - Local file already declares its own top-level `extend` -> respect it.
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
            # --force-exclude: pre-commit always passes an explicit file list,
            # and ruff checks explicitly-named files even when they match the
            # config's exclude/extend-exclude unless this flag is set. Without
            # it, a consuming repo's excludes are silently ignored on commit.
            rc = _run("ruff", [subcommand, *extra, "--force-exclude", "--config", cfg, *_argv_files()])
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
    # Prefer the consuming repo's own .isort.cfg when present (matching the CI
    # style job); otherwise impose the shared bundled config.
    # --filter-files: isort's skip / skip_glob only apply during directory
    # recursion; pre-commit passes an explicit file list, so without this flag
    # skipped files (e.g. __init__.py) would still be sorted. Mirrors ruff's
    # --force-exclude.
    local = os.path.join(os.getcwd(), ".isort.cfg")  # pre-commit cwd == repo root
    if os.path.isfile(local):
        sys.exit(_run("isort", ["--settings-path", local, "--filter-files", *_argv_files()]))
    with _config(".isort.cfg") as cfg:
        sys.exit(_run("isort", ["--settings-path", cfg, "--filter-files", *_argv_files()]))


def pylint() -> None:
    with _config(".pylintrc") as cfg:
        sys.exit(_run("pylint", ["--rcfile", cfg, *_argv_files()]))


def clang_format() -> None:
    # clang-format < 14 has no `--style=file:<path>`; it only discovers a file
    # literally named `.clang-format` by walking up from each input file. We pin
    # clang-format to match the CI version (10.x), so mirror the CI script:
    #   - prefer the consuming repo's own .clang-format when present, otherwise
    #   - stage the bundled shared config at the repo root for the run and remove
    #     it afterward.
    # pre-commit's cwd is the repo root, an ancestor of every file it passes, so
    # a .clang-format there is always discovered.
    staged = os.path.join(os.getcwd(), ".clang-format")  # pre-commit cwd == repo root
    if os.path.isfile(staged):
        sys.exit(_run("clang-format", ["-style=file", "-i", *_argv_files()]))
    with _config(".clang-format") as cfg:
        shutil.copyfile(cfg, staged)
        try:
            rc = _run("clang-format", ["-style=file", "-i", *_argv_files()])
        finally:
            with contextlib.suppress(FileNotFoundError):
                os.unlink(staged)
    sys.exit(rc)


def fprettify() -> None:
    # Prefer the consuming repo's own .fprettify.rc when present (matching the CI
    # script); otherwise impose the shared bundled config.
    local = os.path.join(os.getcwd(), ".fprettify.rc")  # pre-commit cwd == repo root
    if os.path.isfile(local):
        sys.exit(_run("fprettify", ["-c", local, *_argv_files()]))
    with _config(".fprettify.rc") as cfg:
        sys.exit(_run("fprettify", ["-c", cfg, *_argv_files()]))
