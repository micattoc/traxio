import os

import requests

from .types import SourceCandidate, SourceCollectionResult


NEWS_API_URL = "https://newsapi.org/v2/everything"


def fetch_news_sources(company, product):
    """Get sources from News API."""
    api_key = os.getenv("NEWS_API_KEY")

    if not api_key:
        return SourceCollectionResult(
            candidates=[],
            warnings=["News API key is not configured."],
        )

    query = f'"{product}" "{company}" launch OR announces OR releases OR funding OR partnership'

    response = requests.get(
        NEWS_API_URL,
        params={
            "q": query,
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": 10,
            "apiKey": api_key,
        },
        timeout=20,
    )
    response.raise_for_status()

    payload = response.json()
    articles = payload.get("articles", [])

    candidates = []

    for article in articles:
        title = article.get("title") or "Untitled article"
        description = article.get("description") or ""
        content = article.get("content") or description
        url = article.get("url")

        if not url or not content:
            continue

        candidates.append(
            SourceCandidate(
                title=title,
                url=url,
                source_type="press",
                content=content,
                metadata={
                    "company": company,
                    "product": product,
                    "published_at": article.get("publishedAt"),
                    "publisher": (article.get("source") or {}).get("name"),
                },
            )
        )

    return SourceCollectionResult(candidates=candidates)
