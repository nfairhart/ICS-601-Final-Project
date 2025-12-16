"""PydanticAI-powered document assistant agent with expanded tools."""
import os
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv

from .database import SessionLocal
from .models import User, Document, DocumentPermission, DocumentVersion
from .rag import (
    search_rag, 
    get_document_content, 
    get_similar_documents
)

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
Be accurate and concise in your answers.

When asked to summarize or analyze documents, provide clear, structured responses.
If a user asks about multiple documents, compare and contrast them.
Always respect document permissions - only access documents the user has permission to view.""",
)


class AgentContext(BaseModel):
    """Context passed to agent tools."""
    user_id: UUID
    user_email: str
    accessible_doc_ids: list[str]


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
            user_accessible_docs=ctx.deps.accessible_doc_ids,
            top_k=top_k,
            min_relevance=0.2
        )
        
        if not results:
            return f"No documents found matching '{query}'."
        
        response = f"Found {len(results)} relevant documents:\n\n"
        for i, result in enumerate(results, 1):
            score = result['relevance_score']
            preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            response += f"{i}. **{result['title']}** (Relevance: {score:.2f})\n"
            response += f"   Document ID: {result['document_id']}\n"
            response += f"   {preview}\n\n"
        
        return response
    except Exception as e:
        return f"Error searching documents: {str(e)}"


@agent.tool
def list_user_documents(ctx: RunContext[AgentContext], limit: int = 10) -> str:
    """List documents accessible to the current user with summary information."""
    db = SessionLocal()
    try:
        permissions = db.query(DocumentPermission).filter(
            DocumentPermission.user_id == ctx.deps.user_id
        ).limit(limit).all()
        
        if not permissions:
            return "You don't have access to any documents yet."
        
        docs = db.query(Document).filter(
            Document.id.in_([p.document_id for p in permissions])
        ).all()
        
        response = f"You have access to {len(docs)} document(s):\n\n"
        for doc in docs:
            response += f"- **{doc.title}** (ID: {doc.id})\n"
            response += f"  Status: {doc.status}\n"
            if doc.description:
                response += f"  Description: {doc.description}\n"
            response += "\n"
        
        return response
    except Exception as e:
        return f"Error listing documents: {str(e)}"
    finally:
        db.close()


@agent.tool
def get_document_info(ctx: RunContext[AgentContext], document_id: str) -> str:
    """Get detailed information about a specific document including version history."""
    db = SessionLocal()
    try:
        # Check if user has access
        permission = db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == ctx.deps.user_id
        ).first()
        
        if not permission:
            return f"You don't have access to document {document_id}."
        
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return f"Document {document_id} not found."
        
        versions = db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id
        ).order_by(DocumentVersion.version_number.desc()).all()
        
        response = f"""**{doc.title}**

Status: {doc.status}
Description: {doc.description or 'N/A'}
Created: {doc.created_at}
Updated: {doc.updated_at}

Version History ({len(versions)} versions):
"""
        for v in versions:
            response += f"\n- Version {v.version_number}"
            if v.change_summary:
                response += f": {v.change_summary}"
            response += f" (Created: {v.created_at})"
        
        return response
    except Exception as e:
        return f"Error retrieving document info: {str(e)}"
    finally:
        db.close()


@agent.tool
def get_full_document_content(ctx: RunContext[AgentContext], document_id: str) -> str:
    """
    Retrieve the full content of a document for detailed analysis.
    Use this when you need to analyze or summarize the complete document.
    """
    db = SessionLocal()
    try:
        # Check if user has access
        permission = db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == ctx.deps.user_id
        ).first()
        
        if not permission:
            return f"You don't have access to document {document_id}."
        
        # Get document metadata
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return f"Document {document_id} not found."
        
        # Get content from RAG
        content = get_document_content(document_id)
        if not content:
            return f"Document content not available for {doc.title}. It may not have been indexed yet."
        
        response = f"""**{doc.title}**

Full Content:
{content['content']}

---
Document ID: {document_id}
Status: {doc.status}
"""
        return response
    except Exception as e:
        return f"Error retrieving document content: {str(e)}"
    finally:
        db.close()


@agent.tool
def summarize_document(ctx: RunContext[AgentContext], document_id: str, max_length: int = 200) -> str:
    """
    Generate a concise summary of a document.
    Returns key points and main themes from the document.
    """
    db = SessionLocal()
    try:
        # Check if user has access
        permission = db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == ctx.deps.user_id
        ).first()
        
        if not permission:
            return f"You don't have access to document {document_id}."
        
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return f"Document {document_id} not found."
        
        # Get content from RAG
        content = get_document_content(document_id)
        if not content:
            return f"Cannot summarize {doc.title} - content not available."
        
        # Return content for the LLM to summarize
        # The agent will use its own capabilities to create the summary
        full_text = content['content']
        preview = full_text[:max_length * 5]  # Give more context for better summary
        
        return f"""Document to summarize: **{doc.title}**

Content excerpt (for summarization):
{preview}{'...' if len(full_text) > len(preview) else ''}

Please provide a concise summary of the key points from this document."""
        
    except Exception as e:
        return f"Error summarizing document: {str(e)}"
    finally:
        db.close()


@agent.tool
def find_related_documents(ctx: RunContext[AgentContext], document_id: str, top_k: int = 3) -> str:
    """
    Find documents similar to the given document based on content similarity.
    Useful for discovering related materials.
    """
    db = SessionLocal()
    try:
        # Check if user has access to the reference document
        permission = db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == ctx.deps.user_id
        ).first()
        
        if not permission:
            return f"You don't have access to document {document_id}."
        
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return f"Document {document_id} not found."
        
        # Find similar documents
        similar = get_similar_documents(
            document_id=document_id,
            top_k=top_k,
            accessible_docs=ctx.deps.accessible_doc_ids
        )
        
        if not similar:
            return f"No related documents found for '{doc.title}'."
        
        response = f"Documents related to **{doc.title}**:\n\n"
        for i, result in enumerate(similar, 1):
            score = result['relevance_score']
            preview = result['content'][:150] + "..." if len(result['content']) > 150 else result['content']
            response += f"{i}. **{result['title']}** (Similarity: {score:.2f})\n"
            response += f"   Document ID: {result['document_id']}\n"
            response += f"   {preview}\n\n"
        
        return response
    except Exception as e:
        return f"Error finding related documents: {str(e)}"
    finally:
        db.close()


@agent.tool
def compare_documents(ctx: RunContext[AgentContext], document_id_1: str, document_id_2: str) -> str:
    """
    Compare two documents side by side.
    Retrieves content from both documents for comparison.
    """
    db = SessionLocal()
    try:
        # Check access to both documents
        perm1 = db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id_1,
            DocumentPermission.user_id == ctx.deps.user_id
        ).first()
        
        perm2 = db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id_2,
            DocumentPermission.user_id == ctx.deps.user_id
        ).first()
        
        if not perm1:
            return f"You don't have access to document {document_id_1}."
        if not perm2:
            return f"You don't have access to document {document_id_2}."
        
        # Get both documents
        doc1 = db.query(Document).filter(Document.id == document_id_1).first()
        doc2 = db.query(Document).filter(Document.id == document_id_2).first()
        
        if not doc1:
            return f"Document {document_id_1} not found."
        if not doc2:
            return f"Document {document_id_2} not found."
        
        # Get content
        content1 = get_document_content(document_id_1)
        content2 = get_document_content(document_id_2)
        
        response = f"""Comparing two documents:

**Document 1: {doc1.title}**
Status: {doc1.status}
Content preview: {content1['content'][:300] if content1 else 'Content not available'}...

**Document 2: {doc2.title}**
Status: {doc2.status}
Content preview: {content2['content'][:300] if content2 else 'Content not available'}...

Please analyze the similarities and differences between these documents."""
        
        return response
        
    except Exception as e:
        return f"Error comparing documents: {str(e)}"
    finally:
        db.close()


@agent.tool
def extract_key_points(ctx: RunContext[AgentContext], document_id: str, num_points: int = 5) -> str:
    """
    Extract the most important key points and takeaways from a document.
    Returns a bulleted list of main ideas.
    """
    db = SessionLocal()
    try:
        # Check if user has access
        permission = db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == ctx.deps.user_id
        ).first()
        
        if not permission:
            return f"You don't have access to document {document_id}."
        
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return f"Document {document_id} not found."
        
        # Get content from RAG
        content = get_document_content(document_id)
        if not content:
            return f"Cannot extract key points from {doc.title} - content not available."
        
        return f"""Document for key point extraction: **{doc.title}**

Content:
{content['content'][:1000]}{'...' if len(content['content']) > 1000 else ''}

Please extract the {num_points} most important key points from this document."""
        
    except Exception as e:
        return f"Error extracting key points: {str(e)}"
    finally:
        db.close()


@agent.tool
def answer_from_document(ctx: RunContext[AgentContext], document_id: str, question: str) -> str:
    """
    Answer a specific question using information from a particular document.
    Useful for targeted queries about document content.
    """
    db = SessionLocal()
    try:
        # Check if user has access
        permission = db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == ctx.deps.user_id
        ).first()
        
        if not permission:
            return f"You don't have access to document {document_id}."
        
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return f"Document {document_id} not found."
        
        # Get content from RAG
        content = get_document_content(document_id)
        if not content:
            return f"Cannot answer question from {doc.title} - content not available."
        
        return f"""Question: {question}

Document: **{doc.title}**

Content to reference:
{content['content']}

Please answer the question based on the document content above."""
        
    except Exception as e:
        return f"Error answering from document: {str(e)}"
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
            user_prompt=query,
            deps=ctx
        )

        return result.output
        
    finally:
        db.close()