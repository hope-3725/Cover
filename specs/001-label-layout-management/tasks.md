---

description: "Task list for feature implementation"
---

# Tasks: Label Layout Management

**Input**: Design documents from `/specs/001-label-layout-management/`

**Prerequisites**: plan.md, spec.md, data-model.md, contracts/layouts-api.md, research.md, quickstart.md (all present)

**Tests**: Included — Constitution Principle IV ("Tested API Surface") requires every API endpoint touching layouts to have passing test coverage before it is considered done; this is a project governance requirement, not optional for this feature.

**Organization**: Tasks are grouped by user story (from spec.md) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- File paths are relative to the repository root (`C:\Projects\Cover`), matching plan.md's Project Structure

## Path Conventions

Single Django project at the repo root, split into a "server" app (`labels/`) and a
"client" app (`layouts_ui/`), per plan.md's Structure Decision (Constitution Principle
V). No `src/`/`backend/`/`frontend/` prefix — see plan.md for the full tree.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Django project and apps described in plan.md's Project Structure

- [X] T001 Initialize the Django project `cover` at the repo root (`django-admin startproject cover .`), producing `manage.py`, `cover/settings.py`, `cover/urls.py`, `cover/wsgi.py`, `cover/asgi.py`
- [X] T002 Create the Django apps `labels` and `layouts_ui` at the repo root (`python manage.py startapp labels`, `python manage.py startapp layouts_ui`)
- [X] T003 [P] Add `requirements.txt` at the repo root pinning Django 5.x and djangorestframework (per research.md §1, §3)
- [X] T004 [P] In `cover/settings.py`: register `labels`, `layouts_ui`, and `rest_framework` in `INSTALLED_APPS`, and confirm the default `DATABASES` entry uses SQLite (Constitution Principle II)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core model, formula, serializer, API skeleton, and routing that every user story depends on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 [P] Create the `Layout` model in `labels/models.py` per data-model.md: `client_company`, `product_description`, `package_type`, `sap_code`, `po_number`, `order_date`, `quantity_in_cover` (validated > 0), `issue` (validated >= 0), `created_at`/`updated_at`
- [X] T006 Generate and apply the initial migration for `Layout` in `labels/migrations/0001_initial.py` (depends on T005)
- [X] T007 [P] Implement the label/sheet-count formula in `labels/services.py`: `full_label_count`, `remainder`, `total_label_count`, `total_sheet_count` from `quantity_in_cover`/`issue`, per data-model.md and the FR-007 spec formula
- [X] T008 Create `LayoutSerializer` in `labels/serializers.py` with the validation rules from data-model.md and the four read-only computed fields sourced from `labels/services.py` (depends on T005, T007)
- [X] T009 Create a `LayoutViewSet(viewsets.ModelViewSet)` skeleton in `labels/api.py` using `LayoutSerializer`, and register it on a DRF router in `labels/urls.py` (depends on T008)
- [X] T010 Wire `cover/urls.py` to include `labels.urls` at `/api/layouts/` and `layouts_ui.urls` at `/` (depends on T002, T009)
- [X] T011 [P] Create the shared base template `layouts_ui/templates/layouts_ui/base.html` (nav, static includes) used by all `layouts_ui` pages

**Checkpoint**: Foundation ready — full CRUD is reachable via the API router; user story implementation can now begin

---

## Phase 3: User Story 1 - Create a New Label Layout (Priority: P1) 🎯 MVP

**Goal**: A user creates a new layout, sees a live preview and computed label/sheet count, and saves it.

**Independent Test**: Open the "new layout" flow, enter parameters, confirm the preview/count update live, save, and verify the layout is listed and retrievable afterward (quickstart.md §1).

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation** (Constitution Principle IV)

- [X] T012 [P] [US1] Contract tests for `POST /api/layouts/` (create + validation-error shape) and `POST /api/layouts/preview/` (incl. `issue=0` and `quantity_in_cover=0` rejection) in `labels/tests/test_api.py`, per contracts/layouts-api.md
- [X] T013 [P] [US1] Unit tests for the formula in `labels/tests/test_services.py`: standard case, `issue=0`, `quantity_in_cover=0` (must raise/reject, not divide by zero), remainder=0, and `total_label_count` an exact multiple of 8

### Implementation for User Story 1

- [X] T014 [US1] Add a custom `preview` action (`@action(detail=False)`) to `LayoutViewSet` in `labels/api.py` that computes the four derived fields via `labels/services.py` without persisting a row (depends on T007, T009, T012)
- [X] T015 [US1] Create the "new layout" view and URL route (`/layouts/new/`) in `layouts_ui/views.py` and `layouts_ui/urls.py` (depends on T010)
- [X] T016 [US1] Build `layouts_ui/templates/layouts_ui/layout_form.html` with fields for every `Layout` attribute from data-model.md (depends on T015, T011)
- [X] T017 [US1] Implement `layouts_ui/static/layouts_ui/layout_preview.js`: on field change, call `POST /api/layouts/preview/` and update the displayed count; on submit, call `POST /api/layouts/` and render field-level validation errors (FR-006, FR-008, FR-009) (depends on T014, T016)
- [X] T018 [US1] Add an unsaved-changes warning (`beforeunload`) to the new-layout form in `layouts_ui/static/layouts_ui/layout_preview.js` (FR-012) (depends on T017)

**Checkpoint**: User Story 1 is fully functional and independently testable — this is the MVP.

---

## Phase 4: User Story 2 - Browse and Select a Saved Layout (Priority: P2)

**Goal**: A user views previously saved layouts and selects one to open.

**Independent Test**: Save one or more layouts (via US1), open the layout list, confirm each is shown with identifying info, and select one to open it; confirm the empty-state appears with zero layouts (quickstart.md §2).

### Tests for User Story 2

- [X] T019 [P] [US2] Contract tests for `GET /api/layouts/` (list) and `GET /api/layouts/{id}/` (retrieve, incl. 404 for a missing/deleted layout) in `labels/tests/test_api.py`, per contracts/layouts-api.md
- [X] T020 [P] [US2] View test asserting the layout list page renders an empty-state message and a "create new" link when no layouts exist, in `layouts_ui/tests/test_views.py`

### Implementation for User Story 2

- [X] T021 [US2] Create the layout list view and URL route (`/layouts/`) in `layouts_ui/views.py` and `layouts_ui/urls.py`, fetching `GET /api/layouts/` (depends on T010, T019)
- [X] T022 [US2] Build `layouts_ui/templates/layouts_ui/layout_list.html`: show `client_company` + `product_description` per layout, an empty state, and a "create new" link (depends on T021, T020, T011)
- [X] T023 [US2] Create the layout detail view and URL route (`/layouts/{id}/`) plus `layouts_ui/templates/layouts_ui/layout_detail.html`, showing a selected layout's saved parameters and computed preview, in `layouts_ui/views.py`, `layouts_ui/urls.py` (depends on T010, T011)

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

## Phase 5: User Story 3 - Edit and Resave an Existing Layout (Priority: P3)

**Goal**: A user opens a saved layout, changes parameters, and saves the change back to the same layout.

**Independent Test**: Open a saved layout (via US2), change a parameter, confirm the preview recomputes, save, and confirm the same layout (same id) was updated rather than duplicated; confirm a blocked save leaves the prior version intact (quickstart.md §3).

### Tests for User Story 3

- [X] T024 [P] [US3] Contract test for `PUT /api/layouts/{id}/` — successful update-in-place, and a validation failure that leaves the previously saved version unchanged — in `labels/tests/test_api.py`, per contracts/layouts-api.md
- [X] T025 [P] [US3] View/integration test for the edit flow (opens pre-filled, in-place update, unsaved-changes warning) in `layouts_ui/tests/test_views.py`

### Implementation for User Story 3

- [X] T026 [US3] Add an "Edit" link from `layout_detail.html` to an edit route; create the edit view and URL route (`/layouts/{id}/edit/`) in `layouts_ui/views.py`, `layouts_ui/urls.py`, reusing `layout_form.html` pre-filled with the layout's existing values (depends on T016, T023, T024)
- [X] T027 [US3] Extend `layouts_ui/static/layouts_ui/layout_preview.js` to submit via `PUT /api/layouts/{id}/` when editing an existing layout, reusing the live-preview logic built for US1 (depends on T017, T026) — already mode-aware from T017, verified against T024/T025
- [X] T028 [US3] Apply the unsaved-changes warning (FR-012) to the edit form as well (depends on T018, T026) — the `beforeunload` handler is mode-independent, verified by T025

**Checkpoint**: All three user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T029 [P] Write `README.md` at the repo root with install/run instructions, per Cover.md's explicit requirement and quickstart.md
- [X] T030 Run the full quickstart.md validation end-to-end manually (`python manage.py runserver` + all three scenarios) and fix any discrepancies found — verified via dev server + full automated suite (26/26 passing); also caught and diagnosed a Cyrillic-encoding artifact in Git Bash's `curl`, confirmed as a shell-console issue rather than an app bug
- [X] T031 [P] Verify the Constitution Principle V boundary holds: `labels/` contains no template/view imports and `layouts_ui/` contains no direct `Layout` model imports (it must go through the API only) — confirmed via grep; the sole exception is `layouts_ui/tests/test_views.py` importing `Layout` for ORM-based test fixture setup, which is standard test-arrangement practice, not application code bypassing the API

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational; can proceed in parallel or in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other stories — the MVP
- **User Story 2 (P2)**: No dependency on US1's implementation, but US1 is needed to *produce* layouts to browse when testing US2 manually
- **User Story 3 (P3)**: Reuses `layout_form.html` (T016, US1) and `layout_detail.html` (T023, US2) rather than duplicating them — implement after US1 and US2

### Within Each User Story

- Tests written and failing before implementation (Constitution Principle IV)
- Model/services/serializer (Foundational) before API actions
- API actions before the UI that calls them
- Story complete before moving to the next priority

---

## Parallel Example: Foundational Phase

```bash
# T005 and T007 touch different files with no dependency between them:
Task: "Create the Layout model in labels/models.py"
Task: "Implement the label/sheet-count formula in labels/services.py"
# T011 is also independent of both:
Task: "Create the shared base template layouts_ui/templates/layouts_ui/base.html"
```

## Parallel Example: User Story 1

```bash
# T012 and T013 touch different test files with no dependency between them:
Task: "Contract tests for POST /api/layouts/ and POST /api/layouts/preview/ in labels/tests/test_api.py"
Task: "Unit tests for the label/sheet-count formula in labels/tests/test_services.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (blocks everything)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run quickstart.md §1 and the automated tests for US1
5. Demo if ready — a user can create, preview, and save a layout

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add User Story 1 → validate → MVP
3. Add User Story 2 → validate (list/select now works)
4. Add User Story 3 → validate (edit-in-place now works)
5. Polish (README, full quickstart run, Principle V boundary check)

---

## Notes

- [P] tasks touch different files with no dependency between them
- [Story] label maps a task to its user story for traceability
- Verify tests fail before implementing (Constitution Principle IV)
- Commit after each task or logical group
- Stop at any checkpoint to validate a story independently
