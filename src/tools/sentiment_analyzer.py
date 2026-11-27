"""Sentiment analyzer — LLM-based classification of brand mention sentiment."""

import logging
import os

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


def sentiment_analyzer_tool(text: str) -> str:
    """Classify mention sentiment as positive, neutral, or negative.

    Args:
        text: The mention text to classify.

    Returns:
        One of: "positive", "neutral", "negative".
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY"),  # type: ignore[arg-type]
    )
    prompt = PromptTemplate(
        input_variables=["text"],
        template=(
            "Classify the sentiment of this text as exactly one of: "
            "positive, neutral, or negative.\n\n"
            "Text: {text}\n\n"
            "Consider:\n"
            "- Positive: praise, appreciation, excitement, recommendations\n"
            "- Neutral: questions, general mentions, news sharing\n"
            "- Negative: criticism, complaints, bugs, warnings\n\n"
            "Return only the single word: positive, neutral, or negative\n\n"
            "Sentiment:"
        ),
    )
    chain = prompt | llm
    try:
        response = chain.invoke({"text": text[:1000]})
        sentiment = str(response.content).strip().lower()
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Sentiment analysis LLM call failed: %s", exc)
        sentiment = "neutral"
    if sentiment not in {"positive", "neutral", "negative"}:
        sentiment = "neutral"
    return sentiment


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = sentiment_analyzer_tool("I love this product, it's amazing!")
    print(result)
