#!/usr/bin/env python3
"""
Installation script for Content Creation Pipeline MVP
This script installs dependencies one by one to avoid build issues.
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return success status."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def install_package(package):
    """Install a single package."""
    print(f"📦 Installing {package}...")
    success, output = run_command(f"pip install {package}")
    if success:
        print(f"✅ {package} installed successfully")
        return True
    else:
        print(f"❌ Failed to install {package}: {output}")
        return False

def main():
    """Main installation function."""
    print("🚀 Content Creation Pipeline MVP - Installation")
    print("=" * 50)
    
    # Core packages that should install without issues
    packages = [
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0", 
        "pydantic>=2.8.0",
        "pydantic-settings>=2.0.0",
        "python-multipart>=0.0.6",
        "python-dotenv>=1.0.0",
        "httpx>=0.25.0",
        "aiofiles>=23.0.0",
        "openai>=1.12.0",
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "textstat>=0.7.0",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.1.0"
    ]
    
    # Upgrade pip first
    print("⬆️  Upgrading pip...")
    run_command("pip install --upgrade pip")
    
    failed_packages = []
    
    for package in packages:
        if not install_package(package):
            failed_packages.append(package)
    
    print("\n" + "=" * 50)
    if failed_packages:
        print(f"⚠️  {len(failed_packages)} packages failed to install:")
        for pkg in failed_packages:
            print(f"   - {pkg}")
        print("\nThe application should still work with the successfully installed packages.")
    else:
        print("🎉 All packages installed successfully!")
    
    print(f"\n✅ {len(packages) - len(failed_packages)}/{len(packages)} packages installed")
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("\n📝 Creating .env file from template...")
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ .env file created. Please configure your OpenAI API key.")
        else:
            print("❌ .env.example not found")
    
    print("\n🚀 Installation complete! You can now run:")
    print("   python demo.py  # To run the demo")
    print("   uvicorn app.main:app --reload  # To start the API server")

if __name__ == "__main__":
    main()