"""Content-related data models."""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ContentType(str, Enum):
    """Content types supported by the system."""
    BLOG_POST = "blog_post"
    ARTICLE = "article"
    PRODUCT_DESCRIPTION = "product_description"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"


class ContentStatus(str, Enum):
    """Content status options."""
    PENDING = "pending"
    PROCESSING = "processing"
    DRAFT = "draft"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(str, Enum):
    """Types of AI agents."""
    RESEARCH = "research"
    WRITER = "writer"
    EDITOR = "editor"
    SEO = "seo"
    VISUAL = "visual"
    FACT_CHECKER = "fact_checker"


class ContentRequest(BaseModel):
    """Content creation request model."""
    id: Optional[str] = None
    user_id: str
    topic: str
    content_type: ContentType = ContentType.BLOG_POST
    target_audience: Optional[str] = None
    style_requirements: Dict[str, Any] = Field(default_factory=dict)
    keywords: List[str] = Field(default_factory=list)
    word_count: Optional[int] = None
    status: ContentStatus = ContentStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ContentPiece(BaseModel):
    """Generated content model."""
    id: Optional[str] = None
    request_id: str
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    quality_score: float = 0.0
    seo_score: float = 0.0
    fact_check_score: float = 0.0
    status: ContentStatus = ContentStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AgentTask(BaseModel):
    """Agent task execution model."""
    id: Optional[str] = None
    content_request_id: str
    agent_type: AgentType
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    execution_time: int = 0  # in seconds
    status: ContentStatus = ContentStatus.PENDING
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class QualityAssessment(BaseModel):
    """Quality assessment model."""
    id: Optional[str] = None
    content_id: str
    assessment_type: str
    score: float
    details: Dict[str, Any] = Field(default_factory=dict)
    assessed_at: Optional[datetime] = None


class ResearchData(BaseModel):
    """Research agent output model."""
    key_findings: List[str] = Field(default_factory=list)
    main_arguments: List[str] = Field(default_factory=list)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    statistics: List[Dict[str, Any]] = Field(default_factory=list)
    expert_opinions: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = 0.0


class WritingOutput(BaseModel):
    """Writer agent output model."""
    title: str
    content: str
    outline: Dict[str, Any] = Field(default_factory=dict)
    word_count: int
    estimated_reading_time: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SEOAnalysis(BaseModel):
    """SEO agent output model."""
    seo_score: float
    keyword_density: Dict[str, float] = Field(default_factory=dict)
    suggestions: List[str] = Field(default_factory=list)
    meta_description: Optional[str] = None
    title_suggestions: List[str] = Field(default_factory=list)


class QualityIssue(BaseModel):
    """Quality issue model."""
    type: str
    severity: str  # low, medium, high
    message: str
    suggestion: str
    confidence: float