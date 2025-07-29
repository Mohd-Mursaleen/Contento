"""Research Agent for gathering information and sources."""

import json
import asyncio
import httpx
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from app.agents.base_agent import BaseAgent
from app.models.content import AgentType, ResearchData, ContentStatus


class ResearchAgent(BaseAgent):
    """Agent responsible for researching topics and gathering information."""
    
    def __init__(self):
        super().__init__(AgentType.RESEARCH)
        self.search_engines = {
            "duckduckgo": "https://api.duckduckgo.com/",
            "wikipedia": "https://en.wikipedia.org/api/rest_v1/"
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research task."""
        self.update_status(ContentStatus.PROCESSING)
        
        try:
            # Validate input
            if not await self.validate_input(input_data):
                raise ValueError("Invalid input data for research agent")
            
            topic = input_data.get("topic", "")
            depth = input_data.get("depth", 3)
            
            # Generate search queries
            search_queries = await self._generate_search_queries(topic)
            
            # Gather information from multiple sources
            research_data = await self._gather_information(search_queries, depth)
            
            # Structure findings using AI
            structured_research = await self._structure_findings(research_data, topic)
            
            self.update_status(ContentStatus.COMPLETED)
            
            return {
                "status": "success",
                "research_data": structured_research,
                "confidence_score": self._calculate_confidence(structured_research)
            }
            
        except Exception as e:
            self.update_status(ContentStatus.FAILED)
            return {
                "status": "error",
                "message": str(e),
                "research_data": ResearchData().model_dump()
            }
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate research input data."""
        required_fields = ["topic"]
        return all(field in input_data and input_data[field] for field in required_fields)
    
    async def _generate_search_queries(self, topic: str) -> List[str]:
        """Generate diverse search queries for the topic."""
        prompt = f"""
        Generate 5 diverse search queries for researching the topic: "{topic}"
        Include different angles: factual information, recent developments, statistics, expert opinions, and practical applications.
        
        Return only a JSON array of strings, no additional text.
        Example: ["query 1", "query 2", "query 3", "query 4", "query 5"]
        """
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.call_openai(messages)
        
        try:
            # Clean the response to extract JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            queries = json.loads(response)
            return queries if isinstance(queries, list) else [topic]
        except json.JSONDecodeError as e:
            print(f"Error parsing search queries: {e}")
            print(f"Raw response: {response[:200] if 'response' in locals() else 'No response'}")
            # Fallback queries
            return [
                f"{topic} overview",
                f"{topic} latest trends",
                f"{topic} statistics",
                f"{topic} expert opinion",
                f"{topic} practical applications"
            ]
    
    async def _gather_information(self, queries: List[str], depth: int) -> List[Dict[str, Any]]:
        """Gather information from multiple sources."""
        all_results = []
        
        for query in queries[:depth]:
            try:
                # Wikipedia search
                wiki_results = await self._search_wikipedia(query)
                all_results.extend(wiki_results)
                
                # Add a small delay to be respectful to APIs
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error gathering information for query '{query}': {e}")
                continue
        
        return all_results
    
    async def _search_wikipedia(self, query: str) -> List[Dict[str, Any]]:
        """Search Wikipedia for information."""
        results = []
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Search for articles
                search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
                response = await client.get(search_url)
                
                if response.status_code == 200:
                    data = response.json()
                    results.append({
                        "source": "Wikipedia",
                        "title": data.get("title", ""),
                        "content": data.get("extract", ""),
                        "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                        "credibility_score": 0.8  # Wikipedia generally reliable
                    })
        
        except Exception as e:
            print(f"Wikipedia search error: {e}")
        
        return results
    
    async def _structure_findings(self, sources: List[Dict[str, Any]], topic: str) -> Dict[str, Any]:
        """Structure research findings using AI."""
        if not sources:
            return ResearchData().model_dump()
        
        # Combine content from sources
        combined_content = "\n\n".join([
            f"Source: {source.get('source', 'Unknown')}\n"
            f"Title: {source.get('title', 'No title')}\n"
            f"Content: {source.get('content', '')[:500]}..."
            for source in sources[:5]  # Limit to avoid token limits
        ])
        
        prompt = f"""
        Analyze the following research content about "{topic}" and structure it into key findings.
        
        Research Content:
        {combined_content}
        
        Please provide a structured analysis in the following JSON format:
        {{
            "key_findings": ["finding 1", "finding 2", "finding 3"],
            "main_arguments": ["argument 1", "argument 2"],
            "statistics": [
                {{"statistic": "description", "value": "number", "source": "source name"}}
            ],
            "expert_opinions": [
                {{"opinion": "expert view", "expert": "expert name", "source": "source"}}
            ]
        }}
        
        Focus on factual, relevant information. Return only valid JSON.
        """
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = await self.call_openai(messages)
            
            # Clean the response to extract JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            structured_data = json.loads(response)
            
            # Create ResearchData object
            research_data = ResearchData(
                key_findings=structured_data.get("key_findings", []),
                main_arguments=structured_data.get("main_arguments", []),
                sources=[{
                    "title": source.get("title", ""),
                    "url": source.get("url", ""),
                    "source": source.get("source", ""),
                    "credibility_score": source.get("credibility_score", 0.5)
                } for source in sources],
                statistics=structured_data.get("statistics", []),
                expert_opinions=structured_data.get("expert_opinions", []),
                confidence_score=self._calculate_confidence_from_sources(sources)
            )
            
            return research_data.model_dump()
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error structuring findings: {e}")
            print(f"Raw response: {response[:200] if 'response' in locals() else 'No response'}")
            # Return basic structure with available data
            return ResearchData(
                key_findings=[f"Research conducted on {topic}"],
                sources=[{
                    "title": source.get("title", ""),
                    "url": source.get("url", ""),
                    "source": source.get("source", ""),
                    "credibility_score": source.get("credibility_score", 0.5)
                } for source in sources],
                confidence_score=0.5
            ).model_dump()
    
    def _calculate_confidence(self, research_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on research quality."""
        sources = research_data.get("sources", [])
        key_findings = research_data.get("key_findings", [])
        
        if not sources:
            return 0.1
        
        # Base confidence on number of sources and findings
        source_score = min(len(sources) / 5.0, 1.0)  # Max at 5 sources
        findings_score = min(len(key_findings) / 5.0, 1.0)  # Max at 5 findings
        
        # Average credibility of sources
        avg_credibility = sum(s.get("credibility_score", 0.5) for s in sources) / len(sources)
        
        return (source_score + findings_score + avg_credibility) / 3.0
    
    def _calculate_confidence_from_sources(self, sources: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on source quality."""
        if not sources:
            return 0.1
        
        avg_credibility = sum(s.get("credibility_score", 0.5) for s in sources) / len(sources)
        source_diversity = min(len(set(s.get("source", "") for s in sources)) / 3.0, 1.0)
        
        return (avg_credibility + source_diversity) / 2.0