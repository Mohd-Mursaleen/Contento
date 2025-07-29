"""Enhanced Research Agent using Tavily AI Search and Firecrawl."""

import json
import asyncio
import httpx
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.agents.base_agent import BaseAgent
from app.models.content import AgentType, ResearchData, ContentStatus

# Import Tavily client 
from tavily import TavilyClient


class ResearchAgent(BaseAgent):
    """Enhanced research agent using Tavily AI Search and Firecrawl web scraping."""
    
    def __init__(self):
        super().__init__(AgentType.RESEARCH)
        
        # Initialize API clients
        self.tavily_api_key = os.getenv("TAVILY_API_KEY", "")
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY", "")
        
        # Initialize Tavily client
        self.tavily_client = TavilyClient(api_key=self.tavily_api_key)

            
        # Firecrawl API endpoint
        self.firecrawl_base_url = "https://api.firecrawl.dev/v0"
        
        if not self.firecrawl_api_key or self.firecrawl_api_key == "your-firecrawl-api-key-here":
            print("⚠️  Firecrawl API key not configured")
        
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute enhanced research task using Tavily and Firecrawl."""
        self.update_status(ContentStatus.PROCESSING)
        
        try:
            # Validate input
            if not await self.validate_input(input_data):
                raise ValueError("Invalid input data for research agent")
            
            topic = input_data.get("topic", "")
            max_results = input_data.get("max_results", 10)
            include_domains = input_data.get("include_domains", [])
            exclude_domains = input_data.get("exclude_domains", [])
            search_depth = input_data.get("search_depth", "basic")  # basic or advanced
            
            print(f"🔍 Starting research for: '{topic}'")
            
            # Step 1: Use Tavily for AI-powered search
            tavily_results = await self._search_with_tavily(topic, max_results, include_domains, exclude_domains)
            
            # Step 2: Use Firecrawl for additional web scraping if needed
            firecrawl_results = await self._scrape_with_firecrawl(topic, max_results // 2)
            
            # Step 3: Combine and process all results
            all_results = tavily_results + firecrawl_results
            
            # Step 4: Structure findings using AI
            structured_research = await self._structure_enhanced_findings(all_results, topic)
            
            self.update_status(ContentStatus.COMPLETED)
            
            print(f"✅ Research completed: {len(all_results)} sources found")
            
            return {
                "status": "success",
                "research_data": structured_research,
                "confidence_score": self._calculate_enhanced_confidence(structured_research),
                "sources_found": len(all_results),
                "tavily_sources": len(tavily_results),
                "firecrawl_sources": len(firecrawl_results)
            }
            
        except Exception as e:
            self.update_status(ContentStatus.FAILED)
            print(f"❌ Research failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "research_data": ResearchData().model_dump()
            }
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate research input data."""
        required_fields = ["topic"]
        return all(field in input_data and input_data[field] for field in required_fields)
    
    async def _search_with_tavily(self, topic: str, max_results: int = 10, 
                                 include_domains: List[str] = None, 
                                 exclude_domains: List[str] = None) -> List[Dict[str, Any]]:
        """Search using Tavily AI-powered search."""
        results = []
        
        if not self.tavily_client:
            raise Exception("Tavily client not available. Please configure TAVILY_API_KEY.")
        
        try:
            print(f"🔍 Searching with Tavily: '{topic}'")
            
            # Prepare search parameters
            search_params = {
                "query": topic,
                "search_depth": "advanced",  # Use advanced search for better results
                "max_results": max_results,
                "include_answer": True,  # Get AI-generated answer
                "include_raw_content": True,  # Get full content
                "include_images": False  # We don't need images for text research
            }
            
            # Add domain filters if provided
            if include_domains:
                search_params["include_domains"] = include_domains
            if exclude_domains:
                search_params["exclude_domains"] = exclude_domains
            
            # Execute search
            response = self.tavily_client.search(**search_params)
            
            # Process results
            if response and "results" in response:
                for result in response["results"]:
                    processed_result = {
                        "title": result.get("title", ""),
                        "content": result.get("content", ""),
                        "url": result.get("url", ""),
                        "source": "Tavily Search",
                        "credibility_score": result.get("score", 0.8),  # Tavily provides relevance scores
                        "published_date": result.get("published_date"),
                        "raw_content": result.get("raw_content", "")
                    }
                    results.append(processed_result)
                
                # Add AI-generated answer if available
                if "answer" in response and response["answer"]:
                    ai_answer = {
                        "title": f"AI Summary: {topic}",
                        "content": response["answer"],
                        "url": "",
                        "source": "Tavily AI Answer",
                        "credibility_score": 0.9,
                        "published_date": datetime.now().isoformat()
                    }
                    results.insert(0, ai_answer)  # Put AI answer first
            
            print(f"✅ Tavily search completed: {len(results)} results")
            
        except Exception as e:
            print(f"❌ Tavily search error: {e}")
            raise Exception(f"Tavily search failed: {e}")

        return results
    
    async def _scrape_with_firecrawl(self, topic: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Scrape additional content using Firecrawl."""
        results = []
        
        if not self.firecrawl_api_key or self.firecrawl_api_key == "your-firecrawl-api-key-here":
            print("⚠️  Firecrawl API key not configured, skipping web scraping")
            return []
        
        try:
            print(f"🕷️  Scraping with Firecrawl: '{topic}'")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Use Firecrawl search endpoint
                search_url = f"{self.firecrawl_base_url}/search"
                
                headers = {
                    "Authorization": f"Bearer {self.firecrawl_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "query": topic,
                    "limit": max_results,
                    "searchOptions": {
                        "limit": max_results
                    }
                }
                
                response = await client.post(search_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "data" in data:
                        for item in data["data"]:
                            processed_result = {
                                "title": item.get("title", ""),
                                "content": item.get("content", "")[:1000],  # Limit content length
                                "url": item.get("url", ""),
                                "source": "Firecrawl Scraper",
                                "credibility_score": 0.7,  # Default credibility for scraped content
                                "published_date": None
                            }
                            results.append(processed_result)
                else:
                    print(f"❌ Firecrawl API error: {response.status_code} - {response.text}")
                
                print(f"✅ Firecrawl scraping completed: {len(results)} results")
                
        except Exception as e:
            print(f"❌ Firecrawl scraping error: {e}")
        
        return results
    
    async def _structure_enhanced_findings(self, sources: List[Dict[str, Any]], topic: str) -> Dict[str, Any]:
        """Structure research findings using AI with enhanced analysis."""
        if not sources:
            return ResearchData().model_dump()
        
        # Combine content from sources with better formatting
        source_summaries = []
        for i, source in enumerate(sources[:8], 1):  # Limit to 8 sources to avoid token limits
            summary = f"""
Source {i}: {source.get('source', 'Unknown')} (Credibility: {source.get('credibility_score', 0.5)})
Title: {source.get('title', 'No title')}
URL: {source.get('url', 'No URL')}
Content: {source.get('content', '')[:600]}...
Published: {source.get('published_date', 'Unknown')}
"""
            source_summaries.append(summary)
        
        combined_content = "\n".join(source_summaries)
        
        prompt = f"""
        Analyze the following comprehensive research about "{topic}" and provide detailed structured analysis.
        
        Research Sources:
        {combined_content}
        
        Provide analysis in this JSON format:
        {{
            "key_findings": ["finding 1", "finding 2", "finding 3", "finding 4", "finding 5"],
            "main_arguments": ["argument 1", "argument 2", "argument 3"],
            "statistics": [
                {{"statistic": "description", "value": "number/percentage", "source": "source name", "reliability": "high/medium/low"}}
            ],
            "expert_opinions": [
                {{"opinion": "expert view", "expert": "expert name or source", "source": "publication/platform"}}
            ],
            "recent_developments": ["development 1", "development 2"],
            "practical_applications": ["application 1", "application 2"],
            "challenges_limitations": ["challenge 1", "challenge 2"]
        }}
        
        Focus on:
        1. Factual accuracy and source credibility
        2. Current and relevant information
        3. Diverse perspectives and viewpoints
        4. Actionable insights
        5. Clear distinction between facts and opinions
        
        Return only valid JSON.
        """
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = await self.call_openai(messages, max_tokens=2000)
            
            # Clean the response to extract JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            structured_data = json.loads(response)
            
            # Create enhanced ResearchData object
            research_data = ResearchData(
                key_findings=structured_data.get("key_findings", []),
                main_arguments=structured_data.get("main_arguments", []),
                sources=[{
                    "title": source.get("title", ""),
                    "url": source.get("url", ""),
                    "source": source.get("source", ""),
                    "credibility_score": source.get("credibility_score", 0.5),
                    "published_date": source.get("published_date")
                } for source in sources],
                statistics=structured_data.get("statistics", []),
                expert_opinions=structured_data.get("expert_opinions", []),
                confidence_score=self._calculate_enhanced_confidence_from_sources(sources)
            )
            
            # Add enhanced fields to the model dump
            enhanced_data = research_data.model_dump()
            enhanced_data.update({
                "recent_developments": structured_data.get("recent_developments", []),
                "practical_applications": structured_data.get("practical_applications", []),
                "challenges_limitations": structured_data.get("challenges_limitations", []),
                "source_diversity": len(set(s.get("source", "") for s in sources)),
                "total_sources": len(sources),
                "avg_credibility": sum(s.get("credibility_score", 0.5) for s in sources) / len(sources) if sources else 0,
                "has_recent_content": any(s.get("published_date") for s in sources)
            })
            
            return enhanced_data
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error structuring enhanced findings: {e}")
            print(f"Raw response: {response[:200] if 'response' in locals() else 'No response'}")
            # Return basic structure with available data
            return ResearchData(
                key_findings=[f"Comprehensive research conducted on {topic}"],
                sources=[{
                    "title": source.get("title", ""),
                    "url": source.get("url", ""),
                    "source": source.get("source", ""),
                    "credibility_score": source.get("credibility_score", 0.5)
                } for source in sources],
                confidence_score=0.7
            ).model_dump()

    
    def _calculate_enhanced_confidence(self, research_data: Dict[str, Any]) -> float:
        """Calculate enhanced confidence score based on research quality."""
        sources = research_data.get("sources", [])
        key_findings = research_data.get("key_findings", [])
        
        if not sources:
            return 0.1
        
        # Source quantity score (more sources = higher confidence)
        source_score = min(len(sources) / 8.0, 1.0)  # Max at 8 sources
        
        # Findings quality score
        findings_score = min(len(key_findings) / 6.0, 1.0)  # Max at 6 findings
        
        # Source diversity (different platforms/sources)
        source_diversity = research_data.get("source_diversity", 1) / 4.0  # Max at 4 different sources
        source_diversity = min(source_diversity, 1.0)
        
        # Average credibility of sources
        avg_credibility = research_data.get("avg_credibility", 0.5)
        
        # Recent content bonus
        recent_bonus = 0.1 if research_data.get("has_recent_content", False) else 0
        
        # Enhanced features bonus
        enhanced_bonus = 0.05 if research_data.get("recent_developments") else 0
        
        confidence = (
            source_score * 0.25 + 
            findings_score * 0.25 + 
            source_diversity * 0.2 + 
            avg_credibility * 0.3
        ) + recent_bonus + enhanced_bonus
        
        return min(confidence, 1.0)
    
    def _calculate_enhanced_confidence_from_sources(self, sources: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on enhanced source analysis."""
        if not sources:
            return 0.1
        
        # Average credibility
        avg_credibility = sum(s.get("credibility_score", 0.5) for s in sources) / len(sources)
        
        # Source diversity (different platforms)
        unique_sources = len(set(s.get("source", "") for s in sources))
        source_diversity = min(unique_sources / 4.0, 1.0)  # Max at 4 different sources
        
        # Content quality (based on content length and presence)
        content_quality = sum(1 for s in sources if len(s.get("content", "")) > 100) / len(sources)
        
        # Recent content factor
        recent_sources = sum(1 for s in sources if s.get("published_date"))
        recency_factor = min(recent_sources / len(sources), 0.3) + 0.7  # 0.7 to 1.0
        
        confidence = (
            avg_credibility * 0.4 + 
            source_diversity * 0.3 + 
            content_quality * 0.2 + 
            recency_factor * 0.1
        )
        
        return min(confidence, 1.0)
    
    