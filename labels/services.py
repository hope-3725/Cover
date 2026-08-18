import math
from dataclasses import dataclass

LABELS_PER_SHEET = 8  # Constitution Principle III: A4, 2 columns x 4 blocks


@dataclass(frozen=True)
class LabelCount:
    full_label_count: int
    remainder: int
    total_label_count: int
    total_sheet_count: int


def compute_label_count(quantity_in_cover, issue):
    """Compute the label/sheet counts for a layout, per spec.md FR-007.

    `quantity_in_cover` must be a positive integer (validated upstream by the
    model/serializer) - dividing by zero is never a valid state to reach here.
    """
    full_label_count, remainder = divmod(issue, quantity_in_cover)
    total_label_count = full_label_count + (1 if remainder > 0 else 0)
    total_sheet_count = math.ceil(total_label_count / LABELS_PER_SHEET)
    return LabelCount(
        full_label_count=full_label_count,
        remainder=remainder,
        total_label_count=total_label_count,
        total_sheet_count=total_sheet_count,
    )


class InvalidSheetRange(ValueError):
    """Raised when a requested print range falls outside the valid sheets (FR-011)."""


@dataclass(frozen=True)
class PrintSheets:
    sheets: list
    start_sheet: int
    end_sheet: int
    total_sheet_count: int


def build_print_sheets(quantity_in_cover, issue, start_sheet=None, end_sheet=None):
    """Build the per-sheet label quantities for a print job (spec.md FR-005/006/011).

    Sheets and their label quantities are derived in memory from
    `compute_label_count` each call - never stored as individual label rows
    (002-print-layout-a4 research.md S3), so they can never drift from the
    layout's current `quantity_in_cover`/`issue` (research.md S4).
    """
    counts = compute_label_count(quantity_in_cover, issue)

    label_values = [quantity_in_cover] * counts.full_label_count
    if counts.remainder > 0:
        label_values.append(counts.remainder)
    all_sheets = [
        label_values[i : i + LABELS_PER_SHEET]
        for i in range(0, len(label_values), LABELS_PER_SHEET)
    ]

    defaulted = start_sheet is None and end_sheet is None
    if start_sheet is None:
        start_sheet = 1
    if end_sheet is None:
        end_sheet = counts.total_sheet_count

    if counts.total_sheet_count == 0 and defaulted:
        # FR-010: nothing to print is a valid (empty) state, not a range error.
        return PrintSheets(sheets=[], start_sheet=1, end_sheet=0, total_sheet_count=0)

    if start_sheet < 1 or end_sheet > counts.total_sheet_count or start_sheet > end_sheet:
        raise InvalidSheetRange(
            f"start must be between 1 and {counts.total_sheet_count}, and start <= end."
        )

    selected_sheets = all_sheets[start_sheet - 1 : end_sheet]

    return PrintSheets(
        sheets=selected_sheets,
        start_sheet=start_sheet,
        end_sheet=end_sheet,
        total_sheet_count=counts.total_sheet_count,
    )
