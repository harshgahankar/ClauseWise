import chromadb
import requests
import os
import uuid

EMBED_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
EMBED_HEADERS = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection    = chroma_client.get_or_create_collection(
    name="clauses",
    metadata={"heuristic": "cosine"}
)

def embed(text):
    response = requests.post(EMBED_API_URL, headers=EMBED_HEADERS, json={"inputs": text}, timeout=30)
    return response.json()

def store_clause(clause_text, clause_type, risk_level, plain_english, contract_id=None):
    collection.add(
        ids        = [str(uuid.uuid4())],
        embeddings = [embed(clause_text)],
        documents  = [clause_text],
        metadatas  = [{
            'type':          clause_type,
            'risk_level':    risk_level,
            'plain_english': plain_english,
            'contract_id':   contract_id or 'unknown',
        }]
    )

def retrieve_similar(clause_text, n=3):
    count = collection.count()
    if count == 0:
        return []
    results = collection.query(
        query_embeddings = [embed(clause_text)],
        n_results        = min(n, count),
        include          = ['documents', 'metadatas', 'distances']
    )
    similar = []
    for i in range(len(results['documents'][0])):
        similar.append({
            'text':          results['documents'][0][i],
            'type':          results['metadatas'][0][i]['type'],
            'risk_level':    results['metadatas'][0][i]['risk_level'],
            'plain_english': results['metadatas'][0][i]['plain_english'],
            'similarity':    round(1 - results['distances'][0][i], 3),
        })
    return similar

def store_all_clauses(clauses, contract_id=None):
    for clause in clauses:
        store_clause(
            clause_text   = clause.get('full_text', ''),
            clause_type   = clause.get('type', 'general'),
            risk_level    = clause.get('risk_level', 'low'),
            plain_english = clause.get('plain_english', ''),
            contract_id   = contract_id,
        )
    print(f"* Stored {len(clauses)} clauses (total in DB: {collection.count()})")

def get_store_stats():
    return {'total_clauses_stored': collection.count()}
