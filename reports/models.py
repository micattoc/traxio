from django.conf import settings
from django.db import models


class Report(models.Model):
    MODE_SINGLE = "single"
    MODE_COMPARISON = "comparison"

    MODE_CHOICES = [
        (MODE_SINGLE, "Single Competitor"),
        (MODE_COMPARISON, "Comparison"),
    ]

    CONFIDENCE_LOW = "low"
    CONFIDENCE_MEDIUM = "medium"
    CONFIDENCE_HIGH = "high"

    CONFIDENCE_CHOICES = [
        (CONFIDENCE_LOW, "Low"),
        (CONFIDENCE_MEDIUM, "Medium"),
        (CONFIDENCE_HIGH, "High"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    company = models.CharField(max_length=255)
    product = models.CharField(max_length=255)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    confidence_level = models.CharField(max_length=20, choices=CONFIDENCE_CHOICES)
    report_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-saved_at"]

    def __str__(self):
        return f"{self.product} report"