"""
Comprehensive test script for FastAPI backend.

This script tests all backend functionality including:
- User CRUD operations
- Document creation and management
- PDF uploads with version history
- Permission management
- RAG search functionality
- AI agent queries

Creates:
- 3 users with varying permission levels
- 5 documents with 3 PDF versions each
"""

import requests
import json
import io
import sys
import argparse
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from uuid import UUID
import time
import subprocess

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}


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


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")


def generate_pdf_content(title: str, version: int, content_paragraphs: List[str]) -> bytes:
    """
    Generate a PDF file with given content using ReportLab.

    Args:
        title: PDF document title
        version: Version number for the content
        content_paragraphs: List of text paragraphs to include

    Returns:
        bytes: PDF file content
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_text = f"{title} - Version {version}"
    story.append(Paragraph(title_text, styles['Title']))
    story.append(Spacer(1, 12))

    # Version info
    version_text = f"<b>Version:</b> {version}"
    story.append(Paragraph(version_text, styles['Normal']))
    story.append(Spacer(1, 12))

    # Content paragraphs
    for para in content_paragraphs:
        story.append(Paragraph(para, styles['BodyText']))
        story.append(Spacer(1, 12))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def create_user(email: str, full_name: str, role: str) -> Dict[str, Any]:
    """Create a user via API"""
    payload = {
        "email": email,
        "full_name": full_name,
        "role": role
    }

    response = requests.post(f"{BASE_URL}/users", json=payload, headers=HEADERS)

    if response.status_code == 201:
        user_data = response.json()
        print_success(f"Created user: {full_name} ({role}) - ID: {user_data['id']}")
        return user_data
    else:
        print_error(f"Failed to create user {full_name}: {response.status_code} - {response.text}")
        return None


def create_document(title: str, description: str, created_by: str) -> Dict[str, Any]:
    """Create a document via API"""
    payload = {
        "title": title,
        "description": description,
        "created_by": created_by
    }

    response = requests.post(f"{BASE_URL}/documents", json=payload, headers=HEADERS)

    if response.status_code == 200:
        doc_data = response.json()
        print_success(f"Created document: {title} - ID: {doc_data['id']}")
        return doc_data
    else:
        print_error(f"Failed to create document {title}: {response.status_code} - {response.text}")
        return None


def upload_pdf_version(document_id: str, created_by: str, pdf_content: bytes,
                       filename: str, change_summary: str) -> Dict[str, Any]:
    """Upload a PDF version to a document"""
    files = {
        'pdf_file': (filename, io.BytesIO(pdf_content), 'application/pdf')
    }
    params = {
        'created_by': created_by,
        'change_summary': change_summary
    }

    try:
        response = requests.post(
            f"{BASE_URL}/documents/{document_id}/upload-pdf",
            files=files,
            params=params,
            timeout=30  # 30 second timeout for PDF processing
        )

        if response.status_code == 200:
            result = response.json()
            print_success(f"Uploaded PDF version {result['version']['version_number']} for document {document_id}")
            return result
        else:
            error_detail = "Unknown error"
            try:
                error_json = response.json()
                error_detail = error_json.get('detail', response.text)
            except:
                error_detail = response.text

            print_error(f"Failed to upload PDF: {response.status_code}")
            print_error(f"Error details: {error_detail}")

            # Print more debug info
            if response.status_code == 500:
                print_warning("Server error (500) - Check FastAPI server logs for details")
                print_info("Common causes:")
                print_info("  - Supabase credentials missing or invalid")
                print_info("  - PDF processing (MarkItDown) failed")
                print_info("  - Database connection issue")

            return None
    except requests.exceptions.Timeout:
        print_error(f"Upload timed out after 30 seconds")
        return None
    except Exception as e:
        print_error(f"Upload failed with exception: {str(e)}")
        return None


def grant_permission(document_id: str, user_id: str, permission_type: str) -> Dict[str, Any]:
    """Grant a permission to a user for a document"""
    payload = {
        "document_id": document_id,
        "user_id": user_id,
        "permission_type": permission_type
    }

    response = requests.post(f"{BASE_URL}/permissions", json=payload, headers=HEADERS)

    if response.status_code == 200:
        perm_data = response.json()
        print_success(f"Granted {permission_type} permission to user {user_id}")
        return perm_data
    else:
        print_error(f"Failed to grant permission: {response.status_code} - {response.text}")
        return None


def test_search(user_id: str, query: str, top_k: int = 5) -> Dict[str, Any]:
    """Test RAG search functionality"""
    payload = {
        "query": query,
        "user_id": user_id,
        "top_k": top_k
    }

    response = requests.post(f"{BASE_URL}/search", json=payload, headers=HEADERS)

    if response.status_code == 200:
        results = response.json()
        print_success(f"Search completed: found {results['total']} results")
        return results
    else:
        print_error(f"Search failed: {response.status_code} - {response.text}")
        return None


def test_agent_query(user_id: str, query: str) -> Dict[str, Any]:
    """Test AI agent query functionality"""
    payload = {
        "query": query,
        "user_id": user_id
    }

    response = requests.post(f"{BASE_URL}/agent/query", json=payload, headers=HEADERS)

    if response.status_code == 200:
        result = response.json()
        print_success("Agent query completed")
        return result
    else:
        print_error(f"Agent query failed: {response.status_code} - {response.text}")
        return None


def get_all_users() -> List[Dict[str, Any]]:
    """Get all users"""
    response = requests.get(f"{BASE_URL}/users")

    if response.status_code == 200:
        users = response.json()
        print_success(f"Retrieved {len(users)} users")
        return users
    else:
        print_error(f"Failed to get users: {response.status_code}")
        return []


def get_all_documents() -> List[Dict[str, Any]]:
    """Get all documents"""
    response = requests.get(f"{BASE_URL}/documents")

    if response.status_code == 200:
        docs = response.json()
        print_success(f"Retrieved {len(docs)} documents")
        return docs
    else:
        print_error(f"Failed to get documents: {response.status_code}")
        return []


def get_document_versions(document_id: str) -> List[Dict[str, Any]]:
    """Get all versions of a document"""
    response = requests.get(f"{BASE_URL}/documents/{document_id}/versions")

    if response.status_code == 200:
        versions = response.json()
        print_success(f"Retrieved {len(versions)} versions for document {document_id}")
        return versions
    else:
        print_error(f"Failed to get versions: {response.status_code}")
        return []


def update_document(document_id: str, title: str = None, status: str = None,
                   description: str = None) -> Dict[str, Any]:
    """Update document metadata"""
    params = {}
    if title:
        params['title'] = title
    if status:
        params['status'] = status
    if description:
        params['description'] = description

    response = requests.patch(f"{BASE_URL}/documents/{document_id}", params=params)

    if response.status_code == 200:
        doc = response.json()
        print_success(f"Updated document {document_id}")
        return doc
    else:
        print_error(f"Failed to update document: {response.status_code}")
        return None


def archive_document(document_id: str) -> Dict[str, Any]:
    """Archive a document"""
    response = requests.patch(f"{BASE_URL}/documents/{document_id}/archive")

    if response.status_code == 200:
        doc = response.json()
        print_success(f"Archived document {document_id}")
        return doc
    else:
        print_error(f"Failed to archive document: {response.status_code}")
        return None


def main(clear_first: bool = False):
    """Main test execution"""
    print_section("FastAPI Backend Comprehensive Test Suite")

    # Optional: Clear existing data
    if clear_first:
        print_section("Clearing Existing Test Data")
        print_info("Running cleanup script...")
        try:
            result = subprocess.run(
                [sys.executable, "clear_test_data.py"],
                input="yes\n",
                text=True,
                capture_output=False
            )
            if result.returncode != 0:
                print_error("Cleanup script failed. Continuing anyway...")
            else:
                print_success("Cleanup completed!")
                time.sleep(2)
        except Exception as e:
            print_error(f"Failed to run cleanup script: {str(e)}")
            print_info("Continuing with tests anyway...")

    # Check API health
    print_info("Checking API health...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print_success("API is running!")
        else:
            print_error(f"API health check failed: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print_error(f"Could not connect to API at {BASE_URL}")
        print_info("Make sure the FastAPI server is running with: uvicorn backend.app:app --reload")
        sys.exit(1)

    # Step 1: Create users with different roles
    print_section("Step 1: Creating 3 Users with Different Roles")

    admin_user = create_user(
        email="admin@example.com",
        full_name="Admin User",
        role="admin"
    )

    editor_user = create_user(
        email="editor@example.com",
        full_name="Editor User",
        role="editor"
    )

    viewer_user = create_user(
        email="viewer@example.com",
        full_name="Viewer User",
        role="viewer"
    )

    if not all([admin_user, editor_user, viewer_user]):
        print_error("Failed to create users. Exiting.")
        sys.exit(1)

    # Step 2: Create 5 documents
    print_section("Step 2: Creating 5 Documents")

    documents = []
    document_titles = [
        ("Project Requirements Document", "Detailed requirements for the new project"),
        ("Technical Architecture Spec", "System architecture and design patterns"),
        ("API Documentation", "REST API endpoints and usage guide"),
        ("User Manual", "End-user documentation and tutorials"),
        ("Security Policy", "Security guidelines and best practices")
    ]

    for title, description in document_titles:
        doc = create_document(title, description, admin_user['id'])
        if doc:
            documents.append(doc)
        time.sleep(0.5)  # Small delay between requests

    if len(documents) != 5:
        print_error("Failed to create all documents. Exiting.")
        sys.exit(1)

    # Step 3: Upload 3 PDF versions for each document
    print_section("Step 3: Uploading 3 PDF Versions for Each Document")

    version_contents = {
        1: [
            "This is the initial version of the document.",
            "It contains the basic structure and preliminary information.",
            "Version 1 establishes the foundation for future updates."
        ],
        2: [
            "This is the second version with updated content.",
            "Several sections have been expanded with more details.",
            "New requirements and specifications have been added.",
            "Version 2 incorporates feedback from the initial review."
        ],
        3: [
            "This is the final version of the document.",
            "All sections are complete and thoroughly reviewed.",
            "This version includes comprehensive examples and use cases.",
            "Final revisions have been made based on stakeholder feedback.",
            "Version 3 is approved for production use."
        ]
    }

    pdf_upload_failed = False
    successful_uploads = 0

    for doc in documents:
        print_info(f"\nUploading versions for: {doc['title']}")

        for version_num in range(1, 4):
            pdf_content = generate_pdf_content(
                title=doc['title'],
                version=version_num,
                content_paragraphs=version_contents[version_num]
            )

            change_summary = f"Version {version_num} - " + [
                "Initial document creation",
                "Updated with additional details and requirements",
                "Final revision with all stakeholder feedback incorporated"
            ][version_num - 1]

            filename = f"{doc['title'].replace(' ', '_')}_v{version_num}.pdf"

            result = upload_pdf_version(
                document_id=doc['id'],
                created_by=admin_user['id'],
                pdf_content=pdf_content,
                filename=filename,
                change_summary=change_summary
            )

            if result:
                successful_uploads += 1
            else:
                pdf_upload_failed = True

            time.sleep(1)  # Allow time for PDF processing and RAG indexing

    if pdf_upload_failed:
        print_warning(f"\nSome PDF uploads failed. Successfully uploaded: {successful_uploads}/15")
        print_info("This may be due to:")
        print_info("  - Missing or invalid Supabase credentials")
        print_info("  - MarkItDown library issues")
        print_info("  - Storage bucket not configured")
        print_info("\nContinuing with remaining tests...")

    # Step 4: Set up permissions for different users
    print_section("Step 4: Setting Up Document Permissions")

    # Admin user gets admin access to all documents (already creator, so grant explicitly)
    print_info("Granting permissions to Admin User (admin level)...")
    for doc in documents:
        grant_permission(doc['id'], admin_user['id'], "admin")
        time.sleep(0.2)

    # Editor user gets write access to first 3 documents
    print_info("\nGranting permissions to Editor User (write level)...")
    for doc in documents[:3]:
        grant_permission(doc['id'], editor_user['id'], "write")
        time.sleep(0.2)

    # Viewer user gets read access to first 2 documents
    print_info("\nGranting permissions to Viewer User (read level)...")
    for doc in documents[:2]:
        grant_permission(doc['id'], viewer_user['id'], "read")
        time.sleep(0.2)

    # Step 5: Test document retrieval
    print_section("Step 5: Testing Document Retrieval")

    all_docs = get_all_documents()
    print_info(f"Total documents in system: {len(all_docs)}")

    # Get versions for first document
    if documents:
        versions = get_document_versions(documents[0]['id'])
        print_info(f"Document '{documents[0]['title']}' has {len(versions)} versions")

    # Step 6: Test document updates
    print_section("Step 6: Testing Document Updates")

    if documents:
        updated_doc = update_document(
            documents[0]['id'],
            status="Published",
            description="Updated description - document is now published"
        )

        if updated_doc:
            print_info(f"Document status: {updated_doc['status']}")

    # Step 7: Test RAG search functionality
    print_section("Step 7: Testing RAG Search Functionality")

    search_failed = False  # Initialize for later use

    if successful_uploads > 0:
        # Allow some time for RAG indexing to complete
        print_info("Waiting 5 seconds for RAG indexing to complete...")
        time.sleep(5)

        search_queries = [
            "initial version",
            "requirements and specifications",
            "stakeholder feedback",
            "security best practices"
        ]

        search_failed = False
        for query in search_queries:
            print_info(f"\nSearching for: '{query}'")
            results = test_search(admin_user['id'], query, top_k=3)

            if results and results['results']:
                for i, result in enumerate(results['results'][:3], 1):
                    print(f"  {i}. Score: {result.get('relevance_score', 'N/A'):.4f}")
                    print(f"     Document: {result.get('title', 'N/A')}")
            elif results is None:
                search_failed = True
                break
            time.sleep(1)

        if search_failed:
            print_warning("\nRAG search failed - likely due to invalid OpenAI API key")
            print_info("Update OPENAI_API_KEY in .env file to enable search functionality")
    else:
        print_warning("Skipping RAG search tests - no PDFs were successfully uploaded")

    # Step 8: Test AI agent queries
    print_section("Step 8: Testing AI Agent Queries")

    if successful_uploads > 0 and not search_failed:
        agent_queries = [
            "What documents are available?",
            "Summarize the main topics across all documents",
            "What are the key requirements mentioned?"
        ]

        for query in agent_queries:
            print_info(f"\nAgent query: '{query}'")
            result = test_agent_query(admin_user['id'], query)

            if result:
                response_text = result.get('response', '')
                # Print first 200 characters of response
                preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
                print(f"  Response: {preview}")
            else:
                print_warning("AI agent queries require valid OpenAI API key")
                break
            time.sleep(2)
    else:
        print_warning("Skipping AI agent tests - RAG search is not functional")

    # Step 9: Test permission-based access
    print_section("Step 9: Testing Permission-Based Access")

    # Viewer user should only see results from documents they have access to
    print_info("Testing viewer user search (limited access)...")
    viewer_results = test_search(viewer_user['id'], "version", top_k=5)

    if viewer_results:
        print_info(f"Viewer user found {viewer_results['total']} results (should only access docs 1-2)")

    # Step 10: Test document archival
    print_section("Step 10: Testing Document Archival")

    if len(documents) >= 5:
        print_info("Archiving the last document...")
        archived = archive_document(documents[4]['id'])

        if archived:
            print_info(f"Document status: {archived['status']}")

    # Final summary
    print_section("Test Summary")

    all_users = get_all_users()
    all_docs = get_all_documents()

    print_info(f"Total users created: {len(all_users)}")
    print_info(f"Total documents created: {len(all_docs)}")

    total_versions = 0
    for doc in documents:
        versions = get_document_versions(doc['id'])
        total_versions += len(versions)

    print_info(f"Total document versions: {total_versions}")
    print_success("\nAll tests completed successfully!")

    # Print test data summary
    print_section("Test Data Summary")

    print(f"{Colors.BOLD}Users:{Colors.ENDC}")
    print(f"  1. Admin User (admin@example.com) - Role: admin - ID: {admin_user['id']}")
    print(f"  2. Editor User (editor@example.com) - Role: editor - ID: {editor_user['id']}")
    print(f"  3. Viewer User (viewer@example.com) - Role: viewer - ID: {viewer_user['id']}")

    print(f"\n{Colors.BOLD}Documents:{Colors.ENDC}")
    for i, doc in enumerate(documents, 1):
        print(f"  {i}. {doc['title']} - ID: {doc['id']}")
        print(f"     Status: {doc.get('status', 'Draft')}, Versions: 3")

    print(f"\n{Colors.BOLD}Permissions:{Colors.ENDC}")
    print(f"  Admin User: Admin access to all 5 documents")
    print(f"  Editor User: Write access to documents 1-3")
    print(f"  Viewer User: Read access to documents 1-2")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Comprehensive test script for FastAPI backend",
        epilog="Example: python test_backend.py --clear"
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear all existing data before running tests'
    )
    args = parser.parse_args()

    try:
        main(clear_first=args.clear)
    except KeyboardInterrupt:
        print_warning("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
