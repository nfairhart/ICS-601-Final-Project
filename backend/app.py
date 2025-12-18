"""FastAPI app for document management with direct database access."""
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Optional
from uuid import UUID
from datetime import datetime
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

from database import SessionLocal
from models import User, Document, DocumentVersion, DocumentPermission
from rag import add_to_rag, search_rag, delete_from_rag
from utils import process_pdf_upload
from schemas import (
    UserCreate, UserUpdate,
    DocumentCreate, DocumentUpdate, DocumentStatus,
    VersionCreate,
    PermissionCreate, PermissionUpdate, PermissionType,
    RAGSearch,
    AgentQuery, AgentResponse,
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
    allow_headers=["Content-Type", "Authorization", "Accept"],
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

# === USER ENDPOINTS ===

@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    """Create a new user directly in the endpoint"""
    db = SessionLocal()
    try:
        new_user = User(
            email=user.email,
            full_name=user.full_name,
            role=user.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    finally:
        db.close()

@app.get("/users")
def list_users():
    """List all users directly in the endpoint"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return users
    finally:
        db.close()

@app.get("/users/{user_id}")
def get_user(user_id: UUID):
    """Get user details directly in the endpoint"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        db.close()

@app.patch("/users/{user_id}")
def update_user(
    user_id: UUID,
    payload: UserUpdate
):
    """Update user information"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update fields
        for key, value in payload.dict(exclude_unset=True).items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()

# === DOCUMENT ENDPOINTS ===

@app.post("/documents")
def create_document(doc: DocumentCreate):
    """Create a new document directly in the endpoint"""
    db = SessionLocal()
    try:
        if doc.status not in DocumentStatus.__members__.values():
            raise HTTPException(status_code=400, detail="Invalid document status")
        new_doc = Document(
            title=doc.title,
            description=doc.description,
            status=doc.status
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        return new_doc
    finally:
        db.close()

@app.get("/documents")
def list_documents(status: Optional[DocumentStatus] = None):
    """List all documents directly in the endpoint"""
    db = SessionLocal()
    try:
        query = db.query(Document)
        if status:
            query = query.filter(Document.status == status.value)
        documents = query.all()
        return documents
    finally:
        db.close()

@app.get("/documents/{document_id}")
def get_document(
    document_id: UUID
):
    """Get document details directly in the endpoint"""
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    finally:
        db.close()

@app.patch("/documents/{document_id}")
def update_document(
    document_id: UUID,
    payload: DocumentUpdate
):
    """Update document metadata with validation"""
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Update fields
        for key, value in payload.dict(exclude_unset=True).items():
            setattr(document, key, value)

        db.commit()
        db.refresh(document)
        return document
    finally:
        db.close()

@app.patch("/documents/{document_id}/archive")
def archive_document(
    document_id: UUID
):
    """Archive a document and remove from RAG"""
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Update status to archived
        document.status = "archived"
        db.commit()
        db.refresh(document)

        # Remove from RAG
        delete_from_rag(str(document_id))

        return document
    finally:
        db.close()

# === VERSION ENDPOINTS ===

@app.post("/versions")
def create_version(
    version: VersionCreate,
    background_tasks: BackgroundTasks
):
    """Create a new document version"""
    db = SessionLocal()
    try:
        # Get the document
        doc = db.query(Document).filter(Document.id == version.document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Create version
        db_version = DocumentVersion(
            document_id=doc.id,
            version_number=version.version_number,
            markdown_content=version.markdown_content,
            pdf_url=version.pdf_url,
            created_by=version.created_by
        )
        db.add(db_version)
        db.commit()
        db.refresh(db_version)

        # Index in RAG (background)
        if db_version.markdown_content:
            background_tasks.add_task(
                add_to_rag,
                str(version.document_id),
                str(db_version.id),
                doc.title,
                db_version.markdown_content
            )

        return db_version
    finally:
        db.close()

@app.get("/documents/{document_id}/versions")
def list_versions(
    document_id: UUID
):
    """List all versions for a document"""
    db = SessionLocal()
    try:
        versions = db.query(DocumentVersion).filter(DocumentVersion.document_id == document_id).all()
        return versions
    finally:
        db.close()

# === PDF UPLOAD ENDPOINTS ===

@app.post("/documents/{document_id}/upload-pdf")
async def upload_pdf_version(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    created_by: UUID = Form(...),
    pdf_file: UploadFile = File(...),
    change_summary: Optional[str] = Form(None)
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
    db = SessionLocal()
    try:
        # Verify document exists
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await pdf_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        try:
            # Process PDF: convert to markdown and upload to storage
            markdown_content, pdf_url = process_pdf_upload(
                pdf_path=tmp_path,
                document_id=str(document_id),
                filename=pdf_file.filename,
            )

            # Get next version number
            latest_version = (
                db.query(DocumentVersion)
                .filter(DocumentVersion.document_id == document_id)
                .order_by(DocumentVersion.version_number.desc())
                .first()
            )
            version_number = (latest_version.version_number + 1) if latest_version else 1

            # Get old version ID before updating
            old_version_id = str(doc.current_version_id) if doc.current_version_id else None

            # Create version
            db_version = DocumentVersion(
                document_id=document_id,
                created_by=created_by,
                version_number=version_number,
                markdown_content=markdown_content,
                pdf_url=pdf_url,
                change_summary=change_summary or f"Version {version_number} - PDF upload",
            )
            db.add(db_version)
            db.commit()
            db.refresh(db_version)

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
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    finally:
        db.close()

@app.post("/documents/create-from-pdf")
async def create_document_from_pdf(
    background_tasks: BackgroundTasks,
    created_by: UUID = Form(...),
    pdf_file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """
    Create a new document directly from a PDF upload.

    This endpoint:
    1. Creates a new document
    2. Uploads and processes the PDF
    3. Creates the first version
    4. Indexes in RAG
    """
    db = SessionLocal()
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == created_by).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Use filename as title if not provided
        if not title:
            title = os.path.splitext(pdf_file.filename)[0]

        # Create new document
        new_doc = Document(
            created_by=created_by,
            title=title,
            description=description,
            status="active"
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await pdf_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        try:
            # Process PDF: convert to markdown and upload to storage
            markdown_content, pdf_url = process_pdf_upload(
                pdf_path=tmp_path,
                document_id=str(new_doc.id),
                filename=pdf_file.filename,
            )

            # Create first version
            db_version = DocumentVersion(
                document_id=new_doc.id,
                created_by=created_by,
                version_number=1,
                markdown_content=markdown_content,
                pdf_url=pdf_url,
                change_summary="Initial version from PDF upload",
            )
            db.add(db_version)
            db.commit()
            db.refresh(db_version)

            # Update document's current version
            new_doc.current_version_id = db_version.id
            db.commit()

            # Index in RAG (background)
            background_tasks.add_task(
                add_to_rag,
                str(new_doc.id),
                str(db_version.id),
                new_doc.title,
                db_version.markdown_content
            )

            return {
                "message": "Document created successfully from PDF",
                "document": {
                    "id": str(new_doc.id),
                    "title": new_doc.title,
                    "created_at": new_doc.created_at
                },
                "version": {
                    "id": str(db_version.id),
                    "version_number": db_version.version_number,
                    "pdf_url": db_version.pdf_url
                }
            }
        except Exception as e:
            # Rollback document creation if PDF processing fails
            db.delete(new_doc)
            db.commit()
            raise HTTPException(
                status_code=500, detail=f"Failed to process PDF: {str(e)}"
            )
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    finally:
        db.close()

# === PERMISSION ENDPOINTS ===

@app.post("/permissions")
def grant_permission(perm: PermissionCreate):
    """Grant a permission to a user for a document"""
    db = SessionLocal()
    try:
        # Verify document exists
        document = db.query(Document).filter(Document.id == perm.document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Verify user exists
        user = db.query(User).filter(User.id == perm.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if permission already exists
        existing = (
            db.query(DocumentPermission)
            .filter(
                DocumentPermission.document_id == perm.document_id,
                DocumentPermission.user_id == perm.user_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(status_code=400, detail="Permission already exists")

        # Validate permission type using enum
        if perm.permission_type not in [PermissionType.READ, PermissionType.WRITE, PermissionType.ADMIN]:
            raise HTTPException(status_code=400, detail="Invalid permission type")

        # Create permission
        db_perm = DocumentPermission(
            document_id=perm.document_id,
            user_id=perm.user_id,
            permission_type=perm.permission_type.value  # Use enum value
        )
        db.add(db_perm)
        db.commit()
        db.refresh(db_perm)
        return db_perm
    finally:
        db.close()

@app.get("/documents/{document_id}/permissions")
def list_permissions(document_id: UUID):
    """List all permissions for a document"""
    db = SessionLocal()
    try:
        # Verify document exists
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        permissions = (
            db.query(DocumentPermission)
            .filter(DocumentPermission.document_id == document_id)
            .all()
        )
        return permissions
    finally:
        db.close()

@app.patch("/permissions/{permission_id}")
def update_permission(permission_id: UUID, update_data: PermissionUpdate):
    """Update a permission (change permission type)"""
    db = SessionLocal()
    try:
        perm = db.query(DocumentPermission).filter(DocumentPermission.id == permission_id).first()
        if not perm:
            raise HTTPException(status_code=404, detail="Permission not found")

        # Validate permission type using enum
        if update_data.permission_type not in [PermissionType.READ, PermissionType.WRITE, PermissionType.ADMIN]:
            raise HTTPException(status_code=400, detail="Invalid permission type")

        # Update permission type
        perm.permission_type = update_data.permission_type.value
        db.commit()
        db.refresh(perm)
        return perm
    finally:
        db.close()

@app.delete("/permissions/{permission_id}")
def revoke_permission(permission_id: UUID):
    """Revoke a permission"""
    db = SessionLocal()
    try:
        perm = db.query(DocumentPermission).filter(DocumentPermission.id == permission_id).first()
        if not perm:
            raise HTTPException(status_code=404, detail="Permission not found")

        db.delete(perm)
        db.commit()
        return {"message": "Permission revoked successfully"}
    finally:
        db.close()

# === RAG/SEARCH ENDPOINTS ===

@app.post("/search")
def search_documents(search: RAGSearch):
    """
    Search documents using RAG (Retrieval-Augmented Generation).
    Only searches documents the authenticated user has permission to access.
    """
    db = SessionLocal()
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == search.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {search.user_id} not found")

        # Get user's accessible documents
        permissions = (
            db.query(DocumentPermission)
            .filter(DocumentPermission.user_id == search.user_id)
            .all()
        )
        accessible_docs = [str(perm.document_id) for perm in permissions]

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
    finally:
        db.close()

@app.post("/agent/query", response_model=AgentResponse)
async def agent_query(request: AgentQuery):
    """
    Query the AI agent about documents.
    Agent uses RAG to search and analyze documents the authenticated user has access to.
    """
    from ai_agent import run_agent

    db = SessionLocal()
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {request.user_id} not found")

        # Run agent with user context
        response = await run_agent(request.user_id, user.email, request.query)
        return AgentResponse(response=response)
    finally:
        db.close()

@app.get("/")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
