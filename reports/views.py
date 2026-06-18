from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .agents.workflow import WorkflowExecutionError, run_launch_intelligence_workflow
from .evidence.indexing import index_approved_sources
from .guards.output_guard import ReportOutputGuard
from .guards.output_repair import ReportOutputRepairer
from .models import Report
from .sources.collector import collect_source_candidates
from .sources.screening import screen_source_candidates


def generate_report(request):
    """Generate preview of report (that can be later saved)."""
    preview = request.session.get("unsaved_report_preview")
    error = None

    if request.method == "POST":
        company = request.POST.get("company", "").strip()
        product = request.POST.get("product", "").strip()

        if company and product:
            source_result = collect_source_candidates(company, product)
            screening_result = screen_source_candidates(source_result.candidates)
            evidence_result = index_approved_sources(
                approved_sources=screening_result.approved_sources,
                company=company,
                product=product,
            )
            try:
                workflow_result = run_launch_intelligence_workflow(
                    company=company,
                    product=product,
                    evidence_run_id=evidence_result.run_id,
                )
            except WorkflowExecutionError as workflow_error:
                preview = None
                error = f"Workflow failed: {workflow_error}"
                request.session.pop("unsaved_report_preview", None)
                return render(
                    request,
                    "reports/generate.html",
                    {
                        "preview": preview,
                        "error": error,
                    },
                )
            
            guard_result = validate_and_repair_report_data(
                workflow_result.report_data,
                workflow_evidence=workflow_result.workflow_evidence,
                skipped_sources=screening_result.skipped_sources,
            )

            report_data = guard_result["report_data"]

            if guard_result["is_valid"]:
                display_report_data = build_display_report_data(report_data)
                preview = {
                    "company": company,
                    "product": product,
                    "mode": Report.MODE_SINGLE,
                    "confidence_level": Report.CONFIDENCE_LOW,
                    "report_data": report_data,
                    "display_report_data": display_report_data,
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
                    "approved_sources": [
                        {
                            "title": approved_source.candidate.title,
                            "url": approved_source.candidate.url,
                            "source_type": approved_source.candidate.source_type,
                            "metadata": approved_source.candidate.metadata,
                            "guard_summary": approved_source.guard_summary,
                        }
                        for approved_source in screening_result.approved_sources
                    ],
                    "skipped_sources": [
                        {
                            "title": skipped_source.candidate.title,
                            "url": skipped_source.candidate.url,
                            "source_type": skipped_source.candidate.source_type,
                            "reason": skipped_source.reason,
                        }
                        for skipped_source in screening_result.skipped_sources
                    ],
                    "guard_warnings": screening_result.warnings,
                    "output_guard_warnings": guard_result["warnings"],
                    "evidence_run_id": evidence_result.run_id,
                    "indexed_source_count": evidence_result.indexed_source_count,
                    "evidence_warnings": evidence_result.warnings,
                }
                request.session["unsaved_report_preview"] = preview
            else:
                preview = None
                error = guard_result["user_message"]
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


def validate_and_repair_report_data(report_data, workflow_evidence=None, skipped_sources=None):
    output_guard = ReportOutputGuard()
    output_guard_result = output_guard.validate(
        report_data,
        skipped_sources=skipped_sources,
    )

    # Check that the report passes output guard
    if output_guard_result.is_valid:
        return {
            "is_valid": True,
            "report_data": report_data,
            "warnings": [],
            "user_message": "",
        }

    # Fix the report based on output guard failures
    repair_result = ReportOutputRepairer().repair(
        report_data,
        workflow_evidence=workflow_evidence,
    )

    # Check that the repaired report still passes output guard
    repaired_guard_result = output_guard.validate(
        repair_result.report_data,
        skipped_sources=skipped_sources,
    )

    if repaired_guard_result.is_valid:
        return {
            "is_valid": True,
            "report_data": repair_result.report_data,
            "warnings": repair_result.applied_repairs,
            "user_message": "",
        }

    return {
        "is_valid": False,
        "report_data": report_data,
        "warnings": [],
        "user_message": (
            "The generated report could not be safely displayed because it did not "
            "pass final evidence checks. Please try generating the report again."
        ),
    }


def build_display_report_data(report_data):
    """Build the final report ready for display."""
    display_report_data = dict(report_data)
    citation_lookup = {
        citation.get("id"): {
            "label": f"[{index}]",
            "title": citation.get("title", "Source"),
            "url": citation.get("url", ""),
        }
        for index, citation in enumerate(report_data.get("citations", []), start=1)
        if isinstance(citation, dict) and citation.get("id")
    }

    display_report_data["timeline"] = [
        attach_display_citations(item, citation_lookup)
        for item in report_data.get("timeline", [])
    ]
    
    display_report_data["themes"] = [
        attach_display_citations(item, citation_lookup)
        for item in report_data.get("themes", [])
    ]

    display_report_data["user_perception"] = attach_display_citations(
        report_data.get("user_perception", {}),
        citation_lookup,
    )

    return display_report_data


def attach_display_citations(item, citation_lookup):
    if not isinstance(item, dict):
        return item

    display_item = dict(item)
    citation_ids = []

    if item.get("citation_id"):
        citation_ids.append(item["citation_id"])

    if item.get("citation_ids"):
        citation_ids.extend(item["citation_ids"])

    display_item["display_citations"] = [
        citation_lookup[citation_id]
        for citation_id in dict.fromkeys(citation_ids)
        if citation_id in citation_lookup
    ]

    return display_item


@require_POST
def save_report(request):
    """Save generated report to DB."""
    preview = request.session.get("unsaved_report_preview")

    if not preview:
        return redirect("reports:generate")

    output_guard = ReportOutputGuard()
    output_guard_result = output_guard.validate(
        preview.get("report_data", {}),
        skipped_sources=preview.get("skipped_sources", []),
    )

    if not output_guard_result.is_valid:
        request.session.pop("unsaved_report_preview", None)
        return render(
            request,
            "reports/generate.html",
            {
                "preview": None,
                "error": (
                    "The report could not be saved because it no longer passes "
                    "final evidence checks. Please generate it again."
                ),
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
            "display_report_data": build_display_report_data(report.report_data),
        },
    )
