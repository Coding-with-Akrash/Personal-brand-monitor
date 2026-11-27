"""Mention aggregator — scrapes GitHub, Twitter/X, and LinkedIn for brand mentions."""

import logging
import os
from typing import Any, Dict, List

import requests

logger = logging.getLogger(__name__)


def mention_aggregator_tool(brand_name: str) -> List[Dict[str, Any]]:
    """Search GitHub, Twitter/X, and LinkedIn for brand mentions.

    Returns a list of mention dicts with keys: source, title, text, url, author, created_at.
    """
    mentions: List[Dict[str, Any]] = []

    # GitHub search (issues, PRs, comments mentioning brand)
    try:
        url = "https://api.github.com/search/issues"
        headers = {"Accept": "application/vnd.github.v3+json"}
        params = {"q": f'"{brand_name}"', "per_page": 5}
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"
        resp = requests.get(url, headers=headers, params=params, timeout=15)  # type: ignore[arg-type]
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("items", []):
                mentions.append(
                    {
                        "source": "github",
                        "title": item.get("title", ""),
                        "text": (item.get("body") or "")[:500],
                        "url": item.get("html_url", ""),
                        "author": item.get("user", {}).get("login", "unknown"),
                        "created_at": item.get("created_at", ""),
                    }
                )
        else:
            logger.warning("GitHub search returned status %s", resp.status_code)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("GitHub search error: %s", exc)

    # Twitter/X search (requires API v2 bearer token)
    try:
        bearer = os.getenv("TWITTER_BEARER_TOKEN")
        if bearer:
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {"Authorization": f"Bearer {bearer}"}
            params = {
                "query": f'"{brand_name}"',
                "max_results": 5,
                "tweet.fields": "author_id,created_at",
            }
            resp = requests.get(url, headers=headers, params=params, timeout=15)  # type: ignore[arg-type]
            if resp.status_code == 200:
                data = resp.json()
                for tweet in data.get("data", []):
                    mentions.append(
                        {
                            "source": "twitter",
                            "title": "Tweet",
                            "text": tweet.get("text", ""),
                            "url": f"https://twitter.com/i/web/status/{tweet.get('id', '')}",
                            "author": tweet.get("author_id", "unknown"),
                            "created_at": tweet.get("created_at", ""),
                        }
                    )
            else:
                logger.warning("Twitter search returned status %s", resp.status_code)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Twitter search error: %s", exc)

    # LinkedIn (public profile scraping is limited without API)
    mentions.append(
        {
            "source": "linkedin",
            "title": "LinkedIn mention (demo)",
            "text": f"Demo mention of {brand_name} on LinkedIn - connect API for real data",
            "url": "",
            "author": "demo_user",
            "created_at": "",
        }
    )

    logger.info("Aggregated %d mentions for brand %s", len(mentions), brand_name)
    return mentions


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = mention_aggregator_tool("OpenAI")
    for m in result[:3]:
        print(f"[{m['source']}] {m['title']}: {m['text'][:80]}...")
