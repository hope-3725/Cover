# Data Model: Label Layout Management

## Entity: Layout ("Макет")

Represents one saved label order record for a client's box-label print job. Maps
to a single Django model (`labels.models.Layout`), persisted via Django's ORM to
SQLite (Constitution Principle II).

### Stored fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | integer (PK, auto) | system | |
| `client_company` | string | yes | Descriptive/searchable only — no access control derives from this (FR-010). |
| `product_description` | text | yes | Up to two lines, per reference label (spec Assumptions). |
| `package_type` | string | yes | e.g. "колие" in the reference example. |
| `sap_code` | string | yes | |
| `po_number` | string | yes | Purchase order number ("№ PO"). |
| `order_date` | date | yes | |
| `quantity_in_cover` | positive integer | yes | Articles per box; printed on the label (FR-001). Must be > 0 — see Validation. |
| `issue` | non-negative integer | yes | Total articles produced; internal only, never printed (FR-001). |
| `created_at` | datetime (auto) | system | |
| `updated_at` | datetime (auto) | system | |

### Derived fields (computed on read, not stored — FR-007)

Computed from `quantity_in_cover` and `issue` at request time; never persisted, so
they can never drift out of sync with their inputs (supports Success Criterion SC-003).

| Field | Formula |
|---|---|
| `full_label_count` | `issue // quantity_in_cover` (integer division) |
| `remainder` | `issue % quantity_in_cover` |
| `total_label_count` | `full_label_count + (1 if remainder > 0 else 0)` |
| `total_sheet_count` | `ceil(total_label_count / 8)` |

### Validation rules

- `quantity_in_cover` MUST be a positive integer (> 0). A value of 0 is rejected as
  invalid input (FR-009), not treated as a valid layout with an undefined formula
  (spec Edge Cases: division-by-zero must never reach the formula).
- `issue` MUST be a non-negative integer (>= 0). `issue = 0` is valid and yields
  `total_label_count = 0`, `total_sheet_count = 0` (spec Edge Cases).
- `client_company`, `product_description`, `package_type`, `sap_code`, `po_number`,
  `order_date` are all required (non-blank) — FR-009 blocks save and reports which
  field(s) are missing/invalid.
- No two stored fields are derived from each other; only the four computed fields
  above are derived, and only at read time.

### Relationships

None — Layout is a standalone record for this feature. No user/account or
per-company entity exists yet (FR-010, spec Assumptions): `client_company` is a
plain string field, not a foreign key, since there is no company/account table to
reference.

### State

Layouts have no workflow/status field in this feature — they are simply created,
optionally edited in place (FR-005), and remain in the store (no delete requirement
was specified). Editing does not create a new row; the existing row's fields are
updated and `updated_at` refreshed.
