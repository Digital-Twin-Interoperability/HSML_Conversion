import streamlit as st
import json
import os
from hsml_converter import HSMLConverter

# Page configuration
st.set_page_config(
    page_title="HSML Converter",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
        margin: 0.2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize HSML Converter
@st.cache_resource
def get_hsml_converter():
    try:
        # Suppress print statements during initialization
        import sys
        from io import StringIO
        
        # Redirect stdout to suppress initialization messages
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        converter = HSMLConverter()
        
        # Restore stdout
        sys.stdout = old_stdout
        
        return converter
    except Exception as e:
        # Restore stdout in case of error
        sys.stdout = old_stdout
        st.error(f"Error initializing HSML Converter: {e}")
        return None

converter = get_hsml_converter()

# Main content
st.markdown('<h1 class="main-header">HSML Converter</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Convert your JSON data to HSML format</p>', unsafe_allow_html=True)

# Sidebar with sample JSON examples
with st.sidebar:
    st.markdown("### Sample JSON Examples")
    
    # Load example files dynamically
    examples_dir = "examples"
    sample_examples = {}
    
    if os.path.exists(examples_dir):
        for filename in os.listdir(examples_dir):
            # Only show input examples, skip the old HSML examples
            if filename.endswith('_input.json'):
                try:
                    with open(os.path.join(examples_dir, filename), 'r') as f:
                        example_data = json.load(f)
                        # Create clean, simple names for the sidebar
                        if 'person' in filename.lower():
                            example_name = "Person"
                        elif 'agent' in filename.lower():
                            example_name = "Agent"
                        elif 'credential' in filename.lower():
                            example_name = "Credential"
                        elif 'organization' in filename.lower():
                            example_name = "Organization"
                        elif 'object' in filename.lower():
                            example_name = "Object"
                        else:
                            # Fallback to filename without extension
                            example_name = filename.replace('_input.json', '').replace('_', ' ').title()
                        
                        # Only add if we don't already have this type
                        if example_name not in sample_examples:
                            sample_examples[example_name] = example_data
                except Exception as e:
                    st.error(f"Error loading {filename}: {e}")
    
    if sample_examples:
        selected_example = st.selectbox("Choose an example:", list(sample_examples.keys()))
        
        if selected_example:
            example_json = sample_examples[selected_example]
            st.json(example_json)
            
            if st.button("Use this example"):
                st.session_state.sample_json = json.dumps(example_json, indent=2)
                st.rerun()
    else:
        st.info("No example files found in the examples/ directory.")

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
            content = message["content"]
            if content.strip().startswith("{"):
                hsml_json = json.loads(content)
                st.json(hsml_json)
                
                # Add download button for this message
                json_str_formatted = json.dumps(hsml_json, indent=2)
                st.download_button(
                    label="Download",
                    data=json_str_formatted,
                    file_name=f"hsml_{hsml_json.get('@type', 'entity').lower()}_{hsml_json.get('name', 'converted').replace(' ', '_').lower()}.json",
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
    # Place buttons side by side with minimal gap
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        send_button = st.button("Convert", type="primary", use_container_width=True)
    with btn_col2:
        if st.button("Clear Chat", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
with col3_btn:
    st.write("")  # Empty space

# Process input
if send_button and user_input.strip() and converter:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Center the spinner under the buttons
    col1_spin, col2_spin, col3_spin = st.columns([1, 1, 1])
    with col1_spin:
        st.write("")  # Empty space
    with col2_spin:
        with st.spinner("Converting to HSML..."):
            # Convert using OpenAI Assistant
            response = converter.convert_json_to_hsml(user_input)
    with col3_spin:
        st.write("")  # Empty space
    
    if response and not response.startswith("Error"):
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.error(f"Conversion failed: {response}")
    
    st.rerun()

# Instructions
with st.sidebar:
    st.markdown("### How it works")
    st.markdown("""
    This app uses OpenAI's Assistant API with file search capabilities to convert JSON to HSML format.
    
    **Features:**
    - Searches the HSML schema document for accurate field mappings
    - Uses GPT-4 Turbo for high-quality conversions
    - Maintains conversation context
    - Downloads converted HSML files
    
    **Setup:**
    1. Install dependencies: `pip install -r requirements.txt`
    2. Add your OpenAI API key to `.env`
    3. Run the converter to initialize
    """) 