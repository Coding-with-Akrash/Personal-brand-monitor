# Personal Brand Monitor Agent

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/framework-langgraph-green.svg)](https://langchain-ai.github.io/langgraph/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An autonomous agent that monitors GitHub, Twitter/X, and LinkedIn for mentions of your name or brand, analyzes sentiment, scores priority, drafts personalized responses, and routes them through a human-in-the-loop approval queue before anything is posted.

---
## ✨ Features

| Feature | Description |
|---------|-------------|
| **Mention Aggregator** | Scrapes GitHub, Twitter/X, and LinkedIn for brand mentions |
| **Sentiment Analyzer** | Classifies mentions as positive, neutral, or negative via LLM |
| **Priority Scorer** | Ranks mentions by influence, urgency, and sentiment |
| **Response Drafter** | Writes personalized replies in your brand voice |
| **Approval Queue** | Human-in-the-loop — you approve before anything is posted |
| **Auto-Poster** | Optional automated posting once approved |

## 🔄 Agentic Loop

```
1. Aggregate mentions  →  2. Analyze sentiment  →  3. Score priority
                                                        ↓
4. Draft responses  →  5. Await approval  →  6. Post (optional)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- OpenAI API key
- GitHub token (optional, for higher rate limits)
- Twitter/X Bearer Token (optional)
- LinkedIn Access Token (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/personal-brand-monitor.git
cd personal-brand-monitor

# Install the package
pip install -e .

# For development (linting, testing)
pip install -e .[dev]
```

### Configuration

```bash
cp .env.example .env
```

Edit `.env` with your API keys and brand name:

```env
OPENAI_API_KEY=your_openai_api_key_here
BRAND_NAME=YourNameOrBrand
GITHUB_TOKEN=your_github_token_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token_here
OUTPUT_DIR=demo
```

### Run the Agent

```bash
python -m src.agent --brand "YourName"
```

Or use the installed CLI:

```bash
personal-brand-monitor --brand "YourName"
```

## 📁 Project Structure

```
personal-brand-monitor/
├── pyproject.toml          # Package configuration
├── config.yaml             # Agent configuration (model, sources, intervals)
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── LICENSE                 # MIT License
├── README.md               # This file
├── AGENTS.md               # Kilo agent instructions
├── CONTRIBUTING.md         # Contribution guide
├── INSTAGRAM_KIT.md        # Instagram advertising assets
├── src/
│   ├── __init__.py
│   ├── agent.py            # Main LangGraph agent loop
│   └── tools/
│       ├── __init__.py
│       ├── mention_aggregator.py   # GitHub/Twitter/LinkedIn scraping
│       ├── sentiment_analyzer.py   # LLM sentiment classification
│       ├── priority_scorer.py      # Priority ranking
│       ├── response_drafter.py     # Personalized response writing
│       ├── approval_queue.py       # Human approval workflow
│       └── poster.py               # Optional auto-posting
├── prompts/
│   ├── system_prompt.txt
│   ├── sentiment_prompt.txt
│   └── response_prompt.txt
├── demo/
│   ├── example_mentions.json
│   └── sample_output.md
└── tests/
    ├── conftest.py
    └── test_agent.py
```

## 🧪 Testing

```bash
pip install -e .[dev]
pytest
```

### Linting and Type Checking

```bash
ruff check src tests
black --check src tests
mypy src
```

## 🤝 Contributing

Contributions are welcome! Please see [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "feat: add your feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a pull request

## 📄 License

This project is licensed under the MIT License — see [`LICENSE`](LICENSE) for details.

## 🙋‍♂️ Support

- Open an issue for bugs or feature requests
- Follow on Instagram for demo reels and updates

---

Build by Akrash with ❤️ using LangGraph, LangChain, and OpenAI.
