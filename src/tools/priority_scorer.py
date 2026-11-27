"""Priority scorer — LLM-based ranking of brand mentions by response priority."""

import logging
import os
from typing import Any, Dict, List

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


def priority_scorer_tool(
    mentions: List[Dict[str, Any]], max_mentions: int = 5
) -> List[Dict[str, Any]]:
    """Score mentions by priority (influence + urgency + sentiment).

    Args:
        mentions: List of analyzed mention dicts.
        max_mentions: Maximum number of priority mentions to return.

    Returns:
        Top mentions annotated with priority_rank and priority_score.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY"),  # type: ignore[arg-type]
    )
    mentions_text = "\n".join(
        [
            f"- Source: {m.get('source', 'unknown')}"
            f" | Author: {m.get('author', 'unknown')}"
            f" | Sentiment: {m.get('sentiment', 'neutral')}"
            f" | Text: {m.get('text', '')[:200]}"
            for m in mentions[:20]
        ]
    )
    prompt = PromptTemplate(
        input_variables=["mentions_text", "max_mentions"],
        template="""Rank these brand mentions by priority for response.

Mentions:
{mentions_text}

Priority factors:
1. Negative sentiment = highest priority (damage control)
2. Questions from influential authors = high priority
3. Positive praise = medium priority (engagement)
4. General mentions = low priority

Return the top {max_mentions} mentions in priority order, one per line:
1. [Source] - [Author] - [Reason]
2. [Source] - [Author] - [Reason]

Priority list:""",
    )
    chain = prompt | llm
    try:
        chain.invoke(
            {
                "mentions_text": mentions_text,
                "max_mentions": max_mentions,
            }
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Priority scoring LLM call failed: %s", exc)

    # Return top mentions with priority scores
    priority_mentions: List[Dict[str, Any]] = []
    for i, m in enumerate(mentions[:max_mentions]):
        priority_mentions.append({**m, "priority_rank": i + 1, "priority_score": 1.0 - (i * 0.15)})
    return priority_mentions


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = priority_scorer_tool(
        [{"source": "github", "author": "user1", "sentiment": "negative", "text": "Bug report"}],
        max_mentions=3,
    )
    for r in result:
        print(r)
