from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
import os
import streamlit as st

def setup_llm_rag():
    """
    Sets up the LLM and RAG system with the Llama 3 model for both embedding and generation.
    Increases the timeout for Ollama requests.
    """
    st.info("Setting up LLM and RAG system with LlamaIndex...")
    
    # Set the OLLAMA_BASE_URL environment variable to ensure LlamaIndex can connect
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

    # Define LLM and embedding model, increasing the request_timeout
    llm = Ollama(model="llama3", request_timeout=300.0)
    embed_model = OllamaEmbedding(model_name="llama3", request_timeout=300.0)
    
    # Create a knowledge base document from threat intelligence
    docs_dir = "docs"
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
    with open(os.path.join(docs_dir, "threat_intel.txt"), "w") as f:
        f.write("A brute-force attack involves repeated, systematic attempts to guess a password. This technique is often automated and can be detected by monitoring for multiple failed login attempts from a single source IP.\n")
        f.write("Advanced Persistent Threat (APT) group APT29 is known to use brute-force attacks to gain initial access to target networks. Their tactics, techniques, and procedures (TTPs) often evolve to evade detection.\n")

    # Load documents and create vector index
    documents = SimpleDirectoryReader(docs_dir).load_data()
    index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
    query_engine = index.as_query_engine(llm=llm)
    
    return query_engine

def analyze_threat(query_engine, alert_details):
    """
    Uses the RAG system to analyze a threat alert.
    """
    st.info(f"Analyzing threat alert: {alert_details}")
    
    # Generate query for the RAG system
    query = f"Provide a detailed analysis of the following security incident, including potential adversaries and countermeasures: {alert_details}"
    
    response = query_engine.query(query)
    
    st.markdown("### LLM-Augmented Threat Analysis")
    st.write(response)

