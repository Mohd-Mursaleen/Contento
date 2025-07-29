"""Test configuration and fixtures."""

import pytest
import asyncio
from unittest.mock import AsyncMock
import os

# Set test environment variables
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["DATABASE_URL"] = "sqlite:///test.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return "This is a mock response from OpenAI API."


@pytest.fixture
def sample_research_data():
    """Sample research data for testing."""
    return {
        "key_findings": [
            "AI is transforming healthcare",
            "Machine learning improves diagnosis accuracy",
            "AI reduces medical errors"
        ],
        "main_arguments": [
            "AI enhances patient care",
            "AI reduces healthcare costs"
        ],
        "sources": [
            {
                "title": "AI in Healthcare Study",
                "url": "https://example.com/study",
                "source": "Medical Journal",
                "credibility_score": 0.9
            }
        ],
        "statistics": [
            {
                "statistic": "AI improves diagnosis accuracy",
                "value": "95%",
                "source": "Medical Research"
            }
        ],
        "expert_opinions": [
            {
                "opinion": "AI will revolutionize healthcare",
                "expert": "Dr. Smith",
                "source": "Healthcare Today"
            }
        ],
        "confidence_score": 0.8
    }


@pytest.fixture
def sample_writing_output():
    """Sample writing output for testing."""
    return {
        "title": "AI in Healthcare: Transforming Patient Care",
        "content": """# AI in Healthcare: Transforming Patient Care

## Introduction

Artificial Intelligence is revolutionizing the healthcare industry by improving diagnosis accuracy and reducing medical errors.

## Benefits of AI in Healthcare

AI provides numerous benefits including enhanced patient care and reduced healthcare costs.

## Conclusion

The future of healthcare lies in the integration of AI technologies.""",
        "outline": {
            "title": "AI in Healthcare: Transforming Patient Care",
            "introduction": {
                "hook": "AI is revolutionizing healthcare",
                "overview": "Learn about AI benefits in healthcare"
            },
            "main_sections": [
                {
                    "title": "Benefits of AI in Healthcare",
                    "subsections": ["Enhanced Care", "Cost Reduction"]
                }
            ]
        },
        "word_count": 150,
        "estimated_reading_time": 1,
        "metadata": {
            "title": "AI in Healthcare: Transforming Patient Care",
            "meta_description": "Learn how AI is transforming healthcare through improved diagnosis and patient care.",
            "keywords": ["AI", "healthcare", "artificial intelligence", "patient care"],
            "language": "en",
            "content_type": "article"
        }
    }