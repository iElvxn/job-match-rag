import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

load_dotenv()

model = SentenceTransformer("all-mpnet-base-v2")
BATCH_SIZE_EMBED = 200
BATCH_SIZE_UPSERT = 100

def get_index():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    return pc.Index(os.getenv("PINECONE_INDEX_NAME"))


def embed_chunks(texts: list[str]) -> list[list[float]]:
    return model.encode(texts, show_progress_bar=False).tolist()

def upsert_chunks(chunks: list[dict], index) -> None:
    texts = [chunk["text"] for chunk in chunks]
    vectors = embed_chunks(texts)
    
    records = []
    for i, chunk in enumerate(chunks):
        records.append({
            "id": chunk["chunk_id"],
            "values": vectors[i],
            "metadata": {**chunk["metadata"], "text": chunk["text"]},
        })
        
    for i in range(0, len(records), BATCH_SIZE_UPSERT):
        batch = records[i : i + BATCH_SIZE_UPSERT]
        index.upsert(vectors=batch)
