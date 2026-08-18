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


class PrintEventModelTests(TestCase):
    """002-print-layout-a4 User Story 3: PrintEvent model (data-model.md)."""

    def test_create_print_event(self):
        layout = Layout.objects.create(**VALID_LAYOUT)
        event = PrintEvent.objects.create(layout=layout, sheet_start=1, sheet_end=50)
        self.assertIsNotNone(event.printed_at)
        self.assertEqual(event.sheet_start, 1)
        self.assertEqual(event.sheet_end, 50)

    def test_layout_related_name_print_events(self):
        layout = Layout.objects.create(**VALID_LAYOUT)
        PrintEvent.objects.create(layout=layout, sheet_start=1, sheet_end=50)
        PrintEvent.objects.create(layout=layout, sheet_start=51, sheet_end=157)
        self.assertEqual(layout.print_events.count(), 2)

    def test_default_ordering_is_newest_first(self):
        layout = Layout.objects.create(**VALID_LAYOUT)
        first = PrintEvent.objects.create(layout=layout, sheet_start=1, sheet_end=50)
        second = PrintEvent.objects.create(layout=layout, sheet_start=51, sheet_end=157)
        ordered = list(layout.print_events.all())
        self.assertEqual(ordered, [second, first])

    def test_deleting_layout_deletes_its_print_events(self):
        layout = Layout.objects.create(**VALID_LAYOUT)
        PrintEvent.objects.create(layout=layout, sheet_start=1, sheet_end=157)
        layout.delete()
        self.assertEqual(PrintEvent.objects.count(), 0)
