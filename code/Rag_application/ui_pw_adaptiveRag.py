import logging
import os
import streamlit as st
from dotenv import load_dotenv
from pathway.xpacks.llm.question_answering import RAGClient
from create_database import create_database_with_file, create_database_user_input
from query_database import query_database

load_dotenv()

PATHWAY_HOST = "0.0.0.0"
PATHWAY_PORT = 8000

def delete_files_in_directory(directory):
    try:
        # Iterate over all files and directories in the given directory
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            # Check if it's a file before attempting to delete it
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            elif os.path.isdir(file_path):
                print(f"Skipped directory: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


st.set_page_config(page_title="Pathway Dynamic Legal RAG App", page_icon="pathway.ico", layout="wide")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)

logger = logging.getLogger("streamlit")
logger.setLevel(logging.INFO)


def display_relevant_content():
    # Display content from constitution_sections.txt and ipc_sections.txt if they exist
    files = ["constitution_sections.txt", "ipc_sections.txt"]
    for file in files:
        if os.path.exists(file):
            st.subheader(f"Relevant content from {file[:-4]}:")
            with open(file, "r") as f:
                content = f.read()
                st.text(content)


def main():
    # Add three buttons in the header
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])  # Adjust widths for alignment

    with col2:
        if st.button("Dynamic RAG Application", key="dynamic_rag"):
            st.session_state["active_page"] = "dynamic_rag_application"
    # with col3:
    #     if st.button("Legal Form Builder", key="legal_form"):
    #         st.session_state["active_page"] = "legal_form_builder"


    with col4:
        # Add hyperlink-style button
        st.markdown(
            """
            <a href="https://pathway.com/" class="hyperlink-button" target="_blank">Visit Pathway</a>
            """,
            unsafe_allow_html=True,
        )

    # Page logic based on active page
    active_page = st.session_state.get("active_page", "dynamic_rag_application")

    if active_page == "legal_form_builder":
        st.title("Legal Form Builder")
        st.write("Design custom legal forms here!")
        # Add your form-building functionality here
        return

    elif active_page == "dynamic_rag_application":
        st.title("Pathway Legal Navigator")
        
        # Option selection
        mode = st.radio(
            "Select Operation Mode", 
            ["Create Database", "Query Database"],
            index=0  # Default to Query Database
        )
        
        if mode == "Create Database":
            st.subheader("Database Creation")

            # Option to either input text or upload a document
            input_method = st.radio(
                "Choose Input Method",
                ["Type/Paste Document Content", "Upload a File"]
            )

            if input_method == "Type/Paste Document Content":
                document_types = ["Text Document", "FAQ", "Technical Manual", "User Guide", "Other"]
                document_type = st.selectbox("Select Document Type", document_types)

                if document_type == "Other":
                    document_type = st.text_input("Enter your custom document type", placeholder="e.g., Research Paper")

                document_input = st.text_area(
                    "Enter Document Content",
                    placeholder="Paste or type your document here...",
                    height=300
                )

                if st.button("Create Database"):
                    with st.spinner("Creating Database..."):
                        result = create_database_user_input(document_input, document_type)
                        if result:
                            display_relevant_content()  # Display the relevant content if database is created
                            st.session_state.clear()

            elif input_method == "Upload a File":
                uploaded_file = st.file_uploader("Upload your document", type=["txt", "pdf", "docx"])

                if st.button("Upload and Create Database"):
                    with st.spinner("Processing uploaded document..."):
                        result = create_database_with_file(uploaded_file)
                        if result:
                            st.session_state.clear()

        else:  # Query Database
            st.subheader("Database Query")
            query = st.text_input("Enter your query:", placeholder="What would you like to know?")
            
            if st.button("Submit Query") and query:
                with st.spinner("Searching database..."):
                    response = query_database(query)
                    
                    if response:
                        st.markdown("**Query Response:**")
                        st.write(response)
                    else:
                        st.warning("No results found or query failed.")

    # Sidebar for indexed documents
    with st.sidebar:
        st.subheader("Indexed Documents")
        try:
            conn = RAGClient(url=f"http://{PATHWAY_HOST}:{PATHWAY_PORT}")
            document_meta_list = conn.pw_list_documents(keys=[])
            file_names = [os.path.basename(doc['path']) for doc in document_meta_list if 'path' in doc]
            markdown_table = "| Indexed Files |\n| --- |\n"
            for file_name in file_names:
                markdown_table += f"| {file_name} |\n"
            st.markdown(markdown_table)
        except Exception as e:
            # delete_files_in_directory("./data")
            st.error(f"Could not fetch document list: Check your internet connection")

if __name__ == "__main__":
    main()
