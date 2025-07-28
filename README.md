# HSML Converter - Local AI with Schema Integration

A powerful Streamlit application that converts JSON data to HSML (Hyperspace Modeling Language) format using local AI processing and your actual HSML schema documentation.

## 🚀 Features

- **Local AI Processing**: Uses LM Studio for privacy and offline operation
- **Schema-Aware Conversions**: Integrates with your HSML schema document for accurate results
- **Semantic Search**: Automatically finds relevant HSML rules for each conversion
- **Modern UI**: Clean, responsive interface with chat-like conversation
- **Sample Data**: Built-in examples for quick testing
- **No API Keys**: Completely local - no external dependencies

## 📋 Prerequisites

1. **Python 3.8+**
2. **LM Studio** installed and running
3. **HSML Schema Document** (`docs/HSML Schema Doc.docx`)

## 🛠️ Installation

1. **Clone or download** this repository
2. **Navigate** to the project directory:
   ```bash
   cd HSML_Conversion
   ```

3. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Quick Start

1. **Start LM Studio**:
   - Open LM Studio
   - Load your preferred model
   - Ensure it's running on `http://localhost:1234`

2. **Run the Streamlit app**:
   ```bash
   source venv/bin/activate
   streamlit run app.py
   ```

3. **Open your browser** to `http://localhost:8501`

4. **Start converting**:
   - Paste JSON data in the input area
   - Use sample examples from the sidebar
   - Click "Convert" to get HSML output

## 📁 Project Structure

```
HSML_Conversion/
├── app.py                     # Main Streamlit application
├── schema_search.py           # Local schema search engine
├── docs/
│   └── HSML Schema Doc.docx   # Your HSML schema document
├── requirements.txt           # Python dependencies
├── README.md                 # This file
└── venv/                     # Virtual environment
```

## 🔧 How It Works

### 1. Schema Integration
- **Loads** your HSML schema document on startup
- **Creates searchable embeddings** for semantic search
- **No internet required** - everything runs locally

### 2. Smart Conversion Process
1. **Input JSON** → App analyzes the data structure
2. **Schema Search** → Finds relevant HSML rules from your document
3. **Dynamic Prompt** → Includes schema rules in AI instructions
4. **LM Studio Processing** → Local AI generates accurate HSML
5. **Output** → Properly formatted HSML with correct field names

### 3. Enhanced Accuracy
- **Entity Type Classification**: Uses schema to determine correct HSML types
- **Field Name Mapping**: Maps JSON fields to proper HSML properties
- **SWID Generation**: Creates unique identifiers following HSML standards
- **Property Organization**: Correctly structures additional properties

## 📝 Sample Usage

### Input JSON:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "developer",
  "department": "Engineering",
  "employee_id": "EMP001"
}
```

### Output HSML:
```json
{
  "@context": "https://hsml.org/context",
  "swid": "agent-john-doe-emp001",
  "name": "John Doe",
  "description": "Developer in Engineering department",
  "type": "Agent",
  "linkedTo": [],
  "properties": {
    "email": "john@example.com",
    "role": "developer",
    "department": "Engineering",
    "employee_id": "EMP001"
  }
}
```

## 🎨 UI Features

- **Centered Layout**: Clean, modern interface
- **Chat Interface**: Conversation-style message display
- **Sample Examples**: Quick-start examples in sidebar
- **Responsive Design**: Works on desktop and mobile
- **Loading Indicators**: Shows conversion progress

## 🔍 Schema Search Capabilities

The app automatically searches your HSML schema for:
- **Entity types** (Agent, Organization, System, etc.)
- **Field definitions** and requirements
- **Property mappings** and naming conventions
- **Relationship rules** and constraints

## 🛡️ Privacy & Security

- **100% Local**: No data sent to external services
- **No API Keys**: No external dependencies or costs
- **Offline Capable**: Works without internet connection
- **Data Privacy**: Your JSON data never leaves your machine

## 🐛 Troubleshooting

### LM Studio Connection Issues
- Ensure LM Studio is running on port 1234
- Check that a model is loaded in LM Studio
- Verify the model is responding to requests

### Schema Document Issues
- Ensure `docs/HSML Schema Doc.docx` exists
- Check file permissions and readability
- Verify the document contains valid HSML schema content

### Dependencies Issues
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version`

## 📚 Dependencies

- **streamlit**: Web application framework
- **requests**: HTTP client for LM Studio communication
- **python-dotenv**: Environment variable management
- **python-docx**: Microsoft Word document processing
- **sentence-transformers**: Semantic search capabilities
- **scikit-learn**: Machine learning utilities
