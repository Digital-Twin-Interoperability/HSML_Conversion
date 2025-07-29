#!/usr/bin/env python3
"""
Setup script for OpenAI HSML Converter
This script will help you initialize the OpenAI Assistant and vector store.
"""

import os
from dotenv import load_dotenv
from openai_hsml_converter import HSMLConverter

def main():
    print("🚀 Setting up OpenAI HSML Converter...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        print("Please add your OpenAI API key to the .env file:")
        print("OPENAI_API_KEY=your_api_key_here")
        return
    
    print("✅ OpenAI API key found")
    
    try:
        # Initialize the converter (this will create assistant, vector store, and thread)
        print("\n🔧 Initializing HSML Converter...")
        converter = HSMLConverter()
        
        print("\n✅ Setup completed successfully!")
        print("\n📝 Please add these IDs to your .env file:")
        print(f"ASSISTANT_ID={converter.assistant_id}")
        print(f"VECTOR_STORE_ID={converter.vector_store_id}")
        print(f"THREAD_ID={converter.thread_id}")
        
        print("\n🎉 You can now run the Streamlit app:")
        print("streamlit run app_openai.py")
        
        # Test the converter
        print("\n🧪 Testing the converter...")
        test_json = '{"name": "John Doe", "email": "john@example.com", "role": "developer"}'
        print(f"Input: {test_json}")
        
        result = converter.convert_json_to_hsml(test_json)
        print(f"Output: {result}")
        
        if result and not result.startswith("Error"):
            print("✅ Test successful!")
        else:
            print("❌ Test failed!")
            
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        print("\nPlease check your OpenAI API key and try again.")

if __name__ == "__main__":
    main() 