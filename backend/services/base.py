"""Base service class with common functionality"""

from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, Optional
from uuid import UUID
from fastapi import HTTPException

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """
    Base service class with common CRUD operations.

    This eliminates repetitive query patterns and provides
    consistent error handling across all services.
    """

    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model

    def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get a model instance by ID, returns None if not found"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_or_404(self, id: UUID, error_message: Optional[str] = None) -> ModelType:
        """
        Get a model instance by ID or raise 404.

        Args:
            id: The UUID to search for
            error_message: Custom error message (defaults to model name)

        Returns:
            The model instance

        Raises:
            HTTPException: 404 if not found
        """
        obj = self.get_by_id(id)
        if not obj:
            message = error_message or f"{self.model.__name__} not found"
            raise HTTPException(status_code=404, detail=message)
        return obj

    def get_all(self, limit: Optional[int] = None) -> list[ModelType]:
        """Get all instances of the model"""
        query = self.db.query(self.model)
        if limit:
            query = query.limit(limit)
        return query.all()

    def create(self, obj: ModelType) -> ModelType:
        """Create a new instance"""
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelType) -> None:
        """Delete an instance"""
        self.db.delete(obj)
        self.db.commit()

    def commit(self) -> None:
        """Commit the current transaction"""
        self.db.commit()
