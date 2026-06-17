from .feedback import fetch_public_feedback_sources
from .filters import keep_external_sources_only
from .news import fetch_news_sources
from .producthunt import fetch_producthunt_sources
from .types import SourceCollectionResult


def collect_source_candidates(company, product):
    """Gather all sources from external sites and filter for purely external info (not PR)."""
    collected_candidates = []
    warnings = []

    collectors = [
        fetch_producthunt_sources,
        fetch_news_sources,
        fetch_public_feedback_sources,
    ]

    for collector in collectors:
        try:
            result = collector(company, product)
        except Exception as error:
            warnings.append(f"{collector.__name__} failed: {error}")
            continue

        collected_candidates.extend(result.candidates)
        warnings.extend(result.warnings)

    external_candidates = keep_external_sources_only(collected_candidates, company)

    return SourceCollectionResult(
        candidates=external_candidates,
        warnings=warnings,
    )
