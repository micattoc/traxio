from dataclasses import dataclass, field

# Defining class for checking environment variables required for agent orchestration workflow.

@dataclass(frozen=True)
class AgentSettings:
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_api_version: str
    azure_openai_chat_deployment: str

    @property
    def missing_required_values(self):
        required_values = {
            "AZURE_OPENAI_API_KEY": self.azure_openai_api_key,
            "AZURE_OPENAI_ENDPOINT": self.azure_openai_endpoint,
            "AZURE_OPENAI_API_VERSION": self.azure_openai_api_version,
            "AZURE_OPENAI_CHAT_DEPLOYMENT": self.azure_openai_chat_deployment,
        }

        return [
            name
            for name, value in required_values.items()
            if not value
        ]

    @property
    def is_configured(self):
        return not self.missing_required_values


@dataclass(frozen=True)
class WorkflowEvidence:
    timeline: list
    themes: list
    user_perception: list


@dataclass(frozen=True)
class WorkflowResult:
    report_data: dict
    warnings: list[str] = field(default_factory=list)
