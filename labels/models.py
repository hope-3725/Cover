from django.core.validators import MinValueValidator
from django.db import models


class Layout(models.Model):
    """A saved label order record ("макет"). See data-model.md."""

    client_company = models.CharField(max_length=255)
    product_description = models.TextField()
    package_type = models.CharField(max_length=255)
    sap_code = models.CharField(max_length=255)
    po_number = models.CharField(max_length=255)
    order_date = models.DateField()
    quantity_in_cover = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Articles per box; printed on the label.",
    )
    issue = models.PositiveIntegerField(
        default=0,
        help_text="Total articles produced; internal only, never printed.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.client_company} - {self.product_description} (#{self.pk})"


class PrintEvent(models.Model):
    """A record of one print action taken on a Layout. See 002-print-layout-a4 data-model.md."""

    layout = models.ForeignKey(Layout, on_delete=models.CASCADE, related_name="print_events")
    sheet_start = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    sheet_end = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    printed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-printed_at"]

    def __str__(self):
        return f"Layout #{self.layout_id} sheets {self.sheet_start}-{self.sheet_end} @ {self.printed_at}"
