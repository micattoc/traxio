import os

import requests

from .types import SourceCandidate, SourceCollectionResult


PRODUCTHUNT_GRAPHQL_URL = "https://api.producthunt.com/v2/api/graphql"


def fetch_producthunt_sources(company, product):
    """Get sources from ProductHunt via GraphQL."""
    token = os.getenv("PRODUCTHUNT_ACCESS_TOKEN")

    if not token:
        return SourceCollectionResult(
            candidates=[],
            warnings=["ProductHunt token is not configured."],
        )

    query = """
                query SearchPosts($query: String!) {
                posts(first: 5, search: $query) {
                    edges {
                    node {
                        id
                        name
                        tagline
                        description
                        url
                        createdAt
                        votesCount
                        commentsCount
                    }
                    }
                }
                }
            """

    response = requests.post(
        PRODUCTHUNT_GRAPHQL_URL,
        headers={"Authorization": f"Bearer {token}"},
        json={"query": query, "variables": {"query": product}},
        timeout=20,
    )
    response.raise_for_status()

    payload = response.json()
    edges = payload.get("data", {}).get("posts", {}).get("edges", [])

    candidates = []

    for edge in edges:
        node = edge.get("node", {})
        title = node.get("name") or product
        tagline = node.get("tagline") or ""
        description = node.get("description") or ""
        content = "\n".join(part for part in [title, tagline, description] if part)
        url = node.get("url") or ""

        if not url or not content:
            continue

        candidates.append(
            SourceCandidate(
                title=title,
                url=url,
                source_type="producthunt",
                content=content,
                metadata={
                    "producthunt_id": node.get("id"),
                    "company": company,
                    "product": product,
                    "published_at": node.get("createdAt"),
                    "votes_count": node.get("votesCount"),
                    "comments_count": node.get("commentsCount"),
                },
            )
        )

    return SourceCollectionResult(candidates=candidates)
