"""Writer Agent for content creation and narrative structure."""

import json
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.models.content import AgentType, WritingOutput, ContentStatus, ContentType


class WriterAgent(BaseAgent):
    """Agent responsible for creating written content."""
    
    def __init__(self):
        super().__init__(AgentType.WRITER)
        self.style_templates = {
            ContentType.BLOG_POST: "conversational and engaging",
            ContentType.ARTICLE: "informative and professional",
            ContentType.PRODUCT_DESCRIPTION: "persuasive and benefit-focused",
            ContentType.SOCIAL_MEDIA: "concise and attention-grabbing",
            ContentType.EMAIL: "personal and action-oriented"
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute writing task."""
        self.update_status(ContentStatus.PROCESSING)
        
        try:
            # Validate input
            if not await self.validate_input(input_data):
                raise ValueError("Invalid input data for writer agent")
            
            research_data = input_data.get("research_data", {})
            content_type = input_data.get("content_type", ContentType.BLOG_POST)
            target_audience = input_data.get("target_audience", "general audience")
            style_guide = input_data.get("style_guide", {})
            topic = input_data.get("topic", "")
            word_count = input_data.get("word_count", 800)
            
            # Create content outline
            outline = await self._create_outline(research_data, content_type, target_audience, topic)
            
            # Generate content sections
            content_sections = await self._generate_content(outline, research_data, style_guide, word_count)
            
            # Assemble final content
            final_content = await self._assemble_content(content_sections, outline)
            
            # Generate metadata
            metadata = await self._generate_metadata(final_content, topic)
            
            self.update_status(ContentStatus.COMPLETED)
            
            writing_output = WritingOutput(
                title=outline.get("title", topic),
                content=final_content,
                outline=outline,
                word_count=len(final_content.split()),
                estimated_reading_time=self._calculate_reading_time(final_content),
                metadata=metadata
            )
            
            return {
                "status": "success",
                "writing_output": writing_output.dict()
            }
            
        except Exception as e:
            self.update_status(ContentStatus.FAILED)
            return {
                "status": "error",
                "message": str(e),
                "writing_output": {}
            }
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate writer input data."""
        required_fields = ["topic"]
        return all(field in input_data and input_data[field] for field in required_fields)
    
    async def _create_outline(self, research_data: Dict[str, Any], content_type: ContentType, 
                            target_audience: str, topic: str) -> Dict[str, Any]:
        """Create content outline based on research."""
        
        key_findings = research_data.get("key_findings", [])
        main_arguments = research_data.get("main_arguments", [])
        
        findings_text = "\n".join(f"- {finding}" for finding in key_findings[:5])
        arguments_text = "\n".join(f"- {arg}" for arg in main_arguments[:3])
        
        prompt = f"""
        Create a detailed outline for a {content_type.value} about "{topic}" targeted at {target_audience}.
        
        Key research findings:
        {findings_text}
        
        Main arguments to cover:
        {arguments_text}
        
        Create an outline with:
        1. A compelling title (50-60 characters)
        2. Introduction hook and overview
        3. 3-4 main sections with subsections
        4. Conclusion with key takeaways
        5. Call-to-action (if appropriate)
        
        Return the outline in this JSON format:
        {{
            "title": "Compelling Title Here",
            "introduction": {{
                "hook": "Opening hook",
                "overview": "What readers will learn"
            }},
            "main_sections": [
                {{
                    "title": "Section 1 Title",
                    "subsections": ["Subsection 1", "Subsection 2"],
                    "key_points": ["Point 1", "Point 2"]
                }}
            ],
            "conclusion": {{
                "summary": "Key takeaways",
                "call_to_action": "Next steps for reader"
            }}
        }}
        
        Return only valid JSON.
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
            
            outline = json.loads(response)
            return outline
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error creating outline: {e}")
            print(f"Raw response: {response[:200] if 'response' in locals() else 'No response'}")
            # Return basic outline
            return {
                "title": topic,
                "introduction": {
                    "hook": f"Understanding {topic} is crucial in today's world.",
                    "overview": f"This article explores key aspects of {topic}."
                },
                "main_sections": [
                    {
                        "title": f"Understanding {topic}",
                        "subsections": ["Definition", "Importance"],
                        "key_points": key_findings[:2] if key_findings else ["Key concept 1", "Key concept 2"]
                    },
                    {
                        "title": f"Applications of {topic}",
                        "subsections": ["Practical uses", "Benefits"],
                        "key_points": key_findings[2:4] if len(key_findings) > 2 else ["Application 1", "Application 2"]
                    }
                ],
                "conclusion": {
                    "summary": f"Key insights about {topic}",
                    "call_to_action": "Apply these insights in your work"
                }
            }
    
    async def _generate_content(self, outline: Dict[str, Any], research_data: Dict[str, Any], 
                              style_guide: Dict[str, Any], target_word_count: int) -> Dict[str, str]:
        """Generate content for each section."""
        
        sections = {}
        style = style_guide.get("tone", "professional")
        
        # Generate introduction
        intro_prompt = self._create_section_prompt(
            "introduction",
            outline.get("introduction", {}),
            research_data,
            style,
            target_word_count // 6  # ~15% of total
        )
        sections["introduction"] = await self._generate_section_content(intro_prompt)
        
        # Generate main sections
        main_sections = outline.get("main_sections", [])
        words_per_section = (target_word_count * 0.7) // len(main_sections) if main_sections else 200
        
        for i, section in enumerate(main_sections):
            section_prompt = self._create_section_prompt(
                f"main_section_{i+1}",
                section,
                research_data,
                style,
                int(words_per_section)
            )
            sections[f"section_{i+1}"] = await self._generate_section_content(section_prompt)
        
        # Generate conclusion
        conclusion_prompt = self._create_section_prompt(
            "conclusion",
            outline.get("conclusion", {}),
            research_data,
            style,
            target_word_count // 8  # ~12% of total
        )
        sections["conclusion"] = await self._generate_section_content(conclusion_prompt)
        
        return sections
    
    def _create_section_prompt(self, section_type: str, section_data: Dict[str, Any], 
                             research_data: Dict[str, Any], style: str, word_count: int) -> str:
        """Create a prompt for generating a specific section."""
        
        key_findings = research_data.get("key_findings", [])
        sources = research_data.get("sources", [])
        
        base_prompt = f"""
        Write a {section_type} section with approximately {word_count} words.
        
        Style: {style}
        Research context: {'; '.join(key_findings[:3])}
        
        Section details: {json.dumps(section_data)}
        
        Requirements:
        - Write in a {style} tone
        - Use clear, engaging language
        - Include specific details from research when relevant
        - Make it informative and valuable to readers
        - Ensure smooth flow and readability
        """
        
        if section_type == "introduction":
            base_prompt += "\n- Start with a compelling hook\n- Clearly state what readers will learn"
        elif section_type == "conclusion":
            base_prompt += "\n- Summarize key takeaways\n- Provide actionable next steps"
        
        return base_prompt
    
    async def _generate_section_content(self, prompt: str) -> str:
        """Generate content for a single section."""
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = await self.call_openai(messages, max_tokens=800)
            return response.strip()
        except Exception as e:
            print(f"Error generating section content: {e}")
            return "Content generation failed for this section."
    
    async def _assemble_content(self, sections: Dict[str, str], outline: Dict[str, Any]) -> str:
        """Assemble all sections into final content."""
        
        content_parts = []
        
        # Add title as heading
        title = outline.get("title", "Article Title")
        content_parts.append(f"# {title}\n")
        
        # Add introduction
        if "introduction" in sections:
            content_parts.append(sections["introduction"])
        
        # Add main sections with headings
        main_sections = outline.get("main_sections", [])
        for i, section_outline in enumerate(main_sections):
            section_key = f"section_{i+1}"
            if section_key in sections:
                section_title = section_outline.get("title", f"Section {i+1}")
                content_parts.append(f"\n## {section_title}\n")
                content_parts.append(sections[section_key])
        
        # Add conclusion
        if "conclusion" in sections:
            content_parts.append(f"\n## Conclusion\n")
            content_parts.append(sections["conclusion"])
        
        return "\n\n".join(content_parts)
    
    async def _generate_metadata(self, content: str, topic: str) -> Dict[str, Any]:
        """Generate metadata for the content."""
        
        # Extract title from content
        lines = content.split("\n")
        title = lines[0].replace("#", "").strip() if lines else topic
        
        # Generate meta description
        first_paragraph = ""
        for line in lines[1:]:
            if line.strip() and not line.startswith("#"):
                first_paragraph = line.strip()
                break
        
        meta_description = first_paragraph[:150] + "..." if len(first_paragraph) > 150 else first_paragraph
        
        # Extract keywords (simple implementation)
        keywords = self._extract_keywords(content)
        
        return {
            "title": title,
            "meta_description": meta_description,
            "keywords": keywords,
            "language": "en",
            "content_type": "article"
        }
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract important keywords from content."""
        # Simple keyword extraction
        import re
        from collections import Counter
        
        # Remove markdown and get words
        text = re.sub(r'[#*`\[\]()]', '', content.lower())
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
        
        # Filter out common words
        stop_words = {
            'that', 'with', 'have', 'this', 'will', 'from', 'they', 'been', 
            'about', 'would', 'there', 'could', 'other', 'more', 'very', 
            'what', 'know', 'just', 'first', 'into', 'over', 'think', 'also'
        }
        
        words = [word for word in words if word not in stop_words]
        
        # Get most common words
        word_counts = Counter(words)
        return [word for word, count in word_counts.most_common(8)]
    
    def _calculate_reading_time(self, content: str) -> int:
        """Calculate estimated reading time in minutes."""
        word_count = len(content.split())
        # Average reading speed: 200-250 words per minute
        return max(1, round(word_count / 225))