from django.test import TestCase

from labels.models import Layout, PrintEvent

VALID_LAYOUT = {
    "client_company": "Coca Cola HBC Greece",
    "product_description": "Coca Cola Zero Caffeine 0.25 ml",
    "package_type": "колие",
    "sap_code": "1201200012",
    "po_number": "4502825130",
    "order_date": "2025-10-28",
    "quantity_in_cover": 24,
    "issue": 30000,
}


class LayoutNewViewTests(TestCase):
    """Sanity check for User Story 1's new-layout page (T015-T018)."""

    def test_new_layout_page_renders(self):
        response = self.client.get("/layouts/new/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "layout-form")


class LayoutListViewTests(TestCase):
    """Covers the layout list page - User Story 2 (FR-003)."""

    def test_empty_state_shown_when_no_layouts(self):
        response = self.client.get("/layouts/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Нов макет")
        self.assertNotContains(response, "Coca Cola")

    def test_lists_saved_layouts(self):
        Layout.objects.create(**VALID_LAYOUT)
        response = self.client.get("/layouts/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Coca Cola HBC Greece")


class LayoutEditViewTests(TestCase):
    """Covers the edit flow - User Story 3 (FR-005)."""

    def test_edit_page_prefilled_with_existing_values(self):
        layout = Layout.objects.create(**VALID_LAYOUT)
        response = self.client.get(f"/layouts/{layout.id}/edit/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Coca Cola HBC Greece")
        self.assertContains(response, 'data-mode="edit"')
        self.assertContains(response, f'data-layout-id="{layout.id}"')

    def test_detail_page_links_to_edit(self):
        layout = Layout.objects.create(**VALID_LAYOUT)
        response = self.client.get(f"/layouts/{layout.id}/")
        self.assertContains(response, f"/layouts/{layout.id}/edit/")

    def test_edit_missing_layout_returns_404(self):
        response = self.client.get("/layouts/999999/edit/")
        self.assertEqual(response.status_code, 404)


class LayoutDetailViewTests(TestCase):
    """Covers the layout detail page - User Story 2 (FR-004)."""

    def test_detail_shows_saved_parameters_and_preview(self):
        layout = Layout.objects.create(**VALID_LAYOUT)
        response = self.client.get(f"/layouts/{layout.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Coca Cola HBC Greece")
        self.assertContains(response, "1250")  # full_label_count from the reference example

    def test_detail_missing_layout_returns_404(self):
        response = self.client.get("/layouts/999999/")
        self.assertEqual(response.status_code, 404)

    def test_detail_links_to_print(self):
        layout = Layout.objects.create(**VALID_LAYOUT)
        response = self.client.get(f"/layouts/{layout.id}/")
        self.assertContains(response, f"/layouts/{layout.id}/print/")


class LayoutPrintViewTests(TestCase):
    """002-print-layout-a4 User Story 1: full-run printable page."""

    def test_print_page_renders_full_run(self):
        layout = Layout.objects.create(**VALID_LAYOUT)
        response = self.client.get(f"/layouts/{layout.id}/print/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "print-button")
        self.assertContains(response, "ЛИТО")
        self.assertContains(response, "БАЛКАН")
        self.assertContains(response, "EN ISO 9001:2015")
        self.assertContains(response, "ОД 08.05.00.01")
        # 157 sheets for the reference example -> 157 ".sheet" divs
        self.assertEqual(response.content.decode("utf-8").count('class="sheet"'), 157)

    def test_print_page_missing_layout_returns_404(self):
        response = self.client.get("/layouts/999999/print/")
        self.assertEqual(response.status_code, 404)

    def test_print_page_nothing_to_print(self):
        layout = Layout.objects.create(**{**VALID_LAYOUT, "issue": 0})
        response = self.client.get(f"/layouts/{layout.id}/print/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Няма какво да се разпечата")

    def test_valid_range_renders_only_requested_sheets(self):
        layout = Layout.objects.create(**VALID_LAYOUT)
        response = self.client.get(f"/layouts/{layout.id}/print/?start=1&end=50")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8").count('class="sheet"'), 50)

    def test_invalid_range_redirects_to_detail_with_message(self):
        layout = Layout.objects.create(**VALID_LAYOUT)
        response = self.client.get(f"/layouts/{layout.id}/print/?start=150&end=200", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, f"/layouts/{layout.id}/")
        self.assertContains(response, "Неуспешен печат")


class LayoutDetailPrintHistoryTests(TestCase):
    """002-print-layout-a4 User Story 3: print history on the detail page."""

    def test_never_printed_shows_indicator(self):
        layout = Layout.objects.create(**VALID_LAYOUT)
        response = self.client.get(f"/layouts/{layout.id}/")
        self.assertContains(response, "не е бил печатан")

    def test_single_print_event_shown(self):
        layout = Layout.objects.create(**VALID_LAYOUT)
        PrintEvent.objects.create(layout=layout, sheet_start=1, sheet_end=157)
        response = self.client.get(f"/layouts/{layout.id}/")
        self.assertNotContains(response, "не е бил печатан")
        self.assertContains(response, "1")
        self.assertContains(response, "157")

    def test_multiple_print_events_all_shown(self):
        layout = Layout.objects.create(**VALID_LAYOUT)
        PrintEvent.objects.create(layout=layout, sheet_start=1, sheet_end=50)
        PrintEvent.objects.create(layout=layout, sheet_start=51, sheet_end=157)
        response = self.client.get(f"/layouts/{layout.id}/")
        content = response.content.decode("utf-8")
        self.assertEqual(content.count('class="print-event"'), 2)


class LayoutDetailRangeFormTests(TestCase):
    """002-print-layout-a4 User Story 2: range-selection form on the detail page."""

    def test_detail_page_has_range_form(self):
        layout = Layout.objects.create(**VALID_LAYOUT)
        response = self.client.get(f"/layouts/{layout.id}/")
        self.assertContains(response, 'name="start"')
        self.assertContains(response, 'name="end"')
