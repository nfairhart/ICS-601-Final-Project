# filepath: /Users/nicholasfairhart/Documents/GitHub/ICS-601-Final-Project/backend/main.py
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from uuid import UUID

from database import SessionLocal, User, Document, DocumentPermission
from ai_agent import run_agent
from rag import add_document_to_rag, delete_document_from_rag, search_rag

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== User & Document Management ====================

class UserCreate(BaseModel):
    """Data for creating a new user"""
    email: str
    password: str

class UserResponse(BaseModel):
    """User data response"""
    id: UUID
    email: str

class DocumentCreate(BaseModel):
    """Data for creating a new document"""
    title: str
    description: str

class DocumentResponse(BaseModel):
    """Document data response"""
    id: UUID
    title: str
    description: str
    status: str

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user in the system.
    """
    db_user = User(email=user.email)
    db_user.set_password(user.password)  # Assuming User model has this method
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/documents/", response_model=DocumentResponse)
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    """
    Create a new document.
    """
    db_document = Document(
        title=document.title,
        description=document.description,
        status="active",  # default status
        creator_id=1  # TODO: replace with actual creator ID
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

# ==================== RAG & AI Agent Endpoints ====================

class AgentQuery(BaseModel):
    """Query for AI agent"""
    query: str

@app.post("/agent/query")
async def agent_query(
    agent_request: AgentQuery,
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Query the AI agent about documents.
    Agent uses RAG to search and analyze documents the user has access to.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        response = await run_agent(user_id, user.email, agent_request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/{document_id}/index-rag")
def index_document_in_rag(
    document_id: UUID,
    version_id: Optional[UUID] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Index a document or specific version in RAG database.
    Call this after uploading a document version.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    from models import DocumentVersion
    
    if version_id:
        version = db.query(DocumentVersion).filter(
            DocumentVersion.id == version_id,
            DocumentVersion.document_id == document_id
        ).first()
        if not version:
            raise HTTPException(status_code=404, detail="Version not found")
        versions_to_index = [version]
    else:
        versions_to_index = db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id
        ).all()
    
    def index_versions():
        for version in versions_to_index:
            # In real scenario, you'd read from Supabase or file system
            # For now, using version metadata as content
            content = f"{document.title}\n\n{document.description}\n\nVersion: {version.version_number}"
            
            add_document_to_rag(
                document_id=str(document_id),
                version_id=str(version.id),
                title=document.title,
                content=content,
                metadata={
                    "description": document.description,
                    "status": document.status,
                    "version_number": version.version_number
                }
            )
    
    if background_tasks:
        background_tasks.add_task(index_versions)
    else:
        index_versions()
    
    return {
        "status": "indexing",
        "document_id": str(document_id),
        "versions_indexed": len(versions_to_index)
    }

@app.delete("/documents/{document_id}/remove-rag")
def remove_document_from_rag(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Remove document from RAG database when archived/deleted.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    delete_document_from_rag(str(document_id))
    
    return {
        "status": "removed",
        "document_id": str(document_id)
    }

class RAGSearchRequest(BaseModel):
    """Direct RAG search request"""
    query: str
    top_k: int = 5

@app.post("/search/documents")
def search_documents(
    search_request: RAGSearchRequest,
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Direct search of documents using RAG (without AI agent).
    Returns raw search results.
    """
    # Get user's accessible documents
    permissions = db.query(DocumentPermission).filter(
        DocumentPermission.user_id == user_id
    ).all()
    
    accessible_doc_ids = [str(perm.document_id) for perm in permissions]
    
    results = search_rag(
        query=search_request.query,
        user_accessible_docs=accessible_doc_ids,
        top_k=search_request.top_k
    )
    
    return {
        "query": search_request.query,
        "results": results,
        "total_found": len(results)
    }