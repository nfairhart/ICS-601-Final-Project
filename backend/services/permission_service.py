"""Permission service for managing document access control"""

from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from fastapi import HTTPException

from ..models import Document, DocumentPermission, User
from ..schemas import PermissionCreate, PermissionUpdate
from .base import BaseService


class PermissionService(BaseService[DocumentPermission]):
    """Service for document permission management"""

    def __init__(self, db: Session):
        super().__init__(db, DocumentPermission)

    def grant_permission(self, perm_data: PermissionCreate) -> DocumentPermission:
        """
        Grant a permission to a user for a document.

        Args:
            perm_data: Permission creation data

        Returns:
            The created permission

        Raises:
            HTTPException: 404 if document or user not found
            HTTPException: 400 if permission already exists
        """
        # Verify document exists
        document = (
            self.db.query(Document).filter(Document.id == perm_data.document_id).first()
        )
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Verify user exists
        user = self.db.query(User).filter(User.id == perm_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if permission already exists
        existing = (
            self.db.query(DocumentPermission)
            .filter(
                DocumentPermission.document_id == perm_data.document_id,
                DocumentPermission.user_id == perm_data.user_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(status_code=400, detail="Permission already exists")

        # Create permission
        db_perm = DocumentPermission(**perm_data.model_dump())
        return self.create(db_perm)

    def get_document_permissions(self, document_id: UUID) -> list[DocumentPermission]:
        """
        Get all permissions for a document.

        Args:
            document_id: The document ID

        Returns:
            List of permissions

        Raises:
            HTTPException: 404 if document not found
        """
        # Verify document exists
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        return (
            self.db.query(DocumentPermission)
            .filter(DocumentPermission.document_id == document_id)
            .all()
        )

    def get_user_permissions(self, user_id: UUID) -> list[DocumentPermission]:
        """
        Get all permissions for a user.

        Args:
            user_id: The user ID

        Returns:
            List of permissions
        """
        return (
            self.db.query(DocumentPermission)
            .filter(DocumentPermission.user_id == user_id)
            .all()
        )

    def get_user_accessible_documents(self, user_id: UUID) -> list[str]:
        """
        Get list of document IDs accessible to a user.

        This is a convenience method for RAG search filtering.

        Args:
            user_id: The user ID

        Returns:
            List of document ID strings
        """
        permissions = self.get_user_permissions(user_id)
        return [str(perm.document_id) for perm in permissions]

    def revoke_permission(self, permission_id: UUID) -> dict:
        """
        Revoke a permission.

        Args:
            permission_id: The permission ID to revoke

        Returns:
            Status dict

        Raises:
            HTTPException: 404 if permission not found
        """
        perm = self.get_or_404(permission_id, "Permission not found")
        self.delete(perm)
        return {"status": "revoked"}

    def update_permission(
        self, permission_id: UUID, update_data: PermissionUpdate
    ) -> DocumentPermission:
        """
        Update a permission (typically to change permission type).

        Args:
            permission_id: The permission ID
            update_data: Fields to update

        Returns:
            The updated permission

        Raises:
            HTTPException: 404 if permission not found
        """
        perm = self.get_or_404(permission_id, "Permission not found")

        # Update fields
        data = update_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(perm, key, value)

        self.commit()
        self.db.refresh(perm)
        return perm

    def check_user_access(
        self, user_id: UUID, document_id: UUID, required_permission: Optional[str] = None
    ) -> bool:
        """
        Check if a user has access to a document.

        Args:
            user_id: The user ID
            document_id: The document ID
            required_permission: Optional specific permission type required (e.g., "write", "admin")

        Returns:
            True if user has access, False otherwise
        """
        permission = (
            self.db.query(DocumentPermission)
            .filter(
                DocumentPermission.document_id == document_id,
                DocumentPermission.user_id == user_id,
            )
            .first()
        )

        if not permission:
            return False

        # If specific permission level required, check it
        if required_permission:
            # Define permission hierarchy: admin > write > read
            hierarchy = {"read": 0, "write": 1, "admin": 2}
            user_level = hierarchy.get(permission.permission_type, -1)
            required_level = hierarchy.get(required_permission, 0)
            return user_level >= required_level

        return True

    def require_document_access(
        self, user_id: UUID, document_id: UUID, required_permission: Optional[str] = None
    ) -> DocumentPermission:
        """
        Verify user has access to a document, raise exception if not.

        This is a convenience method for route handlers.

        Args:
            user_id: The user ID
            document_id: The document ID
            required_permission: Optional specific permission type required

        Returns:
            The permission object

        Raises:
            HTTPException: 403 if user doesn't have required access
        """
        permission = (
            self.db.query(DocumentPermission)
            .filter(
                DocumentPermission.document_id == document_id,
                DocumentPermission.user_id == user_id,
            )
            .first()
        )

        if not permission:
            raise HTTPException(
                status_code=403,
                detail=f"You don't have access to document {document_id}",
            )

        # Check permission level if specified
        if required_permission:
            hierarchy = {"read": 0, "write": 1, "admin": 2}
            user_level = hierarchy.get(permission.permission_type, -1)
            required_level = hierarchy.get(required_permission, 0)

            if user_level < required_level:
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Required: {required_permission}",
                )

        return permission
