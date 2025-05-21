# HSML JSON Converter Assistant

This project uses the OpenAI Assistants API to convert arbitrary input JSON into valid HSML (Human Semantic Modeling Language) JSON objects. It supports schema-guided conversion using a vector store linked to a custom HSML schema document.

---

##  What It Does

- Classifies input JSON into one of the HSML entity types: `Agent`, `Activity`, `Credential`, `Domain`, etc.
- Searches a schema file using `file_search` to determine proper field names and class structure.
- Outputs a **single valid HSML JSON object** with required fields:
  - `@context`, `swid`, `name`, `description`, `type`, `linkedTo`, `properties`
- Any unmatched keys from the original input are mapped to `properties`.

---

## 📁 Project Structure
HSML_Conversion/
├── hsml_converter.py
├── HSML Schema Doc v1 2-3-25.txt
├── .env # You will create this
└── README.md


---

## ⚙ Requirements

- Python 3.8 or later
- Dependencies:
  - `openai`
  - `python-dotenv`

Install them with:

```bash
pip install openai python-dotenv


Setting Up Your API Key (.env File)
This project requires your OpenAI API key and (optionally) an Assistant ID to run.

Step 1: Create a .env File
In the root directory of the project, create a new file named .env.

Step 2: Add the Following to .env
env
Copy
Edit
OPENAI_API_KEY=your_openai_api_key_herea
ASSISTANT_ID = asst_rSTovgGbHqf9p2pCvH990pa5
Replace your_openai_api_key_here with your actual key from https://platform.openai.com/account/api-keys

If you're letting the script create the assistant for you, you can remove or comment out the ASSISTANT_ID line.




