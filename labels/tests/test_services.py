from django.test import SimpleTestCase

from labels.services import InvalidSheetRange, build_print_sheets, compute_label_count


class ComputeLabelCountTests(SimpleTestCase):
    def test_standard_case_from_reference_example(self):
        result = compute_label_count(quantity_in_cover=24, issue=30000)
        self.assertEqual(result.full_label_count, 1250)
        self.assertEqual(result.remainder, 0)
        self.assertEqual(result.total_label_count, 1250)
        self.assertEqual(result.total_sheet_count, 157)

    def test_issue_zero_yields_zero_labels_and_sheets(self):
        result = compute_label_count(quantity_in_cover=24, issue=0)
        self.assertEqual(result.full_label_count, 0)
        self.assertEqual(result.remainder, 0)
        self.assertEqual(result.total_label_count, 0)
        self.assertEqual(result.total_sheet_count, 0)

    def test_remainder_adds_exactly_one_partial_label(self):
        result = compute_label_count(quantity_in_cover=24, issue=30010)
        self.assertEqual(result.full_label_count, 1250)
        self.assertEqual(result.remainder, 10)
        self.assertEqual(result.total_label_count, 1251)
        self.assertEqual(result.total_sheet_count, 157)

    def test_total_label_count_exact_multiple_of_eight_fills_last_sheet(self):
        # 8 full-cover labels, no remainder -> exactly one full sheet.
        result = compute_label_count(quantity_in_cover=10, issue=80)
        self.assertEqual(result.total_label_count, 8)
        self.assertEqual(result.total_sheet_count, 1)

    def test_quantity_in_cover_zero_raises_instead_of_dividing_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            compute_label_count(quantity_in_cover=0, issue=100)


class BuildPrintSheetsDefaultRangeTests(SimpleTestCase):
    """002-print-layout-a4 User Story 1: full-run (default) behavior."""

    def test_standard_case_from_reference_example(self):
        result = build_print_sheets(quantity_in_cover=24, issue=30000)
        self.assertEqual(result.start_sheet, 1)
        self.assertEqual(result.end_sheet, 157)
        self.assertEqual(result.total_sheet_count, 157)
        self.assertEqual(len(result.sheets), 157)
        self.assertEqual(result.sheets[0], [24] * 8)

    def test_total_label_count_zero_returns_empty_result_not_an_error(self):
        result = build_print_sheets(quantity_in_cover=24, issue=0)
        self.assertEqual(result.sheets, [])
        self.assertEqual(result.total_sheet_count, 0)

    def test_remainder_appears_as_the_final_label(self):
        result = build_print_sheets(quantity_in_cover=24, issue=30010)
        flat = [q for sheet in result.sheets for q in sheet]
        self.assertEqual(flat[-1], 10)
        self.assertEqual(flat.count(24), 1250)

    def test_exact_multiple_of_eight_has_no_partial_final_sheet(self):
        result = build_print_sheets(quantity_in_cover=10, issue=80)
        self.assertEqual(len(result.sheets), 1)
        self.assertEqual(len(result.sheets[-1]), 8)


class BuildPrintSheetsExplicitRangeTests(SimpleTestCase):
    """002-print-layout-a4 User Story 2: explicit start/end range."""

    def test_valid_subrange_returns_matching_slice(self):
        full = build_print_sheets(quantity_in_cover=24, issue=30000)
        subrange = build_print_sheets(quantity_in_cover=24, issue=30000, start_sheet=1, end_sheet=50)
        self.assertEqual(subrange.start_sheet, 1)
        self.assertEqual(subrange.end_sheet, 50)
        self.assertEqual(subrange.sheets, full.sheets[:50])

    def test_start_greater_than_end_is_rejected(self):
        with self.assertRaises(InvalidSheetRange):
            build_print_sheets(quantity_in_cover=24, issue=30000, start_sheet=50, end_sheet=1)

    def test_end_beyond_total_sheet_count_is_rejected(self):
        with self.assertRaises(InvalidSheetRange):
            build_print_sheets(quantity_in_cover=24, issue=30000, start_sheet=150, end_sheet=200)

    def test_start_below_one_is_rejected(self):
        with self.assertRaises(InvalidSheetRange):
            build_print_sheets(quantity_in_cover=24, issue=30000, start_sheet=0, end_sheet=5)
