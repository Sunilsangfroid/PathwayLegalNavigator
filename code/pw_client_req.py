from langchain_community.vectorstores import PathwayVectorClient
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_openai import ChatOpenAI
import os

client = PathwayVectorClient(url= "http://127.0.0.1:8667")
query = ""
retriever = client.as_retriever()

print(retriever.invoke({"query": query}))
print()
print(client.similarity_search_with_relevance_scores(query))

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