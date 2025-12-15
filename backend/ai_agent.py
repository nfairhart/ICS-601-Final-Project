"""PydanticAI-powered document assistant agent."""
import os
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.tools import Tool
from dotenv import load_dotenv

from .database import SessionLocal
from .models import User, Document, DocumentPermission, DocumentVersion
from .rag import search_rag

load_dotenv()

# Initialize agent with OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

agent = Agent(
    model="openai:gpt-4o-mini",
    system_prompt="""You are a helpful document assistant. 
You help users find, understand, and analyze documents from their database.
Use the available tools to search documents and retrieve information.
Always cite which documents you're referencing in your responses.
Be accurate and concise in your answers.""",
)


class AgentContext(BaseModel):
    """Context passed to agent tools."""
    user_id: UUID
    user_email: str
    accessible_doc_ids: list[str]


class DocumentSearchInput(BaseModel):
    """Input for document search."""
    query: str
    top_k: int = 5


class DocumentListInput(BaseModel):
    """Input for listing documents."""
    limit: int = 10


@agent.tool
def search_documents(ctx: RunContext[AgentContext], query: str, top_k: int = 5) -> str:
    """
    Search documents by query using RAG.
    Returns relevant document excerpts based on semantic similarity.
    Only searches documents the user has access to.
    """
    try:
        results = search_rag(
            query=query,
            user_accessible_docs=ctx.state.accessible_doc_ids,
            top_k=top_k,
            min_relevance=0.2
        )
        
        if not results:
            return f"No documents found matching '{query}'."
        
        response = f"Found {len(results)} relevant documents:\n\n"
        for i, result in enumerate(results, 1):
            score = result.relevance_score
            preview = result.content[:200] + "..." if len(result.content) > 200 else result.content
            response += f"{i}. **{result.title}** (Relevance: {score:.2f})\n   {preview}\n\n"
        
        return response
    except Exception as e:
        return f"Error searching documents: {str(e)}"


@agent.tool
def list_user_documents(ctx: RunContext[AgentContext], limit: int = 10) -> str:
    """List documents accessible to the current user."""
    db = SessionLocal()
    try:
        permissions = db.query(DocumentPermission).filter(
            DocumentPermission.user_id == ctx.state.user_id
        ).limit(limit).all()
        
        if not permissions:
            return "You don't have access to any documents yet."
        
        docs = db.query(Document).filter(
            Document.id.in_([p.document_id for p in permissions])
        ).all()
        
        response = f"You have access to {len(docs)} document(s):\n\n"
        for doc in docs:
            response += f"- **{doc.title}** (Status: {doc.status})\n"
            if doc.description:
                response += f"  {doc.description}\n"
        
        return response
    except Exception as e:
        return f"Error listing documents: {str(e)}"
    finally:
        db.close()


@agent.tool
def get_document_info(ctx: RunContext[AgentContext], document_id: str) -> str:
    """Get detailed information about a specific document."""
    db = SessionLocal()
    try:
        # Check if user has access
        permission = db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == ctx.state.user_id
        ).first()
        
        if not permission:
            return f"You don't have access to document {document_id}."
        
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return f"Document {document_id} not found."
        
        versions = db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id
        ).order_by(DocumentVersion.version_number.desc()).all()
        
        response = f"""
**{doc.title}**
Status: {doc.status}
Description: {doc.description or 'N/A'}
Created: {doc.created_at}
Updated: {doc.updated_at}

Versions: {len(versions)}
"""
        return response
    except Exception as e:
        return f"Error retrieving document info: {str(e)}"
    finally:
        db.close()


async def run_agent(user_id: UUID, user_email: str, query: str) -> str:
    """
    Run the AI agent with user context.
    Returns the agent's response to the user's query.
    """
    db = SessionLocal()
    try:
        # Get user's accessible documents
        permissions = db.query(DocumentPermission).filter(
            DocumentPermission.user_id == user_id
        ).all()
        
        accessible_doc_ids = [str(perm.document_id) for perm in permissions]
        
        if not accessible_doc_ids:
            return "You don't have access to any documents. Ask an admin to grant you permissions."
        
        # Create agent context
        ctx = AgentContext(
            user_id=user_id,
            user_email=user_email,
            accessible_doc_ids=accessible_doc_ids
        )
        
        # Run agent
        result = await agent.run(
            user_message=query,
            state=ctx
        )
        
        return result.data
        
    finally:
        db.close()
