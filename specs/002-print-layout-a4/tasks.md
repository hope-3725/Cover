---

description: "Task list for feature implementation"
---

# Tasks: Print Layout to A4

**Input**: Design documents from `/specs/002-print-layout-a4/`

**Prerequisites**: plan.md, spec.md, data-model.md, contracts/print-api.md, research.md, quickstart.md (all present); feature 001 (label-layout-management) already implemented

**Tests**: Included — Constitution Principle IV ("Tested API Surface") requires passing test coverage on every layout-touching endpoint before it is considered done; this is a project governance requirement, not optional for this feature.

**Organization**: Tasks are grouped by user story (from spec.md) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- File paths are relative to the repository root (`C:\Projects\Cover`), matching plan.md's Project Structure — this feature extends the existing `labels`/`layouts_ui` apps from feature 001, no new app

---

## Phase 1: Setup

**Purpose**: Confirm the existing project (feature 001) is a clean baseline before extending it

- [X] T001 Confirm no new dependency is required (research.md §1 — no PDF library) and run `python manage.py check` to verify a clean baseline

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The shared sheet-computation logic and print-rendering path both User Story 1 and User Story 2 build on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 [P] Implement `build_print_sheets(quantity_in_cover, issue, start_sheet=None, end_sheet=None)` in `labels/services.py` per data-model.md and research.md §3-4: defaults to the full run when no range is given; validates `1 <= start_sheet <= end_sheet <= total_sheet_count` — also handles FR-010 (total_sheet_count=0 with defaulted range returns an empty, non-error result)
- [X] T003 Add a `print_sheets` GET action (`@action(detail=True)`) to `LayoutViewSet` in `labels/api.py`, returning the response shape from `contracts/print-api.md` (depends on T002)
- [X] T004 Create the `layout_print` view and URL route (`/layouts/<int:layout_id>/print/`) in `layouts_ui/views.py` and `layouts_ui/urls.py`, calling `print-sheets` in-process (same `RequestFactory` pattern as feature 001, refactored `_call_api` to support arbitrary actions) and passing `start`/`end` query params through (depends on T003)
- [X] T005 [P] Build `layouts_ui/templates/layouts_ui/layout_print.html` and `layouts_ui/static/layouts_ui/layout_print.css`: one `.sheet` div per returned sheet (A4-sized, `page-break-after: always` under `@media print`), each with up to 8 `.label` divs in a 2×4 CSS grid, showing the fixed printing-house letterhead plus the layout's client/product/type/SAP/PO/date fields and the sheet's per-label quantity (depends on T004) — added `extra_head`/`extra_js` blocks to base.html and a `.no-print` class for the nav/toolbar

**Checkpoint**: Foundation ready — visiting `/layouts/{id}/print/` (optionally with `?start=&end=`) renders a correct A4-styled page; nothing is recorded yet.

---

## Phase 3: User Story 1 - Print a Saved Layout's Full Label Run (Priority: P1) 🎯 MVP

**Goal**: Staff open a saved layout and generate its full printable A4 output, matching the reference design, ready for the browser/OS print dialog.

**Independent Test**: Open a saved layout with known values, request printing (no range), and verify the output has exactly `total_sheet_count` pages, each with 8 labels in a 2×4 grid (quickstart.md §1).

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation** (Constitution Principle IV)

- [X] T006 [P] [US1] Contract test for `GET /api/layouts/{id}/print-sheets/` with no range (full run): standard case (reference example), remainder placed on exactly one label, final sheet partial when `total_label_count` isn't a multiple of 8 — in `labels/tests/test_api.py`, per contracts/print-api.md
- [X] T007 [P] [US1] Unit tests for `build_print_sheets` default/full-run behavior in `labels/tests/test_services.py`: standard case, `total_label_count = 0`, remainder on the last label, exact-multiple-of-8

### Implementation for User Story 1

- [X] T008 [US1] Implement `layouts_ui/static/layouts_ui/layout_print.js`: a "Print" button that triggers `window.print()` (depends on T005, T006, T007)
- [X] T009 [P] [US1] Add a "Print" entry point (link to `/layouts/{id}/print/`) on `layouts_ui/templates/layouts_ui/layout_detail.html` (depends on T004) — also added `layouts_ui/tests/test_views.py` coverage rendering all 157 sheets for the reference example, beyond the minimum tasked scope, as a UI sanity check

**Checkpoint**: User Story 1 is fully functional and independently testable — this is the MVP.

---

## Phase 4: User Story 2 - Print a Specific Range of Sheets (Priority: P2)

**Goal**: Staff can request only a portion of a large run (e.g., "sheets 1-50") instead of always generating the full job.

**Independent Test**: Request sheets 1-50 of a 157-sheet run and verify exactly those 50 pages are produced; request an out-of-bounds range and verify it is rejected (quickstart.md §2).

### Tests for User Story 2

- [X] T010 [P] [US2] Contract tests for `GET /api/layouts/{id}/print-sheets/?start=&end=`: valid subrange, out-of-bounds rejection, `start > end` rejection (FR-011) — in `labels/tests/test_api.py`, per contracts/print-api.md
- [X] T011 [P] [US2] Unit tests for `build_print_sheets` explicit-range cases (valid subrange returns the matching slice; invalid bounds raise) in `labels/tests/test_services.py` — written alongside T007 since both share the same function

### Implementation for User Story 2

- [X] T012 [US2] Add a sheet-range form (from/to number inputs, defaulting to blank = full run) to `layouts_ui/templates/layouts_ui/layout_detail.html`, submitting to `/layouts/{id}/print/?start=&end=` (depends on T009)
- [X] T013 [US2] Surface an invalid-range error from the API in `layouts_ui/views.py`'s `layout_print` view — redirects to the detail page with a Django `messages.error()` (rendered via a new messages block in base.html) instead of a raw API error (depends on T004, T010)

**Checkpoint**: User Stories 1 AND 2 both work independently — full runs and specific ranges can both be printed.

---

## Phase 5: User Story 3 - See When a Layout Was Printed (Priority: P3)

**Goal**: Staff can see whether, when, and what range of a layout has already been printed, to avoid accidentally reprinting a large run.

**Independent Test**: Print a layout via its "Print" button, reopen the detail page, and verify the timestamp and range are shown; print again with a different range and verify both events appear (quickstart.md §3).

### Tests for User Story 3

- [X] T014 [P] [US3] Model test for `PrintEvent` in `labels/tests/test_models.py`: creation, `related_name="print_events"` on `Layout`, default ordering (newest first)
- [X] T015 [P] [US3] Contract tests for `POST /api/layouts/{id}/print-events/` (create + range validation) and `GET /api/layouts/{id}/print-events/` (list newest-first; empty when never printed) — in `labels/tests/test_api.py`, per contracts/print-api.md
- [X] T016 [P] [US3] View test for the print-history display on the layout detail page: empty state, single event, multiple events — in `layouts_ui/tests/test_views.py`

### Implementation for User Story 3

- [X] T017 [US3] Create the `PrintEvent` model in `labels/models.py` per data-model.md (`layout` FK with `related_name="print_events"`, `sheet_start`, `sheet_end`, `printed_at`); generate and apply its migration (depends on T014)
- [X] T018 [US3] Create `PrintEventSerializer` in `labels/serializers.py` (depends on T017)
- [X] T019 [US3] Add a `print_events` GET/POST action (`@action(detail=True, methods=["get", "post"])`) to `LayoutViewSet` in `labels/api.py`, reusing `build_print_sheets`' range validation (T002) for the POST body (depends on T002, T018, T015) — POST also guards the FR-010 "nothing to print" case so an empty print is never recorded as history
- [X] T020 [US3] Extend `layouts_ui/static/layouts_ui/layout_print.js`'s "Print" button handler to also `POST` to `print-events` (research.md §2: record on click, not page view) alongside `window.print()` (depends on T008, T019)
- [X] T021 [US3] Add a print-history section to `layouts_ui/templates/layouts_ui/layout_detail.html`, fetched via `GET print-events/` from `layouts_ui/views.py`'s `layout_detail` view (depends on T019, T016)

**Checkpoint**: All three user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T022 [P] Update `README.md` to mention the print feature and how to validate it (references quickstart.md)
- [X] T023 Run the full quickstart.md validation end-to-end manually (`python manage.py runserver` + all three scenarios) and fix any discrepancies found — verified against a live server (157-sheet full run, 10-sheet range, invalid-range redirect, event recording, history display) plus the full automated suite (64/64)
- [X] T024 [P] Re-verify the Constitution Principle V boundary holds for the new files: `labels/` still has no template/view imports, `layouts_ui/` still has no direct model imports — confirmed via grep; sole exception is `layouts_ui/tests/test_views.py` importing `Layout`/`PrintEvent` for ORM-based test fixtures

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational; US3 additionally depends on US1 existing in practice (you can't see print history before anything is printed), though its code changes are independent
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other stories — the MVP
- **User Story 2 (P2)**: Extends the same print page/route as US1 with range query params; no dependency on US1's specific code beyond the shared Foundational work
- **User Story 3 (P3)**: Adds tracking on top of the "Print" button US1 introduces (T008) — implement after US1

### Within Each User Story

- Tests written and failing before implementation (Constitution Principle IV)
- Service/formula logic (Foundational) before API actions
- API actions before the UI that calls them
- Story complete before moving to the next priority

---

## Parallel Example: Foundational Phase

```bash
# T002 and T005 touch different files - T005 depends on T004 (view/route), not on T002 directly:
Task: "Implement build_print_sheets in labels/services.py"
# (T003 must follow T002; T004 must follow T003; T005 follows T004)
```

## Parallel Example: User Story 1

```bash
# T006 and T007 touch different test files with no dependency between them:
Task: "Contract test for GET /api/layouts/{id}/print-sheets/ in labels/tests/test_api.py"
Task: "Unit tests for build_print_sheets in labels/tests/test_services.py"
```

## Parallel Example: User Story 3

```bash
# T014, T015, T016 touch three different test files with no dependency between them:
Task: "Model test for PrintEvent in labels/tests/test_models.py"
Task: "Contract tests for print-events in labels/tests/test_api.py"
Task: "View test for print-history display in layouts_ui/tests/test_views.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (blocks everything)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run quickstart.md §1 and the automated tests for US1
5. Demo if ready — staff can print a full run matching the reference design

### Incremental Delivery

1. Setup + Foundational → foundation ready (print rendering works for any range)
2. Add User Story 1 → validate → MVP (full-run printing)
3. Add User Story 2 → validate (range printing now works)
4. Add User Story 3 → validate (print history now visible)
5. Polish (README, full quickstart run, Principle V boundary re-check)

---

## Notes

- [P] tasks touch different files with no dependency between them
- [Story] label maps a task to its user story for traceability
- Verify tests fail before implementing (Constitution Principle IV)
- Commit after each task or logical group
- Stop at any checkpoint to validate a story independently
