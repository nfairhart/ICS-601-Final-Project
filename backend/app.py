"""Refactored FastAPI app with service layer - business logic extracted to services."""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import os
from dotenv import load_dotenv

load_dotenv()

from .database import get_db
from .models import User
from .rag import add_to_rag, search_rag, delete_from_rag
from .schemas import (
    UserCreate, UserUpdate,
    DocumentCreate, DocumentUpdate, DocumentStatus,
    VersionCreate,
    PermissionCreate, PermissionUpdate, PermissionType,
    RAGSearch,
    AgentQuery, AgentResponse,
)
from .services import (
    UserService,
    DocumentService,
    VersionService,
    PermissionService,
)

app = FastAPI(title="Document Management API")

# Configure CORS with proper origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5001,http://127.0.0.1:5001")
origins_list = [origin.strip() for origin in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-User-ID"],
)

# === EXCEPTION HANDLERS ===

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Custom handler for validation errors with detailed error messages"""
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "detail": errors,
            "body": exc.body
        }
    )

# === AUTHENTICATION HELPERS ===
# TODO: Replace with proper JWT authentication in production

def get_current_user_id(x_user_id: Optional[str] = Header(None)) -> UUID:
    """
    Get the current authenticated user ID from request header.

    SECURITY NOTE: This is a simple header-based authentication for development.
    In production, replace this with proper JWT token validation.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Missing X-User-ID header."
        )

    try:
        user_id = UUID(x_user_id)
        return user_id
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid user ID format"
        )

# === DEPENDENCY INJECTION FOR SERVICES ===

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to inject UserService"""
    return UserService(db)

def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    """Dependency to inject DocumentService"""
    return DocumentService(db)

def get_version_service(db: Session = Depends(get_db)) -> VersionService:
    """Dependency to inject VersionService"""
    return VersionService(db)

def get_permission_service(db: Session = Depends(get_db)) -> PermissionService:
    """Dependency to inject PermissionService"""
    return PermissionService(db)

# === USER ENDPOINTS ===

@app.post("/users", status_code=201)
def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """Create a new user"""
    return user_service.create_user(user)

@app.get("/users")
def list_users(user_service: UserService = Depends(get_user_service)):
    """List all users"""
    return user_service.get_all()

@app.get("/users/{user_id}")
def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service)
):
    """Get user details with relationships"""
    return user_service.get_user_with_relations(user_id)

@app.patch("/users/{user_id}")
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """Update user information"""
    return user_service.update_user(user_id, payload)

# === DOCUMENT ENDPOINTS ===

@app.post("/documents")
def create_document(
    doc: DocumentCreate,
    doc_service: DocumentService = Depends(get_document_service)
):
    """Create a new document"""
    return doc_service.create_document(doc)

@app.get("/documents")
def list_documents(
    status: Optional[DocumentStatus] = None,
    doc_service: DocumentService = Depends(get_document_service)
):
    """List all documents with optional status filter"""
    return doc_service.list_documents(status)

@app.get("/documents/{document_id}")
def get_document(
    document_id: UUID,
    doc_service: DocumentService = Depends(get_document_service)
):
    """Get document details with relationships"""
    return doc_service.get_document_with_relations(document_id)

@app.patch("/documents/{document_id}")
def update_document(
    document_id: UUID,
    payload: DocumentUpdate,
    doc_service: DocumentService = Depends(get_document_service)
):
    """Update document metadata with validation"""
    return doc_service.update_document(document_id, payload)

@app.patch("/documents/{document_id}/archive")
def archive_document(
    document_id: UUID,
    doc_service: DocumentService = Depends(get_document_service)
):
    """Archive a document and remove from RAG"""
    doc = doc_service.archive_document(document_id)

    # Remove from RAG
    delete_from_rag(str(document_id))

    return doc

# === VERSION ENDPOINTS ===

@app.post("/versions")
def create_version(
    version: VersionCreate,
    background_tasks: BackgroundTasks,
    version_service: VersionService = Depends(get_version_service),
    doc_service: DocumentService = Depends(get_document_service)
):
    """Create a new document version"""
    # Get the document
    doc = doc_service.get_or_404(version.document_id)

    # Create version using service
    db_version, old_version_id = version_service.create_version(version, doc)

    # Index in RAG (background)
    if db_version.markdown_content:
        # Remove old version from RAG first, then add new version
        if old_version_id:
            background_tasks.add_task(
                delete_from_rag,
                str(version.document_id),
                old_version_id
            )
        background_tasks.add_task(
            add_to_rag,
            str(version.document_id),
            str(db_version.id),
            doc.title,
            db_version.markdown_content
        )

    return db_version

@app.get("/documents/{document_id}/versions")
def list_versions(
    document_id: UUID,
    version_service: VersionService = Depends(get_version_service),
    doc_service: DocumentService = Depends(get_document_service)
):
    """List all versions for a document"""
    # Verify document exists
    doc_service.get_or_404(document_id)

    return version_service.get_document_versions(document_id)

# === PDF UPLOAD ENDPOINTS ===

@app.post("/documents/{document_id}/upload-pdf")
async def upload_pdf_version(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    created_by: UUID = Form(...),
    pdf_file: UploadFile = File(...),
    change_summary: Optional[str] = Form(None),
    version_service: VersionService = Depends(get_version_service),
    doc_service: DocumentService = Depends(get_document_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    Upload a PDF and create a new document version.

    This endpoint:
    1. Receives the PDF file upload
    2. Converts it to markdown
    3. Uploads the PDF to Supabase storage
    4. Creates a new document version in the database
    5. Indexes the content in RAG (background)
    """
    # Verify document exists
    doc = doc_service.get_or_404(document_id)

    # Verify user exists
    user_service.verify_user_exists(created_by)

    # Process PDF and create version (service handles all the complexity)
    db_version, old_version_id = await version_service.create_version_from_pdf(
        document=doc,
        pdf_file=pdf_file,
        created_by=created_by,
        change_summary=change_summary
    )

    # Index in RAG (background) - remove old version first, then add new
    if old_version_id:
        background_tasks.add_task(
            delete_from_rag,
            str(document_id),
            old_version_id
        )
    background_tasks.add_task(
        add_to_rag,
        str(document_id),
        str(db_version.id),
        doc.title,
        db_version.markdown_content
    )

    return {
        "message": "PDF uploaded and processed successfully",
        "version": {
            "id": str(db_version.id),
            "version_number": db_version.version_number,
            "pdf_url": db_version.pdf_url,
            "created_at": db_version.created_at
        }
    }

@app.post("/documents/create-from-pdf")
async def create_document_from_pdf(
    background_tasks: BackgroundTasks,
    created_by: UUID = Form(...),
    pdf_file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    version_service: VersionService = Depends(get_version_service)
):
    """
    Create a new document directly from a PDF upload.

    This endpoint:
    1. Creates a new document
    2. Uploads and processes the PDF
    3. Creates the first version
    4. Indexes in RAG
    """
    # Service handles all the complexity including user validation
    db_doc, db_version = await version_service.create_document_with_pdf(
        pdf_file=pdf_file,
        created_by=created_by,
        title=title,
        description=description
    )

    # Index in RAG (background)
    background_tasks.add_task(
        add_to_rag,
        str(db_doc.id),
        str(db_version.id),
        db_doc.title,
        db_version.markdown_content
    )

    return {
        "message": "Document created successfully from PDF",
        "document": {
            "id": str(db_doc.id),
            "title": db_doc.title,
            "created_at": db_doc.created_at
        },
        "version": {
            "id": str(db_version.id),
            "version_number": db_version.version_number,
            "pdf_url": db_version.pdf_url
        }
    }

# === PERMISSION ENDPOINTS ===

@app.post("/permissions")
def grant_permission(
    perm: PermissionCreate,
    perm_service: PermissionService = Depends(get_permission_service)
):
    """Grant a permission to a user for a document"""
    return perm_service.grant_permission(perm)

@app.get("/documents/{document_id}/permissions")
def list_permissions(
    document_id: UUID,
    perm_service: PermissionService = Depends(get_permission_service)
):
    """List all permissions for a document"""
    return perm_service.get_document_permissions(document_id)

@app.delete("/permissions/{permission_id}")
def revoke_permission(
    permission_id: UUID,
    perm_service: PermissionService = Depends(get_permission_service)
):
    """Revoke a permission"""
    return perm_service.revoke_permission(permission_id)

# === RAG/SEARCH ENDPOINTS ===

@app.post("/search")
def search_documents(
    search: RAGSearch,
    current_user_id: UUID = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
    perm_service: PermissionService = Depends(get_permission_service)
):
    """
    Search documents using RAG (Retrieval-Augmented Generation).
    Only searches documents the authenticated user has permission to access.

    Authentication: Requires X-User-ID header with valid user UUID.
    """
    # Verify user exists
    user = user_service.verify_user_exists(current_user_id)

    # Get user's accessible documents using service
    accessible_docs = perm_service.get_user_accessible_documents(current_user_id)

    if not accessible_docs:
        return {
            "query": search.query,
            "results": [],
            "total": 0,
            "message": "You don't have access to any documents. Ask an admin to grant you permissions."
        }

    results = search_rag(search.query, accessible_docs, search.top_k)

    return {
        "query": search.query,
        "results": results,
        "total": len(results),
        "user_email": user.email
    }

@app.post("/agent/query", response_model=AgentResponse)
async def agent_query(
    request: AgentQuery,
    current_user_id: UUID = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):
    """
    Query the AI agent about documents.
    Agent uses RAG to search and analyze documents the authenticated user has access to.

    Authentication: Requires X-User-ID header with valid user UUID.
    """
    from .ai_agent import run_agent

    # Verify user exists
    user = user_service.verify_user_exists(current_user_id)

    try:
        response = await run_agent(current_user_id, user.email, request.query)
        return AgentResponse(response=response, user_email=user.email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.get("/")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
