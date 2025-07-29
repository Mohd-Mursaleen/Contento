# Content Creation Pipeline MVP

A simple but robust MVP implementation of an AI-powered content creation pipeline using multi-agent architecture.

## Features

- **Multi-Agent System**: Research and Writer agents working in coordination
- **RESTful API**: FastAPI-based API for content creation
- **Database Integration**: Supabase integration for data persistence
- **Quality Assessment**: Basic quality scoring for generated content
- **Async Processing**: Background task processing for content generation
- **Clean Architecture**: Modular, testable, and extensible codebase

## Architecture

```
┌─────────────────────────────────────────┐
│              FastAPI App                │
├─────────────────────────────────────────┤
│           Content Orchestrator          │
├─────────────────────────────────────────┤
│  Research Agent    │    Writer Agent    │
├─────────────────────────────────────────┤
│            Supabase Database            │
└─────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

1. **Clone and setup environment:**
   ```bash
   git clone <repository>
   cd content-pipeline
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Set up database:**
   The database schema is already created via Supabase MCP. The tables include:
   - `organizations`
   - `users`
   - `content_requests`
   - `content_pieces`
   - `agent_tasks`
   - `quality_assessments`

4. **Run the application:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Usage

### Create Content

```bash
curl -X POST "http://localhost:8000/api/v1/content/create" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "topic": "artificial intelligence in healthcare",
    "content_type": "blog_post",
    "target_audience": "healthcare professionals",
    "word_count": 800,
    "style_requirements": {
      "tone": "professional",
      "include_statistics": true
    }
  }'
```

### Get Content Status

```bash
curl "http://localhost:8000/api/v1/content/{content_id}/status"
```

### Retrieve Generated Content

```bash
curl "http://localhost:8000/api/v1/content/{content_id}"
```

### List All Content

```bash
curl "http://localhost:8000/api/v1/content?limit=10&offset=0"
```

## Project Structure

```
content-pipeline/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Abstract base class for agents
│   │   ├── research_agent.py      # Research and information gathering
│   │   └── writer_agent.py        # Content creation and writing
│   ├── core/
│   │   ├── __init__.py
│   │   └── orchestrator.py        # Main pipeline coordinator
│   ├── models/
│   │   ├── __init__.py
│   │   └── content.py             # Pydantic models and enums
│   ├── config.py                  # Configuration management
│   └── main.py                    # FastAPI application
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Test configuration and fixtures
│   ├── test_agents.py            # Agent tests
│   └── test_orchestrator.py      # Orchestrator tests
├── requirements.txt
├── .env.example
└── README.md
```

## Agent Details

### Research Agent
- **Purpose**: Gathers information and validates sources
- **Capabilities**:
  - Wikipedia API integration
  - Search query generation
  - Source credibility scoring
  - Information structuring using AI

### Writer Agent
- **Purpose**: Creates structured, engaging content
- **Capabilities**:
  - Content outline generation
  - Multi-section writing
  - Style adaptation
  - Metadata generation
  - Reading time calculation

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_agents.py -v
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI agents | Required |
| `DATABASE_URL` | Supabase database connection string | Required |
| `REDIS_URL` | Redis connection for caching | `redis://localhost:6379` |
| `MAX_CONTENT_LENGTH` | Maximum content word count | `5000` |
| `DEFAULT_QUALITY_THRESHOLD` | Minimum quality score | `0.7` |

### Content Types

- `blog_post`: Conversational blog articles
- `article`: Professional informative articles
- `product_description`: Marketing-focused descriptions
- `social_media`: Short, engaging posts
- `email`: Personal, action-oriented content

## Quality Metrics

The system calculates several quality scores:

- **Overall Quality**: Based on content length, research depth, and structure
- **SEO Score**: Title length, meta description, headings, keyword usage
- **Fact-Check Score**: Based on research confidence and source credibility
- **Research Depth**: Number and quality of sources used

## Error Handling

The system includes comprehensive error handling:

- Input validation
- API timeout handling
- Graceful degradation
- Detailed error messages
- Background task error recovery

## Future Enhancements

This MVP provides a solid foundation for adding:

- Additional agents (SEO, Editor, Fact-Checker, Visual)
- Advanced quality gates
- User authentication and authorization
- Rate limiting and usage tracking
- Content templates and personalization
- Multi-language support
- Advanced analytics and reporting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For questions or issues:
1. Check the API documentation at `/docs`
2. Review the test files for usage examples
3. Check logs for detailed error information