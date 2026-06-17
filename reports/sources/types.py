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
