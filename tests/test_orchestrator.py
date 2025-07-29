"""Tests for the content orchestrator."""

import pytest
from unittest.mock import AsyncMock, patch
from app.core.orchestrator import ContentOrchestrator
from app.models.content import ContentRequest, ContentType, ContentStatus


class TestContentOrchestrator:
    """Test cases for ContentOrchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        return ContentOrchestrator()
    
    @pytest.fixture
    def sample_request(self):
        return ContentRequest(
            user_id="test-user-123",
            topic="artificial intelligence in healthcare",
            content_type=ContentType.BLOG_POST,
            target_audience="healthcare professionals",
            word_count=800
        )
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert hasattr(orchestrator, 'research_agent')
        assert hasattr(orchestrator, 'writer_agent')
        assert hasattr(orchestrator, 'active_tasks')
    
    @pytest.mark.asyncio
    async def test_calculate_quality_score(self, orchestrator):
        """Test quality score calculation."""
        writing_output = {
            "title": "AI in Healthcare",
            "content": "This is a test article about AI in healthcare.",
            "word_count": 500,
            "metadata": {"keywords": ["AI", "healthcare"]}
        }
        
        research_data = {
            "sources": [{"title": "Source 1"}, {"title": "Source 2"}],
            "key_findings": ["Finding 1", "Finding 2", "Finding 3"]
        }
        
        score = orchestrator._calculate_quality_score(writing_output, research_data)
        
        assert 0.0 <= score <= 1.0
        assert isinstance(score, float)
    
    @pytest.mark.asyncio
    async def test_calculate_basic_seo_score(self, orchestrator):
        """Test basic SEO score calculation."""
        writing_output = {
            "title": "AI in Healthcare: A Comprehensive Guide",  # Good length
            "content": "## Introduction\nThis article covers AI in healthcare.\n## Benefits\nAI provides many benefits.",
            "metadata": {
                "meta_description": "Learn about artificial intelligence applications in healthcare and how AI is transforming medical practices.",
                "keywords": ["AI", "healthcare", "artificial intelligence"]
            }
        }
        
        score = orchestrator._calculate_basic_seo_score(writing_output)
        
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be decent with good title, meta desc, and structure
    
    @pytest.mark.asyncio
    async def test_create_error_response(self, orchestrator):
        """Test error response creation."""
        request_id = "test-123"
        error_response = orchestrator._create_error_response(
            request_id, "Test Error", "This is a test error message"
        )
        
        assert error_response["status"] == "error"
        assert error_response["request_id"] == request_id
        assert error_response["error_type"] == "Test Error"
        assert error_response["message"] == "This is a test error message"
        assert error_response["content"] is None
    
    @pytest.mark.asyncio
    async def test_get_task_status_not_found(self, orchestrator):
        """Test getting status for non-existent task."""
        result = await orchestrator.get_task_status("non-existent-id")
        assert "error" in result
        assert result["error"] == "Task not found"
    
    @pytest.mark.asyncio
    async def test_cancel_task_not_found(self, orchestrator):
        """Test cancelling non-existent task."""
        result = await orchestrator.cancel_task("non-existent-id")
        assert "error" in result
        assert result["error"] == "Task not found"
    
    @pytest.mark.asyncio
    @patch('app.core.orchestrator.ContentOrchestrator._execute_research_phase')
    @patch('app.core.orchestrator.ContentOrchestrator._execute_writing_phase')
    async def test_create_content_success(self, mock_writing, mock_research, orchestrator, sample_request):
        """Test successful content creation."""
        # Mock research phase
        mock_research.return_value = {
            "status": "success",
            "research_data": {
                "key_findings": ["AI improves diagnosis"],
                "sources": [{"title": "Medical AI Study"}],
                "confidence_score": 0.8
            },
            "confidence_score": 0.8
        }
        
        # Mock writing phase
        mock_writing.return_value = {
            "status": "success",
            "writing_output": {
                "title": "AI in Healthcare",
                "content": "AI is revolutionizing healthcare...",
                "word_count": 800,
                "estimated_reading_time": 4,
                "metadata": {
                    "keywords": ["AI", "healthcare"],
                    "meta_description": "Learn about AI in healthcare"
                }
            }
        }
        
        result = await orchestrator.create_content(sample_request)
        
        assert result["status"] == "success"
        assert "content" in result
        assert "execution_time" in result
        assert result["content"]["title"] == "AI in Healthcare"
    
    @pytest.mark.asyncio
    @patch('app.core.orchestrator.ContentOrchestrator._execute_research_phase')
    async def test_create_content_research_failure(self, mock_research, orchestrator, sample_request):
        """Test content creation with research failure."""
        mock_research.return_value = {
            "status": "error",
            "message": "Research failed"
        }
        
        result = await orchestrator.create_content(sample_request)
        
        assert result["status"] == "error"
        assert "Research phase failed" in result["error_type"]
    
    @pytest.mark.asyncio
    async def test_finalize_content(self, orchestrator):
        """Test content finalization."""
        request = ContentRequest(
            user_id="test-user",
            topic="test topic",
            content_type=ContentType.ARTICLE,
            target_audience="developers"
        )
        
        research_result = {
            "research_data": {
                "sources": [{"title": "Source 1"}],
                "key_findings": ["Finding 1", "Finding 2"]
            },
            "confidence_score": 0.7
        }
        
        writing_result = {
            "writing_output": {
                "title": "Test Article",
                "content": "This is test content.",
                "word_count": 100,
                "estimated_reading_time": 1,
                "metadata": {"keywords": ["test"]}
            }
        }
        
        final_content = await orchestrator._finalize_content(request, research_result, writing_result)
        
        assert "title" in final_content
        assert "content" in final_content
        assert "metadata" in final_content
        assert "quality_metrics" in final_content
        assert "research_summary" in final_content
        
        # Check quality metrics structure
        quality_metrics = final_content["quality_metrics"]
        assert "overall_quality" in quality_metrics
        assert "seo_score" in quality_metrics
        assert "fact_check_score" in quality_metrics
        assert "research_depth" in quality_metrics