from rest_framework import serializers

from .models import Layout, PrintEvent
from .services import compute_label_count

DERIVED_FIELD_NAMES = (
    "full_label_count",
    "remainder",
    "total_label_count",
    "total_sheet_count",
)


class LayoutSerializer(serializers.ModelSerializer):
    full_label_count = serializers.SerializerMethodField()
    remainder = serializers.SerializerMethodField()
    total_label_count = serializers.SerializerMethodField()
    total_sheet_count = serializers.SerializerMethodField()

    class Meta:
        model = Layout
        fields = [
            "id",
            "client_company",
            "product_description",
            "package_type",
            "sap_code",
            "po_number",
            "order_date",
            "quantity_in_cover",
            "issue",
            "full_label_count",
            "remainder",
            "total_label_count",
            "total_sheet_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        # Derived fields (data-model.md) are read-only and must never be
        # accepted as input - contracts/layouts-api.md requires them to be
        # rejected, not silently ignored, if supplied on write.
        submitted_derived = set(self.initial_data or {}) & set(DERIVED_FIELD_NAMES)
        if submitted_derived:
            raise serializers.ValidationError(
                {
                    field: "This field is computed and cannot be set directly."
                    for field in submitted_derived
                }
            )
        return attrs

    def _counts(self, obj):
        quantity_in_cover = obj.get("quantity_in_cover") if isinstance(obj, dict) else obj.quantity_in_cover
        issue = obj.get("issue") if isinstance(obj, dict) else obj.issue
        return compute_label_count(quantity_in_cover, issue)

    def get_full_label_count(self, obj):
        return self._counts(obj).full_label_count

    def get_remainder(self, obj):
        return self._counts(obj).remainder

    def get_total_label_count(self, obj):
        return self._counts(obj).total_label_count

    def get_total_sheet_count(self, obj):
        return self._counts(obj).total_sheet_count


class PrintEventSerializer(serializers.ModelSerializer):
    """Output shaping only - range resolution/validation happens via
    labels.services.build_print_sheets before a PrintEvent is constructed
    (research.md S4), not through this serializer's input validation."""

    class Meta:
        model = PrintEvent
        fields = ["id", "sheet_start", "sheet_end", "printed_at"]
        read_only_fields = fields
