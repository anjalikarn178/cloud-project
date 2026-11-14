import chromadb
from chromadb.utils import embedding_functions
from app.config import DOCS_DIR, MINILM_MODEL
import os

def ingest_documents():
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MINILM_MODEL)
    client = chromadb.PersistentClient(path="data/chroma_db")
    collection = client.get_or_create_collection(name="cloud_docs", embedding_function=ef)

    docs = []
    ids = []
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".txt"):
            with open(os.path.join(DOCS_DIR, filename), 'r') as f:
                content = f.read()
                chunks = [content[i:i+500] for i in range(0, len(content), 400)]
                for i, chunk in enumerate(chunks):
                    docs.append(chunk)
                    ids.append(f"{filename}_{i}")
    
    if docs:
        collection.add(documents=docs, ids=ids)
    print(f"Ingested {len(docs)} chunks into ChromaDB.")

if __name__ == "__main__":
    ingest_documents()