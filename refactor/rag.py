import os
import chromadb
from chromadb.config import Settings

# Initialize ChromaDB
chroma_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb",
    persist_directory=os.getenv('CHROMA_PERSIST_DIR', './chroma_data'),
    anonymized_telemetry=False
))

def get_collection():
    """Get or create the documents collection"""
    try:
        return chroma_client.get_collection("documents")
    except:
        return chroma_client.create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

def add_to_rag(document_id: str, version_id: str, title: str, content: str):
    """Add document version to RAG"""
    collection = get_collection()
    
    embedding_id = f"{document_id}_{version_id}"
    
    collection.upsert(
        ids=[embedding_id],
        documents=[content],
        metadatas=[{
            "document_id": document_id,
            "version_id": version_id,
            "title": title
        }]
    )
    
    return embedding_id

def search_rag(query: str, accessible_docs: list[str], top_k: int = 5):
    """Search documents with permission filtering"""
    collection = get_collection()
    
    # Query with document ID filter
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where={"document_id": {"$in": accessible_docs}} if accessible_docs else None
    )
    
    # Format results
    formatted = []
    if results['ids'] and len(results['ids']) > 0:
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i] if results['distances'] else 0
            
            formatted.append({
                "document_id": metadata['document_id'],
                "version_id": metadata['version_id'],
                "title": metadata['title'],
                "content": results['documents'][0][i][:500],  # Preview
                "relevance": 1 - distance  # Convert distance to similarity
            })
    
    return formatted

def delete_from_rag(document_id: str, version_id: str = None):
    """Remove document or version from RAG"""
    collection = get_collection()
    
    if version_id:
        # Delete specific version
        collection.delete(ids=[f"{document_id}_{version_id}"])
    else:
        # Delete all versions of document
        results = collection.get(where={"document_id": document_id})
        if results['ids']:
            collection.delete(ids=results['ids'])