# Development

## Set up

```bash
uv sync                      # Python 3.12+ environment with dev and docs tools
uv run pre-commit install    # commit, push and commit-message hooks
```

## Quality gates

Every gate is a hook in `.pre-commit-config.yaml`. CI runs the same hooks, so
passing locally means passing in CI.

| Gate | Tool | Runs on |
|---|---|---|
| File hygiene, JSON/TOML/YAML syntax, large files | pre-commit-hooks | commit |
| `uv.lock` matches `pyproject.toml` | `uv lock --check` | commit |
| Lint, including docstrings on public API (numpy style) | ruff | commit |
| Formatting | ruff format | commit |
| Types: strict in `src/`, standard elsewhere | basedpyright | commit |
| Cognitive complexity at most 15 per function | complexipy | commit |
| Core logic never imports its interfaces | import-linter | commit |
| Workflow security | zizmor | commit |
| No AI co-author trailers | `scripts/check_no_ai_coauthors.py` | commit message |
| Tests with 90% branch coverage | pytest, coverage | push |
| Docs build without a warning | sphinx-build `-W -n` | push |

Run everything at once:

```bash
uv run pre-commit run --all-files
uv run pre-commit run --all-files --hook-stage pre-push
```

CI also tests every supported Python version and audits dependencies for known
vulnerabilities with pip-audit, weekly as well as on every change.

## Documentation

Docs are Markdown (MyST) under `docs/`, with the API reference generated from
docstrings.

```bash
uv run sphinx-build -W -n -b html docs docs/_build/html
```

## Dependencies

Dependabot proposes grouped weekly updates for Python packages and GitHub
Actions, skipping versions younger than a week. Actions are pinned by commit
hash; Dependabot updates the hash and the version comment together.

The one remote hook, pre-commit-hooks, is pinned the same way:

```bash
uv run pre-commit autoupdate --freeze
```

## Template updates

This project was generated from [lathe](https://github.com/EssenceSentry/lathe).
Pull later template improvements with:

```bash
uvx copier update --trust
```
