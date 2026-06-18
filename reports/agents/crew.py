import json
import re

from crewai import Agent, Crew, LLM, Process, Task

from .evidence import build_citations_from_evidence, evidence_to_prompt_context


def build_crewai_agents(settings):
    """Define and create four agents that process raw data into usable insights."""
    if not settings.is_configured:
        raise RuntimeError("CrewAI agent settings are incomplete.")

    llm_kwargs = {
        "model": f"azure/{settings.azure_openai_chat_deployment}",
        "api_key": settings.azure_openai_api_key,
        "endpoint": settings.normalised_chat_endpoint,
        "api_version": settings.azure_openai_chat_api_version,
        "api": settings.chat_api_mode,
        "temperature": 0.2,
    }

    llm = LLM(**llm_kwargs)

    return [
        Agent(
            role="Source Collector Agent",
            goal="Collect external source candidates for competitor launch information.",
            backstory="You gather external launch evidence candidates without making claims.",
            llm=llm,
            verbose=False,
        ),

        Agent(
            role="Source Safety Agent",
            goal="Approve or skip untrusted source candidates before ingestion.",
            backstory="You protect the workflow from suspicious source content.",
            llm=llm,
            verbose=False,
        ),

        Agent(
            role="Launch Intelligence Analyst Agent",
            goal="Generate factual findings from approved retrieved evidence only.",
            backstory="You produce cited launch information without recommendations.",
            llm=llm,
            verbose=False,
        ),

        Agent(
            role="Evidence Auditor Agent",
            goal="Reject unsupported, overstated, uncited, or strategic claims.",
            backstory="You audit report claims against retrieved evidence.",
            llm=llm,
            verbose=False,
        ),
    ]


def run_crewai_report_generation(settings, company, product, workflow_evidence):
    agents = build_crewai_agents(settings)

    if len(agents) < 4:
        raise RuntimeError("CrewAI agents could not be initialised.")

    source_collector, source_safety, analyst, auditor = agents
    evidence_context = evidence_to_prompt_context(workflow_evidence)

    # Defining tasks for each of the role-based agents
    collector_task = Task(
        description=(
            "Summarize the retrieved source evidence available for "
            f"{product} by {company}. Use only this evidence:\n\n{evidence_context}"
        ),
        expected_output="A concise inventory of retrieved approved evidence.",
        agent=source_collector,
    )

    safety_task = Task(
        description=(
            "Confirm that only approved evidence is used. Do not use skipped source content. "
            "Return concise safety notes only."
        ),
        expected_output="A concise source-safety note.",
        agent=source_safety,
    )

    analyst_task = Task(
        description=(
            "Generate factual launch intelligence from the retrieved approved evidence. "
            "Do not provide strategic recommendations. Every accepted factual finding "
            "must include a citation_id from the evidence. Return JSON with this shape: "
            "timeline as a list of objects with date and event; themes as a list of "
            "objects with theme and summary; user_perception as an object with summary; "
            "confidence as an object with level and reason; agent_timeline as a list; "
            "rejected_claims as a list; citations as a list."
        ),
        expected_output="A structured JSON draft report with cited factual findings.",
        agent=analyst,
    )

    auditor_task = Task(
        description=(
            "Audit the analyst draft. Reject unsupported, overstated, uncited, or strategic "
            "claims. Return only the final JSON object with keys: timeline, themes, "
            "user_perception, confidence, agent_timeline, rejected_claims, citations. "
            "The user_perception value must be an object with a summary string. "
            "Rejected claim reasons must be one sentence."
        ),
        expected_output="A final audited JSON report object.",
        agent=auditor,
    )

    crew = Crew(
        agents=agents,
        tasks=[collector_task, safety_task, analyst_task, auditor_task],
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff()
    raw_output = getattr(result, "raw", str(result))
    report_data = parse_json_object(raw_output)
    report_data = normalise_report_data(report_data)
    report_data["citations"] = build_citations_from_evidence(workflow_evidence)

    return report_data


def parse_json_object(raw_output):
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_output, re.S)

        if not match:
            raise

        return json.loads(match.group(0))


def normalise_report_data(report_data):
    report_data = dict(report_data)

    user_perception = report_data.get("user_perception")

    if isinstance(user_perception, dict):
        user_perception.setdefault("summary", "")
    elif isinstance(user_perception, list):
        report_data["user_perception"] = {
            "summary": summarize_list_items(user_perception),
        }
    elif isinstance(user_perception, str):
        report_data["user_perception"] = {
            "summary": user_perception,
        }
    else:
        report_data["user_perception"] = {
            "summary": "No user perception evidence was available.",
        }

    return report_data


def summarize_list_items(items):
    summaries = []

    for item in items:
        if isinstance(item, dict):
            summary = item.get("summary") or item.get("text") or item.get("finding")
            if summary:
                summaries.append(str(summary))
        elif item:
            summaries.append(str(item))

    if not summaries:
        return "No user perception evidence was available."

    return " ".join(summaries)
