"""Main FastAPI application for Content Creation Pipeline."""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import time
from app.config import settings
from app.models.content import ContentRequest, ContentType, ContentStatus
from app.core.orchestrator import ContentOrchestrator

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered content creation pipeline with multi-agent system"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = ContentOrchestrator()

# In-memory storage for demo (replace with database in production)
content_store: Dict[str, Dict[str, Any]] = {}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Content Creation Pipeline API",
        "version": settings.app_version,
        "status": "running",
        "endpoints": {
            "create_content": "/api/v1/content/create",
            "get_content": "/api/v1/content/{content_id}",
            "get_status": "/api/v1/content/{content_id}/status",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.app_version
    }


@app.post("/api/v1/content/create")
async def create_content(request: ContentRequest, background_tasks: BackgroundTasks):
    """Create new content using the AI pipeline."""
    
    try:
        # Generate unique request ID
        request_id = f"content_{int(time.time() * 1000)}"
        request.id = request_id
        
        # Validate request
        if not request.topic or len(request.topic.strip()) < 3:
            raise HTTPException(status_code=400, detail="Topic must be at least 3 characters long")
        
        if request.word_count and (request.word_count < 100 or request.word_count > settings.max_content_length):
            raise HTTPException(
                status_code=400, 
                detail=f"Word count must be between 100 and {settings.max_content_length}"
            )
        
        # Store initial request
        content_store[request_id] = {
            "request": request.dict(),
            "status": ContentStatus.PENDING,
            "created_at": time.time(),
            "result": None
        }
        
        # Start content creation in background
        background_tasks.add_task(process_content_creation, request_id, request)
        
        return {
            "message": "Content creation started",
            "request_id": request_id,
            "status": ContentStatus.PENDING,
            "estimated_completion": "2-5 minutes"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start content creation: {str(e)}")


@app.get("/api/v1/content/{content_id}")
async def get_content(content_id: str):
    """Get created content by ID."""
    
    if content_id not in content_store:
        raise HTTPException(status_code=404, detail="Content not found")
    
    content_data = content_store[content_id]
    
    return {
        "content_id": content_id,
        "status": content_data["status"],
        "created_at": content_data["created_at"],
        "request": content_data["request"],
        "result": content_data["result"]
    }


@app.get("/api/v1/content/{content_id}/status")
async def get_content_status(content_id: str):
    """Get content creation status."""
    
    if content_id not in content_store:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Try to get real-time status from orchestrator
    task_status = await orchestrator.get_task_status(content_id)
    
    if "error" not in task_status:
        return task_status
    
    # Fallback to stored status
    content_data = content_store[content_id]
    return {
        "request_id": content_id,
        "status": content_data["status"],
        "progress": 100 if content_data["status"] == ContentStatus.COMPLETED else 0,
        "elapsed_time": time.time() - content_data["created_at"]
    }


@app.delete("/api/v1/content/{content_id}")
async def cancel_content_creation(content_id: str):
    """Cancel content creation task."""
    
    if content_id not in content_store:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Try to cancel in orchestrator
    cancel_result = await orchestrator.cancel_task(content_id)
    
    # Update stored status
    content_store[content_id]["status"] = ContentStatus.FAILED
    
    return {
        "message": "Content creation cancelled",
        "content_id": content_id,
        "status": "cancelled"
    }


@app.get("/api/v1/content")
async def list_content(limit: int = 10, offset: int = 0):
    """List all content with pagination."""
    
    all_content = list(content_store.items())
    total = len(all_content)
    
    # Simple pagination
    paginated = all_content[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "content": [
            {
                "content_id": content_id,
                "status": data["status"],
                "topic": data["request"]["topic"],
                "content_type": data["request"]["content_type"],
                "created_at": data["created_at"]
            }
            for content_id, data in paginated
        ]
    }


@app.get("/api/v1/stats")
async def get_stats():
    """Get system statistics."""
    
    total_requests = len(content_store)
    completed = sum(1 for data in content_store.values() if data["status"] == ContentStatus.COMPLETED)
    failed = sum(1 for data in content_store.values() if data["status"] == ContentStatus.FAILED)
    pending = sum(1 for data in content_store.values() if data["status"] in [ContentStatus.PENDING, ContentStatus.PROCESSING])
    
    return {
        "total_requests": total_requests,
        "completed": completed,
        "failed": failed,
        "pending": pending,
        "success_rate": (completed / total_requests * 100) if total_requests > 0 else 0
    }


async def process_content_creation(request_id: str, request: ContentRequest):
    """Background task to process content creation."""
    
    try:
        # Update status to processing
        content_store[request_id]["status"] = ContentStatus.PROCESSING
        
        # Execute content creation pipeline
        result = await orchestrator.create_content(request)
        
        # Update stored result
        if result["status"] == "success":
            content_store[request_id]["status"] = ContentStatus.COMPLETED
            content_store[request_id]["result"] = result
        else:
            content_store[request_id]["status"] = ContentStatus.FAILED
            content_store[request_id]["result"] = result
            
    except Exception as e:
        # Handle any unexpected errors
        content_store[request_id]["status"] = ContentStatus.FAILED
        content_store[request_id]["result"] = {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)