# API Contract: Printing

Extends `labels-api.md` (feature 001) with two detail actions on the existing
`LayoutViewSet`, at `/api/layouts/{id}/print-sheets/` and
`/api/layouts/{id}/print-events/`. Same JSON conventions as feature 001;
internal-only (feature 001 FR-010 — no new access rules, per this feature's
Assumptions).

## `GET /api/layouts/{id}/print-sheets/`

Read-only, side-effect-free (research.md §2) — computes what a print of the
requested range would contain, for the `layouts_ui` print page to render.

**Query params** (both optional; default to the full run):
- `start` — first sheet, 1-indexed. Default `1`.
- `end` — last sheet, 1-indexed. Default: the layout's current `total_sheet_count`.

**200 OK**
```json
{
  "layout": {
    "id": 1,
    "client_company": "Coca Cola HBC Greece",
    "product_description": "Coca Cola Zero Caffeine 0.25 ml",
    "package_type": "колие",
    "sap_code": "1201200012",
    "po_number": "4502825130",
    "order_date": "2025-10-28"
  },
  "start_sheet": 1,
  "end_sheet": 50,
  "total_sheet_count": 157,
  "sheets": [
    [24, 24, 24, 24, 24, 24, 24, 24],
    [24, 24, 24, 24, 24, 24, 24, 24]
  ]
}
```

`sheets` is a list of up to `end_sheet - start_sheet + 1` entries, one per
requested sheet, each a list of up to 8 integers — the `quantity_in_cover` (or
the single `remainder` value, on whichever label is last overall) to print on
each label position on that sheet, in reading order. A sheet with fewer than 8
entries is the final sheet of the *full run* (fewer labels than a full sheet,
per feature 001 FR-007) — this can only appear as the last entry of `sheets`
when `end_sheet` equals `total_sheet_count`.

**400 Bad Request** — invalid range (FR-011):
```json
{ "errors": { "range": "start must be between 1 and 157, and start <= end." } }
```

**404 Not Found** — layout does not exist.

## `GET /api/layouts/{id}/print-events/`

List this layout's print history (User Story 3), newest first.

**200 OK**
```json
{
  "results": [
    { "id": 5, "sheet_start": 1, "sheet_end": 50, "printed_at": "2026-08-18T10:15:00Z" },
    { "id": 2, "sheet_start": 1, "sheet_end": 157, "printed_at": "2026-08-17T09:00:00Z" }
  ]
}
```

An empty `results` array means the layout has never been printed (US3
acceptance scenario 1).

## `POST /api/layouts/{id}/print-events/`

Record a print action (research.md §2 — called when staff click "Print", not
on page view).

**Request body**:
```json
{ "sheet_start": 1, "sheet_end": 50 }
```
Omitting both defaults to the full run, same as `GET print-sheets/`.

**201 Created**
```json
{ "id": 5, "sheet_start": 1, "sheet_end": 50, "printed_at": "2026-08-18T10:15:00Z" }
```

**400 Bad Request** — same range validation as `GET print-sheets/`:
```json
{ "errors": { "range": "start must be between 1 and 157, and start <= end." } }
```

**404 Not Found** — layout does not exist.
