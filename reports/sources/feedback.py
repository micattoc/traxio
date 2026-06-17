import requests

from .types import SourceCandidate, SourceCollectionResult


HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"


def fetch_public_feedback_sources(company, product):
    """Get sources via full-text search of the HackerNews community site."""
    response = requests.get(
        HN_SEARCH_URL,
        params={
            "query": f"{product} {company}",
            "tags": "story",
            "hitsPerPage": 10,
        },
        timeout=20,
    )
    response.raise_for_status()

    payload = response.json()
    hits = payload.get("hits", [])

    candidates = []

    for hit in hits:
        title = hit.get("title") or hit.get("story_title") or "Hacker News discussion"
        object_id = hit.get("objectID")
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"

        candidates.append(
            SourceCandidate(
                title=title,
                url=url,
                source_type="public_feedback",
                content=title,
                metadata={
                    "company": company,
                    "product": product,
                    "published_at": hit.get("created_at"),
                    "hn_object_id": object_id,
                    "points": hit.get("points"),
                    "comments_count": hit.get("num_comments"),
                },
            )
        )

    return SourceCollectionResult(candidates=candidates)
