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
        missing_values = ", ".join(settings.missing_required_values)
        raise WorkflowExecutionError(
            f"Agent LLM settings are incomplete: {missing_values}."
        )

    workflow_evidence = collect_workflow_evidence(
        company=company,
        product=product,
        run_id=evidence_run_id,
    )

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
    )
