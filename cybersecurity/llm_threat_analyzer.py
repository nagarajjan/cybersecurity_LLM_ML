from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding  # Corrected class name
import os

def setup_llm_rag():
    """
    Sets up the LLM and RAG system with the Llama 3 model for both embedding and generation.
    """
    print("Setting up LLM and RAG system with LlamaIndex...")
    
    # Set the OLLAMA_BASE_URL environment variable to ensure LlamaIndex can connect
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

    # Define LLM and embedding model, increasing the request_timeout
    llm = Ollama(model="llama3", request_timeout=300.0)
    embed_model = OllamaEmbedding(model_name="llama3", request_timeout=300.0)
    
    # Specify the Llama 3 model to use for embedding
    embed_model = OllamaEmbedding(model_name="llama3") 
    
    # Create a knowledge base document from threat intelligence
    if not os.path.exists("docs"):
        os.makedirs("docs")
    with open("docs/threat_intel.txt", "w") as f:
        f.write("A brute-force attack involves repeated, systematic attempts to guess a password. This technique is often automated and can be detected by monitoring for multiple failed login attempts from a single source IP.\n")
        f.write("Advanced Persistent Threat (APT) group APT29 is known to use brute-force attacks to gain initial access to target networks. Their tactics, techniques, and procedures (TTPs) often evolve to evade detection.\n")

    # Load documents and create vector index
    documents = SimpleDirectoryReader("docs").load_data()
    index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
    query_engine = index.as_query_engine(llm=llm)
    
    return query_engine

def analyze_threat(query_engine, alert_details):
    """
    Uses the RAG system to analyze a threat alert.
    """
    print(f"\nAnalyzing threat alert: {alert_details}")
    
    # Generate query for the RAG system
    query = f"Provide a detailed analysis of the following security incident, including potential adversaries and countermeasures: {alert_details}"
    
    response = query_engine.query(query)
    
    print("\n--- LLM-Augmented Threat Analysis ---")
    print(response)
    
if __name__ == "__main__":
    # Simulate an alert from the ML model
    # (assuming the ML model flagged 'brute_force' threat from 10.0.0.5)
    alert_from_ml = "Threat type: brute_force, Source IP: 10.0.0.5, Target: admin account."

    try:
        rag_engine = setup_llm_rag()
        analyze_threat(rag_engine, alert_from_ml)
    except Exception as e:
        print(f"Error: {e}. Ensure Ollama is running and Llama 3 model is installed.")
        print("Please run `ollama run llama3` in your terminal.")

