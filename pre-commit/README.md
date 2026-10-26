# mdolab pre-commit hooks

Repackaged pre-commit hooks that run pinned tools against mdolab's shared
configs, so every consuming repo lints and formats identically without
relying on globally installed tools or PATH ordering.

## Using the hooks

Add to a consuming repo's `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/mdolab/.github
    rev: <tag-or-sha>   # pin to a released tag or commit
    hooks:
      - id: mdolab-ruff-check
      - id: mdolab-ruff-format
      - id: mdolab-isort
      - id: mdolab-pylint
      - id: mdolab-clang-format
      - id: mdolab-fprettify
```

Pick only the hooks you need. Then:

```bash
pre-commit install
pre-commit run --all-files
```

Each hook installs its own pinned tool into an isolated environment, see [.pre-commit-hooks.yaml](../.pre-commit-hooks.yaml).

## Local config overrides

By default each hook uses the bundled shared config in [_config/](_config/).
A consuming repo can override by placing its own config at the repo root:

| Hook                  | Local override file | Behavior                                         |
| --------------------- | ------------------- | ------------------------------------------------ |
| `mdolab-ruff-check`   | `./ruff.toml`       | layered onto the shared base via ruff's `extend` |
| `mdolab-ruff-format`  | `./ruff.toml`       | same as above                                    |
| `mdolab-isort`        | `./.isort.cfg`      | used instead of the shared config                |
| `mdolab-pylint`       | `./.pylintrc`       | used instead of the shared config                |
| `mdolab-clang-format` | `./.clang-format`   | used instead of the shared config                |
| `mdolab-fprettify`    | `./.fprettify.rc`   | used instead of the shared config                |

Ruff is special: a local `./ruff.toml` is *merged on top of* the shared base.
The other tools take the local file as-is.

## Internals

- [cli.py](cli.py) - the console-script entry points. Each runs the pinned tool
  from pre-commit's isolated environment with the local or bundled config,
  against the files pre-commit passes as argv.
- [_config/](_config/) - the shared configs, shipped as package data.
