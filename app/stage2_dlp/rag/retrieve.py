import chromadb
from chromadb.utils import embedding_functions
from app.config import MINILM_MODEL

def retrieve_context(query: str, n_results=2):
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MINILM_MODEL)
    client = chromadb.PersistentClient(path="data/chroma_db")
    collection = client.get_collection(name="cloud_docs", embedding_function=ef)
    
    results = collection.query(query_texts=[query], n_results=n_results)
    return results['documents'][0] if results['documents'] else []