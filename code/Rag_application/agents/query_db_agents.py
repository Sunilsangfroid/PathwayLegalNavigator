from guidance import models
from guidance import capture, Tool
from guidance import guidance
from guidance import models, gen
from guidance import select
from guidance.models import OpenAI
from guidance.models._openai import OpenAI
from guidance.library._role import system , assistant , user
import os
from dotenv import load_dotenv
load_dotenv()

#HERE Replace with the OpenAI model name , additionally give key
lm = models.OpenAI("gpt-3.5-turbo", api_key=os.environ['OPENAI_API_KEY'])

# Extract the last assistant output
def sanitize(lm_content):
    lm_content = str(lm_content)
    segments = lm_content.split('<|im_end|>')
    # Find the last assistant segment
    for segment in reversed(segments):
        if "<|im_start|>assistant" in segment:
            # Extract and clean the output
            return segment.split("<|im_start|>assistant")[-1].strip()
    return None

# Guidance Functions
@guidance
def QueryEnhancing_guidance(lm, query):
    # This prompt is designed to enhance query specificity for better retrieval results in RAG
    with system():
        lm += (
            f"Your task is to improve the given query to make it more specific and relevant for searching through the available knowledge base. "
            "Rephrase the query by focusing on critical keywords, removing ambiguity, and ensuring it is concise. "
            "The goal is to generate a query that will retrieve the most relevant documents or information. End the query with '**'. "
            f"Input Query: {query} Refined Query:"
        )
    with assistant():
        lm += gen(stop='\n')
    return lm

@guidance
def hyde(lm, query, chunk_size):
  with system():
      lm += f'Given the question {query}, generate a hypothetical document that directly answers this question. The document should be detailed and in-depth. The document size has be exactly {chunk_size} characters. Answer:'
  with assistant():
      lm += gen(stop='\n')
  return lm

@guidance
def refine_into_sub_queries(lm, query):
    lm += f"""
    You are an AI assistant tasked with breaking down complex legal queries into simpler sub-queries for a RAG (Retrieval-Augmented Generation) system. Given the original query, decompose it into 2-4 simpler sub-queries that, when answered together, would provide a comprehensive response to the original legal query. Focus on ensuring the sub-queries address specific legal principles, case law, statutes, or procedural aspects related to the original query.

    Original query: {query}

    Example: What are the legal implications of breach of contract in international trade?

    Sub-queries:

    1) What are the general principles of breach of contract under international trade law?
    2) What remedies are available for breach of contract in international trade agreements?
    3) How do specific jurisdictions differ in handling breach of contract cases in international trade?
    4) What precedents or case law are relevant to breach of contract in international trade?
    """
    return lm

@guidance
def step_back(lm, query):
    lm += f' You are an AI assistant tasked with generating broader, more general queries to improve context retrieval in a RAG system. Given the original query, generate a step-back query that is more general and can help retrieve relevant background information. Original query: {query} Step-back query:'
    return lm

@guidance
def LLMGaurdAgent(lm, query, context):
    with system():
        lm += f"""
        You are an AI auditor responsible for annotating and validating the accuracy of a given answer.
        The query is "{query}". The context is "{context}". Your goal is to evaluate the context by considering the following steps:
        For each note:
        Check whether it is supported by the context.
        Identify any assumptions, extrapolations, or contradictions.
        Conclude with one of these categories:
        Fully Accurate: The answer is completely supported by the context.
        Partially Accurate: Some parts are supported, while others rely on external assumptions or knowledge.
        Hallucinated: The answer is unsupported or contradicts the context. Answer:
        """
    with assistant():
        lm += gen(stop='\n')
    return lm

# Query Database Agents

def initialize_model():
    lm = models.OpenAI("gpt-3.5-turbo", api_key=os.environ['OPENAI_API_KEY'])
    return lm

# Query Refinement Agent
def QueryEnhancingAgent(user_query):
    lm = initialize_model()
    lm += QueryEnhancing_guidance(user_query)
    return sanitize(lm)

# LLM Guard Agent
def LLMGuardAgent(query, context):
    lm = initialize_model()
    lm += LLMGaurdAgent(query, context)
    return sanitize(lm)