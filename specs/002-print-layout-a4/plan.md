# Implementation Plan: Print Layout to A4

**Branch**: `002-print-layout-a4` | **Date**: 2026-08-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-print-layout-a4/spec.md`

## Summary

Staff open a saved layout (feature 001) and generate a browser-printable A4
page (full run or a chosen sheet range), showing 8 identical-format labels per
sheet (2 columns × 4 rows) with the printing house's fixed letterhead and the
layout's fields — matching the Litobalkan AD reference design. Printing is
dispatched through the browser/OS's native print dialog (no downloadable file,
per Clarification Q2). Each explicit print action is recorded as a `PrintEvent`
(timestamp + sheet range) and surfaced on the layout's detail page so staff can
see whether/when it was already printed (Clarification Q3), without ever
blocking a reprint (FR-014). Technical approach: extend the existing `labels`
(server) and `layouts_ui` (client) Django apps from feature 001 — no new app,
no new external dependency, since the resolved output format (on-screen,
browser print) needs no PDF-generation library.

## Technical Context

**Language/Version**: Python 3.13, Django 6.1 (as already installed for
feature 001 — plan 001's "Python 3.12/Django 5.x" were floor targets; the
actually-provisioned versions are newer and compatible)

**Primary Dependencies**: Django (ORM, templating), Django REST Framework
(same `LayoutViewSet` gains two new detail actions) — no new dependency is
introduced by this feature (see Research §1: Clarification Q2 ruled out
needing a PDF-generation library)

**Storage**: SQLite via Django's ORM (unchanged from feature 001) — adds one
new model, `PrintEvent`

**Testing**: Django's built-in test framework / DRF `APITestCase` (unchanged
from feature 001)

**Target Platform**: Same server-rendered web app; the new "print" page is a
plain HTML page styled with `@media print` CSS for A4, no browser plugin or
native OS integration

**Project Type**: Extends the existing Django monolith (`labels` + `layouts_ui`
apps) — no new app

**Performance Goals**: Not specified by the brief; SC-001 sets a concrete bar
— ready-to-print output in under 10 seconds for runs up to 200 sheets. Sheet
computation is pure in-memory arithmetic (no per-label DB rows), so this is
not expected to be a bottleneck at this scale.

**Constraints**: Every generated sheet MUST be exactly 8 labels in a 2×4 grid
(Constitution Principle III) — this feature is the first to actually render
that constraint, not just compute a count against it (feature 001 only
computed `total_sheet_count`).

**Scale/Scope**: Same small internal deployment as feature 001; sheet counts
per job can run into the hundreds (real example: 157 sheets), which is why
Clarification Q1 (range printing) matters.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. Confirm Before Building | All three open questions (range printing, output format, print tracking) were confirmed with the user before this plan was written (spec.md Clarifications). | PASS |
| II. Durable Storage Is the Source of Truth | `PrintEvent` persists via Django ORM → SQLite (FR-012); nothing in this feature is held only in session/browser state. | PASS |
| III. Print Output Fidelity | This feature renders the fixed 8-labels-per-A4-sheet (2×4) layout directly — the constant is enforced in `labels/services.py`, shared with feature 001's formula, not re-implemented. | PASS |
| IV. Tested API Surface | The two new `LayoutViewSet` actions (`print-sheets`, `print-events`) get `APITestCase` coverage before being considered done (tasks.md, generated separately). | PASS (planned) |
| V. Modular Client/Server Separation | `PrintEvent` model, sheet-computation logic, and the two API actions live in `labels`; the print page/template/JS and the print-history display live in `layouts_ui`, consuming `labels` only through the API (same in-process pattern as feature 001's `views.py`). | PASS |

No violations requiring justification — Complexity Tracking table is empty.

**Post-Phase 1 re-check**: `data-model.md`, `contracts/print-api.md`, and
`quickstart.md` (Phase 1, below) introduce exactly one new entity
(`PrintEvent`) and two new endpoints, both already covered by the table above
— no new violations. Principle IV is now concretely testable:
`contracts/print-api.md` enumerates both endpoints' request/response/error
shapes for `APITestCase` coverage.

## Project Structure

### Documentation (this feature)

```text
specs/002-print-layout-a4/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md         # Phase 1 output (/speckit-plan command)
├── contracts/             # Phase 1 output (/speckit-plan command)
│   └── print-api.md
└── tasks.md              # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
labels/                        # "server" (extends feature 001's app)
├── models.py                  # + PrintEvent model (data-model.md)
├── services.py                 # + build_print_sheets() (FR-005, FR-006, FR-011)
├── serializers.py              # + PrintEventSerializer
├── api.py                      # + LayoutViewSet.print_sheets, .print_events actions
└── tests/
    ├── test_models.py          # (new) PrintEvent
    ├── test_services.py         # + build_print_sheets cases
    └── test_api.py              # + print-sheets / print-events contract tests

layouts_ui/                    # "client" (extends feature 001's app)
├── views.py                    # + layout_print view
├── urls.py                     # + /layouts/<id>/print/
├── templates/layouts_ui/
│   ├── layout_print.html       # (new) A4-styled printable page (US1, US2)
│   └── layout_detail.html      # + print history section + "Print" entry point (US3)
├── static/layouts_ui/
│   ├── layout_print.css        # (new) @media print rules, A4 sheet/label grid
│   └── layout_print.js         # (new) "Print" button -> record event + window.print()
└── tests/
    └── test_views.py            # + print page + print-history rendering tests
```

**Structure Decision**: No new Django app — `PrintEvent` and the sheet-building
formula are data/business logic, so they extend `labels` (the existing
"server" app from feature 001); the printable page and its print-only CSS/JS
are presentation, so they extend `layouts_ui` (the existing "client" app).
This keeps the Constitution Principle V boundary from feature 001 intact
without introducing a third app for what is, functionally, a new capability
on the same `Layout` resource.

## Complexity Tracking

*No entries — Constitution Check has no unjustified violations.*
