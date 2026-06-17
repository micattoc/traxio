from reports.guards.input_guard import SourceInputGuard

from .types import ApprovedSource, SkippedSource, SourceScreeningResult


def screen_source_candidates(candidates):
    """Check each collected source against Input Guard."""
    input_guard = SourceInputGuard()
    approved_sources = []
    skipped_sources = []
    warnings = []

    if input_guard.warning:
        warnings.append(input_guard.warning)

    for candidate in candidates:
        is_approved, reason = input_guard.validate(candidate)

        if is_approved:
            approved_sources.append(
                ApprovedSource(
                    candidate=candidate,
                    guard_summary=reason,
                )
            )
        else:
            skipped_sources.append(
                SkippedSource(
                    candidate=candidate,
                    reason=reason,
                )
            )

    return SourceScreeningResult(
        approved_sources=approved_sources,
        skipped_sources=skipped_sources,
        warnings=warnings,
    )
