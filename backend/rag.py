# filepath: /Users/nicholasfairhart/Documents/GitHub/ICS-601-Final-Project/backend/rag.py
import chromadb
from chromadb.config import Settings
import os
from typing import Optional
from pydantic import BaseModel
import uuid

# Initialize ChromaDB
chroma_settings = Settings(
    chroma_db_impl="duckdb",
    persist_directory=os.getenv('CHROMA_PERSIST_DIR', './chroma_data'),
    anonymized_telemetry=False
)

chroma_client = chromadb.Client(chroma_settings)

class SearchResult(BaseModel):
    """Search result from RAG"""
    document_id: str
    title: str
    content: str
    version_id: str
    relevance_score: float
    page_number: Optional[int] = None

class RAGQuery(BaseModel):
    """Query for RAG search"""
    query: str
    top_k: int = 5
    min_relevance: float = 0.3

def get_or_create_collection(collection_name: str = "documents"):
    """Get or create ChromaDB collection"""
    try:
        return chroma_client.get_collection(name=collection_name)
    except:
        return chroma_client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

def add_document_to_rag(
    document_id: str,
    version_id: str,
    title: str,
    content: str,
    metadata: dict = None
):
    """Add or update document in RAG database"""
    collection = get_or_create_collection()
    
    # Create unique ID combining document and version
    embedding_id = f"{document_id}_{version_id}"
    
    # Prepare metadata
    doc_metadata = {
        "document_id": document_id,
        "version_id": version_id,
        "title": title,
        **(metadata or {})
    }
    
    # Add to ChromaDB
    collection.upsert(
        ids=[embedding_id],
        documents=[content],
        metadatas=[doc_metadata]
    )
    
    return embedding_id

def search_rag(
    query: str,
    user_accessible_docs: list[str],
    top_k: int = 5,
    min_relevance: float = 0.3
) -> list[SearchResult]:
    """Search RAG with permission filtering"""
    collection = get_or_create_collection()
    
    # Query ChromaDB
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where={
            "document_id": {"$in": user_accessible_docs}
        } if user_accessible_docs else None
    )
    
    # Format results
    search_results = []
    
    if results['ids'] and len(results['ids']) > 0:
        for i, embedding_id in enumerate(results['ids'][0]):
            distance = results['distances'][0][i] if results['distances'] else 0
            # Convert distance to similarity (1 - distance for cosine)
            relevance_score = 1 - distance
            
            if relevance_score >= min_relevance:
                metadata = results['metadatas'][0][i]
                search_results.append(SearchResult(
                    document_id=metadata.get('document_id', ''),
                    title=metadata.get('title', 'Unknown'),
                    content=results['documents'][0][i],
                    version_id=metadata.get('version_id', ''),
                    relevance_score=relevance_score,
                    page_number=metadata.get('page_number')
                ))
    
    return search_results

def delete_document_from_rag(document_id: str, version_id: str = None):
    """Remove document from RAG"""
    collection = get_or_create_collection()
    
    if version_id:
        # Delete specific version
        embedding_id = f"{document_id}_{version_id}"
        collection.delete(ids=[embedding_id])
    else:
        # Delete all versions of document
        results = collection.get(
            where={"document_id": document_id}
        )
        if results['ids']:
            collection.delete(ids=results['ids'])