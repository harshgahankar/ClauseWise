import os
import uuid
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# A very lightweight Tfidf-based retriever to replace heavy SentenceTransformers
class SimpleRetriever:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.clauses = []
        self.matrix = None

    def add_clauses(self, clauses):
        self.clauses = clauses
        if not clauses:
            return
        texts = [c.get('full_text', '') for c in clauses]
        self.matrix = self.vectorizer.fit_transform(texts)

    def search(self, query, top_k=3):
        if not self.clauses or self.matrix is None:
            return []
        
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.matrix).flatten()
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                results.append(self.clauses[idx])
        return results

# Global retriever instance
retriever = SimpleRetriever()

def store_all_clauses(clauses, **kwargs):
    """Stores clauses in the lightweight retriever. Accepts contract_id for compatibility."""
    print(f"* Storing {len(clauses)} clauses in memory...", flush=True)
    retriever.add_clauses(clauses)
    return True


def retrieve_similar(query, top_k=3):
    """Retrieves similar clauses using TF-IDF."""
    return retriever.search(query, top_k)

def get_store_stats():
    """Returns basic stats about the stored clauses."""
    return {"count": len(retriever.clauses)}

# Placeholder for backward compatibility
def embed(text):
    return [0.0] * 384