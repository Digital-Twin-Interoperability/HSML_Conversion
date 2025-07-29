# HSML Converter

A Streamlit application that converts arbitrary JSON data into valid HSML (Hyperspace Modeling Language) JSON objects using OpenAI's Assistant API with file search capabilities.

## Features

- **OpenAI Assistant API**: Uses GPT-4 Turbo with file search for high-quality conversions
- **Schema-Aware Conversion**: Searches the actual HSML schema document for accurate field mappings
- **Multiple Entity Types**: Supports Person, Agent, Credential, Organization, Object, Activity, and Domain entities
- **Interactive UI**: Clean Streamlit interface with sample examples
- **Download Functionality**: Download converted HSML files
- **Conversation Context**: Maintains context across multiple conversions
- **Professional Quality**: Uses OpenAI's production-ready API

## Prerequisites

- Python 3.8+
- OpenAI API key
- HSML Schema Document (`docs/HSML Schema Doc.docx`)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd HSML_Conversion
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your OpenAI API key:**
   - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Add it to your `.env` file:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

5. **Prepare your HSML schema document:**
   - Place your HSML schema document in the `docs/` folder
   - Name it `HSML Schema Doc.docx`

6. **Run the setup script:**
   ```bash
   python setup_openai.py
   ```
   This will create the OpenAI Assistant, vector store, and upload your schema document.

## Usage

1. **Start the application:**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser:**
   - Navigate to the URL shown in the terminal (usually http://localhost:8501)

3. **Convert JSON to HSML:**
   - Enter JSON data in the text area
   - Click "Convert" to generate HSML
   - Use sample examples from the sidebar
   - Download converted files

## Configuration

The application automatically configures:
- **OpenAI Assistant**: Specialized for HSML conversion
- **Vector Store**: Contains your HSML schema document for search
- **Thread**: Maintains conversation context

All IDs are stored in your `.env` file after running the setup script.

## Supported Entity Types

### Person
- Converts `role` to `jobTitle`
- Places `email` at top-level
- Generates proper SWID with `did:key:person-` prefix

### Agent
- Handles 3D objects with position/rotation data
- Supports platform and creator information
- Generates SWID with `did:key:agent-` prefix

### Credential
- Manages access authorization and permissions
- Handles validity periods and domains
- Generates SWID with `did:key:credential-` prefix

### Organization
- Supports company hierarchies and relationships
- Handles department and contact information

### Object
- Generic entity type for other objects
- Flexible property mapping

### Activity & Domain
- Additional HSML entity types supported

## File Structure

```
HSML_Conversion/
├── app.py                    # Main Streamlit application
├── openai_hsml_converter.py  # OpenAI Assistant integration
├── setup_openai.py           # Setup script for OpenAI
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── .env                     # Environment variables (create this)
├── docs/
│   └── HSML Schema Doc.docx   # HSML schema document
├── examples/                # Sample HSML examples
│   ├── personExample.json
│   ├── credentialExample.json
│   └── ...
└── venv/                    # Virtual environment
```

## How It Works

1. **Input Processing**: Takes JSON input and determines entity type
2. **Schema Search**: Uses OpenAI's file search to find relevant HSML rules
3. **AI Conversion**: Uses GPT-4 Turbo to convert JSON to HSML format
4. **Context Maintenance**: Keeps conversation history for better results
5. **Output**: Returns clean, valid HSML JSON

## Advantages Over Local AI

- **Much Higher Quality**: Uses GPT-4 Turbo instead of local models
- **Schema-Aware**: Can actually read and understand your HSML schema document
- **Better Context**: Maintains conversation history across conversions
- **Professional Quality**: Uses OpenAI's production-ready API
- **Cleaner Output**: Produces clean JSON without extra text or formatting issues

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your API key is correct in the `.env` file
   - Check that you have sufficient credits in your OpenAI account

2. **Setup Errors**
   - Run `python setup_openai.py` to recreate the assistant and vector store
   - Check that your HSML schema document exists in the `docs/` folder

3. **Conversion Errors**
   - Check that your JSON is valid
   - Try simpler examples first
   - Ensure the assistant is properly configured

### Performance Tips

- The OpenAI API has rate limits, so avoid rapid successive conversions
- Keep JSON inputs reasonably sized
- The assistant learns from context, so related conversions will improve over time

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the HSML schema documentation
- Open an issue on GitHub
