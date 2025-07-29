"""Content creation orchestrator that coordinates all agents."""

import asyncio
import time
from typing import Dict, Any, Optional
from app.agents.research_agent import ResearchAgent
from app.agents.writer_agent import WriterAgent
from app.models.content import ContentRequest, ContentPiece, ContentStatus, AgentTask
from app.config import settings


class ContentOrchestrator:
    """Orchestrates the content creation pipeline."""
    
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.writer_agent = WriterAgent()
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
    
    async def create_content(self, request: ContentRequest) -> Dict[str, Any]:
        """Main content creation pipeline."""
        
        request_id = request.id or f"req_{int(time.time())}"
        
        try:
            # Initialize tracking
            self.active_tasks[request_id] = {
                "status": ContentStatus.PROCESSING,
                "start_time": time.time(),
                "current_agent": None,
                "progress": 0
            }
            
            # Phase 1: Research
            self.active_tasks[request_id]["current_agent"] = "research"
            self.active_tasks[request_id]["progress"] = 10
            
            research_result = await self._execute_research_phase(request)
            
            if research_result["status"] != "success":
                return self._create_error_response(request_id, "Research phase failed", research_result.get("message", ""))
            
            # Phase 2: Writing
            self.active_tasks[request_id]["current_agent"] = "writer"
            self.active_tasks[request_id]["progress"] = 50
            
            writing_result = await self._execute_writing_phase(request, research_result["research_data"])
            
            if writing_result["status"] != "success":
                return self._create_error_response(request_id, "Writing phase failed", writing_result.get("message", ""))
            
            # Phase 3: Finalization
            self.active_tasks[request_id]["progress"] = 90
            
            final_content = await self._finalize_content(request, research_result, writing_result)
            
            # Complete
            self.active_tasks[request_id]["status"] = ContentStatus.COMPLETED
            self.active_tasks[request_id]["progress"] = 100
            
            return {
                "status": "success",
                "request_id": request_id,
                "content": final_content,
                "execution_time": time.time() - self.active_tasks[request_id]["start_time"]
            }
            
        except Exception as e:
            return self._create_error_response(request_id, "Pipeline execution failed", str(e))
    
    async def _execute_research_phase(self, request: ContentRequest) -> Dict[str, Any]:
        """Execute the research phase."""
        
        research_input = {
            "topic": request.topic,
            "depth": 3,
            "target_audience": request.target_audience
        }
        
        try:
            result = await self.research_agent.execute(research_input)
            return result
        except Exception as e:
            return {"status": "error", "message": f"Research failed: {str(e)}"}
    
    async def _execute_writing_phase(self, request: ContentRequest, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the writing phase."""
        
        writing_input = {
            "topic": request.topic,
            "research_data": research_data,
            "content_type": request.content_type,
            "target_audience": request.target_audience,
            "style_guide": request.style_requirements,
            "word_count": request.word_count or 800
        }
        
        try:
            result = await self.writer_agent.execute(writing_input)
            return result
        except Exception as e:
            return {"status": "error", "message": f"Writing failed: {str(e)}"}
    
    async def _finalize_content(self, request: ContentRequest, research_result: Dict[str, Any], 
                              writing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize the content with metadata and quality scores."""
        
        writing_output = writing_result.get("writing_output", {})
        research_data = research_result.get("research_data", {})
        
        # Calculate basic quality scores
        quality_score = self._calculate_quality_score(writing_output, research_data)
        seo_score = self._calculate_basic_seo_score(writing_output)
        fact_check_score = research_result.get("confidence_score", 0.5)
        
        final_content = {
            "title": writing_output.get("title", request.topic),
            "content": writing_output.get("content", ""),
            "metadata": {
                **writing_output.get("metadata", {}),
                "word_count": writing_output.get("word_count", 0),
                "reading_time": writing_output.get("estimated_reading_time", 1),
                "research_sources": len(research_data.get("sources", [])),
                "key_findings_count": len(research_data.get("key_findings", [])),
                "content_type": request.content_type,
                "target_audience": request.target_audience
            },
            "quality_metrics": {
                "overall_quality": quality_score,
                "seo_score": seo_score,
                "fact_check_score": fact_check_score,
                "research_depth": len(research_data.get("sources", [])) / 5.0  # Normalized to 0-1
            },
            "research_summary": {
                "key_findings": research_data.get("key_findings", [])[:3],
                "source_count": len(research_data.get("sources", [])),
                "confidence": research_result.get("confidence_score", 0.5)
            }
        }
        
        return final_content
    
    def _calculate_quality_score(self, writing_output: Dict[str, Any], research_data: Dict[str, Any]) -> float:
        """Calculate basic quality score."""
        
        # Content length score (0.3 weight)
        word_count = writing_output.get("word_count", 0)
        length_score = min(word_count / 500, 1.0) if word_count > 100 else 0.2
        
        # Research depth score (0.4 weight)
        sources_count = len(research_data.get("sources", []))
        findings_count = len(research_data.get("key_findings", []))
        research_score = min((sources_count + findings_count) / 8.0, 1.0)
        
        # Structure score (0.3 weight)
        has_title = bool(writing_output.get("title"))
        has_content = bool(writing_output.get("content"))
        has_metadata = bool(writing_output.get("metadata"))
        structure_score = (has_title + has_content + has_metadata) / 3.0
        
        return (length_score * 0.3) + (research_score * 0.4) + (structure_score * 0.3)
    
    def _calculate_basic_seo_score(self, writing_output: Dict[str, Any]) -> float:
        """Calculate basic SEO score."""
        
        score = 0.0
        metadata = writing_output.get("metadata", {})
        content = writing_output.get("content", "")
        title = writing_output.get("title", "")
        
        # Title length (0.3 weight)
        if 30 <= len(title) <= 60:
            score += 0.3
        elif len(title) > 0:
            score += 0.15
        
        # Meta description (0.3 weight)
        meta_desc = metadata.get("meta_description", "")
        if 120 <= len(meta_desc) <= 160:
            score += 0.3
        elif len(meta_desc) > 0:
            score += 0.15
        
        # Content structure (0.2 weight)
        if "##" in content:  # Has headings
            score += 0.2
        elif "#" in content:
            score += 0.1
        
        # Keywords presence (0.2 weight)
        keywords = metadata.get("keywords", [])
        if keywords and any(keyword.lower() in content.lower() for keyword in keywords):
            score += 0.2
        
        return min(score, 1.0)
    
    def _create_error_response(self, request_id: str, error_type: str, message: str) -> Dict[str, Any]:
        """Create standardized error response."""
        
        if request_id in self.active_tasks:
            self.active_tasks[request_id]["status"] = ContentStatus.FAILED
        
        return {
            "status": "error",
            "request_id": request_id,
            "error_type": error_type,
            "message": message,
            "content": None
        }
    
    async def get_task_status(self, request_id: str) -> Dict[str, Any]:
        """Get current status of a content creation task."""
        
        if request_id not in self.active_tasks:
            return {"error": "Task not found"}
        
        task_info = self.active_tasks[request_id]
        
        return {
            "request_id": request_id,
            "status": task_info["status"],
            "progress": task_info["progress"],
            "current_agent": task_info.get("current_agent"),
            "elapsed_time": time.time() - task_info["start_time"]
        }
    
    async def cancel_task(self, request_id: str) -> Dict[str, Any]:
        """Cancel a running task."""
        
        if request_id not in self.active_tasks:
            return {"error": "Task not found"}
        
        self.active_tasks[request_id]["status"] = ContentStatus.FAILED
        
        return {
            "request_id": request_id,
            "status": "cancelled"
        }