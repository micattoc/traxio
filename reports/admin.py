from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "company",
        "mode",
        "confidence_level",
        "saved_at",
    )
    list_filter = ("mode", "confidence_level", "saved_at")
    search_fields = ("company", "product")