# Data Model: Print Layout to A4

## Entity: PrintEvent

A record of one print action taken on a `Layout` (feature 001). Maps to
`labels.models.PrintEvent`, persisted via Django's ORM to SQLite (Constitution
Principle II). Immutable once created — no update path (a mistaken print isn't
"corrected," a new print event is simply created later, per FR-014).

### Stored fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | integer (PK, auto) | system | |
| `layout` | FK → `labels.Layout` | yes | `on_delete=CASCADE`, `related_name="print_events"`. Deleting a layout deletes its print history — there is no requirement to keep print history for a layout that no longer exists. |
| `sheet_start` | positive integer | yes | 1-indexed; first sheet included in this print action. |
| `sheet_end` | positive integer | yes | 1-indexed; last sheet included in this print action. A full-run print stores `1` and that print's `total_sheet_count`. |
| `printed_at` | datetime (auto, `auto_now_add`) | system | When the print action was recorded (Research §2: on explicit "Print" button click, not page view). |

### Validation rules

- `sheet_start >= 1` and `sheet_end >= sheet_start` (mirrors FR-011's range
  validation — a `PrintEvent` can only be created for a range that was
  actually valid against the layout's `total_sheet_count` at creation time).
- No upper bound is stored on `PrintEvent` itself against `total_sheet_count`
  — that check happens at request time in `build_print_sheets()` (research.md
  §4), using the layout's *current* `quantity_in_cover`/`issue`. A `PrintEvent`
  is a historical record of what was requested; it is not re-validated after
  creation even if the layout is later edited (feature 001 US3) to a smaller
  `total_sheet_count`.

### Relationships

- Many `PrintEvent` rows per `Layout` (one per print action, `related_name="print_events"`) — feature 001's `Layout` gains this reverse relation but is not otherwise modified.

### Derived (not stored)

| Field | Computed by | Used by |
|---|---|---|
| Per-sheet label quantities for a given range | `labels.services.build_print_sheets(quantity_in_cover, issue, start_sheet, end_sheet)` | The print page (US1, US2) — never persisted as rows (research.md §3). |
| "Has this layout ever been printed?" | `layout.print_events.exists()` | Layout detail page (US3) empty-state vs. history display. |

### State

No status/workflow field — printing is stateless and repeatable (FR-014).
`PrintEvent` is purely additive history; it never blocks, locks, or alters a
`Layout`'s editability (inherits feature 001 User Story 3 behavior).
