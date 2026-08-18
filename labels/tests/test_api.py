from rest_framework import status
from rest_framework.test import APITestCase

from labels.models import Layout

VALID_PAYLOAD = {
    "client_company": "Coca Cola HBC Greece",
    "product_description": "Coca Cola Zero Caffeine 0.25 ml",
    "package_type": "колие",
    "sap_code": "1201200012",
    "po_number": "4502825130",
    "order_date": "2025-10-28",
    "quantity_in_cover": 24,
    "issue": 30000,
}


class LayoutCreateTests(APITestCase):
    """Covers POST /api/layouts/ - User Story 1 (FR-001, FR-007, FR-009)."""

    def test_create_layout_returns_computed_fields(self):
        response = self.client.post("/api/layouts/", VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["full_label_count"], 1250)
        self.assertEqual(response.data["remainder"], 0)
        self.assertEqual(response.data["total_label_count"], 1250)
        self.assertEqual(response.data["total_sheet_count"], 157)
        self.assertEqual(Layout.objects.count(), 1)

    def test_create_blocks_missing_required_field(self):
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "client_company"}
        response = self.client.post("/api/layouts/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("client_company", response.data)
        self.assertEqual(Layout.objects.count(), 0)

    def test_create_rejects_zero_quantity_in_cover(self):
        payload = {**VALID_PAYLOAD, "quantity_in_cover": 0}
        response = self.client.post("/api/layouts/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity_in_cover", response.data)

    def test_create_rejects_derived_fields_supplied_by_client(self):
        payload = {**VALID_PAYLOAD, "total_sheet_count": 999}
        response = self.client.post("/api/layouts/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("total_sheet_count", response.data)


class LayoutListRetrieveTests(APITestCase):
    """Covers GET /api/layouts/ and GET /api/layouts/{id}/ - User Story 2 (FR-003, FR-004)."""

    def test_list_returns_saved_layouts(self):
        Layout.objects.create(**{**VALID_PAYLOAD, "order_date": "2025-10-28"})
        response = self.client.get("/api/layouts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["client_company"], "Coca Cola HBC Greece")

    def test_list_empty_when_no_layouts(self):
        response = self.client.get("/api/layouts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_retrieve_returns_single_layout(self):
        layout = Layout.objects.create(**{**VALID_PAYLOAD, "order_date": "2025-10-28"})
        response = self.client.get(f"/api/layouts/{layout.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], layout.id)

    def test_retrieve_missing_layout_returns_404(self):
        response = self.client.get("/api/layouts/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LayoutPrintSheetsTests(APITestCase):
    """Covers GET /api/layouts/{id}/print-sheets/ - 002 User Story 1 (full run)."""

    def _create(self, **overrides):
        return Layout.objects.create(**{**VALID_PAYLOAD, "order_date": "2025-10-28", **overrides})

    def test_full_run_standard_case(self):
        layout = self._create(quantity_in_cover=24, issue=30000)
        response = self.client.get(f"/api/layouts/{layout.id}/print-sheets/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["start_sheet"], 1)
        self.assertEqual(response.data["end_sheet"], 157)
        self.assertEqual(response.data["total_sheet_count"], 157)
        self.assertEqual(len(response.data["sheets"]), 157)
        self.assertEqual(len(response.data["sheets"][0]), 8)
        self.assertEqual(response.data["sheets"][0], [24] * 8)
        self.assertNotIn("issue", response.data["layout"])
        self.assertEqual(response.data["layout"]["client_company"], "Coca Cola HBC Greece")

    def test_remainder_placed_on_exactly_one_label(self):
        layout = self._create(quantity_in_cover=24, issue=30010)
        response = self.client.get(f"/api/layouts/{layout.id}/print-sheets/")
        flat = [q for sheet in response.data["sheets"] for q in sheet]
        self.assertEqual(flat.count(10), 1)
        self.assertEqual(flat.count(24), 1250)

    def test_final_sheet_partial_when_not_multiple_of_eight(self):
        layout = self._create(quantity_in_cover=10, issue=85)  # 9 labels -> last sheet has 1
        response = self.client.get(f"/api/layouts/{layout.id}/print-sheets/")
        self.assertEqual(response.data["total_sheet_count"], 2)
        self.assertEqual(len(response.data["sheets"][0]), 8)
        self.assertEqual(len(response.data["sheets"][1]), 1)

    def test_nothing_to_print_when_issue_zero(self):
        layout = self._create(quantity_in_cover=24, issue=0)
        response = self.client.get(f"/api/layouts/{layout.id}/print-sheets/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["sheets"], [])
        self.assertEqual(response.data["total_sheet_count"], 0)

    def test_print_sheets_missing_layout_returns_404(self):
        response = self.client.get("/api/layouts/999999/print-sheets/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LayoutPrintSheetsRangeTests(APITestCase):
    """Covers GET /api/layouts/{id}/print-sheets/?start=&end= - 002 User Story 2."""

    def _create(self, **overrides):
        return Layout.objects.create(**{**VALID_PAYLOAD, "order_date": "2025-10-28", **overrides})

    def test_valid_subrange(self):
        layout = self._create(quantity_in_cover=24, issue=30000)
        response = self.client.get(f"/api/layouts/{layout.id}/print-sheets/?start=1&end=50")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["start_sheet"], 1)
        self.assertEqual(response.data["end_sheet"], 50)
        self.assertEqual(len(response.data["sheets"]), 50)
        self.assertEqual(response.data["total_sheet_count"], 157)

    def test_out_of_bounds_range_rejected(self):
        layout = self._create(quantity_in_cover=24, issue=30000)
        response = self.client.get(f"/api/layouts/{layout.id}/print-sheets/?start=150&end=200")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("range", response.data["errors"])

    def test_start_greater_than_end_rejected(self):
        layout = self._create(quantity_in_cover=24, issue=30000)
        response = self.client.get(f"/api/layouts/{layout.id}/print-sheets/?start=50&end=1")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_range_defaults_to_full_run(self):
        layout = self._create(quantity_in_cover=24, issue=30000)
        response = self.client.get(f"/api/layouts/{layout.id}/print-sheets/")
        self.assertEqual(response.data["start_sheet"], 1)
        self.assertEqual(response.data["end_sheet"], 157)

    def test_non_integer_range_rejected(self):
        layout = self._create(quantity_in_cover=24, issue=30000)
        response = self.client.get(f"/api/layouts/{layout.id}/print-sheets/?start=abc&end=50")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LayoutUpdateTests(APITestCase):
    """Covers PUT /api/layouts/{id}/ - User Story 3 (FR-005, FR-009)."""

    def test_update_saves_changes_in_place(self):
        layout = Layout.objects.create(**{**VALID_PAYLOAD, "order_date": "2025-10-28"})
        payload = {**VALID_PAYLOAD, "issue": 30024}
        response = self.client.put(f"/api/layouts/{layout.id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], layout.id)
        self.assertEqual(response.data["full_label_count"], 1251)
        self.assertEqual(Layout.objects.count(), 1)  # no duplicate created
        layout.refresh_from_db()
        self.assertEqual(layout.issue, 30024)

    def test_update_validation_failure_leaves_prior_version_intact(self):
        layout = Layout.objects.create(**{**VALID_PAYLOAD, "order_date": "2025-10-28"})
        payload = {**VALID_PAYLOAD, "quantity_in_cover": 0}
        response = self.client.put(f"/api/layouts/{layout.id}/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        layout.refresh_from_db()
        self.assertEqual(layout.quantity_in_cover, 24)  # unchanged


class LayoutPrintEventsTests(APITestCase):
    """Covers GET/POST /api/layouts/{id}/print-events/ - 002 User Story 3."""

    def _create(self, **overrides):
        return Layout.objects.create(**{**VALID_PAYLOAD, "order_date": "2025-10-28", **overrides})

    def test_list_empty_when_never_printed(self):
        layout = self._create()
        response = self.client.get(f"/api/layouts/{layout.id}/print-events/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])

    def test_create_print_event_full_run(self):
        layout = self._create(quantity_in_cover=24, issue=30000)
        response = self.client.post(f"/api/layouts/{layout.id}/print-events/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["sheet_start"], 1)
        self.assertEqual(response.data["sheet_end"], 157)
        self.assertIn("printed_at", response.data)

    def test_create_print_event_explicit_range(self):
        layout = self._create(quantity_in_cover=24, issue=30000)
        response = self.client.post(
            f"/api/layouts/{layout.id}/print-events/",
            {"sheet_start": 1, "sheet_end": 50},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["sheet_start"], 1)
        self.assertEqual(response.data["sheet_end"], 50)

    def test_create_print_event_invalid_range_rejected(self):
        layout = self._create(quantity_in_cover=24, issue=30000)
        response = self.client.post(
            f"/api/layouts/{layout.id}/print-events/",
            {"sheet_start": 150, "sheet_end": 200},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_returns_events_newest_first(self):
        layout = self._create(quantity_in_cover=24, issue=30000)
        self.client.post(f"/api/layouts/{layout.id}/print-events/", {"sheet_start": 1, "sheet_end": 50}, format="json")
        self.client.post(f"/api/layouts/{layout.id}/print-events/", {"sheet_start": 51, "sheet_end": 157}, format="json")
        response = self.client.get(f"/api/layouts/{layout.id}/print-events/")
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["sheet_start"], 51)

    def test_print_events_missing_layout_returns_404(self):
        response = self.client.get("/api/layouts/999999/print-events/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LayoutPreviewTests(APITestCase):
    """Covers POST /api/layouts/preview/ - User Story 1 (FR-006, FR-008)."""

    def test_preview_computes_without_persisting(self):
        response = self.client.post(
            "/api/layouts/preview/",
            {"quantity_in_cover": 24, "issue": 30010},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["full_label_count"], 1250)
        self.assertEqual(response.data["remainder"], 10)
        self.assertEqual(response.data["total_label_count"], 1251)
        self.assertEqual(response.data["total_sheet_count"], 157)
        self.assertEqual(Layout.objects.count(), 0)

    def test_preview_issue_zero(self):
        response = self.client.post(
            "/api/layouts/preview/",
            {"quantity_in_cover": 24, "issue": 0},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_label_count"], 0)
        self.assertEqual(response.data["total_sheet_count"], 0)

    def test_preview_rejects_zero_quantity_in_cover(self):
        response = self.client.post(
            "/api/layouts/preview/",
            {"quantity_in_cover": 0, "issue": 100},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity_in_cover", response.data)
