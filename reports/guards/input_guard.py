"""Input Guard checks the source content of extracted sources,
skipping suspicious sources (identified via prompt injection patterns).
"""

import re

from reports.sources.types import SourceCandidate


PROMPT_INJECTION_PATTERNS = [
    re.compile(r"\bignore (all )?(previous|prior|above) instructions\b", re.I),
    re.compile(r"\bdisregard (all )?(previous|prior|above) instructions\b", re.I),
    re.compile(r"\bsystem prompt\b", re.I),
    re.compile(r"\bdeveloper message\b", re.I),
    re.compile(r"\byou are (now )?(chatgpt|an ai|an assistant|a language model)\b", re.I),
    re.compile(r"\bact as\b.*\b(dan|jailbreak|unrestricted)\b", re.I),
    re.compile(r"\bdo anything now\b", re.I),
    re.compile(r"\breveal\b.*\b(instructions|prompt|system message)\b", re.I),
    re.compile(r"\bexfiltrate\b", re.I),
]


class SourceInputGuard:
    def validate(self, source_candidate: SourceCandidate):
        content = source_candidate.content.strip()

        if not content:
            return False, "Source content is empty."

        heuristic_reason = self._check_prompt_injection_patterns(content)

        if heuristic_reason:
            return False, heuristic_reason

        return True, "Passed input guard checks."

    @property
    def warning(self):
        return ""

    def _check_prompt_injection_patterns(self, content):
        for pattern in PROMPT_INJECTION_PATTERNS:
            if pattern.search(content):
                return "Skipped by input guard for prompt-injection-like instructions."

        return ""
