#!/usr/bin/env python3
"""
Test file upload capabilities for Z.ai API - Fixed version with proper encoding
Demonstrates how to upload files and use them in chat conversations
"""

import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize the OpenAI client with Z.ai's coding endpoint
client = OpenAI(
    api_key=os.getenv("ZAI_API_KEY"),
    base_url="https://api.z.ai/api/coding/paas/v4"
)

def upload_file_properly(file_path):
    """
    Upload a file to Z.ai API using the proper file upload method
    Based on the documentation: POST to /api/paas/v4/files with purpose=agent
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None
    
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
            
        # Use the client's file upload method (if available)
        # Manually constructing the multipart request
        import requests
        
        url = "https://api.z.ai/api/paas/v4/files"
        headers = {
            "Authorization": f"Bearer {os.getenv('ZAI_API_KEY')}",
            "Accept": "application/json"
        }
        
        # Proper multipart form data
        files = {
            'file': (os.path.basename(file_path), file_data, 'text/plain'),
            'purpose': (None, 'agent')
        }
        
        response = requests.post(url, headers=headers, files=files)
        
        print(f"Upload status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Upload successful!")
                print(f"File ID: {result.get('id')}")
                print(f"Filename: {result.get('filename')}")
                print(f"Size: {result.get('bytes')} bytes")
                return result.get('id')
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {e}")
                print(f"Raw response: {response.text}")
                return None
        else:
            print(f"Upload failed with status {response.status_code}")
            try:
                error_info = response.json()
                print(f"Error details: {error_info}")
            except:
                print(f"Raw error response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return None

def chat_with_file_content(file_path, question):
    """
    Alternative approach: Read file content directly and include it in chat
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # Include the content in the chat message
        response = client.chat.completions.create(
            model="glm-4.6",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful assistant that can answer questions based on document content provided by the user."
                },
                {
                    "role": "user",
                    "content": f"Based on the following document content, please answer this question: {question}\n\nDocument content:\n{file_content}"
                }
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error chatting with file content: {str(e)}"

def create_sample_document():
    """Create a sample text file for testing"""
    sample_content = """Sample Knowledge Base Document

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

Important Facts:
- AI can process large amounts of data faster than humans
- Machine learning models improve with more data
- Deep learning has revolutionized computer vision
- NLP is used in chatbots and translation services

Conclusion:
AI and machine learning are transforming many industries and will continue to advance rapidly in the coming years."""
    
    with open("sample_knowledge.txt", "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    print("Sample document 'sample_knowledge.txt' created successfully!")
    return "sample_knowledge.txt"

def test_knowledge_retrieval(file_path):
    """Test how well the AI can retrieve information from the document"""
    test_questions = [
        "What are the 5 main topics mentioned in the document?",
        "Define what a Neural Network is according to the document.",
        "What are 3 applications of AI mentioned?",
        "What is the difference between AI and Machine Learning according to this text?",
        "What conclusion does the document reach about AI?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\nQuestion {i}: {question}")
        answer = chat_with_file_content(file_path, question)
        print(f"Answer: {answer}")
        print("-" * 60)

def main():
    """Main demonstration function"""
    print("Z.ai File Upload and Knowledge Base Test")
    print("="*60)
    
    # Check API key
    if not os.getenv("ZAI_API_KEY"):
        print("Error: ZAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your Z.ai API key:")
        print("ZAI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Step 1: Create a sample document
    print("\n1. Creating sample knowledge document...")
    sample_file = create_sample_document()
    
    # Step 2: Try the official file upload method
    print(f"\n2. Testing official file upload method...")
    file_id = upload_file_properly(sample_file)
    
    if file_id:
        print("Official file upload works!")
        # You could then use this file_id in subsequent API calls
    else:
        print("Official file upload failed, will use content embedding method")
    
    # Step 3: Test knowledge retrieval using content embedding
    print("\n3. Testing knowledge retrieval using content embedding...")
    test_knowledge_retrieval(sample_file)
    
    # Step 4: Clean up (optional)
    cleanup = input("\nRemove sample file? (y/n): ").lower().strip()
    if cleanup == 'y':
        try:
            os.remove(sample_file)
            print(f"Sample file '{sample_file}' removed.")
        except:
            print(f"Could not remove '{sample_file}'.")
    
    print("\nKnowledge base test completed!")
    print("\nSummary:")
    print("- File upload support: Available via official API")
    print("- Alternative method: Embed content directly in chat messages")
    print("- Supported formats: pdf, doc, xlsx, ppt, txt, jpg, png")
    print("- File limit: 100MB max, 100 files total, 180 days retention")

if __name__ == "__main__":
    main()
