#!/usr/bin/env python3
"""
Z.ai Knowledge Agent Demo
Shows how to create a chatbot agent with persistent knowledge files
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize the OpenAI client with Z.ai's coding endpoint
client = OpenAI(
    api_key=os.getenv("ZAI_API_KEY"),
    base_url="https://api.z.ai/api/coding/paas/v4"  # Only use coding endpoint
)

class KnowledgeAgent:
    """Chatbot agent with persistent knowledge base"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.uploaded_files = {}  # Store file_id: filename mapping
        self.conversation_history = []
    
    def upload_knowledge_file(self, file_path):
        """Upload a knowledge file and store its ID"""
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return None
        
        try:
            url = "https://api.z.ai/api/paas/v4/files"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            files = {
                'file': (os.path.basename(file_path), file_data, 'text/plain'),
                'purpose': (None, 'agent')
            }
            
            response = requests.post(url, headers=headers, files=files)
            
            if response.status_code == 200:
                result = response.json()
                file_id = result.get('id')
                filename = result.get('filename')
                
                # Store the uploaded file info
                self.uploaded_files[file_id] = {
                    'filename': filename,
                    'size': result.get('bytes'),
                    'local_path': file_path
                }
                
                print(f"✓ Knowledge file uploaded: {filename} (ID: {file_id})")
                return file_id
            else:
                print(f"Upload failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return None
    
    def add_file_to_conversation(self, file_id, user_message):
        """Add conversation with reference to uploaded file"""
        
        # Build conversation with file reference
        messages = [
            {
                "role": "system",
                "content": f"You are a helpful assistant with access to uploaded knowledge files. The user has uploaded the following files: {', '.join([f['filename'] for f in self.uploaded_files.values()])}. Use this information to answer questions accurately."
            },
            {
                "role": "user",
                "content": f"Based on the uploaded file (ID: {file_id}), {user_message}"
            }
        ]
        
        # Add conversation history
        for msg in self.conversation_history[-5:]:  # Keep last 5 messages for context
            messages.append(msg)
        
        try:
            response = client.chat.completions.create(
                model="glm-4.6",
                messages=messages,
                max_tokens=1500,
                temperature=0.3
            )
            
            assistant_response = response.choices[0].message.content
            
            # Store conversation
            self.conversation_history.append({
                "role": "user", 
                "content": f"Question about file {self.uploaded_files.get(file_id, {}).get('filename', 'unknown')}: {user_message}"
            })
            self.conversation_history.append({
                "role": "assistant", 
                "content": assistant_response
            })
            
            return assistant_response
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat_with_knowledge(self, question):
        """Chat using all uploaded knowledge files"""
        
        # Build system message with file context
        file_list = "\n".join([f"- {info['filename']} (ID: {file_id})" for file_id, info in self.uploaded_files.items()])
        
        messages = [
            {
                "role": "system",
                "content": f"""You are a helpful assistant with access to the following uploaded knowledge files:
{file_list}

These files contain relevant information. When answering questions, reference the appropriate uploaded files and use their content to provide accurate, helpful responses. If information isn't available in the uploaded files, say so clearly."""
            },
            {
                "role": "user",
                "content": question
            }
        ]
        
        # Add relevant conversation history
        for msg in self.conversation_history[-3:]:
            messages.append(msg)
        
        try:
            response = client.chat.completions.create(
                model="glm-4.6",
                messages=messages,
                max_tokens=1500,
                temperature=0.3
            )
            
            assistant_response = response.choices[0].message.content
            
            # Store conversation
            self.conversation_history.append({
                "role": "user", 
                "content": question
            })
            self.conversation_history.append({
                "role": "assistant", 
                "content": assistant_response
            })
            
            return assistant_response
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def list_uploaded_files(self):
        """Show all uploaded knowledge files"""
        if not self.uploaded_files:
            print("No knowledge files uploaded yet.")
            return
        
        print("\nUploaded Knowledge Files:")
        print("-" * 50)
        for file_id, info in self.uploaded_files.items():
            print(f"Filename: {info['filename']}")
            print(f"File ID: {file_id}")
            print(f"Size: {info['size']} bytes")
            print(f"Local path: {info['local_path']}")
            print("-" * 50)
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("Conversation history cleared.")

def create_sample_knowledge_files():
    """Create sample knowledge files for testing"""
    
    # File 1: Company Policies
    policies = """
Company Policies and Procedures

Employee Handbook - 2025 Edition

1. Working Hours
   - Standard hours: 9:00 AM - 5:00 PM, Monday to Friday
   - Lunch break: 12:00 PM - 1:00 PM
   - Overtime requires prior approval from manager

2. Remote Work Policy
   - Employees may work up to 3 days per week remotely
   - Remote work must be approved by direct manager
   - Must be available during core hours (10 AM - 3 PM)

3. Leave Policy
   - Vacation: 20 days per year (pro-rated for new hires)
   - Sick leave: 10 days per year
   - Personal leave: 5 days per year
   - All leave requests must be submitted 2 weeks in advance

4. IT Security
   - Use company-issued devices for work
   - Passwords must be changed every 90 days
   - Two-factor authentication required for all systems
   - Report security incidents immediately to IT

5. Communication Guidelines
   - Use official email for work communication
   - Response time: within 24 hours for emails
   - Slack for urgent matters (response within 2 hours)
   - All client communications must be professional
"""
    
    # File 2: Product Information
    product_info = """
Product Technical Specifications

Z.ai GLM-4.6 Language Model

Technical Specifications:
- Parameters: 355 billion
- Context Length: 128K tokens
- Training Data: Multi-language corpus up to 2024
- Response Format: Text, JSON, structured output
- Languages: 100+ including English, Chinese, Spanish, French

Performance Metrics:
- Accuracy: 94% on standard benchmarks
- Speed: Average response time 2.3 seconds
- Throughput: 1000 requests per minute
- Reliability: 99.9% uptime

Use Cases:
1. Customer Support Automation
   - Handle common inquiries
   - Provide product information
   - Escalate complex issues to human agents

2. Content Generation
   - Blog posts and articles
   - Marketing copy
   - Technical documentation

3. Data Analysis
   - Summarize large datasets
   - Extract insights from text
   - Generate reports

4. Code Assistance
   - Code generation and debugging
   - Documentation creation
   - Test case generation

Pricing:
- Pay-as-you-go: $0.6/1K input tokens, $2.2/1K output tokens
- Enterprise: Custom pricing available
- Free tier: Available for development testing
"""
    
    with open("company_policies.txt", "w", encoding="utf-8") as f:
        f.write(policies)
    
    with open("product_specifications.txt", "w", encoding="utf-8") as f:
        f.write(product_info)
    
    print("Sample knowledge files created:")
    print("- company_policies.txt")
    print("- product_specifications.txt")

def interactive_demo():
    """Interactive demonstration of the knowledge agent"""
    
    print("Z.ai Knowledge Agent Demo")
    print("=" * 50)
    
    # Check API key
    if not os.getenv("ZAI_API_KEY"):
        print("Error: ZAI_API_KEY not found. Please set it in .env file.")
        sys.exit(1)
    
    # Create knowledge agent
    agent = KnowledgeAgent(os.getenv("ZAI_API_KEY"))
    
    # Create sample files
    print("\nCreating sample knowledge files...")
    create_sample_knowledge_files()
    
    # Upload knowledge files
    print("\nUploading knowledge files...")
    file1_id = agent.upload_knowledge_file("company_policies.txt")
    file2_id = agent.upload_knowledge_file("product_specifications.txt")
    
    if not file1_id or not file2_id:
        print("Failed to upload files. Please check your API key and balance.")
        return
    
    # Show uploaded files
    agent.list_uploaded_files()
    
    # Interactive chat
    print("\nKnowledge Agent Ready!")
    print("Commands:")
    print("  'ask <question>' - Ask about your uploaded files")
    print("  'file <file_id> <question>' - Ask about specific file")
    print("  'list' - Show uploaded files")
    print("  'clear' - Clear conversation history")
    print("  'quit' - Exit")
    print()
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
        
        if user_input.lower() == 'list':
            agent.list_uploaded_files()
            continue
        
        if user_input.lower() == 'clear':
            agent.clear_history()
            continue
        
        if user_input.startswith('file '):
            parts = user_input[5:].strip().split(' ', 1)
            if len(parts) == 2:
                file_id, question = parts
                if file_id in agent.uploaded_files:
                    response = agent.add_file_to_conversation(file_id, question)
                    print(f"Agent: {response}")
                else:
                    print(f"File ID '{file_id}' not found. Use 'list' to see available files.")
            else:
                print("Format: file <file_id> <question>")
            continue
        
        if user_input.startswith('ask '):
            question = user_input[4:].strip()
            response = agent.chat_with_knowledge(question)
            print(f"Agent: {response}")
            continue
        
        print("Please use: ask <question>, file <file_id> <question>, list, clear, or quit")

if __name__ == "__main__":
    interactive_demo()
