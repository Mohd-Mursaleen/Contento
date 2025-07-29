"""Tests for AI agents."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.agents.research_agent import ResearchAgent
from app.agents.writer_agent import WriterAgent
from app.models.content import AgentType, ContentType


class TestResearchAgent:
    """Test cases for ResearchAgent."""
    
    @pytest.fixture
    def research_agent(self):
        return ResearchAgent()
    
    @pytest.mark.asyncio
    async def test_research_agent_initialization(self, research_agent):
        """Test research agent initialization."""
        assert research_agent.agent_type == AgentType.RESEARCH
        assert hasattr(research_agent, 'search_engines')
    
    @pytest.mark.asyncio
    async def test_validate_input_valid(self, research_agent):
        """Test input validation with valid data."""
        valid_input = {"topic": "artificial intelligence"}
        result = await research_agent.validate_input(valid_input)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_input_invalid(self, research_agent):
        """Test input validation with invalid data."""
        invalid_input = {}
        result = await research_agent.validate_input(invalid_input)
        assert result is False
    
    @pytest.mark.asyncio
    @patch('app.agents.research_agent.ResearchAgent.call_openai')
    async def test_generate_search_queries(self, mock_openai, research_agent):
        """Test search query generation."""
        mock_openai.return_value = '["AI overview", "AI trends", "AI statistics", "AI expert opinion", "AI applications"]'
        
        queries = await research_agent._generate_search_queries("artificial intelligence")
        
        assert isinstance(queries, list)
        assert len(queries) == 5
        assert "AI overview" in queries
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.get')
    async def test_search_wikipedia(self, mock_get, research_agent):
        """Test Wikipedia search functionality."""
        # Mock Wikipedia API response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Artificial Intelligence",
            "extract": "AI is a branch of computer science...",
            "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/AI"}}
        }
        mock_get.return_value = mock_response
        
        results = await research_agent._search_wikipedia("artificial intelligence")
        
        assert len(results) == 1
        assert results[0]["source"] == "Wikipedia"
        assert results[0]["title"] == "Artificial Intelligence"
    
    @pytest.mark.asyncio
    @patch('app.agents.research_agent.ResearchAgent.call_openai')
    @patch('app.agents.research_agent.ResearchAgent._gather_information')
    async def test_execute_success(self, mock_gather, mock_openai, research_agent):
        """Test successful research execution."""
        # Mock data
        mock_gather.return_value = [
            {"source": "Wikipedia", "title": "AI", "content": "AI content", "credibility_score": 0.8}
        ]
        mock_openai.return_value = '{"key_findings": ["AI is important"], "main_arguments": ["AI helps automation"]}'
        
        input_data = {"topic": "artificial intelligence", "depth": 2}
        result = await research_agent.execute(input_data)
        
        assert result["status"] == "success"
        assert "research_data" in result
        assert "confidence_score" in result


class TestWriterAgent:
    """Test cases for WriterAgent."""
    
    @pytest.fixture
    def writer_agent(self):
        return WriterAgent()
    
    @pytest.mark.asyncio
    async def test_writer_agent_initialization(self, writer_agent):
        """Test writer agent initialization."""
        assert writer_agent.agent_type == AgentType.WRITER
        assert hasattr(writer_agent, 'style_templates')
    
    @pytest.mark.asyncio
    async def test_validate_input_valid(self, writer_agent):
        """Test input validation with valid data."""
        valid_input = {"topic": "machine learning"}
        result = await writer_agent.validate_input(valid_input)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_input_invalid(self, writer_agent):
        """Test input validation with invalid data."""
        invalid_input = {}
        result = await writer_agent.validate_input(invalid_input)
        assert result is False
    
    @pytest.mark.asyncio
    @patch('app.agents.writer_agent.WriterAgent.call_openai')
    async def test_create_outline(self, mock_openai, writer_agent):
        """Test content outline creation."""
        mock_outline = {
            "title": "Understanding Machine Learning",
            "introduction": {"hook": "ML is transforming industries", "overview": "Learn ML basics"},
            "main_sections": [{"title": "What is ML", "subsections": ["Definition", "Types"]}],
            "conclusion": {"summary": "ML is powerful", "call_to_action": "Start learning"}
        }
        mock_openai.return_value = str(mock_outline).replace("'", '"')
        
        research_data = {"key_findings": ["ML is important"], "main_arguments": ["ML automates tasks"]}
        outline = await writer_agent._create_outline(research_data, ContentType.BLOG_POST, "developers", "machine learning")
        
        assert "title" in outline
        assert "introduction" in outline
        assert "main_sections" in outline
    
    @pytest.mark.asyncio
    def test_calculate_reading_time(self, writer_agent):
        """Test reading time calculation."""
        content = " ".join(["word"] * 225)  # 225 words
        reading_time = writer_agent._calculate_reading_time(content)
        assert reading_time == 1  # Should be 1 minute
        
        content = " ".join(["word"] * 450)  # 450 words
        reading_time = writer_agent._calculate_reading_time(content)
        assert reading_time == 2  # Should be 2 minutes
    
    @pytest.mark.asyncio
    def test_extract_keywords(self, writer_agent):
        """Test keyword extraction."""
        content = "Machine learning algorithms are powerful tools for data analysis and artificial intelligence applications."
        keywords = writer_agent._extract_keywords(content)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert any("machine" in keyword.lower() or "learning" in keyword.lower() for keyword in keywords)


@pytest.mark.asyncio
async def test_agent_integration():
    """Test integration between research and writer agents."""
    research_agent = ResearchAgent()
    writer_agent = WriterAgent()
    
    # Mock research data
    research_data = {
        "key_findings": ["AI is transforming industries", "Machine learning is a subset of AI"],
        "main_arguments": ["AI improves efficiency", "AI enables automation"],
        "sources": [{"title": "AI Overview", "url": "example.com", "source": "Wikipedia"}],
        "confidence_score": 0.8
    }
    
    # Test writer agent with research data
    writer_input = {
        "topic": "artificial intelligence",
        "research_data": research_data,
        "content_type": ContentType.BLOG_POST,
        "target_audience": "general audience",
        "word_count": 500
    }
    
    # This would normally call OpenAI, so we'll just test the structure
    assert await writer_agent.validate_input(writer_input) is True