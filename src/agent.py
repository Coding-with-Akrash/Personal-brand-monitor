"""Personal Brand Monitor Agent — main LangGraph loop with human-in-the-loop approval."""

import argparse
import logging
import os
from datetime import datetime
from operator import add
from typing import Any, Dict, List

import yaml
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import Annotated, TypedDict

from tools.approval_queue import approval_queue_tool  # type: ignore[import]
from tools.mention_aggregator import mention_aggregator_tool  # type: ignore[import]
from tools.poster import poster_tool  # type: ignore[import]
from tools.priority_scorer import priority_scorer_tool  # type: ignore[import]
from tools.response_drafter import response_drafter_tool  # type: ignore[import]
from tools.sentiment_analyzer import sentiment_analyzer_tool  # type: ignore[import]

logger = logging.getLogger(__name__)

load_dotenv()

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.yaml")

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    logger.warning("config.yaml not found at %s, using defaults", CONFIG_PATH)
    config = {
        "agent": {"model": "gpt-4o-mini", "temperature": 0.5, "max_iterations": 10},
        "tools": {
            "mention_aggregator": {
                "enabled": True,
                "sources": ["github", "twitter", "linkedin"],
                "max_mentions_per_source": 10,
            },
            "sentiment_analyzer": {"enabled": True},
            "priority_scorer": {"enabled": True, "max_priority_mentions": 5},
            "response_drafter": {"enabled": True, "brand_voice": "professional_and_friendly"},
            "approval_queue": {"enabled": True, "auto_post": False},
            "poster": {"enabled": False},
        },
        "monitor": {"check_interval_minutes": 60, "brand_name": "YourNameOrBrand"},
    }


class AgentState(TypedDict):
    """State shared across the LangGraph agent nodes."""

    brand_name: str
    mentions: List[Dict[str, Any]]
    analyzed_mentions: List[Dict[str, Any]]
    priority_mentions: List[Dict[str, Any]]
    drafted_responses: List[Dict[str, Any]]
    approved_responses: List[Dict[str, Any]]
    posted_responses: List[Dict[str, Any]]
    messages: Annotated[list, add]


llm = ChatOpenAI(
    model=config["agent"]["model"],
    temperature=config["agent"]["temperature"],
    api_key=os.getenv("OPENAI_API_KEY"),  # type: ignore[arg-type]
)


def _get_brand(state: AgentState) -> str:
    return state.get("brand_name", os.getenv("BRAND_NAME", "YourName"))


def aggregate_node(state: AgentState) -> Dict[str, Any]:
    """Gather brand mentions from all configured sources."""
    brand = _get_brand(state)
    logger.info("Aggregating brand mentions for: %s", brand)
    try:
        mentions = mention_aggregator_tool(brand)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Mention aggregation failed: %s", exc)
        mentions = []
    return {
        "mentions": mentions,
        "messages": [f"Aggregated {len(mentions)} brand mentions"],
    }


def sentiment_node(state: AgentState) -> Dict[str, Any]:
    """Analyze sentiment of each mention."""
    mentions = state.get("mentions", [])
    analyzed: List[Dict[str, Any]] = []
    for m in mentions:
        try:
            sentiment = sentiment_analyzer_tool(m.get("text", ""))
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Sentiment analysis failed for mention: %s", exc)
            sentiment = "neutral"
        analyzed.append({**m, "sentiment": sentiment})
    return {
        "analyzed_mentions": analyzed,
        "messages": [f"Analyzed sentiment for {len(analyzed)} mentions"],
    }


def priority_node(state: AgentState) -> Dict[str, Any]:
    """Score and prioritize mentions."""
    analyzed = state.get("analyzed_mentions", [])
    max_mentions = config["tools"]["priority_scorer"]["max_priority_mentions"]
    try:
        priority = priority_scorer_tool(analyzed, max_mentions=max_mentions)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Priority scoring failed: %s", exc)
        priority = analyzed[:max_mentions]
    return {
        "priority_mentions": priority,
        "messages": [f"Selected {len(priority)} priority mentions"],
    }


def draft_node(state: AgentState) -> Dict[str, Any]:
    """Draft responses for priority mentions."""
    priority = state.get("priority_mentions", [])
    brand = _get_brand(state)
    responses: List[Dict[str, Any]] = []
    for m in priority:
        try:
            response = response_drafter_tool(m, brand)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Response drafting failed: %s", exc)
            response = f"Thanks for your mention of {brand}!"
        responses.append(
            {
                "mention": m,
                "drafted_response": response,
                "status": "pending_approval",
                "created_at": datetime.now().isoformat(),
            }
        )
    return {
        "drafted_responses": responses,
        "messages": [f"Drafted {len(responses)} responses"],
    }


def approval_node(state: AgentState) -> Dict[str, Any]:
    """Present responses for human approval via the approval queue."""
    responses = state.get("drafted_responses", [])
    try:
        approval_queue_tool(responses)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Approval queue save failed: %s", exc)
    approved = [{**r, "status": "pending_approval"} for r in responses]
    return {
        "approved_responses": approved,
        "messages": [f"{len(approved)} responses awaiting your approval"],
    }


def post_node(state: AgentState) -> Dict[str, Any]:
    """Post approved responses only if auto_post is enabled."""
    approved = state.get("approved_responses", [])
    auto_post = config["tools"]["poster"]["enabled"]
    posted: List[Dict[str, Any]] = []
    if auto_post:
        for r in approved:
            if r["status"] == "approved":
                try:
                    result = poster_tool(r["mention"], r["drafted_response"])
                    posted.append({**r, "status": "posted", "post_result": result})
                except Exception as exc:  # pylint: disable=broad-except
                    logger.exception("Posting failed: %s", exc)
                    posted.append({**r, "status": "failed", "error": str(exc)})
        return {
            "posted_responses": posted,
            "messages": [f"Posted {len(posted)} responses"],
        }
    posted = approved
    return {
        "posted_responses": posted,
        "messages": [f"Auto-post disabled. {len(posted)} responses ready for manual posting."],
    }


def build_workflow() -> CompiledStateGraph:
    """Build and compile the LangGraph agent workflow."""
    workflow = StateGraph(AgentState)

    workflow.add_node("aggregate", aggregate_node)
    workflow.add_node("sentiment", sentiment_node)
    workflow.add_node("priority", priority_node)
    workflow.add_node("draft", draft_node)
    workflow.add_node("approval", approval_node)
    workflow.add_node("post", post_node)

    workflow.set_entry_point("aggregate")
    workflow.add_edge("aggregate", "sentiment")
    workflow.add_edge("sentiment", "priority")
    workflow.add_edge("priority", "draft")
    workflow.add_edge("draft", "approval")
    workflow.add_edge("approval", "post")
    workflow.add_edge("post", END)

    return workflow.compile()


app = build_workflow()


def run_agent(brand_name: str = "YourName") -> Dict[str, Any]:
    """Execute the full agent loop for a given brand name.

    Returns the final agent state including all processed mentions and responses.
    """
    initial_state: AgentState = {
        "brand_name": brand_name,
        "mentions": [],
        "analyzed_mentions": [],
        "priority_mentions": [],
        "drafted_responses": [],
        "approved_responses": [],
        "posted_responses": [],
        "messages": [],
    }
    result = app.invoke(initial_state)
    for msg in result["messages"]:
        logger.info(msg)
    return result


def main() -> None:
    """CLI entry point for running the agent."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    parser = argparse.ArgumentParser(description="Personal Brand Monitor Agent")
    parser.add_argument("--brand", default="YourName", help="Brand name to monitor")
    args = parser.parse_args()
    run_agent(args.brand)


if __name__ == "__main__":
    main()
