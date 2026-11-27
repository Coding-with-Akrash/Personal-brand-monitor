"""Approval queue — saves drafted responses for human review before posting."""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def approval_queue_tool(responses: List[Dict[str, Any]]) -> bool:
    """Present drafted responses for human approval and save to queue.

    Writes approval_queue.json and approval_queue.md to the OUTPUT_DIR
    (defaults to demo/).

    Args:
        responses: List of drafted response dicts.

    Returns:
        True if the queue was saved successfully.
    """
    output_dir = os.getenv("OUTPUT_DIR", "demo")
    os.makedirs(output_dir, exist_ok=True)

    queue_data = {
        "generated_at": datetime.now().isoformat(),
        "total_pending": len(responses),
        "responses": responses,
    }

    try:
        with open(os.path.join(output_dir, "approval_queue.json"), "w", encoding="utf-8") as f:
            json.dump(queue_data, f, indent=2)

        md_lines = ["# Approval Queue - Responses Pending Review\n"]
        for r in responses:
            m = r["mention"]
            md_lines.append(
                f"## Source: {m.get('source', 'unknown')}"
                f" | Sentiment: {m.get('sentiment', 'neutral')}"
            )
            md_lines.append(f"**Mention:** {m.get('text', '')[:200]}")
            md_lines.append(f"**Drafted Response:** {r['drafted_response']}")
            md_lines.append(f"**Status:** {r['status']}\n")
        with open(os.path.join(output_dir, "approval_queue.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        logger.info(
            "[approval_queue] %d responses saved to %s/approval_queue.*", len(responses), output_dir
        )
        return True
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to save approval queue: %s", exc)
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    approval_queue_tool(
        [{"mention": {"text": "test"}, "drafted_response": "Thanks!", "status": "pending_approval"}]
    )
