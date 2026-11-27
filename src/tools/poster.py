"""Poster — placeholder auto-posting tool for approved responses."""

import logging
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)


def poster_tool(mention: dict, response: str) -> Dict[str, Any]:
    """Post a response to the original platform (placeholder for API integration).

    Args:
        mention: The original mention dict.
        response: The approved response text.

    Returns:
        A result dict with platform, response, posted_at, and status.
    """
    source = mention.get("source", "unknown")
    logger.info("[poster] Would post to %s: %s...", source, response[:100])
    return {
        "platform": source,
        "response": response,
        "posted_at": datetime.now().isoformat(),
        "status": "simulated",
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    poster_tool({"source": "twitter", "text": "test"}, "Thanks for the mention!")
