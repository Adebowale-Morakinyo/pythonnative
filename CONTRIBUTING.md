### Contributing to PythonNative

Thanks for your interest in contributing. This repository contains the PythonNative library, CLI, templates, a demo app, and a Django site used for docs/demo hosting and E2E. Contributions should keep the code reliable, cross‑platform, and easy to use.

## Quick start

Development uses Python ≥ 3.9.

```bash
# create and activate a venv (recommended)
python3 -m venv .venv && source .venv/bin/activate

# install dev tools (lint/format/test)
pip install -e ".[dev]"

# install library (editable) and CLI
pip install -e .

# run tests
pytest -q

# format and lint
black src examples tests || true
ruff check .
```

Common library and CLI entry points:

```bash
# CLI help
pn --help

# create a new sample app (template fetch is remote)
pn init my_app

# run the Hello World example
cd examples/hello-world && pn run android
```

## Project layout (high‑level)

- `src/pythonnative/` – installable library and CLI
  - `pythonnative/` – core cross‑platform UI components and utilities
  - `cli/` – `pn` command
- `tests/` – unit tests for the library
- `templates/` – Android/iOS project templates and zips
- `examples/` – runnable example apps
  - `hello-world/` – minimal demo app using the library
- `README.md`, `pyproject.toml` – repo docs and packaging

## Coding guidelines

- Style: Black; lint: Ruff; typing where useful. Keep APIs stable.
- Prefer explicit, descriptive names; keep platform abstractions clean.
- Add/extend tests under `tests/` for new behavior.
- Do not commit generated artifacts or large binaries; templates live under `templates/`.

Common commands:

```bash
pytest -q                     # run tests
ruff check .                  # lint
black src examples tests      # format
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
  - `cli` – `src/pythonnative/cli/` (the `pn` command)
  - `core` – `src/pythonnative/pythonnative/` package internals
  - `components` – UI view modules under `src/pythonnative/pythonnative/` (e.g., `button.py`, `label.py`)
  - `utils` – utilities like `utils.py`
  - `tests` – `tests/`

- Templates and examples:
  - `templates` – `templates/` (Android/iOS templates, zips)
  - `examples` – `examples/` (e.g., `hello-world/`)

<!-- Django app and site removed: the old Django project has been retired -->

- Repo‑level and ops:
  - `deps` – dependency updates and version pins
  - `docker` – containerization files (e.g., `Dockerfile`)
  - `repo` – top‑level files (`README.md`, `CONTRIBUTING.md`, `.gitignore`, licenses)
  - `mkdocs` – documentation site (MkDocs/Material) configuration and content under `docs/`
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

Scope ordering (house style):

- Put the most impacted scope first (e.g., `repo`), then any secondary scopes.
- For extra consistency, alphabetize the remaining scopes after the primary.
- Keep it to 1–3 scopes max.

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

- PR title: Conventional Commits format (CI-enforced by `pr-lint.yml`).
- Tests: added/updated; `pytest` passes.
- Lint/format: `ruff check .`, `black` pass.
- Docs: update `README.md` if behavior changes.
- Templates: update `templates/` if generator output changes.
- No generated artifacts committed.

## Versioning and releases

- The version is tracked in `pyproject.toml` (`project.version`) and mirrored in `src/pythonnative/__init__.py` as `__version__`. Both files are updated automatically by [python-semantic-release](https://python-semantic-release.readthedocs.io/).
- **Automated release pipeline** (on every merge to `main`):
  1. `python-semantic-release` scans Conventional Commit messages since the last tag.
  2. It determines the next SemVer bump: `feat` → **minor**, `fix`/`perf` → **patch**, `BREAKING CHANGE` → **major** (minor while version < 1.0).
  3. Version files are updated, `CHANGELOG.md` is generated, and a tagged release commit (`chore(release): vX.Y.Z`) is pushed.
  4. A GitHub Release is created with auto-generated release notes and the built sdist/wheel attached.
  5. When drafts are disabled, the package is also published to PyPI via Trusted Publishing.
- **Draft / published toggle**: the `DRAFT_RELEASE` variable at the top of `.github/workflows/release.yml` controls release mode. Set to `"true"` (the default) for draft GitHub Releases with PyPI publishing skipped; flip to `"false"` to publish releases and upload to PyPI immediately.
- Commit types that trigger a release: `feat` (minor), `fix` and `perf` (patch), `BREAKING CHANGE` (major). All other types (`build`, `chore`, `ci`, `docs`, `refactor`, `revert`, `style`, `test`) are recorded in the changelog but do **not** trigger a release on their own.
- Tag format: `v`-prefixed (e.g., `v0.4.0`).
- Manual version bumps are no longer needed — just merge PRs with valid Conventional Commit titles. For ad-hoc runs, use the workflow's **Run workflow** button (`workflow_dispatch`).

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

### CI

- **CI** (`ci.yml`): runs formatter, linter, type checker, and tests on every push and PR.
- **PR Lint** (`pr-lint.yml`): validates the PR title against Conventional Commits format (protects squash merges) and checks individual commit messages via commitlint (protects rebase merges). Recommended: add the **PR title** job as a required status check in branch-protection settings.
- **Release** (`release.yml`): runs on merge to `main`; computes version, generates changelog, tags, creates GitHub Release, and (when `DRAFT_RELEASE` is `"false"`) publishes to PyPI.
- **Docs** (`docs.yml`): deploys documentation to GitHub Pages on push to `main`.

## Security and provenance

- Avoid bundling secrets or credentials in templates or code.
- Prefer runtime configuration via environment variables for Django and CI.

## License

By contributing, you agree that your contributions are licensed under the repository’s MIT License.
