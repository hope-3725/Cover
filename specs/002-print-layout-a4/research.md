# Research: Print Layout to A4

## 1. No PDF-generation library is needed

**Decision**: Render the printable output as a plain Django-templated HTML
page styled with CSS `@media print` rules (and `@page { size: A4; }`); staff
print it via the browser/OS's native print function. No server-side PDF
library (e.g., WeasyPrint, ReportLab, wkhtmltopdf) is introduced.

**Rationale**: Clarification Q2 resolved this directly — the user chose "печат
през стандартния диалог" (print via the standard dialog), not a downloadable
file. A browser already turns any page into a paginated, printable A4 document
given correct print CSS, and every modern browser's print dialog can itself
"Save as PDF" if staff want a file — so no dependency is needed to satisfy the
resolved requirement.

**Alternatives considered**:
- *WeasyPrint/ReportLab-generated PDF*: rejected — this is exactly what
  Clarification Q2 ruled out; would add a new dependency and a download/file
  UX the user explicitly didn't ask for.

## 2. When a print is "recorded" (Clarification Q3 / FR-012)

**Decision**: Split viewing the printable page from recording a print event.
`GET` the print page / `GET /api/layouts/{id}/print-sheets/` never records
anything (safe, repeatable, side-effect-free). A `PrintEvent` is created only
when staff click the page's explicit "Print" button, via a `POST
/api/layouts/{id}/print-events/` fired alongside `window.print()`.

**Rationale**: A web page cannot reliably detect whether a user actually
completed or cancelled the OS print dialog — `window.print()` is synchronous
from the page's perspective in some browsers and asynchronous in others, and
there is no cross-browser "user confirmed print" event. Recording on every
page *view* would over-count (e.g., a refresh, or navigating back to the print
page to look at it again) — an explicit "Print" button click is the closest,
least surprising signal to "staff intended to print this," and keeps the GET
endpoints properly side-effect-free.

**Alternatives considered**:
- *Record on page load (GET)*: rejected — double-counts on refresh/back-
  navigation, and conflates "viewed" with "printed," undermining the very
  purpose of Clarification Q3 (avoiding a false sense of "this wasn't printed
  yet" or the reverse).
- *Try to detect actual print completion via `window.onafterprint`*: rejected
  — `onafterprint` fires whether the user actually printed or cancelled the
  dialog, so it would not be a meaningfully more accurate signal than the
  button click, while adding cross-browser fragility.

## 3. Sheet/label computation reuses feature 001's formula, not model rows

**Decision**: A new pure function, `build_print_sheets(quantity_in_cover,
issue, start_sheet, end_sheet)` in `labels/services.py`, built directly on top
of feature 001's existing `compute_label_count()` — it does not create or read
any per-label database rows; sheets and their label quantities are computed
in memory each time.

**Rationale**: Feature 001 already established `full_label_count` /
`remainder` / `total_label_count` / `total_sheet_count` as derived, not
stored (data-model.md: "so they can never drift out of sync with their
inputs"). Individual labels are just positions within that derived count —
storing 1250 label rows for a single layout would be pure duplication of
arithmetic already proven correct in feature 001's tests, with no query or
business need that requires them to be individually addressable rows.

**Alternatives considered**:
- *A `Label` row per physical label*: rejected — no requirement reads or
  filters individual labels independently of their layout; would multiply
  storage for no behavioral benefit and duplicate the source of truth for the
  count (violating the "derive, don't duplicate" precedent from feature 001).

## 4. Range validation reuses the same boundary as the derived count

**Decision**: `build_print_sheets` validates `1 <= start_sheet <= end_sheet <=
total_sheet_count` (FR-011) using the `total_sheet_count` computed by the same
call to `compute_label_count`, so range validation can never disagree with the
count a client last saw.

**Rationale**: Avoids a class of bug where a client-supplied `total_sheet_count`
(e.g., cached from an earlier API call) could drift from the server's current
computation if `quantity_in_cover`/`issue` changed between the two requests
(feature 001 FR-009 / this feature's FR-009 both require using current values).
