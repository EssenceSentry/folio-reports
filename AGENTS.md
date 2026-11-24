# Folio Reports: notes for coding agents

Typeset decision briefs and research reports from Markdown.

## Layout

- `src/folio_reports/core.py` holds the logic, free of input and output.
- `src/folio_reports/cli.py` is a thin command line over `core`.
- `tests/` mirrors the modules; `docs/` is Sphinx with MyST Markdown.
- `scripts/` holds repository checks that run as hooks.

## Commands

```bash
uv sync                                                   # environment
uv run pytest                                             # tests with coverage
uv run pre-commit run --all-files                         # every commit gate
uv run pre-commit run --all-files --hook-stage pre-push   # tests and docs build
```

Run both pre-commit commands before saying a change is done; CI runs exactly
these hooks.

## Rules

- Keep every gate green, and never weaken one to get there: don't lower the
  coverage floor or the complexity limit, and don't add `# type: ignore`,
  `# noqa` or `pyright: ignore` without a comment saying why it is needed.
- Library code is type-checked in strict mode. Give every public function and
  class a numpy-style docstring; the docs build fails on a broken reference.
- Write a failing test first for new behavior or a bug fix.
- `core` must not import the command line or the service; import-linter
  enforces it.
- Add dependencies with `uv add` (runtime) or `uv add --group dev`, so
  `uv.lock` stays in step.
- Commit messages never credit an AI assistant as an author; a commit-msg hook
  rejects them. Stage explicit paths, never `git add -A` or `git add .`.
