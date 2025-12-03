#!/usr/bin/env python3
"""
Test file upload capabilities for Z.ai API
Demonstrates how to upload files and use them in chat conversations
"""

import os
import sys
import base64
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize the OpenAI client with Z.ai's coding endpoint
client = OpenAI(
    api_key=os.getenv("ZAI_API_KEY"),
    base_url="https://api.z.ai/api/coding/paas/v4"
)

def upload_file(file_path):
    """
    Upload a file to Z.ai API using the file upload endpoint
    Returns the file ID if successful
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None
    
    try:
        # Use the file upload endpoint
        url = "https://api.z.ai/api/paas/v4/files"
        headers = {
            "Authorization": f"Bearer {os.getenv('ZAI_API_KEY')}"
        }
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/plain')}
            response = requests.post(url, headers=headers, files=files)
        
        if response.status_code == 200:
            try:
                file_data = response.json()
                print(f"File uploaded successfully!")
                print(f"File ID: {file_data.get('id')}")
                print(f"Filename: {file_data.get('filename')}")
                print(f"Size: {file_data.get('size')} bytes")
                return file_data.get('id')
            except:
                print(f"Response: {response.text}")
                return None
        else:
            print(f"Upload failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return None

def chat_with_uploaded_file(file_id, question):
    """
    Chat with the AI using the uploaded file as context
    """
    try:
        # Create a message that references the uploaded file
        response = client.chat.completions.create(
            model="glm-4.6",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Based on the file I've uploaded (ID: {file_id}), please answer: {question}"
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error chatting with file: {str(e)}"

def create_sample_document():
    """Create a sample text file for testing"""
    sample_content = """
Sample Knowledge Base Document

Title: Artificial Intelligence Basics
Created: December 2025

Content:
This document provides basic information about AI and machine learning.

1. Artificial Intelligence (AI) is the simulation of human intelligence in machines.
2. Machine Learning is a subset of AI that enables systems to learn from data.
3. Deep Learning is a subset of machine learning using neural networks.
4. Natural Language Processing (NLP) helps computers understand human language.
5. Computer Vision enables machines to interpret visual information.

Key Terms:
- Neural Networks: Computing systems inspired by biological neural networks
- Algorithm: A set of rules to be followed in calculations or problem-solving
- Data Science: An interdisciplinary field that uses scientific methods to extract knowledge from data

Applications:
- Virtual assistants (like Siri, Alexa)
- Recommendation systems (Netflix, Amazon)
- Autonomous vehicles
- Medical diagnosis
- Financial fraud detection
"""
    
    with open("sample_knowledge.txt", "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    print("Sample document 'sample_knowledge.txt' created successfully!")
    return "sample_knowledge.txt"

def test_knowledge_retrieval(file_id):
    """Test how well the AI can retrieve information from the uploaded document"""
    test_questions = [
        "What are the 5 main topics mentioned in the document?",
        "Define what a Neural Network is according to the document.",
        "What are 3 applications of AI mentioned?",
        "What is the difference between AI and Machine Learning according to this text?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\nQuestion {i}: {question}")
        answer = chat_with_uploaded_file(file_id, question)
        print(f"Answer: {answer}")
        print("-" * 50)

def main():
    """Main demonstration function"""
    print("Z.ai File Upload and Knowledge Base Test")
    print("="*50)
    
    # Check API key
    if not os.getenv("ZAI_API_KEY"):
        print("Error: ZAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your Z.ai API key:")
        print("ZAI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Step 1: Create a sample document
    print("\n1. Creating sample knowledge document...")
    sample_file = create_sample_document()
    
    # Step 2: Upload the file
    print(f"\n2. Uploading file '{sample_file}'...")
    file_id = upload_file(sample_file)
    
    if not file_id:
        print("File upload failed. Exiting.")
        return
    
    # Step 3: Test knowledge retrieval
    print("\n3. Testing knowledge retrieval from uploaded file...")
    test_knowledge_retrieval(file_id)
    
    # Step 4: Clean up (optional)
    cleanup = input("\nRemove sample file? (y/n): ").lower().strip()
    if cleanup == 'y':
        try:
            os.remove(sample_file)
            print(f"Sample file '{sample_file}' removed.")
        except:
            print(f"Could not remove '{sample_file}'.")
    
    print("\nFile upload test completed!")

if __name__ == "__main__":
    main()
