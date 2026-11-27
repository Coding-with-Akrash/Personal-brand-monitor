import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from tools.approval_queue import approval_queue_tool
from tools.poster import poster_tool
from tools.priority_scorer import priority_scorer_tool
from tools.response_drafter import response_drafter_tool
from tools.sentiment_analyzer import sentiment_analyzer_tool


class _MockChain:
    """Credential-free stand-in for the LangChain runnable chain."""

    def __init__(self, sentiment="neutral", response="Thanks! — Brand team"):
        self._sentiment = sentiment
        self._response = response

    def invoke(self, inputs):
        text = str(inputs.get("text", "") or "")
        mentions_text = str(inputs.get("mentions_text", "") or "")
        mention_text = str(inputs.get("mention_text", "") or "")
        brand = str(inputs.get("brand_name", "MyBrand") or "MyBrand")

        if "Rank these brand mentions" in mentions_text:
            return MagicMock(content="")
        if "Classify the sentiment" in mentions_text or not mention_text:
            low = text.lower()
            if any(w in low for w in ["love", "great", "amazing", "🚀"]):
                content = "positive"
            elif any(w in low for w in ["bug", "error", "fail", "broken", "timeout"]):
                content = "negative"
            else:
                content = "neutral"
        else:
            content = (
                f"Thanks for your mention of {brand}! "
                f"We appreciate your feedback. — {brand} team"
            )
        return MagicMock(content=content)


class _MockLLM:
    """Callable LLM stand-in so `prompt | llm` resolves via RunnableLambda."""

    def __call__(self, *args, **kwargs):
        return _MockChain()

    def __or__(self, prompt):
        return _MockChain()


class TestTools(unittest.TestCase):

    @patch("tools.sentiment_analyzer.ChatOpenAI", _MockLLM)
    def test_sentiment_returns_valid(self):
        result = sentiment_analyzer_tool("I love this product!")
        self.assertIn(result, ["positive", "neutral", "negative"])

    @patch("tools.priority_scorer.ChatOpenAI", _MockLLM)
    def test_priority_scorer_ranks(self):
        mentions = [
            {"source": "github", "author": "u1", "sentiment": "negative", "text": "Bug report"},
            {"source": "twitter", "author": "u2", "sentiment": "positive", "text": "Great!"},
        ]
        result = priority_scorer_tool(mentions, max_mentions=2)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["priority_rank"], 1)

    @patch("tools.response_drafter.ChatOpenAI", _MockLLM)
    def test_response_drafter(self):
        mention = {
            "text": "Great product!",
            "sentiment": "positive",
            "source": "twitter",
            "author": "user1",
        }
        result = response_drafter_tool(mention, "MyBrand")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 10)

    def test_poster_simulation(self):
        result = poster_tool({"source": "twitter"}, "Test response")
        self.assertEqual(result["status"], "simulated")

    def test_approval_queue_returns_true(self):
        responses = [
            {
                "mention": {"text": "test"},
                "drafted_response": "Thanks!",
                "status": "pending_approval",
            }
        ]
        result = approval_queue_tool(responses)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
