import os
import streamlit as st
import logging
from agents.KanoonIQAgent import KanoonIQAgent
from agents.create_db_agents import LexicographerAgent, CaseSummarizerAgent
from agents.webAgent import WebAgentTavily

logger = logging.getLogger("streamlit")
logger.setLevel(logging.INFO)

# Add at the beginning of the script
DATA_DIR = "./data"  # Directory to store uploaded files
# os.makedirs(DATA_DIR, exist_ok=True)  # Ensure the data directory exists

def create_database_with_file(uploaded_file):
    """
    Function to create a database using an uploaded document.
    
    Args:
        uploaded_file (UploadedFile): The uploaded file object from Streamlit.
    
    Returns:
        bool: True if database creation successful, False otherwise.
    """
    try:
        if uploaded_file is None:
            st.error("No file uploaded!")
            return False
        
        # Save the uploaded file to the data directory
        file_path = os.path.join(DATA_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # # Optional: Process the uploaded document for database
        # KanoonIQAgent(file_path)

        st.success(f"Database created successfully with file: {uploaded_file.name}")
        # st.balloons()
        return True
    
    except Exception as e:
        st.error(f"Failed to process uploaded document: {e}")
        logger.error(f"Error processing uploaded file: {e}")
        return False

def create_database_user_input(document_input, document_type):
    """
    Function to create database with user-provided input
    
    Args:
        document_input (str): User-provided document content
        document_type (str): Type of document being input
    
    Returns:
        bool: True if database creation successful, False otherwise
    """
    try:
        # Validate input
        if not document_input.strip():
            st.error("Document content cannot be empty!")
            return False
        
        document_data = {
            "content": document_input,
            "type": document_type,
            "source": "user_input"
        }
        
        case_cat = LexicographerAgent(document_data['content'])
        CaseSummarizerAgent(document_data['content'])

        # Process the user input for database
        KanoonIQAgent(case_cat)

        if not os.listdir(DATA_DIR):  # Directory is empty
            WebAgentTavily(document_data['content'])

        # User feedback
        st.success("Database Created Successfully!")
        # st.balloons()
        return True
    
    except Exception as e:
        st.error(f"Database Creation Failed: {e}")
        logger.error(f"Database creation error: {e}")
        return False
