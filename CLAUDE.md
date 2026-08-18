# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status: pre-implementation

This repository currently contains **no application code** — only a Spec-Kit (Spec-Driven Development, "speckit") scaffold and a single project brief. There is no `specs/` directory yet, no `src/`, no README, no package manifest, and no test suite. Do not assume any build/lint/test commands exist until they've actually been created as part of implementing a feature — check before claiming a command works.

## Project brief

The full brief is `Cover.md` (written in Bulgarian). Summary of what is to be built:

- A web application for printing product/company labels from layouts ("макети").
- Users create layouts with label data, select and edit a layout, save it, and preview the print result. A formula computes the number of labels.
- Labels print in **A4 format, 2 columns × 4 blocks per page**.
- Layouts must also be exportable/importable as **JSON files**.
- Layouts must be searchable/filterable by their parameters, and searched results must be printable.
- Stated tech stack: **Python/Django** for backend, **Django templates** for frontend, **SQLite** for storage — but accessed via **Prisma ORM** (note: Prisma is a Node/TypeScript ORM, not natively compatible with Django's ORM-centric design; this is what the brief literally asks for, so treat it as a requirement to clarify/confirm during planning rather than silently resolve one way or the other).
- The brief also asks to initialize a new GitHub repo (`Cover_app`), use a modular client/server folder split, write Jest/Vitest tests for the main API endpoints (again implying a JS-based test/runtime layer alongside Django), run the app locally to verify it works, and write a README with setup/run instructions.
- Before building, the brief asks to confirm label/template parameters with the user rather than guessing them.

Because of the Django-vs-Prisma/Jest tension above, the first real planning pass (`/speckit-specify` or `/speckit-clarify`) should surface this as a clarification rather than assume an answer.

## Workflow: this is a Spec-Kit project

Development here follows Spec-Kit's SDD cycle: **constitution → specify → clarify → plan → tasks → analyze → implement**, driven by the skills under `.claude/skills/speckit-*` (invoked as `/speckit-specify`, `/speckit-plan`, etc.). Typical order:

1. `speckit-constitution` — establish/update project principles in `.specify/memory/constitution.md`. **Ratified as v1.0.0 on 2026-08-18.** Five principles: confirm print/layout parameters before building rather than guessing them, SQLite is the durable source of truth (JSON is export/import only, not primary storage), print output is fixed at A4/2 columns×4 blocks per page unless the constitution is amended, every API endpoint touching layouts/labels/print needs passing tests before it's done, and client/server code stays structurally separated. It deliberately leaves the Django-vs-Prisma/Jest tech-stack conflict (see above) unresolved — that's flagged as a TODO to settle in the first `/speckit-plan`'s Technical Context, not in the constitution.
2. `speckit-specify` — turn a feature description into `specs/<NNN-short-name>/spec.md` (business-facing, no implementation details), plus a `checklists/requirements.md` quality gate. Feature numbering is `sequential` per `.specify/init-options.json`.
3. `speckit-clarify` — resolve `[NEEDS CLARIFICATION]` markers in a spec via targeted Q&A.
4. `speckit-plan` — produce the technical plan/design artifacts for a spec'd feature.
5. `speckit-tasks` — turn a plan into a dependency-ordered `tasks.md`.
6. `speckit-analyze` — cross-check spec.md/plan.md/tasks.md for consistency (non-destructive).
7. `speckit-checklist` — generate custom review checklists on demand.
8. `speckit-implement` — execute `tasks.md`.
9. `speckit-converge` — diff the actual codebase against spec/plan/tasks and append any unbuilt work as new tasks.
10. `speckit-taskstoissues` — export tasks as GitHub issues.

Key mechanics to know before touching this scaffold:

- **Feature context is stateful**, not just branch-based: the active feature directory is read from `.specify/feature.json` (`feature_directory` key), optionally overridden by the `SPECIFY_FEATURE_DIRECTORY` env var. Downstream commands (`plan`, `tasks`, `implement`, ...) resolve paths through this, not by inferring from the git branch.
- **PowerShell is the scripting backend** for this integration (`.specify/init-options.json` → `"script": "ps"`): helper logic lives in `.specify/scripts/powershell/` (`common.ps1`, `check-prerequisites.ps1`, `create-new-feature.ps1`, `setup-plan.ps1`, `setup-tasks.ps1`). There are no bash equivalents installed.
- **Templates are resolved through a layered override stack**, not read directly: project overrides (`.specify/templates/overrides/`) → installed presets (`.specify/presets/`) → extensions (`.specify/extensions/`) → core templates (`.specify/templates/`). None of the override/preset/extension layers exist yet in this repo, so core templates in `.specify/templates/` are what's currently active.
- Repo root for spec-kit purposes is wherever `.specify/` lives (found by walking upward), not necessarily a git repo root — note there is **no `.git` in this project yet** ("Is a git repository: false"); initializing one is part of the brief's setup instructions, not yet done.

## Secrets

`.env` holds `ANTHROPIC_API_KEY`. Never print its value or commit it; there is no `.gitignore` yet, so once a git repo is initialized here, `.env` must be excluded explicitly.
