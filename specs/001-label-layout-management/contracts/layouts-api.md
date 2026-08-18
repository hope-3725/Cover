# API Contract: Layouts

Internal JSON API (Django REST Framework), consumed by the `layouts_ui` app's
templates/JS — not exposed to client companies (FR-010). Base path: `/api/layouts/`.

All request/response bodies are JSON. Field names match `data-model.md` exactly.

## Common: Layout representation (response body)

```json
{
  "id": 1,
  "client_company": "Coca Cola HBC Greece",
  "product_description": "Coca Cola Zero Caffeine 0.25 ml",
  "package_type": "колие",
  "sap_code": "1201200012",
  "po_number": "4502825130",
  "order_date": "2025-10-28",
  "quantity_in_cover": 24,
  "issue": 30000,
  "full_label_count": 1250,
  "remainder": 0,
  "total_label_count": 1250,
  "total_sheet_count": 157,
  "created_at": "2026-08-18T10:00:00Z",
  "updated_at": "2026-08-18T10:00:00Z"
}
```

The five `full_label_count` / `remainder` / `total_label_count` / `total_sheet_count`
fields are always present on read but are rejected if supplied on write (they are
derived — see data-model.md).

## `GET /api/layouts/`

List saved layouts (User Story 2). Supports no filtering/search in this feature (out
of scope per spec Assumptions) — returns all layouts, ordered newest-updated-first.

**200 OK**
```json
{
  "results": [ /* array of Layout representations */ ]
}
```

## `POST /api/layouts/`

Create a new layout (User Story 1 / FR-001, FR-011).

**Request body**: all stored fields from data-model.md except `id`, `created_at`,
`updated_at`, and the four derived fields.

**201 Created** — Layout representation (including computed fields).

**400 Bad Request** — validation failure (FR-009):
```json
{
  "errors": {
    "quantity_in_cover": ["Must be a positive integer."]
  }
}
```

## `GET /api/layouts/{id}/`

Retrieve one saved layout (User Story 2 — opening a selected layout).

**200 OK** — Layout representation.
**404 Not Found** — layout does not exist or was deleted by someone else since the
list was loaded (spec Edge Cases).

## `PUT /api/layouts/{id}/`

Update an existing layout in place (User Story 3 / FR-005). Same body/validation
shape as `POST`. Never creates a new row.

**200 OK** — updated Layout representation.
**400 Bad Request** — validation failure, same shape as `POST`; the previously saved
version remains unchanged (spec Acceptance Scenario US3.3).
**404 Not Found** — layout no longer exists.

## `POST /api/layouts/preview/`

Stateless compute-only endpoint: given a candidate `quantity_in_cover` and `issue`
(not yet saved), returns the four derived fields, so the UI can show a live preview
while the user is still typing (FR-006, FR-008) without creating or mutating a row.

**Request body**:
```json
{ "quantity_in_cover": 24, "issue": 30000 }
```

**200 OK**:
```json
{ "full_label_count": 1250, "remainder": 0, "total_label_count": 1250, "total_sheet_count": 157 }
```

**400 Bad Request** — same validation as the stored fields (e.g. `quantity_in_cover`
must be > 0); response shape matches `POST /api/layouts/`'s error shape.
