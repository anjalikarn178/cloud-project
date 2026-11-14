import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import MINILM_MODEL, DATA_DIR
import os
import json

class VectorChecker:
    def __init__(self):
        self.embedder = SentenceTransformer(MINILM_MODEL)
        self.index = None
        self.signatures = []
        self._load_index()

    def _load_index(self):
        sig_path = os.path.join(DATA_DIR, "attack_signatures.json")
        if os.path.exists(sig_path):
            with open(sig_path, 'r') as f:
                self.signatures = json.load(f)
            embeddings = self.embedder.encode(self.signatures)
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
            self.index.add(np.array(embeddings).astype('float32'))

    def check(self, text: str):
        if self.index is None or self.index.ntotal == 0:
            return False, 0.0
        emb = self.embedder.encode([text]).astype('float32')
        distances, _ = self.index.search(emb, 1)
        return distances[0][0] < 0.85, float(distances[0][0])

vector_checker = None
def load_vector_db():
    global vector_checker
    vector_checker = VectorChecker()