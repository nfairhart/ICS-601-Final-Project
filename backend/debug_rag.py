"""Debug utility to inspect and rebuild RAG database"""
import sys
from backend.database import get_db
from backend.models import Document, DocumentVersion
from backend.rag import get_collection, add_to_rag, delete_from_rag

def inspect_rag():
    """Show what's currently in the RAG database"""
    collection = get_collection()

    # Get all documents in RAG
    results = collection.get()

    print(f"\n=== RAG Database Contents ===")
    print(f"Total embeddings: {len(results['ids'])}")

    if results['ids']:
        print("\nDocuments:")
        for i, (id, metadata, doc) in enumerate(zip(results['ids'], results['metadatas'], results['documents'])):
            print(f"\n{i+1}. ID: {id}")
            print(f"   Title: {metadata.get('title', 'N/A')}")
            print(f"   Document ID: {metadata.get('document_id', 'N/A')}")
            print(f"   Version ID: {metadata.get('version_id', 'N/A')}")
            print(f"   Chunk Index: {metadata.get('chunk_index', 'N/A')}")
            print(f"   Section: {metadata.get('section_title', 'N/A')[:50]}")
            print(f"   Content length: {len(doc)} chars")
            print(f"   Preview: {doc[:100]}...")

    return results

def rebuild_rag():
    """Rebuild RAG from all documents in the database"""
    db = next(get_db())

    print("\n=== Rebuilding RAG Database ===")

    # Get all documents with their current versions
    documents = db.query(Document).all()

    print(f"Found {len(documents)} documents in database")

    rebuilt = 0
    for doc in documents:
        if doc.current_version_id:
            # Get the current version
            version = db.query(DocumentVersion).filter(
                DocumentVersion.id == doc.current_version_id
            ).first()

            if version and version.markdown_content:
                print(f"\nRebuilding: {doc.title}")
                print(f"  Document ID: {doc.id}")
                print(f"  Version: {version.version_number}")
                print(f"  Content length: {len(version.markdown_content)} chars")

                # Delete old entries first
                delete_from_rag(str(doc.id), str(version.id))

                # Re-add with new chunking
                result = add_to_rag(
                    str(doc.id),
                    str(version.id),
                    doc.title,
                    version.markdown_content
                )
                print(f"  Result: {result}")
                rebuilt += 1

    print(f"\n✓ Rebuilt {rebuilt} documents")

    # Show final state
    inspect_rag()

def search_test(query: str):
    """Test search functionality"""
    from .rag import search_rag

    print(f"\n=== Testing Search: '{query}' ===")

    # Search without permission filtering (get all)
    results = search_rag(query, [], top_k=10)

    print(f"Found {len(results)} results")

    for i, result in enumerate(results):
        print(f"\n{i+1}. {result['title']}")
        print(f"   Score: {result['score']:.4f}")
        print(f"   Preview: {result['content'][:150]}...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python debug_rag.py inspect          - Show RAG contents")
        print("  python debug_rag.py rebuild          - Rebuild RAG from database")
        print("  python debug_rag.py search <query>   - Test search")
        sys.exit(1)

    command = sys.argv[1]

    if command == "inspect":
        inspect_rag()
    elif command == "rebuild":
        rebuild_rag()
    elif command == "search" and len(sys.argv) > 2:
        search_test(" ".join(sys.argv[2:]))
    else:
        print("Unknown command")
