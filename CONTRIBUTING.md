# Contributing

Thanks for considering a contribution. This project is small and opinionated — read this guide before filing a large PR.

## What lives where

```
SKILL.md           # Skill definition — the main file Claude Code loads
references/        # Template frontmatter/format for raw, article, archive, index, presets
tools/             # Python helpers (search, graph, dashboard, watcher)
hooks/             # Shell hook templates
tests/             # Pytest unit + integration tests
docs/superpowers/  # Plans and specs for historical milestones
examples/          # Sample wikis
```

Two kinds of changes are common:

1. **Skill-level changes** (most PRs): edit `SKILL.md` or a file in `references/`. These do not require running Python; they require coherence with the rest of the skill.
2. **Tool changes**: edit a file under `tools/` and its matching test in `tests/`.

## Setup

```bash
git clone <fork>
cd second-brain
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

Run the tests:

```bash
.venv/bin/python -m pytest
```

## Style

- **Markdown**: standard commonmark. Semicolon-separated lists where the template says so; do not invent new delimiters.
- **Python**: PEP 8, type-hinted, no print-debugging in committed code. JSON on stdout for any tool the skill will parse.
- **Commits**: conventional prefixes — `feat:`, `fix:`, `docs:`, `refactor:`, `test:`. One feature per commit; no "misc cleanup" commits.
- **Filenames in markdown**: use kebab-case. Slugs max 60 chars.

## Adding a new template

1. Put the template file in `references/`.
2. Document its frontmatter fields under a `## Field rules` section.
3. Reference it from `SKILL.md` at the point it's used (don't copy the format into SKILL.md).

## Adding a new tool

1. Create `tools/<name>.py`. Expose `main(argv: list[str] | None = None) -> int`.
2. All user-visible output is JSON on stdout. Progress chatter goes to stderr.
3. Add an entry to `[project.scripts]` in `pyproject.toml` so `pip install -e .` exposes a CLI.
4. Add a test in `tests/test_<name>.py`. Prefer subprocess-style tests that invoke `python -m tools.<name>` against the `sample_wiki` fixture in `tests/conftest.py`.
5. Reference the tool from `SKILL.md` where it should be called.

## Changing the schema

Schema changes require a migration path.

1. Bump the `Current schema version` in the Migration section of `SKILL.md` (patch / minor / major — see the bump policy in that section).
2. Document the migration steps (what fields are added, renamed, removed).
3. Update `references/*.md` templates.
4. Add a note to the README's FAQ if the change is user-visible.

## Running the sample wiki

```bash
cd examples/ml-wiki
.venv/bin/python -m tools.search index --wiki wiki --no-embeddings
.venv/bin/python -m tools.graph build --wiki wiki
```

If those commands succeed, your change hasn't broken the basic flow.

## Submitting a PR

- Keep the diff small. Split unrelated changes into separate PRs.
- Every skill-level change should include an updated test or sample where appropriate.
- Link to the plan in `docs/superpowers/plans/` if your PR implements a milestone step.
- Describe the behavior change in the PR body. "Why" matters more than "what".
