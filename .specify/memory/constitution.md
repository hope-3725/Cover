<!--
Sync Impact Report
- Version change: [TEMPLATE] → 1.0.0 (initial ratification)
- Modified principles: n/a (first fill of template placeholders)
- Added sections:
  - Core Principles: I. Confirm Before Building, II. Durable Storage Is the
    Source of Truth, III. Print Output Fidelity, IV. Tested API Surface,
    V. Modular Client/Server Separation
  - Technology & Platform Constraints (was [SECTION_2_NAME])
  - Development Workflow (was [SECTION_3_NAME])
  - Governance
- Removed sections: none
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (Constitution Check gate is generic/dynamic — no edit needed)
  - ✅ .specify/templates/spec-template.md (no principle-specific references — no edit needed)
  - ✅ .specify/templates/tasks-template.md (no principle-specific references — no edit needed)
  - ✅ CLAUDE.md (already flags the stack ambiguity this constitution defers — no edit needed)
  - ⚠ .claude/skills/speckit-*/SKILL.md — no agent-specific stale references found; none require edits
- Follow-up TODOs:
  - TODO(TECH_STACK_CONFLICT): Cover.md requests Django (Python) as the
    backend/frontend framework, Prisma ORM (Node/TypeScript-native, not a
    natural fit for Django) for data access, and Jest/Vitest (JS test
    runners) for API tests. This constitution intentionally does NOT resolve
    that conflict — it is a technical-approach decision, not a governance
    one. Resolve it during /speckit-clarify or /speckit-plan for the first
    feature, and record the resolution in that feature's plan.md Technical
    Context section.
-->

# Cover Constitution

## Core Principles

### I. Confirm Before Building

The system deals in physical print layouts (label templates, dimensions,
column/row counts, per-company parameters) where a wrong assumption is
expensive to discover after implementation — it means mis-registered labels
on physical media. Before implementing any label/template parameter,
calculation formula, or print layout that is not explicitly specified in a
feature's spec, the assumption MUST be surfaced to the user for confirmation
(via `[NEEDS CLARIFICATION]` in the spec, or a direct question) rather than
guessed. Reasonable defaults MAY be proposed, but MUST be stated as
assumptions and confirmed before implementation begins, not discovered
during review.

**Rationale**: The originating project brief explicitly asks to be
consulted on label/template parameters rather than have them invented. This
principle generalizes that instruction to all print-affecting parameters.

### II. Durable Storage Is the Source of Truth

All layouts ("макети"), label data, and their parameters MUST be persisted
to the project's relational database — nothing user-created may exist only
in browser/session state. Layouts MUST additionally be exportable to, and
importable from, standalone JSON files, but JSON files are a portability
format, not a replacement for the database as the system of record.

**Rationale**: Directly required by the project brief ("Устойчивост:
всички данни са запазени в базата данни"). Treating JSON export as the
primary store would make search/filter and multi-user durability unreliable.

### III. Print Output Fidelity

Label sheets MUST render as A4 pages laid out in exactly 2 columns × 4
blocks per page (8 labels per sheet) unless a future spec explicitly amends
this layout. Any feature that changes label count, page size, or column/row
geometry MUST update this principle via a constitution amendment first — it
MUST NOT be changed silently inside a single feature's implementation.

**Rationale**: This is a fixed physical constraint from the brief, not a
UI preference; getting it wrong wastes printed media and defeats the
application's core purpose.

### IV. Tested API Surface

Every API endpoint that creates, edits, deletes, or computes over layouts,
labels, or print jobs MUST have automated unit and/or integration test
coverage before it is considered done. Tests MUST be run, and MUST pass,
before a feature implementing or changing an endpoint is marked complete.

**Rationale**: Directly required by the project brief ("Напишете
модулни/интеграционни тестове за крайните точки на основния API" and
"...се уверете, че тестовете са преминали успешно"). This principle states
the *requirement* (tested, passing endpoints); the specific test
runner/framework is a technical-context decision left to
`/speckit-plan` (see the TECH_STACK_CONFLICT TODO above).

### V. Modular Client/Server Separation

The codebase MUST maintain a clear structural separation between
server-side code (routing, business logic, data access, print/label
computation) and client-facing code (templates/views, static assets,
client-side interaction). Features MUST NOT blur this boundary by embedding
server logic in client code or vice versa, even when the chosen framework
would technically allow it.

**Rationale**: Directly required by the project brief ("Създайте модулна
структура от папки, разделяща клиента и сървъра").

## Technology & Platform Constraints

- Backend language/framework: Python with Django, per the project brief.
- Frontend: Django-rendered templates, per the project brief.
- Database: SQLite.
- Data-access layer, and the test runner for API tests, are NOT settled by
  this constitution — see the TECH_STACK_CONFLICT TODO in the Sync Impact
  Report above. The first `/speckit-plan` MUST record the resolved choice
  in its Technical Context section; that record then governs all
  subsequent features until amended here.
- Layout/label data MUST support JSON serialization for export/import
  (Principle II).
- Print output MUST target A4, 2 columns × 4 blocks per page (Principle
  III).

## Development Workflow

- Work proceeds through the Spec Kit SDD cycle: constitution → specify →
  clarify → plan → tasks → analyze → implement, using this repository's
  `speckit-*` skills.
- Source control: the project is developed in a Git repository (to be
  initialized, per the brief, as `Cover_app`); commits accompany logical
  units of work rather than being batched at the end of a feature.
- Before a feature is reported complete: run the application locally,
  exercise the feature's primary flows, and run its automated tests —
  matching the brief's explicit instruction to verify locally rather than
  assume correctness from code review alone.
- A README with install and local-run instructions MUST be kept current as
  setup steps change, per the project brief.

## Governance

This constitution supersedes any conflicting ad hoc practice. Amendments
are made via the `/speckit-constitution` command and MUST:

1. State the change and its rationale.
2. Bump `CONSTITUTION_VERSION` per semantic versioning: MAJOR for backward-
   incompatible principle removals/redefinitions, MINOR for new principles
   or materially expanded guidance, PATCH for clarifications/wording.
3. Update the Sync Impact Report and check dependent templates
   (`plan-template.md`, `spec-template.md`, `tasks-template.md`) and
   `CLAUDE.md` for now-stale references.

Every `/speckit-plan` invocation MUST pass its Constitution Check gate
against the principles above before proceeding to design, and re-check
after Phase 1 design. Any violation MUST be justified in that plan's
Complexity Tracking table or the simpler, compliant alternative MUST be
used instead. Use `CLAUDE.md` for day-to-day agent operating guidance;
this document governs *what must always be true*, not *how to run a given
command*.

**Version**: 1.0.0 | **Ratified**: 2026-08-18 | **Last Amended**: 2026-08-18
