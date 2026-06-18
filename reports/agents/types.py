from dataclasses import dataclass, field
from urllib.parse import urlparse

# Defining class for checking environment variables required for agent orchestration workflow.

@dataclass(frozen=True)
class AgentSettings:
    azure_openai_api_key: str
    azure_openai_chat_endpoint: str
    azure_openai_chat_api_version: str
    azure_openai_chat_deployment: str

    @property
    def missing_required_values(self):
        required_values = {
            "AZURE_OPENAI_API_KEY": self.azure_openai_api_key,
            "AZURE_OPENAI_CHAT_ENDPOINT": self.azure_openai_chat_endpoint,
            "AZURE_OPENAI_CHAT_API_VERSION": self.azure_openai_chat_api_version,
            "AZURE_OPENAI_CHAT_DEPLOYMENT": self.azure_openai_chat_deployment,
        }

        return [
            name
            for name, value in required_values.items()
            if not value
        ]

    @property
    def normalised_chat_endpoint(self):
        endpoint = self.azure_openai_chat_endpoint.strip().rstrip("/")

        if not endpoint:
            return endpoint

        parsed_endpoint = urlparse(endpoint)

        if not parsed_endpoint.scheme or not parsed_endpoint.netloc:
            return endpoint

        return f"{parsed_endpoint.scheme}://{parsed_endpoint.netloc}"

    @property
    def chat_api_mode(self):
        endpoint = self.normalised_chat_endpoint

        if not endpoint:
            return "completions"

        hostname = urlparse(endpoint).hostname or ""

        if hostname.endswith(".services.ai.azure.com"):
            return "responses"

        return "completions"

    @property
    def configuration_errors(self):
        errors = []

        if self.missing_required_values:
            missing_values = ", ".join(self.missing_required_values)
            errors.append(f"Agent LLM settings are incomplete: {missing_values}.")

        endpoint = self.azure_openai_chat_endpoint.strip()

        if endpoint:
            parsed_endpoint = urlparse(endpoint)
            hostname = parsed_endpoint.hostname or ""

            if parsed_endpoint.scheme not in {"http", "https"} or not parsed_endpoint.netloc:
                errors.append(
                    "AZURE_OPENAI_CHAT_ENDPOINT must be an absolute URL, for example "
                    "https://<chat-resource>.services.ai.azure.com/openai/v1/responses."
                )
            elif (
                hostname.endswith(".services.ai.azure.com")
                and parsed_endpoint.path
                and not parsed_endpoint.path.rstrip("/").endswith(("/openai/v1", "/openai/v1/responses"))
            ):
                errors.append(
                    "AZURE_OPENAI_CHAT_ENDPOINT for a Foundry services.ai.azure.com "
                    "chat deployment must be the target URI ending in /openai/v1/responses, "
                    "or the same resource host without a path."
                )

        return errors

    @property
    def is_configured(self):
        return not self.configuration_errors


@dataclass(frozen=True)
class WorkflowEvidence:
    timeline: list
    themes: list
    user_perception: list


@dataclass(frozen=True)
class WorkflowResult:
    report_data: dict
    workflow_evidence: WorkflowEvidence | None = None
    warnings: list[str] = field(default_factory=list)
