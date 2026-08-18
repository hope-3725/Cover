# Feature Specification: Label Layout Management

**Feature Branch**: `001-label-layout-management`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "Create and manage label layouts (\"макети\"): users can create a new layout with label data/parameters, select an existing layout, edit it, and save it. The system visualizes/previews the layout and computes the number of labels using a formula based on the layout's parameters. This is the foundational feature — layout creation/editing/saving must exist before search/filter, print, or JSON export/import features can be built on top of it."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a New Label Layout (Priority: P1)

A user starts a new label layout from scratch, specifies its label parameters, sees a live preview of the layout with the computed number of labels it will produce, and saves it so it exists for future use.

**Why this priority**: Nothing else in this system — search, print, JSON export — has anything to operate on until a layout can be created and durably saved. This is the minimum slice that delivers value on its own.

**Independent Test**: Can be fully tested by opening the "new layout" flow, entering a set of label parameters, confirming the preview and label count update accordingly, saving, and verifying the layout is retrievable afterward.

**Acceptance Scenarios**:

1. **Given** a user with no existing layouts, **When** they create a new layout and provide all required label parameters, **Then** the system shows a live preview of the layout and the computed number of labels it produces.
2. **Given** a user is filling in a new layout's parameters, **When** they change a parameter (e.g., a value that affects label count), **Then** the preview and computed label count update to reflect the change before saving.
3. **Given** a user has finished specifying a new layout, **When** they save it, **Then** the layout persists and is retrievable in a later session.
4. **Given** a user is creating a new layout, **When** they attempt to save while a required parameter is missing, **Then** the system blocks the save and indicates which parameter(s) are missing.

---

### User Story 2 - Browse and Select a Saved Layout (Priority: P2)

A user views the layouts they have previously saved and selects one to open.

**Why this priority**: Creating layouts only has lasting value if users can find them again later; this is the retrieval half of durable storage, and it is a prerequisite for editing (User Story 3) as well as for the future search/filter and print features.

**Independent Test**: Can be fully tested by saving one or more layouts (via User Story 1), then opening the layout list, confirming each saved layout appears with identifying information, and selecting one to open it.

**Acceptance Scenarios**:

1. **Given** one or more layouts have been saved, **When** the user opens the layout list, **Then** each saved layout is shown with enough identifying information (e.g., name, associated company) to distinguish it from the others.
2. **Given** the layout list is open, **When** the user selects a layout, **Then** the system opens that layout showing its current saved parameters and preview.
3. **Given** no layouts have been saved yet, **When** the user opens the layout list, **Then** the system shows an empty state rather than an error, and offers a way to create a new layout.

---

### User Story 3 - Edit and Resave an Existing Layout (Priority: P3)

A user opens a previously saved layout, changes one or more of its parameters, and saves the changes back to the same layout.

**Why this priority**: Layouts are not necessarily right the first time; being able to correct and refine a saved layout is a distinct, independently testable slice of value on top of create (P1) and select (P2), but the system is still useful without it (users could otherwise only ever create new layouts).

**Independent Test**: Can be fully tested by opening a previously saved layout (via User Story 2), changing a parameter, saving, and confirming the change is reflected both in the preview and when the layout is reopened later — without a duplicate layout being created.

**Acceptance Scenarios**:

1. **Given** a saved layout is open for editing, **When** the user changes a parameter, **Then** the preview and computed label count update to reflect the change before saving.
2. **Given** a saved layout has been changed, **When** the user saves it, **Then** the same layout is updated in place (no duplicate layout is created) and the change persists across sessions.
3. **Given** a saved layout is open for editing, **When** the user attempts to save while a required parameter is missing or invalid, **Then** the system blocks the save and indicates the problem, leaving the previously saved version intact.
4. **Given** a user has made unsaved changes to an open layout, **When** they attempt to navigate away without saving, **Then** the system warns them before the changes are lost.

---

### Edge Cases

- What happens when `issue` is 0 (no articles produced yet)? The computed label/sheet count would be zero — the system must handle this without erroring.
- What happens when `quantity_in_cover` is 0? Division by zero must be prevented; the system must treat this as an invalid/missing required parameter (FR-009) rather than compute a result.
- What happens when `issue` divides evenly by `quantity_in_cover` (remainder = 0)? No additional partial-quantity label should be produced — only the `full_label_count` labels.
- What happens when `total_label_count` is not an exact multiple of 8? The final A4 sheet is only partially filled; the system must still produce it rather than dropping the remaining labels.
- What happens when two staff users have the same layout open and both attempt to save changes (concurrent edit)?
- What happens when a user selects a layout that was deleted or renamed by someone else since the list was loaded?
- What happens when a user starts creating a new layout, leaves required parameters blank, and tries to preview it before providing enough data to compute a valid preview?
- How does the system distinguish a genuinely new layout (User Story 1) from an edit accidentally saved as a new one, or vice versa?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to create a new label layout by specifying: the client company name, product description (up to two lines), package/type designation, SAP code, purchase order (PO) number, order date, the quantity of articles per box (`quantity_in_cover`, printed on the label), and the total quantity of articles produced for the order (`issue`, used only for calculation — see FR-007 — and NOT printed on the label). The printing house's own letterhead (logo, address, ISO certification mark) and a document/page control code are part of the fixed print template rather than per-layout user input.
- **FR-002**: The system MUST persist every saved layout so that it remains retrievable in later sessions (durable storage; see Constitution Principle II).
- **FR-003**: Users MUST be able to browse a list of previously saved layouts, each shown with identifying information (at minimum a name and its associated company).
- **FR-004**: Users MUST be able to select a saved layout from the list to open it for viewing or editing.
- **FR-005**: Users MUST be able to edit an existing layout's parameters and save the changes back to that same layout (update in place, not a new layout).
- **FR-006**: The system MUST show a visual preview of the layout reflecting its current parameters, both while creating a new layout and while editing an existing one.
- **FR-007**: The system MUST compute, from a layout's `issue` (total articles produced) and `quantity_in_cover` (articles per box) values, the number of labels to print as follows:
  - `full_label_count` = `issue` ÷ `quantity_in_cover`, integer division (rounded down) — this many labels are printed showing the standard `quantity_in_cover` value.
  - `remainder` = `issue` mod `quantity_in_cover`. If `remainder` > 0, exactly one additional label is produced, printed with the remainder as its quantity value instead of the standard `quantity_in_cover` (representing the last, partially-filled box). If `remainder` = 0, no additional label is produced.
  - `total_label_count` = `full_label_count` + (1 if `remainder` > 0, else 0).
  - `total_sheet_count` = `total_label_count` ÷ 8, rounded up (Constitution Principle III: 8 labels per A4 sheet). The final sheet MAY be only partially filled.
- **FR-008**: The system MUST recompute the preview and the label/sheet count immediately when the user changes a parameter, before the layout is saved.
- **FR-009**: The system MUST validate that all required layout parameters are present and valid before allowing a save, and MUST tell the user which parameter(s) are missing or invalid when a save is blocked.
- **FR-010**: The application is an internal tool used exclusively by the printing house's own staff — client companies (e.g., Coca Cola) do not have accounts or access to this system. Every layout MUST record its associated client company as a descriptive attribute, but there is NO per-company access restriction: any staff user may view, select, and edit any saved layout regardless of which client company it belongs to.
- **FR-011**: Users MUST be able to start a new layout from a blank state (not only by copying/editing an existing one).
- **FR-012**: The system MUST warn a user before discarding unsaved changes to a layout that is being created or edited.

### Key Entities

- **Layout ("Макет")**: A saved label order record. Attributes: client company name, product description (up to two lines), package/type designation, SAP code, PO number, order date, `quantity_in_cover` (articles per box, printed on the label), `issue` (total articles produced, internal-only, not printed), created/updated timestamps. Derived/computed (not stored, recalculated from `quantity_in_cover` and `issue` — see FR-007): `full_label_count`, `remainder`, `total_label_count`, `total_sheet_count`. One Layout may later be printed or exported, but printing and JSON export are out of scope for this feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user with no prior experience with the system can create and save a valid new layout in under 5 minutes.
- **SC-002**: 100% of layouts saved by a user remain retrievable and editable in a later session.
- **SC-003**: The label/sheet count shown in the preview always matches what the defined formula computes for the layout's current parameters (zero discrepancy between displayed and computed values).
- **SC-004**: A user can locate and open a specific previously saved layout from the layout list in under 30 seconds when they know its name or company.
- **SC-005**: 100% of attempts to save a layout with missing or invalid required parameters are blocked with a specific, actionable message, and 0% result in a partially-saved or corrupted layout.

## Assumptions

- Printing the layout to paper and exporting/importing it as JSON are explicitly out of scope for this feature — they depend on layouts existing first, per the feature description, and will be specified separately.
- Searching and filtering the layout list by parameters (beyond the simple browse list in User Story 2) is out of scope for this feature and will be specified separately.
- Whether individual staff members need their own login/authentication (as opposed to the application simply not being exposed to client companies at all) is not addressed by this feature; FR-010 only establishes that there is no per-client-company access restriction. A staff authentication capability, if needed, will be specified separately.
- The printing house's letterhead (logo, address, ISO certification mark) and the document/page control code are treated as a fixed part of the print template rather than editable per-layout data, based on the reference example. If different orders eventually need different letterhead content, that would require revisiting FR-001.
- "Product description" is assumed to be a maximum of two lines of text, matching the reference example; no limit on characters per line is assumed beyond what fits the fixed label dimensions from Constitution Principle III.
