import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Simple HSML schema reader
def load_hsml_schema():
    """Load HSML schema from the document"""
    try:
        from docx import Document
        doc = Document("docs/HSML Schema Doc.docx")
        schema_text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                schema_text.append(paragraph.text.strip())
        return "\n".join(schema_text)
    except Exception as e:
        st.warning(f"Could not load HSML schema document: {e}")
        return ""

def get_relevant_schema_rules(input_json, schema_text):
    """Get relevant schema rules based on input"""
    if not schema_text:
        return ""
    
    # Simple keyword matching
    keywords = []
    if isinstance(input_json, dict):
        keywords.extend(input_json.keys())
        
        # Add entity type hints
        for key, value in input_json.items():
            if key in ['email', 'role', 'job_title', 'works_for']:
                keywords.append('Person')
            elif key in ['issued_by', 'access_authorization', 'valid_for']:
                keywords.append('Credential')
            elif key in ['position', 'rotation', 'space_location']:
                keywords.append('Agent')
            elif key in ['parent_company', 'subsidiaries']:
                keywords.append('Organization')
    
    # Find relevant schema sections
    relevant_rules = []
    schema_lines = schema_text.split('\n')
    
    for keyword in keywords[:5]:  # Limit to top 5 keywords
        for i, line in enumerate(schema_lines):
            if keyword.lower() in line.lower():
                # Get context around the match
                start = max(0, i-2)
                end = min(len(schema_lines), i+3)
                context = '\n'.join(schema_lines[start:end])
                if context not in relevant_rules:
                    relevant_rules.append(context)
    
    if relevant_rules:
        return "**HSML Schema Rules:**\n\n" + "\n\n".join(relevant_rules[:3])
    return ""

# Page configuration
st.set_page_config(
    page_title="HSML Converter",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple, clean styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .section-title {
        color: #2c3e50;
        font-size: 1.3rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3498db;
    }
    
    .stExpander > div > div {
        text-align: center;
    }
    
    div[data-testid="stExpander"] {
        text-align: center;
    }
    
    .streamlit-expanderHeader {
        text-align: center;
    }
    
    /* Make buttons bigger and same size */
    .stButton > button {
        height: 50px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        min-width: 120px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "lm_studio_url" not in st.session_state:
    st.session_state.lm_studio_url = "http://localhost:1234/v1/chat/completions"



# LM Studio configuration (hardcoded)
lm_url = "http://localhost:1234/v1/chat/completions"
model_name = "llama-3.2-3b-instruct"  # Use available model in LM Studio

# Sidebar content
with st.sidebar:
    st.markdown("### Quick Start:")
    st.markdown("""
    1. **Start LM Studio** and load your preferred model
    2. **Make sure LM Studio is running** on the default port (1234)
    3. **Paste JSON data** in the input below or use sample data
    4. **Click Convert** to transform to HSML format
    """)
    
    st.markdown("---")
    st.markdown("### Sample JSON Examples")
    
    st.markdown("**User/Agent Example:**")
    user_json = {
        "name": "John Doe",
        "email": "john@example.com",
        "role": "developer",
        "department": "Engineering",
        "employee_id": "EMP001"
    }
    st.code(json.dumps(user_json, indent=2), language="json")
    
    if st.button("Use User Example", key="user_example", use_container_width=True):
        st.session_state.sample_json = json.dumps(user_json, indent=2)
        st.rerun()
    
    st.markdown("**Organization Example:**")
    org_json = {
        "name": "TechCorp Inc",
        "industry": "Technology",
        "founded": "2020",
        "employees": 150,
        "location": "San Francisco"
    }
    st.code(json.dumps(org_json, indent=2), language="json")
    
    if st.button("Use Organization Example", key="org_example", use_container_width=True):
        st.session_state.sample_json = json.dumps(org_json, indent=2)
        st.rerun()
    
    st.markdown("**Credential Example:**")
    cred_json = {
        "name": "AWS Access Key",
        "type": "access_key",
        "user": "john.doe",
        "created": "2024-01-15",
        "permissions": ["s3:read", "ec2:write"]
    }
    st.code(json.dumps(cred_json, indent=2), language="json")
    
    if st.button("Use Credential Example", key="cred_example", use_container_width=True):
        st.session_state.sample_json = json.dumps(cred_json, indent=2)
        st.rerun()
    
    st.markdown("**System Example:**")
    sys_json = {
        "name": "Production Server",
        "ip_address": "192.168.1.100",
        "os": "Ubuntu 22.04",
        "cpu": "8 cores",
        "ram": "32GB",
        "status": "running"
    }
    st.code(json.dumps(sys_json, indent=2), language="json")
    
    if st.button("Use System Example", key="sys_example", use_container_width=True):
        st.session_state.sample_json = json.dumps(sys_json, indent=2)
        st.rerun()
    




# Main content
st.markdown('<h1 class="main-header">HSML Converter</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Convert your JSON data to HSML format using local AI</p>', unsafe_allow_html=True)




# Function to enhance HSML structure based on entity type
def enhance_hsml_structure(hsml_data, original_input):
    """Simple enhancement - just convert type to @type and preserve basic structure"""
    enhanced = hsml_data.copy()
    
    # Convert 'type' to '@type' if present
    if "type" in enhanced and "@type" not in enhanced:
        enhanced["@type"] = enhanced.pop("type")
    
    return enhanced

# Function to call LM Studio
def call_lm_studio(messages, url, model, temp, max_tokens):
    try:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temp,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to LM Studio: {e}")
        return None
    except KeyError as e:
        st.error(f"Unexpected response format from LM Studio: {e}")
        return None

# HSML system prompt template
HSML_SYSTEM_PROMPT = """You are an expert HSML (Hyperspace Modeling Language) converter AI. 

Your job is to convert arbitrary input JSON into a valid HSML JSON object. 

**IMPORTANT**: If schema rules are provided below, you MUST follow them exactly for accurate HSML conversion.

Follow these strict rules:

1. **Classify the object** as one of the HSML types: Agent, Activity, Credential, Domain, Entity, Event, Group, Identity, Location, Object, Organization, Process, Resource, Service, System, Threat, Vulnerability, etc.

2. **Include required fields**:
   - `@context`: "https://hsml.org/context"
   - `@type`: The HSML type you classified it as
   - `swid`: Generate a unique SWID (Software ID) if not provided
   - `name`: The name/title of the entity
   - `linkedTo`: Array of related entities (if any)
   - `properties`: Object containing additional properties
   
   **IMPORTANT**: Only include fields that are explicitly provided in the input. Do NOT add description, birthDate, or other fields unless they are in the original input.

3. **Keep it simple**: 
   - Convert `role` to `jobTitle` for Person entities
   - Move `email` to top-level for Person entities
   - Put other fields in `properties` object
   - Do NOT wrap simple strings in complex schema objects

4. **Output only valid JSON** - no text, no code blocks, no explanation.

5. **Ensure the output is properly formatted** and follows HSML schema requirements.

Example Person conversion:
Input: {"name": "John Doe", "email": "john@example.com", "role": "developer", "department": "Engineering"}
Output: {
  "@context": "https://hsml.org/context",
  "swid": "did:key:person-john-doe-12345",
  "name": "John Doe",
  "@type": "Person",
  "email": "john@example.com",
  "jobTitle": "developer",
  "linkedTo": [],
  "properties": {
    "department": "Engineering"
  }
}"""

# Display chat messages
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        st.markdown("**You:**")
        try:
            if message["content"].strip().startswith("{"):
                st.json(json.loads(message["content"]))
            else:
                st.text(message["content"])
        except:
            st.text(message["content"])
    else:
        st.markdown("**HSML Converter:**")
        # Try to parse as JSON for better formatting
        try:
            # Extract JSON from markdown code blocks if present
            content = message["content"]
            if "```json" in content:
                # Extract JSON from code block
                start = content.find("```json") + 7
                end = content.find("```", start)
                json_str = content[start:end].strip()
                hsml_json = json.loads(json_str)
                st.json(hsml_json)
                
                # Add download button for this message
                json_str_formatted = json.dumps(hsml_json, indent=2)
                st.download_button(
                    label="Download",
                    data=json_str_formatted,
                    file_name=f"hsml_{hsml_json.get('type', 'entity').lower()}_{hsml_json.get('name', 'converted').replace(' ', '_').lower()}.json",
                    mime="application/json",
                    key=f"download_{i}"
                )
            elif content.strip().startswith("{"):
                hsml_json = json.loads(content)
                st.json(hsml_json)
                
                # Add download button for this message
                json_str_formatted = json.dumps(hsml_json, indent=2)
                st.download_button(
                    label="Download",
                    data=json_str_formatted,
                    file_name=f"hsml_{hsml_json.get('type', 'entity').lower()}_{hsml_json.get('name', 'converted').replace(' ', '_').lower()}.json",
                    mime="application/json",
                    key=f"download_{i}"
                )
            else:
                st.text(content)
        except:
            st.text(content)

# Input area
st.markdown("<h3 style='text-align: center;'>Enter JSON to convert to HSML</h3>", unsafe_allow_html=True)

# Initialize sample_json in session state if not exists
if "sample_json" not in st.session_state:
    st.session_state.sample_json = ""

col1, col2, col3 = st.columns([0.5, 3, 0.5])
with col2:
    user_input = st.text_area(
        "JSON Input",
        height=200,
        value=st.session_state.sample_json,
        placeholder='{"name": "example", "email": "example@email.com"}',
        key="user_input",
        label_visibility="collapsed"
    )

# Center the buttons under the text area
col1_btn, col2_btn, col3_btn = st.columns([1, 1, 1])
with col1_btn:
    st.write("")  # Empty space
with col2_btn:
    send_button = st.button("Convert", type="primary", use_container_width=True)
    if st.button("Clear Chat", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
with col3_btn:
    st.write("")  # Empty space

# Process input
if send_button and user_input.strip():
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Parse input JSON
    try:
        input_json = json.loads(user_input)
    except json.JSONDecodeError:
        input_json = {}
    
    # Load HSML schema and get relevant rules
    schema_text = load_hsml_schema()
    schema_rules = get_relevant_schema_rules(input_json, schema_text)
    
    # Create system prompt with schema rules
    if schema_rules:
        system_prompt = HSML_SYSTEM_PROMPT + "\n\n" + schema_rules
    else:
        system_prompt = HSML_SYSTEM_PROMPT
    
    # Prepare messages for LM Studio
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Convert this JSON to HSML format: {user_input}"}
    ]
    
    # Center the spinner under the buttons
    col1_spin, col2_spin, col3_spin = st.columns([1, 1, 1])
    with col1_spin:
        st.write("")  # Empty space
    with col2_spin:
        with st.spinner("Converting to HSML..."):
            # Call LM Studio with default settings
            response = call_lm_studio(
                messages, 
                lm_url, 
                model_name, 
                0.7,  # default temperature
                2000   # default max_tokens
            )
    with col3_spin:
        st.write("")  # Empty space
    
    if response:
        # Post-process the response to enhance complex structures
        try:
            # Try to parse the response as JSON
            if "```json" in response:
                # Extract JSON from code block
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
                hsml_data = json.loads(json_str)
            elif response.strip().startswith("{"):
                hsml_data = json.loads(response)
            else:
                hsml_data = None
            
            if hsml_data:
                # Enhance the HSML structure based on type
                enhanced_hsml = enhance_hsml_structure(hsml_data, input_json)
                enhanced_response = json.dumps(enhanced_hsml, indent=2)
                st.session_state.messages.append({"role": "assistant", "content": enhanced_response})
            else:
                st.session_state.messages.append({"role": "assistant", "content": response})
        except:
            # If enhancement fails, use original response
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.rerun()
    else:
        st.error("Failed to get response from LM Studio. Please check your connection.")