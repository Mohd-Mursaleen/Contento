"""Database service for Supabase integration."""

import json
import time
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from supabase import create_client, Client
from app.config import settings
from app.models.content import ContentRequest, ContentPiece, ContentStatus, AgentTask, QualityAssessment


class DatabaseService:
    """Service for handling all database operations with Supabase."""
    
    def __init__(self):
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key
        )
    
    # Content Request Operations
    async def create_content_request(self, request: ContentRequest) -> str:
        """Create a new content request in the database."""
        try:
            data = {
                "id": request.id,
                "user_id": request.user_id,
                "topic": request.topic,
                "content_type": request.content_type,
                "target_audience": request.target_audience,
                "style_requirements": request.style_requirements,
                "status": request.status,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("content_requests").insert(data).execute()
            return result.data[0]["id"] if result.data else request.id
            
        except Exception as e:
            print(f"Error creating content request: {e}")
            raise
    
    async def get_content_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get a content request by ID."""
        try:
            result = self.supabase.table("content_requests").select("*").eq("id", request_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting content request: {e}")
            return None
    
    async def update_content_request_status(self, request_id: str, status: ContentStatus) -> bool:
        """Update the status of a content request."""
        try:
            data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("content_requests").update(data).eq("id", request_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating content request status: {e}")
            return False
    
    # Content Piece Operations
    async def create_content_piece(self, content_data: Dict[str, Any]) -> str:
        """Create a new content piece in the database."""
        try:
            # Generate unique ID if not provided
            content_id = content_data.get("id", str(uuid.uuid4()))
            
            data = {
                "id": content_id,
                "request_id": content_data.get("request_id"),
                "title": content_data.get("title"),
                "content": content_data.get("content"),
                "metadata": content_data.get("metadata", {}),
                "quality_score": content_data.get("quality_score", 0.0),
                "seo_score": content_data.get("seo_score", 0.0),
                "fact_check_score": content_data.get("fact_check_score", 0.0),
                "status": content_data.get("status", ContentStatus.DRAFT),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("content_pieces").insert(data).execute()
            return result.data[0]["id"] if result.data else content_id
            
        except Exception as e:
            print(f"Error creating content piece: {e}")
            raise
    
    async def get_content_piece(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get a content piece by ID."""
        try:
            result = self.supabase.table("content_pieces").select("*").eq("id", content_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting content piece: {e}")
            return None
    
    async def get_content_pieces_by_request(self, request_id: str) -> List[Dict[str, Any]]:
        """Get all content pieces for a request."""
        try:
            result = self.supabase.table("content_pieces").select("*").eq("request_id", request_id).execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting content pieces by request: {e}")
            return []
    
    async def update_content_piece(self, content_id: str, updates: Dict[str, Any]) -> bool:
        """Update a content piece."""
        try:
            updates["updated_at"] = datetime.utcnow().isoformat()
            result = self.supabase.table("content_pieces").update(updates).eq("id", content_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating content piece: {e}")
            return False
    
    # Agent Task Operations
    async def create_agent_task(self, task_data: Dict[str, Any]) -> str:
        """Create a new agent task record."""
        try:
            task_id = task_data.get("id", str(uuid.uuid4()))
            
            data = {
                "id": task_id,
                "content_request_id": task_data.get("content_request_id"),
                "agent_type": task_data.get("agent_type"),
                "input_data": task_data.get("input_data", {}),
                "output_data": task_data.get("output_data", {}),
                "execution_time": task_data.get("execution_time", 0),
                "status": task_data.get("status", ContentStatus.PENDING),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("agent_tasks").insert(data).execute()
            return result.data[0]["id"] if result.data else task_id
            
        except Exception as e:
            print(f"Error creating agent task: {e}")
            raise
    
    async def update_agent_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update an agent task."""
        try:
            updates["updated_at"] = datetime.utcnow().isoformat()
            result = self.supabase.table("agent_tasks").update(updates).eq("id", task_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating agent task: {e}")
            return False
    
    async def get_agent_tasks_by_request(self, request_id: str) -> List[Dict[str, Any]]:
        """Get all agent tasks for a content request."""
        try:
            result = self.supabase.table("agent_tasks").select("*").eq("content_request_id", request_id).execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting agent tasks: {e}")
            return []
    
    # Quality Assessment Operations
    async def create_quality_assessment(self, assessment_data: Dict[str, Any]) -> str:
        """Create a quality assessment record."""
        try:
            assessment_id = str(uuid.uuid4())
            
            data = {
                "id": assessment_id,
                "content_id": assessment_data.get("content_id"),
                "assessment_type": assessment_data.get("assessment_type"),
                "score": assessment_data.get("score"),
                "details": assessment_data.get("details", {}),
                "assessed_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("quality_assessments").insert(data).execute()
            return result.data[0]["id"] if result.data else assessment_id
            
        except Exception as e:
            print(f"Error creating quality assessment: {e}")
            raise
    
    async def get_quality_assessments(self, content_id: str) -> List[Dict[str, Any]]:
        """Get all quality assessments for a content piece."""
        try:
            result = self.supabase.table("quality_assessments").select("*").eq("content_id", content_id).execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting quality assessments: {e}")
            return []
    
    # List Operations
    async def list_content_requests(self, user_id: Optional[str] = None, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List content requests with pagination."""
        try:
            query = self.supabase.table("content_requests").select("*")
            
            if user_id:
                query = query.eq("user_id", user_id)
            
            # Get total count
            count_result = query.execute()
            total = len(count_result.data) if count_result.data else 0
            
            # Get paginated results
            result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return {
                "data": result.data or [],
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            print(f"Error listing content requests: {e}")
            return {"data": [], "total": 0, "limit": limit, "offset": offset}
    
    async def get_content_with_request(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content piece with its associated request."""
        try:
            # Get content piece
            content_result = self.supabase.table("content_pieces").select("*").eq("id", content_id).execute()
            
            if not content_result.data:
                return None
            
            content = content_result.data[0]
            
            # Get associated request
            if content.get("request_id"):
                request_result = self.supabase.table("content_requests").select("*").eq("id", content["request_id"]).execute()
                if request_result.data:
                    content["request"] = request_result.data[0]
            
            return content
            
        except Exception as e:
            print(f"Error getting content with request: {e}")
            return None
    
    # Statistics Operations
    async def get_content_stats(self) -> Dict[str, Any]:
        """Get content creation statistics."""
        try:
            # Get all content requests
            requests_result = self.supabase.table("content_requests").select("status").execute()
            requests = requests_result.data or []
            
            total_requests = len(requests)
            completed = len([r for r in requests if r["status"] == ContentStatus.COMPLETED])
            failed = len([r for r in requests if r["status"] == ContentStatus.FAILED])
            pending = len([r for r in requests if r["status"] in [ContentStatus.PENDING, ContentStatus.PROCESSING]])
            
            return {
                "total_requests": total_requests,
                "completed": completed,
                "failed": failed,
                "pending": pending,
                "success_rate": (completed / total_requests * 100) if total_requests > 0 else 0
            }
        except Exception as e:
            print(f"Error getting content stats: {e}")
            return {
                "total_requests": 0,
                "completed": 0,
                "failed": 0,
                "pending": 0,
                "success_rate": 0
            }
    
    # Utility Methods
    async def health_check(self) -> bool:
        """Check if database connection is healthy."""
        try:
            result = self.supabase.table("organizations").select("id").limit(1).execute()
            return True
        except Exception as e:
            print(f"Database health check failed: {e}")
            return False