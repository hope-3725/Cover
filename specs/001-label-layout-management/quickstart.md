# Quickstart: Label Layout Management

Validates that the feature works end-to-end, exercising the User Story acceptance
scenarios from `spec.md` against a running local instance.

## Prerequisites

- Python 3.12+ installed.
- Repository dependencies installed (`requirements.txt`, once the setup tasks from
  `/speckit-tasks` have created it) — includes Django and Django REST Framework.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Validation scenarios

Each scenario references the acceptance scenario it proves in `spec.md`.

### 1. Create a new layout (User Story 1)

1. Open the "new layout" page in the browser.
2. Enter: client company, product description, package type, SAP code, PO number,
   order date, `quantity_in_cover = 24`, `issue = 30000`.
3. **Expect**: preview updates live and shows `full_label_count = 1250`,
   `remainder = 0`, `total_label_count = 1250`, `total_sheet_count = 157`
   (matches `contracts/layouts-api.md` example) — proves US1 scenario 1–2.
4. Save. **Expect**: redirect/confirmation, and the layout is now listed on the
   layout list page — proves US1 scenario 3.
5. Repeat with a required field left blank and attempt to save. **Expect**: save is
   blocked with a message naming the missing field — proves US1 scenario 4.

### 2. Browse and select a saved layout (User Story 2)

1. With at least one layout saved, open the layout list page.
2. **Expect**: each layout is listed with at least client company and an identifying
   label (e.g. product description) — proves US2 scenario 1.
3. Select a layout. **Expect**: its saved parameters and preview load — proves US2
   scenario 2.
4. With zero layouts (fresh database), open the list. **Expect**: an empty-state
   message with a link to create a new layout, not an error — proves US2 scenario 3.

### 3. Edit and resave a layout (User Story 3)

1. Open a saved layout, change `issue` to `30024`.
2. **Expect**: preview recomputes live to `full_label_count = 1251`, `remainder = 0`,
   `total_label_count = 1251`, `total_sheet_count = 157` — proves US3 scenario 1.
3. Save. **Expect**: the same layout (same `id`) is updated, not duplicated; reopening
   the layout list still shows exactly one entry for it — proves US3 scenario 2.
4. Set `quantity_in_cover` to `0` and attempt to save. **Expect**: save is blocked,
   the previously saved values remain intact when reloading the layout — proves US3
   scenario 3.
5. Change a field and navigate away without saving. **Expect**: a warning appears
   before the change is discarded — proves US3 scenario 4.

## Automated tests

```powershell
python manage.py test labels layouts_ui
```

**Expect**: all tests pass, including `labels/tests/test_services.py` (the
`full_label_count`/`remainder`/`total_label_count`/`total_sheet_count` formula from
`data-model.md`, covering the zero-`issue`, zero-`quantity_in_cover`, and
exact-multiple-of-8 edge cases from spec.md) and `labels/tests/test_api.py` (contract
coverage for every endpoint in `contracts/layouts-api.md`).
