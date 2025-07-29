#!/usr/bin/env python3
"""
Demo script for Content Creation Pipeline MVP
Run this to test the system functionality.
"""

import asyncio
import json
from app.models.content import ContentRequest, ContentType
from app.core.orchestrator import ContentOrchestrator


async def demo_content_creation():
    """Demonstrate the content creation pipeline."""
    
    print("🚀 Content Creation Pipeline MVP Demo")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = ContentOrchestrator()
    
    # Create a sample content request
    request = ContentRequest(
        user_id="c7058e35-79ea-4127-a69b-79be8327e8f6",  # Test user from database
        topic="artificial intelligence in healthcare",
        content_type=ContentType.BLOG_POST,
        target_audience="healthcare professionals",
        word_count=600,
        style_requirements={
            "tone": "professional",
            "include_statistics": True
        }
    )
    
    print(f"📝 Creating content about: {request.topic}")
    print(f"📊 Content type: {request.content_type}")
    print(f"👥 Target audience: {request.target_audience}")
    print(f"📏 Target word count: {request.word_count}")
    print("\n⏳ Processing... (this may take 1-2 minutes)")
    
    try:
        # Execute content creation
        result = await orchestrator.create_content(request)
        
        if result["status"] == "success":
            print("\n✅ Content creation successful!")
            print("=" * 50)
            
            content = result["content"]
            
            # Display results
            print(f"📰 Title: {content['title']}")
            print(f"📊 Word count: {content['metadata']['word_count']}")
            print(f"⏱️  Reading time: {content['metadata']['reading_time']} minutes")
            print(f"🔍 Research sources: {content['metadata']['research_sources']}")
            
            # Quality metrics
            quality = content["quality_metrics"]
            print(f"\n📈 Quality Metrics:")
            print(f"   Overall Quality: {quality['overall_quality']:.2f}")
            print(f"   SEO Score: {quality['seo_score']:.2f}")
            print(f"   Fact-check Score: {quality['fact_check_score']:.2f}")
            print(f"   Research Depth: {quality['research_depth']:.2f}")
            
            # Show key findings
            research = content["research_summary"]
            print(f"\n🔬 Key Research Findings:")
            for i, finding in enumerate(research["key_findings"], 1):
                print(f"   {i}. {finding}")
            
            # Show content preview
            content_text = content["content"]
            preview = content_text[:300] + "..." if len(content_text) > 300 else content_text
            print(f"\n📄 Content Preview:")
            print("-" * 30)
            print(preview)
            print("-" * 30)
            
            print(f"\n⚡ Execution time: {result['execution_time']:.2f} seconds")
            
        else:
            print(f"\n❌ Content creation failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n💥 Error during demo: {str(e)}")


async def demo_individual_agents():
    """Demonstrate individual agent functionality."""
    
    print("\n🤖 Individual Agent Demo")
    print("=" * 50)
    
    from app.agents.research_agent import ResearchAgent
    from app.agents.writer_agent import WriterAgent
    
    # Test Research Agent
    print("🔍 Testing Research Agent...")
    research_agent = ResearchAgent()
    
    research_input = {
        "topic": "machine learning applications",
        "depth": 2
    }
    
    try:
        research_result = await research_agent.execute(research_input)
        if research_result["status"] == "success":
            research_data = research_result["research_data"]
            print(f"   ✅ Found {len(research_data['key_findings'])} key findings")
            print(f"   ✅ Gathered {len(research_data['sources'])} sources")
            print(f"   ✅ Confidence score: {research_result['confidence_score']:.2f}")
        else:
            print(f"   ❌ Research failed: {research_result.get('message')}")
    except Exception as e:
        print(f"   💥 Research agent error: {str(e)}")
    
    # Test Writer Agent
    print("\n✍️  Testing Writer Agent...")
    writer_agent = WriterAgent()
    
    # Use mock research data for writer
    mock_research_data = {
        "key_findings": [
            "Machine learning improves decision making",
            "AI reduces operational costs",
            "Automation increases efficiency"
        ],
        "main_arguments": [
            "ML transforms business processes",
            "AI enables predictive analytics"
        ],
        "sources": [
            {"title": "ML in Business", "url": "example.com", "source": "Tech Journal"}
        ]
    }
    
    writer_input = {
        "topic": "machine learning in business",
        "research_data": mock_research_data,
        "content_type": ContentType.ARTICLE,
        "target_audience": "business executives",
        "word_count": 400
    }
    
    try:
        writer_result = await writer_agent.execute(writer_input)
        if writer_result["status"] == "success":
            writing_output = writer_result["writing_output"]
            print(f"   ✅ Generated content: {writing_output['word_count']} words")
            print(f"   ✅ Title: {writing_output['title']}")
            print(f"   ✅ Reading time: {writing_output['estimated_reading_time']} minutes")
        else:
            print(f"   ❌ Writing failed: {writer_result.get('message')}")
    except Exception as e:
        print(f"   💥 Writer agent error: {str(e)}")


def print_system_info():
    """Print system information."""
    print("\n💻 System Information")
    print("=" * 50)
    
    from app.config import settings
    
    print(f"App Name: {settings.app_name}")
    print(f"Version: {settings.app_version}")
    print(f"OpenAI Model: {settings.openai_model}")
    print(f"Max Content Length: {settings.max_content_length}")
    print(f"Quality Threshold: {settings.default_quality_threshold}")
    
    # Check if API key is configured
    api_key_status = "✅ Configured" if settings.openai_api_key else "❌ Missing"
    print(f"OpenAI API Key: {api_key_status}")


async def main():
    """Main demo function."""
    print_system_info()
    
    # Run individual agent tests first
    await demo_individual_agents()
    
    # Run full pipeline demo
    await demo_content_creation()
    
    print("\n🎉 Demo completed!")
    print("\nTo start the API server, run:")
    print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\nThen visit: http://localhost:8000/docs for API documentation")


if __name__ == "__main__":
    asyncio.run(main())