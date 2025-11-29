#!/usr/bin/env python3
"""
Setup script for Z.ai chatbot examples
"""

import subprocess
import sys
import os

def install_requirements():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install dependencies")
        return False

def setup_env_file():
    """Set up .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("Creating .env file...")
        try:
            with open('.env', 'w') as f:
                f.write("# Z.ai API Configuration\n")
                f.write("# Get your API key from: https://z.ai/manage-apikey/apikey-list\n")
                f.write("ZAI_API_KEY=your_zai_api_key_here\n")
            print(".env file created!")
            print("Please edit .env file and add your Z.ai API key")
            return True
        except Exception as e:
            print(f"Failed to create .env file: {e}")
            return False
    else:
        print(".env file already exists")
        return True

def main():
    """Main setup function"""
    print("Z.ai Chatbot Setup")
    print("=" * 30)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("Python 3.7 or higher is required")
        return
    
    # Install dependencies
    if not install_requirements():
        return
    
    # Set up .env file
    if not setup_env_file():
        return
    
    print("\nSetup completed!")
    print("\nNext steps:")
    print("1. Get your API key from https://z.ai/manage-apikey/apikey-list")
    print("2. Edit .env file and replace 'your_zai_api_key_here' with your actual API key")
    print("3. Run one of the examples:")
    print("   - python zai_chatbot.py (basic chatbot)")
    print("   - python advanced_zai_chatbot.py (with streaming and function calling)")
    print("   - python multimodal_example.py (vision capabilities)")

if __name__ == "__main__":
    main()