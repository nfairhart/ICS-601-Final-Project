"""
Rebuild RAG database from current document versions.

This script:
1. Clears the existing ChromaDB collection
2. Fetches all documents from the database
3. Re-indexes only the CURRENT version of each document into RAG

This is useful after fixing bugs or when you need to ensure only
current versions are in the RAG database.
"""

import os
import sys
from dotenv import load_dotenv
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Import from backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from backend.models import Document, DocumentVersion
from backend.rag import add_to_rag

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


def get_database_session():
    """Create database session"""
    # Build database URL from environment variables (matching backend/database.py)
    user = os.getenv('user')
    password = os.getenv('password')
    host = os.getenv('host')
    port = os.getenv('port')
    dbname = os.getenv('dbname')

    if not all([user, password, host, port, dbname]):
        raise ValueError("Missing database credentials in .env file. Required: user, password, host, port, dbname")

    database_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"

    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def clear_rag_database():
    """Clear the entire RAG database"""
    print_section("Step 1: Clearing RAG Database")

    try:
        client = chromadb.PersistentClient(
            path=os.getenv('CHROMA_PERSIST_DIR', './chroma_data')
        )

        embedding_fn = OpenAIEmbeddingFunction(
            api_key=os.getenv('OPENAI_API_KEY'),
            model_name="text-embedding-3-small"
        )

        # Delete and recreate collection
        print_info("Deleting old collection...")
        try:
            client.delete_collection(name="documents")
            print_success("Old collection deleted")
        except:
            print_warning("Collection doesn't exist (this is fine)")

        print_info("Creating fresh collection...")
        client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"},
            embedding_function=embedding_fn
        )
        print_success("Fresh collection created")

        return True

    except Exception as e:
        print_error(f"Failed to clear RAG database: {str(e)}")
        return False


def rebuild_rag_index():
    """Rebuild RAG index from current document versions"""
    print_section("Step 2: Rebuilding RAG Index")

    db = get_database_session()

    try:
        # Get all documents with their current versions
        documents = db.query(Document).filter(
            Document.current_version_id.isnot(None),
            Document.status != "Archived"
        ).all()

        print_info(f"Found {len(documents)} active documents with current versions")

        if len(documents) == 0:
            print_warning("No documents to index")
            return True

        indexed_count = 0
        skipped_count = 0
        error_count = 0

        for doc in documents:
            # Get the current version
            version = db.query(DocumentVersion).filter(
                DocumentVersion.id == doc.current_version_id
            ).first()

            if not version:
                print_warning(f"Skipping '{doc.title}': current version not found")
                skipped_count += 1
                continue

            if not version.markdown_content:
                print_warning(f"Skipping '{doc.title}': no markdown content")
                skipped_count += 1
                continue

            try:
                print_info(f"Indexing: {doc.title} (v{version.version_number})")

                result = add_to_rag(
                    document_id=str(doc.id),
                    version_id=str(version.id),
                    title=doc.title,
                    content=version.markdown_content
                )

                print_success(f"  Indexed: {result}")
                indexed_count += 1

            except Exception as e:
                print_error(f"  Failed to index '{doc.title}': {str(e)}")
                error_count += 1

        # Summary
        print_section("Indexing Summary")
        print_success(f"Successfully indexed: {indexed_count} documents")
        if skipped_count > 0:
            print_warning(f"Skipped: {skipped_count} documents")
        if error_count > 0:
            print_error(f"Errors: {error_count} documents")

        return error_count == 0

    except Exception as e:
        print_error(f"Failed to rebuild RAG index: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


def verify_rebuild():
    """Verify the rebuild was successful"""
    print_section("Step 3: Verification")

    try:
        client = chromadb.PersistentClient(
            path=os.getenv('CHROMA_PERSIST_DIR', './chroma_data')
        )

        embedding_fn = OpenAIEmbeddingFunction(
            api_key=os.getenv('OPENAI_API_KEY'),
            model_name="text-embedding-3-small"
        )

        collection = client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"},
            embedding_function=embedding_fn
        )

        count = collection.count()
        print_info(f"Total chunks in RAG database: {count}")

        if count > 0:
            # Get unique document IDs
            results = collection.get(limit=1000)
            if results['metadatas']:
                doc_ids = set(meta.get('document_id') for meta in results['metadatas'])
                version_ids = set(meta.get('version_id') for meta in results['metadatas'])

                print_success(f"Unique documents: {len(doc_ids)}")
                print_success(f"Unique versions: {len(version_ids)}")

                # Check for duplicate versions (should be none)
                if len(version_ids) == len(doc_ids):
                    print_success("✓ Each document has exactly one version (as expected)")
                else:
                    print_warning(f"⚠ Found {len(version_ids)} versions for {len(doc_ids)} documents")

        return True

    except Exception as e:
        print_error(f"Verification failed: {str(e)}")
        return False


def main():
    """Main rebuild execution"""
    print_section("RAG Database Rebuild Script")
    print_info("This script will rebuild your RAG database from scratch")
    print_info("Only CURRENT versions of active documents will be indexed")

    # Confirm with user
    if "--yes" not in sys.argv:
        print_warning("\nThis will DELETE all existing RAG data and rebuild from scratch")
        response = input(f"\n{Colors.YELLOW}Continue? (yes/no): {Colors.ENDC}")

        if response.lower() not in ['yes', 'y']:
            print_info("Operation cancelled")
            sys.exit(0)

    print()

    # Step 1: Clear RAG database
    if not clear_rag_database():
        print_error("Failed to clear RAG database")
        sys.exit(1)

    # Step 2: Rebuild index
    if not rebuild_rag_index():
        print_error("Failed to rebuild RAG index")
        sys.exit(1)

    # Step 3: Verify
    verify_rebuild()

    # Final summary
    print_section("Rebuild Complete!")
    print_success("✓ RAG database has been successfully rebuilt")
    print_info("\nYour RAG database now contains only the current versions")
    print_info("of all active documents. Old versions have been removed.")


if __name__ == "__main__":
    try:
        if "--help" in sys.argv:
            print("RAG Database Rebuild Script")
            print("\nUsage:")
            print("  python rebuild_rag_database.py        # Interactive mode")
            print("  python rebuild_rag_database.py --yes  # Auto-confirm")
            print("  python rebuild_rag_database.py --help # Show this help")
            print("\nThis script will:")
            print("  1. Clear the entire RAG database")
            print("  2. Re-index all current document versions")
            print("  3. Verify the rebuild was successful")
            sys.exit(0)

        main()

    except KeyboardInterrupt:
        print_warning("\n\nRebuild interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
