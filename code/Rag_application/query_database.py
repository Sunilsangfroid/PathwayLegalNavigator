from pathway.xpacks.llm.question_answering import RAGClient
import streamlit as st
import requests
import logging
from agents.query_db_agents import QueryEnhancingAgent

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_openai import ChatOpenAI
from agents.query_db_agents import LLMGuardAgent
import os

logger = logging.getLogger("streamlit")
logger.setLevel(logging.INFO)

PATHWAY_HOST = "0.0.0.0"
PATHWAY_PORT = 8000

def get_case_summary():
    with open("case_summary.txt", "r") as f:
        return f.read()

def create_payload(query):
    summary = get_case_summary()

    # Check if the summary is relevant?
    is_summary_present = len(summary) > 15

    # Create the base prompt
    prompt = f"""
    You are a legal expert. A user has provided a query related to legal cases. Your task is to not just state references or documents, but to offer a detailed and insightful response. When answering, make sure to:

    1. Thoroughly analyze the query and provide context where necessary.
    2. Break down any complex legal aspects of the case in clear and concise language.
    3. Offer explanations or reasoning for how the laws or relevant sections apply to the case.
    4. Avoid simply listing legal provisions or documents; instead, integrate them into the explanation to make the response comprehensive and user-friendly.
    """

    # Include the summary in the prompt if it has actual content
    if is_summary_present:
        prompt += f"""
        Before proceeding, consider the following case summary, which may provide additional context to the query:
        {summary}

        Use this summary only if it is directly relevant to understanding or answering the user's query. If it is not relevant, focus entirely on the user's input without relying on the summary.
        """

    # Add the user's query to the prompt
    prompt += f"""
    User Query: {query}
    """

    # Return the final payload
    payload = {
        "prompt": prompt
    }
    return payload


def query_database(query):
    """
    Function to query the existing database using RAG client.
    """
    try:
        # Initialize RAG Client
        conn = RAGClient(url=f"http://{PATHWAY_HOST}:{PATHWAY_PORT}")

        # Prepare API URL for AI assistant
        api_url = f"http://{PATHWAY_HOST}:{PATHWAY_PORT}/v1/pw_ai_answer"

        # Refine the query
        query = QueryEnhancingAgent(query)
        print(query)

        # payload = {
        #     "prompt": f"""
        #     You are a legal expert. A user has provided a query related to legal cases. Your task is to not just state references or documents, but to offer a detailed and insightful response. When answering, make sure to:

        #     1. Thoroughly analyze the query and provide context where necessary.
        #     2. Break down any complex legal aspects of the case in clear and concise language.
        #     3. Offer explanations or reasoning for how the laws or relevant sections apply to the case.
        #     4. Avoid simply listing legal provisions or documents; instead, integrate them into the explanation to make the response comprehensive and user-friendly.

        #     User Query: {query}
        #     """
        # }

        payload = create_payload(query)
        # Send request to retrieve relevant documents
        response = requests.post(api_url, json=payload, timeout=20)
        response.raise_for_status()

        # is_hallu = LLMGuardAgent(response.json())

        # if "hallucinated" in is_hallu:
        #     return query_database(query)
        
        # Return the response
        return response.json()
    
    except requests.exceptions.RequestException as e:
        st.error(f"Query Failed: {e}")
        logger.error(f"Database query error: {e}")
        return None

def query_database_langchain_client(query,client):
    """
    Function to query the existing database using RAG client.
    """
    query = QueryEnhancingAgent(query)

    retriever = client.as_retriever()
    case = get_case_summary()
    print(case)
    
    llm = ChatOpenAI(model="gpt-3.5-turbo",api_key=os.environ['OPENAI_API_KEY'])
    system_prompt = (
        "You are an assistant for question-answering legal tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    try:
        # response = client.similarity_search_with_relevance_scores(query)
        response = rag_chain.invoke({"input": query})
        return response
    
    except requests.exceptions.RequestException as e:
        st.error(f"Query Failed: {e}")
        logger.error(f"Database query error: {e}")
        return None