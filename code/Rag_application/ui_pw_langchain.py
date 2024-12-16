import logging
import os
from langchain_community.vectorstores import PathwayVectorClient
import streamlit as st
from dotenv import load_dotenv
from create_database import create_database_with_file, create_database_user_input
from query_database import query_database_langchain_client

load_dotenv()

client = PathwayVectorClient(url= "http://127.0.0.1:8667")

st.set_page_config(page_title="Pathway RAG App", page_icon="pathway.ico")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)

logger = logging.getLogger("streamlit")
logger.setLevel(logging.INFO)

def main():
    st.title("Pathway RAG Application")
    
    # Option selection
    mode = st.radio(
        "Select Operation Mode", 
        ["Create Database", "Query Database"],
        index=1  # Default to Query Database
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
                print(query)
                response = query_database_langchain_client(query,client)
                
                if response:
                    st.markdown("**Query Response:**")
                    st.write(response)
                else:
                    st.warning("No results found or query failed.")

    with st.sidebar:
        st.subheader("Indexed Documents")
        try:
            document_meta_list = client.get_input_files()
            
            # Extract file paths (or file names) from the dictionaries in the document_meta_list
            # Assuming each item in document_meta_list is a dictionary with a 'path' key
            file_names = [os.path.basename(doc['path']) for doc in document_meta_list if 'path' in doc]
            
            # Construct markdown table to display in the sidebar
            markdown_table = "| Indexed Files |\n| --- |\n"
            for file_name in file_names:
                markdown_table += f"| {file_name} |\n"
            
            # Display the markdown table in the sidebar with custom CSS for padding
            st.markdown(
                f"""
                <style>
                .streamlit-expanderHeader {{
                    padding-right: 20px;
                }}
                .css-1v3fvcr {{
                    padding-right: 20px;
                }}
                </style>
                """, 
                unsafe_allow_html=True
            )
            
            # Display the markdown table in the sidebar
            st.markdown(markdown_table)
        except Exception as e:
            st.error(f"Could not fetch document list: {e}")


if __name__ == "__main__":
    main()