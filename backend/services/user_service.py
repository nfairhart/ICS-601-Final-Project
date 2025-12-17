"""User service for managing user operations"""

from sqlalchemy.orm import Session, joinedload
from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException

from ..models import User
from ..schemas import UserCreate, UserUpdate
from .base import BaseService


class UserService(BaseService[User]):
    """Service for user management operations"""

    def __init__(self, db: Session):
        super().__init__(db, User)

    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user_data: User creation data

        Returns:
            The created user

        Raises:
            HTTPException: 400 if email already exists
        """
        # Check if email already exists
        existing_user = (
            self.db.query(User).filter(User.email == user_data.email).first()
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")

        # Create user
        db_user = User(**user_data.model_dump())
        return self.create(db_user)

    def get_user_with_relations(self, user_id: UUID) -> User:
        """
        Get a user with all their relationships loaded.

        Args:
            user_id: The user ID

        Returns:
            User with documents and permissions loaded

        Raises:
            HTTPException: 404 if user not found
        """
        user = (
            self.db.query(User)
            .options(joinedload(User.documents), joinedload(User.permissions))
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def update_user(self, user_id: UUID, update_data: UserUpdate) -> User:
        """
        Update user information.

        Args:
            user_id: The user ID
            update_data: Fields to update

        Returns:
            The updated user

        Raises:
            HTTPException: 404 if user not found
        """
        user = self.get_or_404(user_id, "User not found")

        # Update only provided fields
        data = update_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(user, key, value)

        user.updated_at = datetime.utcnow()
        self.commit()
        self.db.refresh(user)
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email address.

        Args:
            email: The email to search for

        Returns:
            User if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()

    def verify_user_exists(self, user_id: UUID) -> User:
        """
        Verify that a user exists in the database.

        This is a convenience method for authentication/authorization checks.

        Args:
            user_id: The user ID to verify

        Returns:
            The user if found

        Raises:
            HTTPException: 404 if user not found
        """
        return self.get_or_404(user_id, f"User with ID {user_id} not found")
