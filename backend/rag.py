import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# ✅ NEW API: Use PersistentClient instead of Client(Settings(...))
chroma_client = chromadb.PersistentClient(
    path=os.getenv('CHROMA_PERSIST_DIR', './chroma_data')
)

# Add embedding function (required for new API)
embedding_fn = OpenAIEmbeddingFunction(
    api_key=os.getenv('OPENAI_API_KEY'),
    model_name="text-embedding-3-small"
)

def get_collection():
    """Get or create the documents collection"""
    return chroma_client.get_or_create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine"},
        embedding_function=embedding_fn
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

def search_rag(
    query: str, 
    user_accessible_docs: list[str], 
    top_k: int = 5, 
    min_relevance: Optional[float] = None
):
    """
    Search documents with permission filtering.
    
    Args:
        query: Search query text
        user_accessible_docs: List of document IDs the user can access
        top_k: Maximum number of results to return
        min_relevance: Minimum relevance score (0-1). Results below this are filtered out.
    
    Returns:
        List of search results with relevance_score field
    """
    collection = get_collection()
    
    # Query with document ID filter
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where={"document_id": {"$in": user_accessible_docs}} if user_accessible_docs else None
    )
    
    # Format results
    formatted = []
    if results['ids'] and len(results['ids']) > 0:
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i] if results['distances'] else 0
            relevance = 1 - distance  # Convert distance to similarity
            
            # Filter by minimum relevance if specified
            if min_relevance is not None and relevance < min_relevance:
                continue
            
            formatted.append({
                "document_id": metadata['document_id'],
                "version_id": metadata['version_id'],
                "title": metadata['title'],
                "content": results['documents'][0][i],
                "relevance_score": relevance  # ✅ Fixed field name
            })
    
    return formatted

def get_document_content(document_id: str, version_id: Optional[str] = None) -> Optional[dict]:
    """
    Retrieve full content of a specific document version from RAG.
    
    Args:
        document_id: The document ID
        version_id: Optional specific version ID. If None, gets latest.
    
    Returns:
        Dictionary with content and metadata, or None if not found
    """
    collection = get_collection()
    
    if version_id:
        embedding_id = f"{document_id}_{version_id}"
        results = collection.get(ids=[embedding_id])
    else:
        # Get all versions of this document
        results = collection.get(where={"document_id": document_id})
    
    if results['ids'] and len(results['ids']) > 0:
        # Return the first (or only) result
        return {
            "document_id": results['metadatas'][0]['document_id'],
            "version_id": results['metadatas'][0]['version_id'],
            "title": results['metadatas'][0]['title'],
            "content": results['documents'][0]
        }
    
    return None

def delete_from_rag(document_id: str, version_id: Optional[str] = None):
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

def get_similar_documents(document_id: str, top_k: int = 5, accessible_docs: Optional[list[str]] = None) -> list[dict]:
    """
    Find documents similar to the given document.
    
    Args:
        document_id: The reference document ID
        top_k: Number of similar documents to return
        accessible_docs: Optional list of document IDs to filter by
    
    Returns:
        List of similar documents with relevance scores
    """
    collection = get_collection()
    
    # Get the reference document content
    ref_doc = get_document_content(document_id)
    if not ref_doc:
        return []
    
    # Search using the reference document's content
    where_clause = None
    if accessible_docs:
        where_clause = {"document_id": {"$in": accessible_docs}}
    
    results = collection.query(
        query_texts=[ref_doc['content']],
        n_results=top_k + 1,  # +1 because the reference doc might be included
        where=where_clause
    )
    
    # Format and filter out the reference document itself
    formatted = []
    if results['ids'] and len(results['ids']) > 0:
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            
            # Skip the reference document itself
            if metadata['document_id'] == document_id:
                continue
            
            distance = results['distances'][0][i] if results['distances'] else 0
            relevance = 1 - distance
            
            formatted.append({
                "document_id": metadata['document_id'],
                "version_id": metadata['version_id'],
                "title": metadata['title'],
                "content": results['documents'][0][i][:500],  # Preview
                "relevance_score": relevance
            })
    
    return formatted[:top_k]  # Return exactly top_k results