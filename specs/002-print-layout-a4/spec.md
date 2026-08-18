# Feature Specification: Print Layout to A4

**Feature Branch**: `002-print-layout-a4`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "Print a saved label layout (\"макет\") to A4 sheets, matching the printing house's real label design (reference: Etiket produkcia.pdf — Litobalkan AD letterhead/logo, ISO certification mark, and the layout's Client/Product/Type/SAP/PO/Date/quantity_in_cover/Signature fields, with a vertical document-code strip). Each A4 sheet holds exactly 8 identical labels (2 columns x 4 rows), per Constitution Principle III. The user selects a saved layout (from feature 001, label-layout-management) and prints it; the system generates total_sheet_count A4 sheets using the formula from feature 001 (full_label_count labels showing the standard quantity_in_cover, plus one extra label showing the remainder quantity if remainder > 0), with the final sheet possibly only partially filled. This depends on layouts already existing (feature 001) and is a separate feature from layout creation/editing."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Print a Saved Layout's Full Label Run (Priority: P1)

Printing-house staff open a saved layout and generate its printable A4 output —
one page per sheet needed for the full run — matching the shop's standard label
design, ready to send to a printer.

**Why this priority**: This is the entire point of the feature; feature 001 only
gets a layout as far as "saved with a computed count," this story is what turns
that into something that can actually be printed and glued onto boxes.

**Independent Test**: Open a saved layout with known `quantity_in_cover`/`issue`
values, request printing, and verify the output has exactly `total_sheet_count`
pages, each with 8 labels in a 2×4 grid, matching the reference design and the
feature 001 formula.

**Acceptance Scenarios**:

1. **Given** a saved layout with `quantity_in_cover=24`, `issue=30000`
   (`full_label_count=1250`, `remainder=0`, `total_sheet_count=157`), **When**
   staff request to print it, **Then** the system produces 157 A4 pages, each
   containing exactly 8 labels (2 columns × 4 rows) showing the layout's client,
   product, package type, SAP code, PO number, order date, and `quantity_in_cover`,
   plus the printing house's fixed letterhead on every label.
2. **Given** a layout whose formula produces `remainder > 0`, **When** printed,
   **Then** exactly one label across all generated sheets shows the remainder
   value instead of the standard `quantity_in_cover`, and every other label shows
   the standard value.
3. **Given** `total_label_count` is not an exact multiple of 8, **When** printed,
   **Then** the final sheet contains only the remaining labels (fewer than 8)
   rather than blank or duplicate placeholder labels.
4. **Given** a saved layout is open on its detail page (feature 001), **When**
   staff choose to print, **Then** the printable output is generated using the
   layout's already-saved values, without re-entering any data.
5. **Given** a layout is edited and re-saved after an earlier print, **When**
   staff print it again, **Then** the new output reflects the current saved
   values, not the values from before the edit.

---

### User Story 2 - Print a Specific Range of Sheets (Priority: P2)

Staff printing a large run can request only a portion of it (e.g., "sheets
1-50") instead of generating the full job in one action.

**Why this priority**: Large runs (150+ sheets) are common given real order
sizes (e.g., 30,000 units at 24/box = 157 sheets); staff need to print in
manageable batches — to match press capacity, resume an interrupted print, or
avoid a very long single print job — without that being the only way to print.

**Independent Test**: Open a saved layout, request sheets 1-50 of a 157-sheet
run, and verify the output contains exactly those 50 sheets, correctly
numbered/labeled, with no sheets outside the requested range.

**Acceptance Scenarios**:

1. **Given** a layout with `total_sheet_count = 157`, **When** staff request
   sheets 1-50, **Then** the output contains exactly 50 pages, containing the
   same labels that sheets 1-50 of the full run would contain.
2. **Given** a layout with `total_sheet_count = 157`, **When** staff request a
   range with a start or end outside 1-157 (e.g., 150-200), **Then** the system
   rejects the request and explains the valid range.
3. **Given** a layout with `total_sheet_count = 157`, **When** staff do not
   specify a range, **Then** the system defaults to printing the full run
   (User Story 1's behavior).

---

### User Story 3 - See When a Layout Was Printed (Priority: P3)

Staff viewing a saved layout can see whether, when, and what range of it has
already been printed, so they don't accidentally reprint a large run.

**Why this priority**: Reprinting a 150+ sheet run by mistake wastes material
and time; this is a safety net on top of Stories 1 and 2, not required for
printing to work at all.

**Independent Test**: Print a layout (fully or a range), reopen its detail
page, and verify the print timestamp and range are shown; print it again and
verify the new print event is also visible.

**Acceptance Scenarios**:

1. **Given** a layout has never been printed, **When** staff view its detail
   page, **Then** it clearly indicates no print has happened yet.
2. **Given** a layout was printed (full run or a range), **When** staff view
   its detail page, **Then** they see when it was printed and which sheet
   range, without needing to check any external record.
3. **Given** a layout has been printed more than once (e.g., a range, then
   later the rest, or a full reprint), **When** staff view its detail page,
   **Then** they can see that history, not just the single most recent event.

---

### Edge Cases

- What happens when a layout's `quantity_in_cover`/`issue` combination yields
  `total_label_count = 0` (nothing to print)? The system should indicate there is
  nothing to print rather than generate an empty or broken output.
- What happens when the layout being printed is deleted or changed by someone
  else between opening it and generating the output?
- What happens when staff request a range that has already been printed before
  — is a repeat print of the same range allowed (e.g., a sheet was damaged and
  needs reprinting)? Yes — printing is repeatable; the print-history record
  (User Story 3) is informational, not a lock that blocks reprinting.

## Clarifications

### Session 2026-08-18

- Q1: When a layout's full run is very large (e.g., 157 sheets), should the
  system always generate the complete run in one action, or must staff be able
  to request a smaller range (e.g., "sheets 1-50") to print now? → **Staff must
  be able to request a specific range of sheets** (User Story 2); printing the
  full run remains available and is the default when no range is given.
- Q2: Should printing produce a downloadable/archivable file (e.g., PDF) staff
  can save/email/re-print later, or is an on-screen, browser-printable page
  (printed via the OS/browser print dialog) sufficient? → **On-screen,
  browser-printable page**, dispatched via the standard browser/OS print
  dialog — no separate downloadable file is required by this feature.
- Q3: Should the system remember and display that a layout was already printed
  (to help staff avoid accidentally re-printing a large run), or is printing
  stateless with no tracking? → **Yes** — the system must record and display
  when (and what range of) a layout was printed (User Story 3).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Staff MUST be able to generate a printable A4 output for any
  layout saved via feature 001.
- **FR-002**: Every generated page MUST contain exactly 8 labels arranged in 2
  columns × 4 rows (Constitution Principle III).
- **FR-003**: Each printed label MUST show: client company, product description,
  package type, SAP code, PO number, order date, and `quantity_in_cover` (or the
  remainder value on the one partial label, per feature 001 FR-007) — `issue` is
  never printed, matching feature 001's FR-001.
- **FR-004**: Every printed label MUST include the printing house's fixed
  letterhead (logo, address, ISO certification mark) and document-code strip,
  matching the reference design — inheriting feature 001's Assumption that this
  content is fixed presentation, not per-layout data.
- **FR-005**: The system MUST support printing the full run (all
  `total_sheet_count` pages, per feature 001's FR-007 formula) as the default
  action when no range is specified.
- **FR-006**: The system MUST allow staff to instead request a specific range
  of sheets (a start and end sheet number) to print, producing only the pages
  in that range.
- **FR-011**: The system MUST validate a requested range is within
  `1` to `total_sheet_count` and reject (with an explanation) any range whose
  start is greater than its end or whose bounds fall outside that span.
- **FR-007**: Print output MUST be presented as an on-screen page styled for
  standard A4 printing, dispatched through the browser/OS's native print
  function — this feature does not generate or offer a separately downloadable
  file.
- **FR-012**: Each time staff print a layout (full run or a range), the system
  MUST record the timestamp and the sheet range that was printed.
- **FR-013**: A layout's detail page MUST display its print history (or
  clearly indicate it has never been printed) — at minimum the most recent
  print's timestamp and range, and MUST make prior print events visible when
  more than one exists (User Story 3).
- **FR-008**: Staff MUST be able to initiate printing directly from a layout's
  detail page (feature 001) without re-entering any already-saved data.
- **FR-009**: If a layout is edited and re-saved after an earlier print, a
  subsequent print MUST reflect the layout's current saved values, not a stale
  copy from before the edit.
- **FR-010**: When a layout's computed `total_label_count` is 0, the system MUST
  indicate there is nothing to print rather than generate an empty or broken
  output.
- **FR-014**: Printing (full run or any range) MUST remain repeatable — a
  previously printed layout or range MUST NOT be locked or blocked from being
  printed again.

### Key Entities

- **PrintEvent**: A record of one print action taken on a layout. Attributes:
  the layout it belongs to, the sheet range printed (start sheet, end sheet —
  a full-run print records `1` to that print's `total_sheet_count`), and the
  timestamp it was printed. A Layout may have zero or many PrintEvents
  (User Story 3); a PrintEvent never blocks or alters future printing (FR-014).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Staff can go from a saved layout to a ready-to-print output in
  under 10 seconds, regardless of run size (tested up to 200 sheets).
- **SC-002**: 100% of generated labels show the correct `quantity_in_cover` or
  remainder value, verified against the layout's stored values and feature 001's
  formula.
- **SC-003**: Every generated page matches the fixed 2×4 layout with zero
  missing or extra labels relative to `total_label_count`, whether printing the
  full run or a requested range.
- **SC-004**: Printed output visually matches the reference label design
  (Etiket produkcia.pdf) — same fields, same fixed letterhead, same per-sheet
  label count — verified by side-by-side comparison.
- **SC-005**: 100% of print actions (full run or range) are visible in the
  layout's print history within the same session, with zero print events lost
  or unrecorded.

## Assumptions

- This feature covers exactly one printing house (the one already established
  in feature 001, FR-010 — internal staff only); the letterhead/logo/ISO mark
  are fixed content for this single tenant, not configurable per print job.
- Printing one layout at a time is in scope; selecting multiple layouts and
  printing them together as a batch is out of scope for this feature.
- Access to printing is governed by feature 001's existing FR-010 (internal
  staff only, no per-client-company restriction) — this feature does not
  introduce any new access rules.
- Printing does not lock or otherwise change a layout's editability — a layout
  can still be edited (feature 001, User Story 3) after being printed.
- Print history (PrintEvent records) is informational only in this feature —
  no export, filtering, or deletion of print history is in scope.
- Sheet numbering for range selection (User Story 2) is 1-indexed and refers to
  the same sheet ordering the full-run print already produces (sheet 1 is the
  first page of the full run).
