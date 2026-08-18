from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Layout, PrintEvent
from .serializers import LayoutSerializer, PrintEventSerializer
from .services import InvalidSheetRange, build_print_sheets, compute_label_count


class PreviewInputSerializer(serializers.Serializer):
    quantity_in_cover = serializers.IntegerField(min_value=1)
    issue = serializers.IntegerField(min_value=0)


def _parse_optional_int(raw, field_name):
    if raw in (None, ""):
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise InvalidSheetRange(f"'{field_name}' must be an integer.")


def _parse_sheet_range(query_params):
    """Parse optional start/end query params to ints, or None if absent (full run)."""
    return (
        _parse_optional_int(query_params.get("start"), "start"),
        _parse_optional_int(query_params.get("end"), "end"),
    )


def _layout_summary(layout):
    """The subset of a layout's fields printed on its labels (FR-003) - never `issue`.

    `order_date` is serialized to an ISO string explicitly (not left as a raw
    `date` object) so behavior matches contracts/print-api.md regardless of
    whether this dict is consumed through DRF's JSON renderer (real HTTP) or
    in-process (layouts_ui's RequestFactory pattern) - a raw `date` object
    passed into a Django template gets auto-localized (e.g. "Oct. 28, 2025"),
    which would silently diverge from the documented "2025-10-28" contract.
    """
    return {
        "id": layout.id,
        "client_company": layout.client_company,
        "product_description": layout.product_description,
        "package_type": layout.package_type,
        "sap_code": layout.sap_code,
        "po_number": layout.po_number,
        "order_date": layout.order_date.isoformat(),
    }


class LayoutViewSet(viewsets.ModelViewSet):
    queryset = Layout.objects.all()
    serializer_class = LayoutSerializer

    def list(self, request, *args, **kwargs):
        # contracts/layouts-api.md: list responses are wrapped in "results"
        # (no filtering/search in this feature - spec Assumptions).
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({"results": serializer.data})

    @action(detail=False, methods=["post"])
    def preview(self, request):
        """Compute derived counts for candidate values without persisting (FR-006, FR-008)."""
        input_serializer = PreviewInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        counts = compute_label_count(**input_serializer.validated_data)
        return Response(
            {
                "full_label_count": counts.full_label_count,
                "remainder": counts.remainder,
                "total_label_count": counts.total_label_count,
                "total_sheet_count": counts.total_sheet_count,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get", "post"], url_path="print-events")
    def print_events(self, request, pk=None):
        """List a layout's print history, or record a new print action (research.md S2)."""
        layout = self.get_object()

        if request.method == "GET":
            events = layout.print_events.all()
            return Response({"results": PrintEventSerializer(events, many=True).data})

        try:
            start_sheet = _parse_optional_int(request.data.get("sheet_start"), "sheet_start")
            end_sheet = _parse_optional_int(request.data.get("sheet_end"), "sheet_end")
            result = build_print_sheets(layout.quantity_in_cover, layout.issue, start_sheet, end_sheet)
        except InvalidSheetRange as exc:
            return Response({"errors": {"range": str(exc)}}, status=status.HTTP_400_BAD_REQUEST)

        if not result.sheets:
            return Response(
                {"errors": {"range": "There is nothing to print for this layout."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event = PrintEvent.objects.create(
            layout=layout, sheet_start=result.start_sheet, sheet_end=result.end_sheet
        )
        return Response(PrintEventSerializer(event).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="print-sheets")
    def print_sheets(self, request, pk=None):
        """Compute the sheets/labels for a print job, without recording anything (research.md S2)."""
        layout = self.get_object()
        try:
            start_sheet, end_sheet = _parse_sheet_range(request.query_params)
            result = build_print_sheets(layout.quantity_in_cover, layout.issue, start_sheet, end_sheet)
        except InvalidSheetRange as exc:
            return Response({"errors": {"range": str(exc)}}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "layout": _layout_summary(layout),
                "start_sheet": result.start_sheet,
                "end_sheet": result.end_sheet,
                "total_sheet_count": result.total_sheet_count,
                "sheets": result.sheets,
            },
            status=status.HTTP_200_OK,
        )
