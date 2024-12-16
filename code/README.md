# Pathway Legal Navigator

**Pathway Legal Navigator** is a dynamic Retrieval-Augmented Generation (RAG) application designed for legal case analysis and querying. The platform integrates multiple functionalities using cutting-edge tools like LangChain, Pathway vector stores, and Microsoft-guided dynamic agent implementation.

---

## Features

1. **Two Modes of Operation:**
   - **AdaptiveRAG**: Implements RAG using a custom `app.yaml` configuration file.
   - **LangChain**: Leverages LangChain components for RAG using the Pathway vector store.

2. **Dynamic Vector Store Creation:**
   - Builds vector stores dynamically based on relevant legal case data stored in the `data` folder.

3. **Custom UI Integration:**
   - **AdaptiveRAG UI**: Managed via `ui_pw_adaptiveRag.py`.
   - **LangChain UI**: Managed via `ui_pw_langchain.py`.

4. **Agent Implementation:**
   - Dynamic agents for querying and analysis, inspired by Microsoft best practices, located in the `agents` folder.

5. **Support for Legal APIs:**
   - Fetches legal data using the **Indian Kanoon API**.

---

## File Structure

```plaintext
code/
├── data/                    # Dynamic vector store data
├── Rag_application/         # Core RAG application code
│   ├── ui_pw_adaptiveRag.py # AdaptiveRAG user interface
│   ├── ui_pw_langchain.py   # LangChain user interface
│   └── agents/              # Agents for dynamic RAG platform
├── DiskANN.ipynb            # DiskANN implementation with FAISS
├── main_pw_adaptiveRag.py   # Main AdaptiveRAG entry point
├── main_pw_langchain.py     # Main LangChain entry point
├── requirements.txt         # Project dependencies
└── .env.example             # Environment variables template
```
---

## Prerequisites

1. **Keys and Licenses:**
   - Obtain the **Indian Kanoon API Key**: [API Documentation](https://api.indiankanoon.org/)
   - Get your **OpenAI API Key**: [OpenAI](https://openai.com/api/)
   - Acquire a **Pathway License Key**: [Pathway](https://pathway.com/get-license)

2. **Set up Environment Variables:**
   - Create an `.env` file in the root directory:
     ```env
     OPENAI_API_KEY=your_openai_key
     PW_KEY=your_pathway_license_key
     INDIAN_KANOON_API=your_indian_kanoon_api_key
     TAVILY_API_KEY=tavily_key
     ```

---

# Installation and Setup Guide

## Install Pyenv

To manage Python versions and environments, first install `pyenv`:

```bash
curl https://pyenv.run | bash
```

## Set Up Python Environment

Once `pyenv` is installed, set up the Python environment:

```bash
pyenv install 3.10.12
pyenv virtualenv 3.10.12 myenv
pyenv activate myenv
```

## Install Dependencies
After setting up the Python environment, install the required dependencies:

```bash
pip install -r requirements.txt
```
## Running the Application
### AdaptiveRAG Mode
**Start the Pathway Vector Store**:
To start the Pathway vector store, run the following command:

```bash 
python main_pw_adaptiveRag.py
```
The Pathway vector store will be live at: **http://0.0.0.0:8000**

**Launch the AdaptiveRAG Streamlit UI**:
To launch the AdaptiveRAG Streamlit UI, use the following command:
```bash
streamlit run Rag_application/ui_pw_adaptiveRag.py
```

The application will be live at: **http://localhost:8501**

### Test Query
A test query is provided in the **test_query.txt** file to try out the Dynamic RAG system.
