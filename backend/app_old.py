from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

from .database import get_db
from .models import User, Document, DocumentVersion, DocumentPermission
from .rag import add_to_rag, search_rag, delete_from_rag

app = FastAPI(title="Document Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None

class DocumentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    created_by: UUID

class VersionCreate(BaseModel):
    document_id: UUID
    version_number: int
    markdown_content: Optional[str] = None
    pdf_url: Optional[str] = None
    change_summary: Optional[str] = None
    created_by: Optional[UUID] = None

class PermissionCreate(BaseModel):
    document_id: UUID
    user_id: UUID
    permission_type: str  # 'read', 'write', 'admin'

class RAGSearch(BaseModel):
    query: str
    user_id: UUID
    top_k: int = 5

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
def list_documents(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Document)
    if status:
        query = query.filter(Document.status == status)
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
def update_document(document_id: UUID, title: Optional[str] = None, 
                    status: Optional[str] = None, description: Optional[str] = None,
                    db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    
    if title:
        doc.title = title
    if status:
        doc.status = status
    if description:
        doc.description = description
    
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
    
    # Update document's current version
    doc.current_version_id = db_version.id
    doc.updated_at = datetime.utcnow()
    db.commit()
    
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

@app.get("/documents/{document_id}/versions")
def list_versions(document_id: UUID, db: Session = Depends(get_db)):
    if not db.query(Document).filter(Document.id == document_id).first():
        raise HTTPException(404, "Document not found")
    
    return db.query(DocumentVersion).filter(
        DocumentVersion.document_id == document_id
    ).order_by(DocumentVersion.version_number.desc()).all()

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
def search_documents(search: RAGSearch, db: Session = Depends(get_db)):
    # Get user's accessible documents
    perms = db.query(DocumentPermission).filter(
        DocumentPermission.user_id == search.user_id
    ).all()
    
    accessible_docs = [str(p.document_id) for p in perms]
    
    results = search_rag(search.query, accessible_docs, search.top_k)
    
    return {
        "query": search.query,
        "results": results,
        "total": len(results)
    }

@app.get("/")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)