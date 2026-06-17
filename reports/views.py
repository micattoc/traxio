from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Report
from .services import build_mock_report, validate_report_data
from .sources.collector import collect_source_candidates


def generate_report(request):
    """Generate preview of report (that can be later saved)."""
    preview = request.session.get("unsaved_report_preview")
    error = None

    if request.method == "POST":
        company = request.POST.get("company", "").strip()
        product = request.POST.get("product", "").strip()

        if company and product:
            report_data = build_mock_report(company, product)
            source_result = collect_source_candidates(company, product)
            is_valid, validation_error = validate_report_data(report_data)

            if is_valid:
                preview = {
                    "company": company,
                    "product": product,
                    "mode": Report.MODE_SINGLE,
                    "confidence_level": Report.CONFIDENCE_LOW,
                    "report_data": report_data,
                    "source_candidates": [
                        {
                            "title": candidate.title,
                            "url": candidate.url,
                            "source_type": candidate.source_type,
                            "metadata": candidate.metadata,
                        }
                        for candidate in source_result.candidates
                    ],
                    "source_warnings": source_result.warnings,
                }
                request.session["unsaved_report_preview"] = preview
            else:
                preview = None
                error = validation_error
                request.session.pop("unsaved_report_preview", None)
        else:
            preview = None
            error = "Company and product are required."
            request.session.pop("unsaved_report_preview", None)

    return render(
        request,
        "reports/generate.html",
        {
            "preview": preview,
            "error": error,
        },
    )


@require_POST
def save_report(request):
    """Save generated report to DB."""
    preview = request.session.get("unsaved_report_preview")

    if not preview:
        return redirect("reports:generate")

    is_valid, validation_error = validate_report_data(preview.get("report_data", {}))

    if not is_valid:
        request.session.pop("unsaved_report_preview", None)
        return render(
            request,
            "reports/generate.html",
            {
                "preview": None,
                "error": validation_error,
            },
        )

    report = Report.objects.create(
        user=request.user if request.user.is_authenticated else None,
        company=preview["company"],
        product=preview["product"],
        mode=preview["mode"],
        confidence_level=preview["confidence_level"],
        report_data=preview["report_data"],
    )

    request.session.pop("unsaved_report_preview", None)

    return redirect("reports:detail", pk=report.pk)


def history(request):
    """Return all saved reports that were previously generated."""
    reports = Report.objects.all()

    return render(
        request,
        "reports/history.html",
        {
            "reports": reports,
        },
    )


def report_detail(request, pk):
    """Get details of specific report."""
    report = get_object_or_404(Report, pk=pk)

    return render(
        request,
        "reports/detail.html",
        {
            "report": report,
            "report_data": report.report_data,
        },
    )
