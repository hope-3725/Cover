# Quickstart: Print Layout to A4

Validates the feature end-to-end against a running local instance, extending
feature 001's quickstart (a saved layout must already exist).

## Prerequisites

Same as feature 001's quickstart — venv active, `pip install -r
requirements.txt`, migrations applied. No new dependency is added by this
feature (research.md §1).

## Setup

```powershell
python manage.py migrate   # picks up the new PrintEvent table
python manage.py runserver
```

## Validation scenarios

### 1. Print the full run (User Story 1)

1. Open a saved layout's detail page (feature 001) — e.g. `quantity_in_cover =
   24`, `issue = 30000` (`total_sheet_count = 157`).
2. Choose "Print full run". **Expect**: a new page shows 157 A4-sized sheets,
   each with exactly 8 labels in a 2×4 grid, each label showing the layout's
   client/product/type/SAP/PO/date fields, `quantity_in_cover = 24`, and the
   fixed printing-house letterhead — proves US1 scenarios 1 and 4.
3. Confirm exactly one label, somewhere in the run, shows a different quantity
   than the rest whenever the layout's `issue` isn't an exact multiple of
   `quantity_in_cover` — proves US1 scenario 2.
4. Confirm the very last label's sheet has fewer than 8 labels when
   `total_label_count` isn't a multiple of 8 — proves US1 scenario 3.
5. Edit the layout (feature 001 US3), changing `issue`; print again. **Expect**:
   the new output reflects the updated value — proves US1 scenario 5.

### 2. Print a range of sheets (User Story 2)

1. From the same layout, request sheets `1` to `50`.
2. **Expect**: exactly 50 A4 sheets, identical in content to sheets 1-50 of
   the full run — proves US2 scenario 1.
3. Request sheets `150` to `200` (out of the valid 1-157 range). **Expect**:
   the request is rejected with an explanation — proves US2 scenario 2.
4. Print without specifying a range. **Expect**: the full run (157 sheets) —
   proves US2 scenario 3.

### 3. See print history (User Story 3)

1. Open a layout that has never been printed. **Expect**: its detail page
   clearly shows no print has happened yet — proves US3 scenario 1.
2. Print it (full run or a range) via the "Print" button (not just viewing the
   print page — research.md §2). Reopen the detail page. **Expect**: the
   timestamp and sheet range of that print are shown — proves US3 scenario 2.
3. Print it again with a different range. **Expect**: both print events are
   visible in the history, not just the latest — proves US3 scenario 3.

## Automated tests

```powershell
python manage.py test labels layouts_ui
```

**Expect**: all tests pass, including `labels/tests/test_services.py`
(`build_print_sheets` — standard range, default full-run, out-of-bounds
rejection, remainder placement) and `labels/tests/test_api.py` (contract
coverage for `print-sheets` and `print-events`, per
`contracts/print-api.md`).
