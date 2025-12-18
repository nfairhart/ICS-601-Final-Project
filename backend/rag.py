import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from typing import Optional
import re

# Load environment variables from .env file
load_dotenv()

# Initialize ChromaDB client
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

def chunk_by_markdown_sections(text: str, max_chars: int = 2000) -> list[dict]:
    """
    Split markdown text by paragraphs into semantic chunks.
    Preserves markdown headings as context when they precede paragraphs.
    Uses character count as rough approximation (typically ~4 chars per token).

    Args:
        text: Markdown text to chunk
        max_chars: Maximum characters per chunk (default 2000 ≈ 500 tokens)

    Returns:
        List of dicts with 'text' and 'section_title'
    """
    chunks = []

    # Split text into paragraphs (separated by double newlines)
    paragraphs = text.split('\n\n')

    current_chunk = ""
    current_heading = None

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Check if this paragraph is a heading
        heading_match = re.match(r'^(#{1,6}\s+.+)$', para, re.MULTILINE)

        if heading_match:
            # Save previous chunk if it exists
            if current_chunk.strip():
                chunks.append({
                    'text': current_chunk.strip(),
                    'section_title': current_heading
                })
                current_chunk = ""

            # Update current heading
            current_heading = para
            # Include heading in the next chunk
            current_chunk = para + "\n\n"
        else:
            # Regular paragraph
            potential_chunk = current_chunk + para + "\n\n"

            # Check if adding this paragraph would exceed max_chars
            if len(potential_chunk) > max_chars and current_chunk.strip():
                # Save current chunk and start new one
                chunks.append({
                    'text': current_chunk.strip(),
                    'section_title': current_heading
                })
                # Start new chunk with heading (if exists) and current paragraph
                if current_heading:
                    current_chunk = current_heading + "\n\n" + para + "\n\n"
                else:
                    current_chunk = para + "\n\n"
            else:
                # Add paragraph to current chunk
                current_chunk = potential_chunk

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append({
            'text': current_chunk.strip(),
            'section_title': current_heading
        })

    return chunks


def add_to_rag(document_id: str, version_id: str, title: str, content: str):
    """
    Add document version to RAG, splitting into chunks if needed.
    Each chunk is stored as a separate embedding with a chunk index.
    """
    collection = get_collection()

    # Split content into chunks by markdown sections
    chunks = chunk_by_markdown_sections(content)

    # Prepare batch data
    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        chunk_id = f"{document_id}_{version_id}_chunk{i}"
        ids.append(chunk_id)
        documents.append(chunk['text'])
        metadatas.append({
            "document_id": document_id,
            "version_id": version_id,
            "title": title,
            "chunk_index": i,
            "section_title": chunk.get('section_title', '')
        })

    # Upsert all chunks at once
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    return f"{document_id}_{version_id} ({len(chunks)} chunks)"

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
                "score": relevance  # Changed from relevance_score to score to match API spec
            })
    
    return formatted

def get_document_content(document_id: str, version_id: Optional[str] = None) -> Optional[dict]:
    """
    Retrieve full content of a specific document version from RAG.
    Reconstructs content from all chunks in order.

    Args:
        document_id: The document ID
        version_id: Optional specific version ID. If None, gets latest.

    Returns:
        Dictionary with content and metadata, or None if not found
    """
    collection = get_collection()

    if version_id:
        # Get all chunks for this version
        results = collection.get(where={
            "$and": [
                {"document_id": document_id},
                {"version_id": version_id}
            ]
        })
    else:
        # Get all chunks of this document
        results = collection.get(where={"document_id": document_id})

    if results['ids'] and len(results['ids']) > 0:
        # Sort chunks by chunk_index to reconstruct in correct order
        chunks_data = list(zip(
            results['metadatas'],
            results['documents']
        ))

        # Sort by chunk_index if available
        chunks_data.sort(key=lambda x: x[0].get('chunk_index', 0))

        # Reconstruct full content
        full_content = '\n\n'.join([doc for _, doc in chunks_data])

        return {
            "document_id": chunks_data[0][0]['document_id'],
            "version_id": chunks_data[0][0]['version_id'],
            "title": chunks_data[0][0]['title'],
            "content": full_content
        }

    return None

def delete_from_rag(document_id: str, version_id: Optional[str] = None):
    """Remove document or version from RAG (including all chunks)"""
    collection = get_collection()

    if version_id:
        # Delete all chunks of specific version
        # ChromaDB requires $and for multiple conditions
        results = collection.get(where={
            "$and": [
                {"document_id": document_id},
                {"version_id": version_id}
            ]
        })
        if results['ids']:
            collection.delete(ids=results['ids'])
    else:
        # Delete all versions and chunks of document
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