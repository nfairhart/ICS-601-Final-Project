"""Version service for managing document versions and PDF uploads"""

from sqlalchemy.orm import Session
from typing import Optional, Tuple
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, UploadFile
import tempfile
import os

from ..models import Document, DocumentVersion, User
from ..schemas import VersionCreate
from .base import BaseService


class VersionService(BaseService[DocumentVersion]):
    """Service for document version management"""

    def __init__(self, db: Session):
        super().__init__(db, DocumentVersion)

    def create_version(
        self, version_data: VersionCreate, document: Document
    ) -> Tuple[DocumentVersion, Optional[str]]:
        """
        Create a new document version and update the document's current version.

        Args:
            version_data: Version creation data
            document: The document to add the version to

        Returns:
            Tuple of (new_version, old_version_id)
        """
        # Create the version
        db_version = DocumentVersion(**version_data.model_dump())
        self.create(db_version)

        # Get the old version ID before updating
        old_version_id = str(document.current_version_id) if document.current_version_id else None

        # Update document's current version
        document.current_version_id = db_version.id
        document.updated_at = datetime.utcnow()
        self.commit()

        return db_version, old_version_id

    def get_document_versions(self, document_id: UUID) -> list[DocumentVersion]:
        """
        Get all versions for a document, ordered by version number descending.

        Args:
            document_id: The document ID

        Returns:
            List of versions
        """
        return (
            self.db.query(DocumentVersion)
            .filter(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
            .all()
        )

    def get_next_version_number(self, document_id: UUID) -> int:
        """
        Get the next version number for a document.

        Args:
            document_id: The document ID

        Returns:
            The next version number (1 if no versions exist)
        """
        latest_version = (
            self.db.query(DocumentVersion)
            .filter(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
            .first()
        )

        return (latest_version.version_number + 1) if latest_version else 1

    async def create_version_from_pdf(
        self,
        document: Document,
        pdf_file: UploadFile,
        created_by: UUID,
        change_summary: Optional[str] = None,
    ) -> Tuple[DocumentVersion, Optional[str]]:
        """
        Create a new document version from a PDF upload.

        This method:
        1. Saves the PDF to a temp file
        2. Converts it to markdown
        3. Uploads to storage
        4. Creates the version
        5. Updates the document
        6. Returns version and old version ID for RAG indexing

        Args:
            document: The document to add the version to
            pdf_file: The uploaded PDF file
            created_by: User ID creating the version
            change_summary: Optional description of changes

        Returns:
            Tuple of (new_version, old_version_id)

        Raises:
            HTTPException: If PDF processing fails
        """
        from ..utils import process_pdf_upload

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await pdf_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        try:
            # Process PDF: convert to markdown and upload to storage
            markdown_content, pdf_url = process_pdf_upload(
                pdf_path=tmp_path,
                document_id=str(document.id),
                filename=pdf_file.filename,
            )

            # Get next version number
            version_number = self.get_next_version_number(document.id)

            # Create version data
            version_data = VersionCreate(
                document_id=document.id,
                created_by=created_by,
                version_number=version_number,
                markdown_content=markdown_content,
                pdf_url=pdf_url,
                change_summary=change_summary or f"Version {version_number} - PDF upload",
            )

            # Create the version using the base method
            return self.create_version(version_data, document)

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    async def create_document_with_pdf(
        self,
        pdf_file: UploadFile,
        created_by: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Tuple[Document, DocumentVersion]:
        """
        Create a new document directly from a PDF upload.

        This is a convenience method that combines document creation
        and first version creation in one operation.

        Args:
            pdf_file: The uploaded PDF file
            created_by: User ID creating the document
            title: Document title (defaults to filename)
            description: Optional document description

        Returns:
            Tuple of (document, version)

        Raises:
            HTTPException: If user not found or PDF processing fails
        """
        from ..utils import process_pdf_upload

        # Verify user exists
        user = self.db.query(User).filter(User.id == created_by).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Use filename as title if not provided
        if not title:
            title = os.path.splitext(pdf_file.filename)[0]

        # Create document first
        db_doc = Document(
            created_by=created_by,
            title=title,
            description=description,
            status="Draft",
        )
        self.db.add(db_doc)
        self.db.commit()
        self.db.refresh(db_doc)

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await pdf_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        try:
            # Process PDF
            markdown_content, pdf_url = process_pdf_upload(
                pdf_path=tmp_path,
                document_id=str(db_doc.id),
                filename=pdf_file.filename,
            )

            # Create first version
            db_version = DocumentVersion(
                document_id=db_doc.id,
                created_by=created_by,
                version_number=1,
                markdown_content=markdown_content,
                pdf_url=pdf_url,
                change_summary="Initial version from PDF upload",
            )

            self.db.add(db_version)
            self.db.commit()
            self.db.refresh(db_version)

            # Update document's current version
            db_doc.current_version_id = db_version.id
            self.db.commit()

            return db_doc, db_version

        except Exception as e:
            # Rollback document creation if PDF processing fails
            self.db.delete(db_doc)
            self.db.commit()
            raise HTTPException(
                status_code=500, detail=f"Failed to process PDF: {str(e)}"
            )

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
