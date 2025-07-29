"""Base agent class for all AI agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import time
import openai
from app.config import get_agent_config
from app.models.content import AgentTask, AgentType, ContentStatus


class BaseAgent(ABC):
    """Abstract base class for all AI agents."""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.config = get_agent_config()
        self.client = openai.AsyncOpenAI(api_key=self.config["openai_api_key"])
        self.status = ContentStatus.PENDING
        self.execution_start_time: Optional[float] = None
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task."""
        pass
    
    async def create_task_record(self, content_request_id: str, input_data: Dict[str, Any]) -> AgentTask:
        """Create a task record for tracking."""
        return AgentTask(
            content_request_id=content_request_id,
            agent_type=self.agent_type,
            input_data=input_data,
            status=ContentStatus.PENDING
        )
    
    async def update_task_status(self, task: AgentTask, status: ContentStatus, 
                               output_data: Optional[Dict[str, Any]] = None,
                               error_message: Optional[str] = None):
        """Update task status and execution time."""
        task.status = status
        if output_data:
            task.output_data = output_data
        if error_message:
            task.error_message = error_message
        
        if self.execution_start_time:
            task.execution_time = int(time.time() - self.execution_start_time)
    
    async def call_openai(self, messages: list, **kwargs) -> str:
        """Make a call to OpenAI API with error handling."""
        try:
            response = await self.client.chat.completions.create(
                model=self.config["model"],
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self.config["max_tokens"]),
                temperature=kwargs.get("temperature", self.config["temperature"]),
                timeout=self.config["timeout"]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    def update_status(self, status: ContentStatus):
        """Update agent status."""
        self.status = status
        if status == ContentStatus.PROCESSING:
            self.execution_start_time = time.time()
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for the agent."""
        return True  # Override in subclasses for specific validation
    
    async def process_with_retry(self, func, *args, max_retries: int = 3, **kwargs):
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(wait_time)
                    continue
                break
        
        raise last_exception