"""Pytest configuration and fixtures for Personal Brand Monitor tests."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def sample_mention():
    """Return a sample mention dict."""
    return {
        "source": "twitter",
        "title": "Tweet",
        "text": "Just launched my project using MyBrand! Love the developer experience. 🚀",
        "url": "https://twitter.com/i/web/status/1234567890",
        "author": "tech_guru",
        "created_at": "2024-01-15T09:00:00Z",
        "sentiment": "positive",
    }


@pytest.fixture
def sample_mentions():
    """Return a list of sample mentions."""
    return [
        {
            "source": "github",
            "author": "developer123",
            "sentiment": "negative",
            "text": "I keep getting timeout errors on large files. Any ETA on a fix?",
        },
        {
            "source": "twitter",
            "author": "tech_guru",
            "sentiment": "positive",
            "text": "Just launched my project using MyBrand! Love the developer experience. 🚀",
        },
        {
            "source": "linkedin",
            "author": "recruiter_99",
            "sentiment": "neutral",
            "text": "Has anyone used MyBrand for production workloads?",
        },
    ]
