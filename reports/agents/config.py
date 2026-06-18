import os

from .types import AgentSettings


def get_agent_settings():
    return AgentSettings(
        azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
        azure_openai_chat_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT", ""),
        azure_openai_chat_api_version=os.getenv("AZURE_OPENAI_CHAT_API_VERSION", ""),
        azure_openai_chat_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", ""),
    )
