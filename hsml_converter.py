import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class HSMLConverter:
    def __init__(self):
        self.key = os.getenv("OPENAI_API_KEY")
        if not self.key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=self.key)
        self.assistant_id = os.getenv("ASSISTANT_ID")
        self.vector_store_id = os.getenv("VECTOR_STORE_ID")
        self.thread_id = os.getenv("THREAD_ID")
        
        # Initialize if not already set up
        if not self.assistant_id:
            self.setup_assistant()
        if not self.vector_store_id:
            self.setup_vector_store()
        if not self.thread_id:
            self.setup_thread()
        
        # Always update assistant with latest instructions
        if self.assistant_id:
            self.update_assistant()
    
    def setup_assistant(self):
        """Create the HSML converter assistant"""
        instructions = self.get_instructions()
        
        assistant = self.client.beta.assistants.create(
            name="HSML Converter",
            instructions=instructions,
            model="gpt-4-turbo",
            tools=[{"type": "file_search"}]
        )
        
        self.assistant_id = assistant.id
        print(f"Created assistant with ID: {self.assistant_id}")
        print("Please add this to your .env file: ASSISTANT_ID=" + self.assistant_id)
    
    def get_instructions(self):
        """Get the instructions for the HSML converter assistant"""
        return """You are an expert HSML converter AI. Before responding, search the HSML schema file and example files using the file_search tool to determine the correct field names, class rules, and formatting patterns.

Your job is to convert arbitrary input JSON into a valid HSML JSON object. Follow these strict rules:

- **MOST CRITICAL - ARRAY FORMATTING**: Arrays MUST be formatted as simple JSON arrays with square brackets and no index keys
  - CORRECT: "specialties": ["3D Modeling", "Simulation", "AI", "VR"]
  - CORRECT: "skills": ["Python", "JavaScript", "React"]
  - WRONG: "specialties": [0:"3D Modeling", 1:"Simulation", 2:"AI", 3:"VR"]
  - WRONG: "specialties": {"0": "3D Modeling", "1": "Simulation", "2": "AI", "3": "VR"}
  - WRONG: "specialties": [0:"3D Modeling" 1:"Simulation" 2:"AI" 3:"VR"]
- **CRITICAL JSON SYNTAX**: Include commas between all properties and array elements
  - CORRECT: "name": "John", "email": "john@example.com"
  - CORRECT: "items": ["item1", "item2", "item3"]
  - WRONG: "name": "John" "email": "john@example.com"
  - WRONG: "items": ["item1" "item2" "item3"]
- **DATA TYPES**: Preserve original data types (numbers as numbers, strings as strings)
  - CORRECT: "age": 25, "score": 95.5
  - WRONG: "age": "25", "score": "95.5"
- **REFERENCE EXAMPLES**: Use the HSML example files as templates for proper structure and formatting
- **PRESERVE NESTED STRUCTURES**: Keep nested objects intact when they make logical sense (e.g., coordinates, specifications, position, etc.)
  - CORRECT: "properties": {"coordinates": {"latitude": 37.7749, "longitude": -122.4194}}
  - WRONG: "properties": {"latitude": 37.7749, "longitude": -122.4194}
- Classify the object as one of the HSML types: Agent, Activity, Credential, Domain, Person, Organization, Object, etc.
- Include fields: @context, swid, name, @type, linkedTo, properties
- Use "@context": "https://hsml.org/context"
- Generate swid as "did:key:entity-name-12345"
- Move unmapped keys into the "properties" field, but preserve logical groupings
- Output a **single valid JSON object only**. No text, no code blocks, no explanation.
- **FINAL CHECK**: Before outputting, verify that all arrays use proper JSON syntax: ["value1", "value2", "value3"]"""
    
    def update_assistant(self):
        """Update the assistant with improved instructions"""
        instructions = self.get_instructions()
        
        try:
            self.client.beta.assistants.update(
                assistant_id=self.assistant_id,
                instructions=instructions
            )
            print("Updated assistant with improved instructions")
        except Exception as e:
            print(f"Warning: Could not update assistant: {e}")
    
    def force_update_assistant(self):
        """Force update the assistant with latest instructions"""
        if not self.assistant_id:
            print("No assistant ID found. Please set up the assistant first.")
            return
        
        instructions = self.get_instructions()
        
        try:
            self.client.beta.assistants.update(
                assistant_id=self.assistant_id,
                instructions=instructions
            )
            print("Successfully updated assistant with latest instructions")
            print("The assistant should now properly format arrays as JSON arrays")
        except Exception as e:
            print(f"Error updating assistant: {e}")
    
    def setup_vector_store(self):
        """Create vector store and upload HSML schema and examples"""
        # Create vector store
        vector_store = self.client.vector_stores.create(name="HSML Schema")
        self.vector_store_id = vector_store.id
        print(f"Created vector store with ID: {self.vector_store_id}")
        print("Please add this to your .env file: VECTOR_STORE_ID=" + self.vector_store_id)
        
        file_ids = []
        
        # Upload HSML schema document
        schema_path = "docs/HSML Schema Doc.docx"
        if os.path.exists(schema_path):
            uploaded_file = self.client.files.create(
                file=open(schema_path, "rb"), 
                purpose="assistants"
            )
            file_ids.append(uploaded_file.id)
            print(f"Uploaded schema file to vector store: {uploaded_file.id}")
        else:
            print(f"Warning: Schema file not found at {schema_path}")
        
        # Upload HSML example files
        examples_dir = "examples"
        if os.path.exists(examples_dir):
            for filename in os.listdir(examples_dir):
                if filename.endswith('Example.json'):
                    example_path = os.path.join(examples_dir, filename)
                    try:
                        uploaded_file = self.client.files.create(
                            file=open(example_path, "rb"),
                            purpose="assistants"
                        )
                        file_ids.append(uploaded_file.id)
                        print(f"Uploaded HSML example: {filename} -> {uploaded_file.id}")
                    except Exception as e:
                        print(f"Error uploading {filename}: {e}")
        
        # Add all files to vector store
        if file_ids:
            vector_store_file_batch = self.client.vector_stores.file_batches.create(
                vector_store_id=self.vector_store_id,
                file_ids=file_ids
            )
            print(f"Added {len(file_ids)} files to vector store")
        
        # Update assistant with vector store
        if self.assistant_id:
            self.client.beta.assistants.update(
                assistant_id=self.assistant_id,
                tool_resources={"file_search": {"vector_store_ids": [self.vector_store_id]}}
            )
            print("Updated assistant with vector store")
    
    def setup_thread(self):
        """Create a thread for conversations"""
        thread = self.client.beta.threads.create()
        self.thread_id = thread.id
        print(f"Created thread with ID: {self.thread_id}")
        print("Please add this to your .env file: THREAD_ID=" + self.thread_id)
    
    def convert_json_to_hsml(self, input_json):
        """Convert JSON to HSML using OpenAI Assistant"""
        try:
            # Create message with the input JSON
            message = self.client.beta.threads.messages.create(
                thread_id=self.thread_id,
                role="user",
                content=input_json
            )
            
            # Run the assistant
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.thread_id,
                assistant_id=self.assistant_id
            )
            
            # Get the response
            messages = list(self.client.beta.threads.messages.list(
                thread_id=self.thread_id, 
                run_id=run.id
            ))
            
            if messages:
                message_content = messages[0].content[0].text.value
                return message_content.strip()
            else:
                return "Error: No response received"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def interactive_mode(self):
        """Run in interactive mode for testing"""
        print("HSML Converter - Interactive Mode")
        print("Enter JSON to convert to HSML (or 'quit' to exit)")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\nInput JSON to convert to HSML: ")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not user_input.strip():
                    continue
                
                print("\nConverting...")
                result = self.convert_json_to_hsml(user_input)
                print(f"\nHSML Output:\n{result}\n")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main function to run the converter"""
    try:
        converter = HSMLConverter()
        
        # Check command line arguments
        import sys
        if len(sys.argv) > 1:
            if sys.argv[1] == "--interactive":
                converter.interactive_mode()
            elif sys.argv[1] == "--update":
                converter.force_update_assistant()
            else:
                print("HSML Converter initialized!")
                print("Available options:")
                print("  --interactive  Run in interactive mode")
                print("  --update       Force update assistant with latest instructions")
                print("Or import and use the convert_json_to_hsml() method")
        else:
            print("HSML Converter initialized!")
            print("Available options:")
            print("  --interactive  Run in interactive mode")
            print("  --update       Force update assistant with latest instructions")
            print("Or import and use the convert_json_to_hsml() method")
            
    except Exception as e:
        print(f"Error initializing HSML Converter: {e}")

if __name__ == "__main__":
    main() 