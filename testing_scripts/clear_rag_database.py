"""
Clear RAG database (ChromaDB).

This script:
1. Deletes all documents and embeddings from the ChromaDB collection
2. Optionally resets the entire collection
3. Provides options for partial cleanup by document ID

WARNING: This will delete data from your RAG database!
"""

import os
import sys
from dotenv import load_dotenv
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

load_dotenv()


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {message}{Colors.ENDC}")


def get_chroma_client():
    """Initialize ChromaDB client"""
    return chromadb.PersistentClient(
        path=os.getenv('CHROMA_PERSIST_DIR', './chroma_data')
    )


def get_embedding_function():
    """Get OpenAI embedding function"""
    return OpenAIEmbeddingFunction(
        api_key=os.getenv('OPENAI_API_KEY'),
        model_name="text-embedding-3-small"
    )


def show_collection_stats():
    """Display current collection statistics"""
    print_section("Current RAG Database Statistics")

    try:
        client = get_chroma_client()
        embedding_fn = get_embedding_function()

        # Get or create collection
        collection = client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"},
            embedding_function=embedding_fn
        )

        # Get count
        count = collection.count()
        print_info(f"Total chunks in RAG database: {count}")

        # Get some sample data to show document IDs
        if count > 0:
            results = collection.get(limit=100)
            if results['metadatas']:
                doc_ids = set(meta.get('document_id') for meta in results['metadatas'])
                print_info(f"Unique documents found (sample): {len(doc_ids)}")
                print_info(f"Sample document IDs: {list(doc_ids)[:5]}")

        return collection, count

    except Exception as e:
        print_error(f"Failed to get collection stats: {str(e)}")
        return None, 0


def confirm_deletion(count: int):
    """Ask user to confirm deletion"""
    print_warning(f"This will DELETE ALL {count} chunks from your RAG database!")
    print_warning("This action cannot be undone.")

    response = input(f"\n{Colors.YELLOW}Are you sure you want to continue? (yes/no): {Colors.ENDC}")

    if response.lower() not in ['yes', 'y']:
        print_info("Operation cancelled.")
        sys.exit(0)

    print()


def clear_all_documents(collection):
    """Clear all documents from the RAG database"""
    print_section("Clearing RAG Database")

    try:
        # Get all IDs
        results = collection.get()

        if not results['ids']:
            print_info("RAG database is already empty")
            return True

        total_chunks = len(results['ids'])
        print_info(f"Deleting {total_chunks} chunks...")

        # Delete all
        collection.delete(ids=results['ids'])

        print_success(f"Successfully deleted {total_chunks} chunks from RAG database")
        return True

    except Exception as e:
        print_error(f"Failed to clear RAG database: {str(e)}")
        return False


def clear_by_document_id(collection, document_id: str):
    """Clear specific document from RAG database"""
    print_section(f"Clearing Document: {document_id}")

    try:
        # Get chunks for this document
        results = collection.get(where={"document_id": document_id})

        if not results['ids']:
            print_warning(f"No chunks found for document ID: {document_id}")
            return True

        chunk_count = len(results['ids'])
        print_info(f"Found {chunk_count} chunks for document {document_id}")

        # Delete all chunks for this document
        collection.delete(ids=results['ids'])

        print_success(f"Successfully deleted {chunk_count} chunks")
        return True

    except Exception as e:
        print_error(f"Failed to clear document: {str(e)}")
        return False


def reset_collection():
    """Completely reset the collection (delete and recreate)"""
    print_section("Resetting Collection")

    try:
        client = get_chroma_client()

        # Delete collection
        print_info("Deleting collection...")
        client.delete_collection(name="documents")
        print_success("Collection deleted")

        # Recreate collection
        print_info("Recreating collection...")
        embedding_fn = get_embedding_function()
        client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"},
            embedding_function=embedding_fn
        )
        print_success("Collection recreated")

        return True

    except Exception as e:
        print_error(f"Failed to reset collection: {str(e)}")
        return False


def verify_cleanup(collection):
    """Verify that cleanup was successful"""
    print_section("Verifying Cleanup")

    try:
        count = collection.count()

        if count == 0:
            print_success("RAG database is empty")
        else:
            print_warning(f"RAG database still contains {count} chunks")

        return count == 0

    except Exception as e:
        print_error(f"Verification failed: {str(e)}")
        return False


def main():
    """Main cleanup execution"""
    print_section("RAG Database Cleanup Script")

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--document-id" and len(sys.argv) > 2:
            document_id = sys.argv[2]
            collection, _ = show_collection_stats()
            if collection:
                clear_by_document_id(collection, document_id)
            return
        elif sys.argv[1] == "--reset":
            collection, count = show_collection_stats()
            if count > 0:
                confirm_deletion(count)
            success = reset_collection()
            if success:
                print_success("\nCollection reset complete!")
            return
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python clear_rag_database.py                    # Clear all documents")
            print("  python clear_rag_database.py --document-id <ID> # Clear specific document")
            print("  python clear_rag_database.py --reset            # Reset entire collection")
            print("  python clear_rag_database.py --help             # Show this help")
            return

    # Default: clear all documents
    collection, count = show_collection_stats()

    if not collection:
        print_error("Failed to initialize collection")
        sys.exit(1)

    if count == 0:
        print_info("RAG database is already empty. Nothing to do.")
        sys.exit(0)

    # Confirm with user
    confirm_deletion(count)

    # Clear all documents
    success = clear_all_documents(collection)

    # Verify cleanup
    if success:
        verify_cleanup(collection)

    # Summary
    print_section("Cleanup Summary")

    if success:
        print_success("RAG database cleanup completed successfully!")
    else:
        print_error("Cleanup failed. Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\nCleanup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
