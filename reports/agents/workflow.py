from .config import get_agent_settings
from .crew import run_crewai_report_generation
from .evidence import collect_workflow_evidence
from .types import WorkflowResult


class WorkflowExecutionError(Exception):
    pass


def run_launch_intelligence_workflow(company, product, evidence_run_id):
    """Initiate CrewAI orchestration workflow."""
    settings = get_agent_settings()

    if not settings.is_configured:
        raise WorkflowExecutionError(
            " ".join(settings.configuration_errors)
        )

    try:
        workflow_evidence = collect_workflow_evidence(
            company=company,
            product=product,
            run_id=evidence_run_id,
        )
    except Exception as error:
        raise WorkflowExecutionError(f"Evidence retrieval failed: {error}") from error

    if not workflow_evidence.timeline and not workflow_evidence.themes:
        raise WorkflowExecutionError(
            "No retrieved indexed evidence was available for timeline or theme analysis."
        )

    try:
        report_data = run_crewai_report_generation(
            settings=settings,
            company=company,
            product=product,
            workflow_evidence=workflow_evidence,
        )
    except Exception as error:
        raise WorkflowExecutionError(f"CrewAI workflow failed: {error}") from error

    return WorkflowResult(
        report_data=report_data,
        workflow_evidence=workflow_evidence,
    )
