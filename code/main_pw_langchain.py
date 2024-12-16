import pathway as pw
from pyngrok import ngrok
from pathway.xpacks.llm.vector_store import VectorStoreServer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings

pw.set_license_key("59BCD9-BF9E27-DA7F35-907D85-8ACA45-V3")
data = pw.io.fs.read(
    "./data",
    format="binary",
    mode="streaming",
    with_metadata=True,
)

embeddings = SentenceTransformerEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"trust_remote_code":True}) 

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

host = "127.0.0.1"
port = 8667

server = VectorStoreServer.from_langchain_components(
    data, embedder=embeddings, splitter=splitter, parser = pw.xpacks.llm.parsers.ParseUnstructured()
)
server.run_server(host, port=port, with_cache=True, cache_backend=pw.persistence.Backend.filesystem("./Cache"))