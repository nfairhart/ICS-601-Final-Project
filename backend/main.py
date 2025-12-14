import os
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
from uuid import UUID

# Import your models and schemas
import sys
from pathlib import Path

# Add parent directory to path to import from root
sys.path.append(str(Path(__file__).parent.parent))

from create_schema import Base, User, Document, DocumentVersion, DocumentPermission
from schemas import (
    UserCreate, UserUpdate, UserResponse, UserWithDocuments,
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentWithDetails,
    DocumentVersionCreate, DocumentVersionUpdate, DocumentVersionResponse,
    DocumentPermissionCreate, DocumentPermissionUpdate, DocumentPermissionResponse
)

# Load environment variables
load_dotenv()

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

# Create engine
engine = create_engine(DATABASE_URL, poolclass=NullPool)

# Create FastAPI app
app = FastAPI(title="Document Management API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== User Endpoints ====================

@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all users"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserWithDocuments)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    """Get user by ID with their documents and permissions"""
    user = db.query(User).options(
        joinedload(User.documents),
        joinedload(User.permissions)
    ).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: UUID, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user information"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    """Delete a user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return None

# ==================== Document Endpoints ====================

@app.post("/documents/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    """Create a new document"""
    # Verify user exists
    user = db.query(User).filter(User.id == document.created_by).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_document = Document(**document.model_dump())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@app.get("/documents/", response_model=List[DocumentResponse])
def list_documents(
    skip: int = 0, 
    limit: int = 100, 
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all documents with optional status filter"""
    query = db.query(Document)
    
    if status_filter:
        query = query.filter(Document.status == status_filter)
    
    documents = query.offset(skip).limit(limit).all()
    return documents

@app.get("/documents/{document_id}", response_model=DocumentWithDetails)
def get_document(document_id: UUID, db: Session = Depends(get_db)):
    """Get document by ID with all related information"""
    document = db.query(Document).options(
        joinedload(Document.creator),
        joinedload(Document.versions),
        joinedload(Document.permissions)
    ).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@app.patch("/documents/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: UUID, 
    document_update: DocumentUpdate, 
    db: Session = Depends(get_db)
):
    """Update document information"""
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    update_data = document_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_document, field, value)
    
    db_document.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_document)
    return db_document

@app.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: UUID, db: Session = Depends(get_db)):
    """Delete a document and all its versions"""
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(db_document)
    db.commit()
    return None

@app.get("/users/{user_id}/documents", response_model=List[DocumentResponse])
def get_user_documents(user_id: UUID, db: Session = Depends(get_db)):
    """Get all documents created by a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    documents = db.query(Document).filter(Document.created_by == user_id).all()
    return documents

# ==================== Document Version Endpoints ====================

@app.post("/versions/", response_model=DocumentVersionResponse, status_code=status.HTTP_201_CREATED)
def create_document_version(version: DocumentVersionCreate, db: Session = Depends(get_db)):
    """Create a new document version"""
    # Verify document exists
    document = db.query(Document).filter(Document.id == version.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db_version = DocumentVersion(**version.model_dump())
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    
    # Update document's current_version_id
    document.current_version_id = db_version.id
    document.updated_at = datetime.utcnow()
    db.commit()
    
    return db_version

@app.get("/documents/{document_id}/versions", response_model=List[DocumentVersionResponse])
def get_document_versions(document_id: UUID, db: Session = Depends(get_db)):
    """Get all versions of a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    versions = db.query(DocumentVersion).filter(
        DocumentVersion.document_id == document_id
    ).order_by(DocumentVersion.version_number.desc()).all()
    
    return versions

@app.get("/versions/{version_id}", response_model=DocumentVersionResponse)
def get_version(version_id: UUID, db: Session = Depends(get_db)):
    """Get a specific document version"""
    version = db.query(DocumentVersion).filter(DocumentVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version

@app.patch("/versions/{version_id}", response_model=DocumentVersionResponse)
def update_version(
    version_id: UUID, 
    version_update: DocumentVersionUpdate, 
    db: Session = Depends(get_db)
):
    """Update a document version (e.g., edit markdown content)"""
    db_version = db.query(DocumentVersion).filter(DocumentVersion.id == version_id).first()
    if not db_version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    update_data = version_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_version, field, value)
    
    db.commit()
    db.refresh(db_version)
    return db_version

# ==================== Document Permission Endpoints ====================

@app.post("/permissions/", response_model=DocumentPermissionResponse, status_code=status.HTTP_201_CREATED)
def grant_permission(permission: DocumentPermissionCreate, db: Session = Depends(get_db)):
    """Grant a user permission to a document"""
    # Verify document exists
    document = db.query(Document).filter(Document.id == permission.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Verify user exists
    user = db.query(User).filter(User.id == permission.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if permission already exists
    existing = db.query(DocumentPermission).filter(
        DocumentPermission.document_id == permission.document_id,
        DocumentPermission.user_id == permission.user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Permission already exists")
    
    db_permission = DocumentPermission(**permission.model_dump())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

@app.get("/documents/{document_id}/permissions", response_model=List[DocumentPermissionResponse])
def get_document_permissions(document_id: UUID, db: Session = Depends(get_db)):
    """Get all permissions for a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    permissions = db.query(DocumentPermission).filter(
        DocumentPermission.document_id == document_id
    ).all()
    
    return permissions

@app.patch("/permissions/{permission_id}", response_model=DocumentPermissionResponse)
def update_permission(
    permission_id: UUID, 
    permission_update: DocumentPermissionUpdate, 
    db: Session = Depends(get_db)
):
    """Update a permission (e.g., change from read to write)"""
    db_permission = db.query(DocumentPermission).filter(
        DocumentPermission.id == permission_id
    ).first()
    
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    update_data = permission_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_permission, field, value)
    
    db.commit()
    db.refresh(db_permission)
    return db_permission

@app.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_permission(permission_id: UUID, db: Session = Depends(get_db)):
    """Revoke a user's permission to a document"""
    db_permission = db.query(DocumentPermission).filter(
        DocumentPermission.id == permission_id
    ).first()
    
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    db.delete(db_permission)
    db.commit()
    return None

@app.get("/users/{user_id}/accessible-documents", response_model=List[DocumentResponse])
def get_accessible_documents(user_id: UUID, db: Session = Depends(get_db)):
    """Get all documents a user has permission to access"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get documents where user has explicit permissions
    permissions = db.query(DocumentPermission).filter(
        DocumentPermission.user_id == user_id
    ).all()
    
    document_ids = [p.document_id for p in permissions]
    
    # Also include documents created by the user
    documents = db.query(Document).filter(
        (Document.id.in_(document_ids)) | (Document.created_by == user_id)
    ).all()
    
    return documents

# ==================== Health Check ====================

@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Document Management API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)