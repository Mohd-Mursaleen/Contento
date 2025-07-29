#!/usr/bin/env python3
"""
Quick system test to verify the Content Creation Pipeline is working.
"""

import asyncio
import sys
from app.models.content import ContentRequest, ContentType
from app.core.orchestrator import ContentOrchestrator


async def test_system():
    """Test the system with a simple request."""
    print("🧪 Testing Content Creation Pipeline")
    print("=" * 40)
    
    try:
        # Initialize orchestrator
        orchestrator = ContentOrchestrator()
        
        # Create a simple test request
        request = ContentRequest(
            user_id="test-user",
            topic="benefits of renewable energy",
            content_type=ContentType.ARTICLE,
            target_audience="general public",
            word_count=300
        )
        
        print(f"📝 Testing content creation for: {request.topic}")
        print("⏳ Processing...")
        
        # Execute content creation
        result = await orchestrator.create_content(request)
        
        if result["status"] == "success":
            content = result["content"]
            print("\n✅ Test PASSED!")
            print(f"📰 Title: {content['title']}")
            print(f"📊 Word count: {content['metadata']['word_count']}")
            print(f"⭐ Quality score: {content['quality_metrics']['overall_quality']:.2f}")
            print(f"⚡ Execution time: {result['execution_time']:.1f}s")
            
            # Show content preview
            content_preview = content['content'][:200] + "..."
            print(f"\n📄 Content preview:\n{content_preview}")
            
            return True
        else:
            print(f"\n❌ Test FAILED: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n💥 Test ERROR: {str(e)}")
        return False


async def main():
    """Main test function."""
    success = await test_system()
    
    if success:
        print("\n🎉 System is working correctly!")
        print("\nNext steps:")
        print("1. Run 'uvicorn app.main:app --reload' to start the API server")
        print("2. Visit http://localhost:8000/docs for API documentation")
        print("3. Use the API endpoints to create content")
        sys.exit(0)
    else:
        print("\n❌ System test failed. Please check the configuration.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())