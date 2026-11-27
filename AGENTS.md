# Personal Brand Monitor Agent

This document describes how to work with the Personal Brand Monitor agent in Kilo.

## Project Overview

The Personal Brand Monitor is an autonomous agent that monitors GitHub, Twitter/X, and LinkedIn for mentions of your name or brand, analyzes sentiment, scores priority, drafts personalized responses, and routes them through a human-in-the-loop approval queue before anything is posted.

## Agent Loop

1. Aggregate mentions → 2. Analyze sentiment → 3. Score priority → 4. Draft responses → 5. Await approval → 6. Post (optional)

## Key Files

- `src/agent.py` — Main LangGraph agent loop with human-in-the-loop approval
- `src/tools/mention_aggregator.py` — Scrapes GitHub, Twitter/X, LinkedIn mentions
- `src/tools/sentiment_analyzer.py` — LLM-based sentiment classification
- `src/tools/priority_scorer.py` — LLM-based priority scoring
- `src/tools/response_drafter.py` — LLM-based personalized response drafting
- `src/tools/approval_queue.py` — Human approval queue (saves to demo/)
- `src/tools/poster.py` — Placeholder auto-posting tool
- `config.yaml` — Agent configuration (model, sources, intervals)
- `prompts/` — System, sentiment, and response prompts
- `tests/test_agent.py` — Unit tests for tools

## Running the Agent

```bash
pip install -e .
cp .env.example .env
# Edit .env with your API keys and brand name
python -m src.agent --brand "YourName"
```

## Testing

```bash
pip install -e .[dev]
pytest
```

## Linting and Type Checking

```bash
ruff check src tests
black --check src tests
mypy src
```

## Instagram Advertising

See `INSTAGRAM_KIT.md` for reel scripts, captions, hashtags, and demo assets.
