### Contributing to PythonNative

Thanks for your interest in contributing. This repository contains the PythonNative library, CLI, templates, a demo app, and a Django site used for docs/demo hosting and E2E. Contributions should keep the code reliable, cross‑platform, and easy to use.

## Quick start

Development uses Python ≥ 3.9.

```bash
# create and activate a venv (recommended)
python3 -m venv .venv && source .venv/bin/activate

# install root tooling (lint/format/test)
pip install -r requirements.txt

# install library (editable) and CLI
pip install -e libs/pythonnative

# run tests
pytest -q

# format and lint
black libs apps tests || true
ruff check .
```

Common library and CLI entry points:

```bash
# CLI help
pn --help

# create a new sample app (template fetch is remote)
pn init my_app

# run a local demo app skeleton
cd apps/pythonnative_demo && pn run android
```

## Project layout (high‑level)

- `libs/pythonnative/` – installable library and CLI
  - `pythonnative/` – core cross‑platform UI components and utilities
  - `cli/` – `pn` command
  - `tests/` – unit tests for the library
- `libs/templates/` – Android/iOS project templates and zips
- `apps/` – application projects
  - `django_pythonnative/` – Django project for docs/demo hosting and E2E
  - `experiments/` – platform experiments (Android/iOS/Briefcase)
  - `pythonnative_demo/` – minimal demo app using the library
- `README.md`, `requirements.txt` – repo docs and dev tooling

## Coding guidelines

- Style: Black; lint: Ruff; typing where useful. Keep APIs stable.
- Prefer explicit, descriptive names; keep platform abstractions clean.
- Add/extend tests under `libs/pythonnative/tests/` for new behavior.
- Do not commit generated artifacts or large binaries; templates live under `libs/templates/`.

Common commands:

```bash
pytest -q                     # run tests
ruff check .                  # lint
black libs apps               # format
```

## Conventional Commits

This project uses Conventional Commits. Use the form:

```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

### Commit message character set

- Encoding: UTF‑8 is allowed and preferred across subjects and bodies.
- Keep the subject ≤ 72 chars; avoid emoji.

Accepted types (standard):

- `build` – build system or external dependencies (e.g., requirements, packaging)
- `chore` – maintenance (no library behavior change)
- `ci` – continuous integration configuration (workflows, pipelines)
- `docs` – documentation only
- `feat` – user‑facing feature or capability
- `fix` – bug fix
- `perf` – performance improvements
- `refactor` – code change that neither fixes a bug nor adds a feature
- `revert` – revert of a previous commit
- `style` – formatting/whitespace (no code behavior)
- `test` – add/adjust tests only

Recommended scopes (match the smallest accurate directory/module):

- Library/CLI scopes:
  - `cli` – `libs/pythonnative/cli/` (the `pn` command)
  - `core` – `libs/pythonnative/pythonnative/` package internals
  - `components` – UI view modules under `libs/pythonnative/pythonnative/` (e.g., `button.py`, `label.py`)
  - `utils` – utilities like `utils.py`
  - `tests` – `libs/pythonnative/tests/`

- Templates and examples:
  - `templates` – `libs/templates/` (Android/iOS templates, zips)
  - `demo` – `apps/pythonnative_demo/`
  - `experiments` – `apps/experiments/`

- Django app and site:
  - `django` – `apps/django_pythonnative/` (site, docs pages, E2E harness)

- Repo‑level and ops:
  - `deps` – dependency updates and version pins
  - `docker` – containerization files (e.g., `Dockerfile`)
  - `repo` – top‑level files (`README.md`, `CONTRIBUTING.md`, `.gitignore`, licenses)
  - `workflows` – CI pipelines (e.g., `.github/workflows/`)

Note: Avoid redundant type==scope pairs (e.g., `docs(docs)`). Prefer a module scope (e.g., `docs(core)`) or `docs(repo)` for top‑level updates.

Examples:

```text
build(deps): refresh pinned versions
chore(repo): add contributing guidelines
ci(workflows): add publish job
docs(core): clarify ListView data contract
feat(components): add MaterialSearchBar
fix(cli): handle missing Android SDK gracefully
perf(core): reduce allocations in list diffing
refactor(utils): extract path helpers
test(tests): cover ios template copy flow
```

Examples (no scope):

```text
build: update packaging metadata
chore: update .gitignore patterns
docs: add project overview
```

Breaking changes:

- Use `!` after the type/scope or a `BREAKING CHANGE:` footer.

```text
feat(core)!: rename Page.set_root_view to set_root

BREAKING CHANGE: API renamed; update app code and templates.
```

### Multiple scopes (optional)

- Comma‑separate scopes without spaces: `type(scope1,scope2): ...`
- Prefer a single scope when possible; use multiple only when the change genuinely spans tightly related areas.

Example:

```text
feat(templates,cli): add ios template and wire pn init
```

## Pull requests and squash merges

- PR title: use Conventional Commit format.
  - Example: `feat(cli): add init subcommand`
  - Imperative mood; no trailing period; ≤ 72 chars; `!` for breaking changes.
- PR description: include brief sections: What, Why, How (brief), Testing, Risks/Impact, Docs/Follow‑ups.
  - Link issues with keywords (e.g., `Closes #123`).
- Merging: prefer “Squash and merge” with “Pull request title and description”.
- Keep PRs focused; avoid unrelated changes in the same PR.

Recommended PR template:

```text
What
- Short summary of the change

Why
- Motivation/user value

How (brief)
- Key implementation notes or decisions

Testing
- Local/CI coverage; links to tests if relevant

Risks/Impact
- Compat, rollout, perf, security; mitigations

Docs/Follow-ups
- Docs updated or TODO next steps

Closes #123
BREAKING CHANGE: <details if any>
Co-authored-by: Name <email>
```

## Pull request checklist

- Tests: added/updated; `pytest` passes.
- Lint/format: `ruff check .`, `black` pass.
- Docs: update `README.md` and any Django docs pages if behavior changes.
- Templates: update `libs/templates/` if generator output changes.
- No generated artifacts committed.

## Versioning and releases

- The library version is tracked in `libs/pythonnative/setup.py`. Use SemVer.
- Workflow:
  - Contributors: branch off `main` (or `dev` if used) and open PRs.
  - Maintainer (release): bump version, tag, and publish to PyPI.
  - Tag on `main`: `git tag -a vX.Y.Z -m "Release vX.Y.Z" && git push --tags`.

### Branch naming (suggested)

- Use lowercase kebab‑case; concise (≤ 40 chars).
- Prefix conventions:
  - `feature/<scope>-<short-desc>`
  - `fix/<issue-or-bug>-<short-desc>`
  - `chore/<short-desc>`
  - `docs/<short-desc>`
  - `ci/<short-desc>`
  - `refactor/<scope>-<short-desc>`
  - `test/<short-desc>`
  - `perf/<short-desc>`
  - `build/<short-desc>`
  - `release/vX.Y.Z`
  - `hotfix/<short-desc>`

Examples:

```text
feature/cli-init
fix/core-threading-deadlock-123
docs/contributing
ci/publish-pypi
build/lock-versions
refactor/utils-paths
test/templates-android
release/v0.2.0
hotfix/cli-regression
```

## Security and provenance

- Avoid bundling secrets or credentials in templates or code.
- Prefer runtime configuration via environment variables for Django and CI.

## License

By contributing, you agree that your contributions are licensed under the repository’s MIT License.
