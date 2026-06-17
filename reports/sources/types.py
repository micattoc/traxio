from dataclasses import dataclass, field
from typing import Any

# Definining types for storing source information


@dataclass(frozen=True)
class SourceCandidate:
    title: str
    url: str
    source_type: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SourceCollectionResult:
    candidates: list[SourceCandidate]
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ApprovedSource:
    candidate: SourceCandidate
    guard_summary: str


@dataclass(frozen=True)
class SkippedSource:
    candidate: SourceCandidate
    reason: str


@dataclass(frozen=True)
class SourceScreeningResult:
    approved_sources: list[ApprovedSource]
    skipped_sources: list[SkippedSource]
    warnings: list[str] = field(default_factory=list)
