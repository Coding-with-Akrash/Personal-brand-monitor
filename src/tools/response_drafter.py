"""Response drafter — LLM-based personalized response drafting for brand mentions."""

import logging
import os

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


def response_drafter_tool(mention: dict, brand_name: str) -> str:
    """Draft a personalized response to a brand mention.

    Args:
        mention: Mention dict with keys text, sentiment, source, author.
        brand_name: The brand name to sign off with.

    Returns:
        A personalized response string.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.6,
        api_key=os.getenv("OPENAI_API_KEY"),  # type: ignore[arg-type]
    )
    prompt = PromptTemplate(
        input_variables=["mention_text", "sentiment", "source", "author", "brand_name"],
        template="""Draft a personalized response to this brand mention.

Brand: {brand_name}
Source: {source}
Author: {author}
Sentiment: {sentiment}
Mention: {mention_text}

Requirements:
- Match the sentiment tone (apologetic for negative, grateful for positive)
- Keep it under 200 characters for Twitter/X, under 500 for LinkedIn/GitHub
- Sound human, not robotic
- Include a call to action when appropriate
- Sign off with {brand_name} team

Response:""",
    )
    chain = prompt | llm
    try:
        response = chain.invoke(
            {
                "mention_text": mention.get("text", ""),
                "sentiment": mention.get("sentiment", "neutral"),
                "source": mention.get("source", "unknown"),
                "author": mention.get("author", "unknown"),
                "brand_name": brand_name,
            }
        )
        return str(response.content).strip()
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Response drafting LLM call failed: %s", exc)
        return (
            f"Thanks for your mention of {brand_name}! "
            f"We'll get back to you shortly. — {brand_name} team"
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = response_drafter_tool(
        {"text": "Great product!", "sentiment": "positive", "source": "twitter", "author": "user1"},
        "MyBrand",
    )
    print(result)
