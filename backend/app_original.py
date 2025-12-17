"""Updated FastAPI app with PDF upload and PydanticAI agent integration."""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from uuid import UUID
from datetime import datetime
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

from .database import get_db
from .models import User, Document, DocumentVersion, DocumentPermission
from .rag import add_to_rag, search_rag, delete_from_rag
from .utils import process_pdf_upload
from .schemas import (
    UserCreate, UserUpdate, UserResponse,
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentStatus,
    VersionCreate, VersionResponse,
    PermissionCreate, PermissionUpdate, PermissionResponse, PermissionType,
    RAGSearch, SearchResponse,
    AgentQuery, AgentResponse,
    PDFUploadResponse,
    ErrorResponse
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
    In production, replace this with proper JWT token validation:
    - Use OAuth2PasswordBearer or similar
    - Validate JWT tokens
    - Verify token signature and expiration

    For now, we require clients to send X-User-ID header.
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

def verify_user_exists(user_id: UUID, db: Session) -> User:
    """Verify that the user exists in the database"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found"
        )
    return user

# === USER ENDPOINTS ===

@app.post("/users", status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(400, "Email already exists")
    
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/users/{user_id}")
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).options(
        joinedload(User.documents),
        joinedload(User.permissions)
    ).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(404, "User not found")
    return user

@app.patch("/users/{user_id}")
def update_user(user_id: UUID, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(user, k, v)
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user

# === DOCUMENT ENDPOINTS ===

@app.post("/documents")
def create_document(doc: DocumentCreate, db: Session = Depends(get_db)):
    if not db.query(User).filter(User.id == doc.created_by).first():
        raise HTTPException(404, "User not found")
    
    db_doc = Document(**doc.model_dump())
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

@app.get("/documents")
def list_documents(status: Optional[DocumentStatus] = None, db: Session = Depends(get_db)):
    """List all documents with optional status filter"""
    query = db.query(Document)
    if status:
        query = query.filter(Document.status == status.value)
    return query.all()

@app.get("/documents/{document_id}")
def get_document(document_id: UUID, db: Session = Depends(get_db)):
    doc = db.query(Document).options(
        joinedload(Document.creator),
        joinedload(Document.versions),
        joinedload(Document.permissions)
    ).filter(Document.id == document_id).first()
    
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc

@app.patch("/documents/{document_id}")
def update_document(document_id: UUID, payload: DocumentUpdate, db: Session = Depends(get_db)):
    """Update document metadata with validation"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")

    # Update only provided fields
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        if k == "status" and isinstance(v, DocumentStatus):
            setattr(doc, k, v.value)
        else:
            setattr(doc, k, v)

    doc.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(doc)
    return doc

@app.patch("/documents/{document_id}/archive")
def archive_document(document_id: UUID, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    
    doc.status = "Archived"
    doc.updated_at = datetime.utcnow()
    db.commit()
    
    # Remove from RAG
    delete_from_rag(str(document_id))
    
    return doc

# === VERSION ENDPOINTS ===

@app.post("/versions")
def create_version(version: VersionCreate, background_tasks: BackgroundTasks,
                   db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == version.document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")

    db_version = DocumentVersion(**version.model_dump())
    db.add(db_version)
    db.commit()
    db.refresh(db_version)

    # Get the old version ID before updating
    old_version_id = str(doc.current_version_id) if doc.current_version_id else None

    # Update document's current version
    doc.current_version_id = db_version.id
    doc.updated_at = datetime.utcnow()
    db.commit()

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
def list_versions(document_id: UUID, db: Session = Depends(get_db)):
    if not db.query(Document).filter(Document.id == document_id).first():
        raise HTTPException(404, "Document not found")
    
    return db.query(DocumentVersion).filter(
        DocumentVersion.document_id == document_id
    ).order_by(DocumentVersion.version_number.desc()).all()

# === PDF UPLOAD ENDPOINTS ===

@app.post("/documents/{document_id}/upload-pdf")
async def upload_pdf_version(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    created_by: UUID = Form(...),
    pdf_file: UploadFile = File(...),
    change_summary: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF, convert to markdown, and create a new document version.
    
    This endpoint:
    1. Receives the PDF file upload
    2. Converts it to markdown
    3. Uploads the PDF to Supabase storage
    4. Creates a new document version in the database
    5. Indexes the content in RAG (background)
    """
    # Verify document exists
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    
    # Verify user exists
    user = db.query(User).filter(User.id == created_by).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        content = await pdf_file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Process PDF: convert to markdown and upload to storage
        markdown_content, pdf_url = process_pdf_upload(
            pdf_path=tmp_path,
            document_id=str(document_id),
            filename=pdf_file.filename
        )
        
        # Get next version number
        latest_version = db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id
        ).order_by(DocumentVersion.version_number.desc()).first()
        
        version_number = (latest_version.version_number + 1) if latest_version else 1
        
        # Create new version
        db_version = DocumentVersion(
            document_id=document_id,
            created_by=created_by,
            version_number=version_number,
            markdown_content=markdown_content,
            pdf_url=pdf_url,
            change_summary=change_summary or f"Version {version_number} - PDF upload"
        )
        
        db.add(db_version)
        db.commit()
        db.refresh(db_version)
        
        # Get the old version ID before updating
        old_version_id = str(doc.current_version_id) if doc.current_version_id else None

        # Update document's current version
        doc.current_version_id = db_version.id
        doc.updated_at = datetime.utcnow()
        db.commit()

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
            markdown_content
        )
        
        return {
            "message": "PDF uploaded and processed successfully",
            "version": {
                "id": str(db_version.id),
                "version_number": db_version.version_number,
                "pdf_url": pdf_url,
                "created_at": db_version.created_at
            }
        }
        
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/documents/create-from-pdf")
async def create_document_from_pdf(
    background_tasks: BackgroundTasks,
    created_by: UUID = Form(...),
    pdf_file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Create a new document directly from a PDF upload.
    
    This endpoint:
    1. Creates a new document
    2. Uploads and processes the PDF
    3. Creates the first version
    4. Indexes in RAG
    """
    # Verify user exists
    user = db.query(User).filter(User.id == created_by).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    # Use filename as title if not provided
    if not title:
        title = os.path.splitext(pdf_file.filename)[0]
    
    # Create document first
    db_doc = Document(
        created_by=created_by,
        title=title,
        description=description,
        status="Draft"
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        content = await pdf_file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Process PDF
        markdown_content, pdf_url = process_pdf_upload(
            pdf_path=tmp_path,
            document_id=str(db_doc.id),
            filename=pdf_file.filename
        )
        
        # Create first version
        db_version = DocumentVersion(
            document_id=db_doc.id,
            created_by=created_by,
            version_number=1,
            markdown_content=markdown_content,
            pdf_url=pdf_url,
            change_summary="Initial version from PDF upload"
        )
        
        db.add(db_version)
        db.commit()
        db.refresh(db_version)
        
        # Update document's current version
        db_doc.current_version_id = db_version.id
        db.commit()
        
        # Index in RAG (background)
        background_tasks.add_task(
            add_to_rag,
            str(db_doc.id),
            str(db_version.id),
            db_doc.title,
            markdown_content
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
                "pdf_url": pdf_url
            }
        }
        
    except Exception as e:
        # Rollback document creation if PDF processing fails
        db.delete(db_doc)
        db.commit()
        raise HTTPException(500, f"Failed to process PDF: {str(e)}")
        
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

# === PERMISSION ENDPOINTS ===

@app.post("/permissions")
def grant_permission(perm: PermissionCreate, db: Session = Depends(get_db)):
    if not db.query(Document).filter(Document.id == perm.document_id).first():
        raise HTTPException(404, "Document not found")
    if not db.query(User).filter(User.id == perm.user_id).first():
        raise HTTPException(404, "User not found")
    
    existing = db.query(DocumentPermission).filter(
        DocumentPermission.document_id == perm.document_id,
        DocumentPermission.user_id == perm.user_id
    ).first()
    
    if existing:
        raise HTTPException(400, "Permission already exists")
    
    db_perm = DocumentPermission(**perm.model_dump())
    db.add(db_perm)
    db.commit()
    db.refresh(db_perm)
    return db_perm

@app.get("/documents/{document_id}/permissions")
def list_permissions(document_id: UUID, db: Session = Depends(get_db)):
    if not db.query(Document).filter(Document.id == document_id).first():
        raise HTTPException(404, "Document not found")
    
    return db.query(DocumentPermission).filter(
        DocumentPermission.document_id == document_id
    ).all()

@app.delete("/permissions/{permission_id}")
def revoke_permission(permission_id: UUID, db: Session = Depends(get_db)):
    perm = db.query(DocumentPermission).filter(DocumentPermission.id == permission_id).first()
    if not perm:
        raise HTTPException(404, "Permission not found")
    
    db.delete(perm)
    db.commit()
    return {"status": "revoked"}

# === RAG/SEARCH ENDPOINTS ===

@app.post("/search")
def search_documents(
    search: RAGSearch,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Search documents using RAG (Retrieval-Augmented Generation).
    Only searches documents the authenticated user has permission to access.

    Authentication: Requires X-User-ID header with valid user UUID.
    """
    # Verify user exists
    user = verify_user_exists(current_user_id, db)

    # Get user's accessible documents
    perms = db.query(DocumentPermission).filter(
        DocumentPermission.user_id == current_user_id
    ).all()

    accessible_docs = [str(p.document_id) for p in perms]

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

@app.post("/agent/query")
async def agent_query(
    request: AgentQuery,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Query the AI agent about documents.
    Agent uses RAG to search and analyze documents the authenticated user has access to.

    Authentication: Requires X-User-ID header with valid user UUID.
    """
    from .ai_agent import run_agent

    # Verify user exists
    user = verify_user_exists(current_user_id, db)

    try:
        response = await run_agent(current_user_id, user.email, request.query)
        return {
            "response": response,
            "user_email": user.email
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.get("/")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)