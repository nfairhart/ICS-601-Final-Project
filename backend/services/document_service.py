"""Document service for managing document operations"""

from sqlalchemy.orm import Session, joinedload
from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException

from ..models import Document, User
from ..schemas import DocumentCreate, DocumentUpdate, DocumentStatus
from .base import BaseService


class DocumentService(BaseService[Document]):
    """Service for document management operations"""

    def __init__(self, db: Session):
        super().__init__(db, Document)

    def create_document(self, doc_data: DocumentCreate) -> Document:
        """
        Create a new document.

        Args:
            doc_data: Document creation data

        Returns:
            The created document

        Raises:
            HTTPException: 404 if user not found
        """
        # Verify user exists
        user = self.db.query(User).filter(User.id == doc_data.created_by).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create document
        db_doc = Document(**doc_data.model_dump())
        return self.create(db_doc)

    def get_document_with_relations(self, document_id: UUID) -> Document:
        """
        Get a document with all its relationships loaded.

        Args:
            document_id: The document ID

        Returns:
            Document with creator, versions, and permissions loaded

        Raises:
            HTTPException: 404 if document not found
        """
        doc = (
            self.db.query(Document)
            .options(
                joinedload(Document.creator),
                joinedload(Document.versions),
                joinedload(Document.permissions),
            )
            .filter(Document.id == document_id)
            .first()
        )

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc

    def update_document(
        self, document_id: UUID, update_data: DocumentUpdate
    ) -> Document:
        """
        Update document metadata.

        Args:
            document_id: The document ID
            update_data: Fields to update

        Returns:
            The updated document

        Raises:
            HTTPException: 404 if document not found
        """
        doc = self.get_or_404(document_id)

        # Update only provided fields
        data = update_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            if key == "status" and isinstance(value, DocumentStatus):
                setattr(doc, key, value.value)
            else:
                setattr(doc, key, value)

        doc.updated_at = datetime.utcnow()
        self.commit()
        self.db.refresh(doc)
        return doc

    def archive_document(self, document_id: UUID) -> Document:
        """
        Archive a document.

        Args:
            document_id: The document ID

        Returns:
            The archived document

        Raises:
            HTTPException: 404 if document not found
        """
        doc = self.get_or_404(document_id)

        doc.status = DocumentStatus.ARCHIVED.value
        doc.updated_at = datetime.utcnow()
        self.commit()

        return doc

    def list_documents(
        self, status: Optional[DocumentStatus] = None
    ) -> list[Document]:
        """
        List all documents with optional status filter.

        Args:
            status: Optional status to filter by

        Returns:
            List of documents
        """
        query = self.db.query(Document)
        if status:
            query = query.filter(Document.status == status.value)
        return query.all()
