from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

# ==================== User Schemas ====================

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user"""
    pass

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None

class UserResponse(UserBase):
    """Schema for user response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== Document Schemas ====================

class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    status: Optional[str] = "Draft"
    description: Optional[str] = None

class DocumentCreate(DocumentBase):
    """Schema for creating a new document"""
    created_by: UUID

class DocumentUpdate(BaseModel):
    """Schema for updating document information"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = None
    description: Optional[str] = None
    current_version_id: Optional[UUID] = None

class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: UUID
    created_by: UUID
    current_version_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== Document Version Schemas ====================

class DocumentVersionBase(BaseModel):
    version_number: int = Field(..., ge=1)
    markdown_content: Optional[str] = None
    pdf_url: Optional[str] = None
    change_summary: Optional[str] = None

class DocumentVersionCreate(DocumentVersionBase):
    """Schema for creating a new document version"""
    document_id: UUID
    created_by: Optional[UUID] = None

class DocumentVersionUpdate(BaseModel):
    """Schema for updating document version"""
    markdown_content: Optional[str] = None
    pdf_url: Optional[str] = None
    change_summary: Optional[str] = None

class DocumentVersionResponse(DocumentVersionBase):
    """Schema for document version response"""
    id: UUID
    document_id: UUID
    created_by: Optional[UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== Document Permission Schemas ====================

class DocumentPermissionBase(BaseModel):
    permission_type: str = Field(..., pattern="^(read|write|admin)$")

class DocumentPermissionCreate(DocumentPermissionBase):
    """Schema for creating document permission"""
    document_id: UUID
    user_id: UUID

class DocumentPermissionUpdate(BaseModel):
    """Schema for updating document permission"""
    permission_type: Optional[str] = Field(None, pattern="^(read|write|admin)$")

class DocumentPermissionResponse(DocumentPermissionBase):
    """Schema for document permission response"""
    id: UUID
    document_id: UUID
    user_id: UUID
    granted_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== Nested/Detailed Response Schemas ====================

class DocumentVersionWithCreator(DocumentVersionResponse):
    """Document version with creator information"""
    creator: Optional[UserResponse] = None

class DocumentWithDetails(DocumentResponse):
    """Document with full details including creator and versions"""
    creator: Optional[UserResponse] = None
    versions: list[DocumentVersionResponse] = []
    permissions: list[DocumentPermissionResponse] = []

class UserWithDocuments(UserResponse):
    """User with their created documents"""
    documents: list[DocumentResponse] = []
    permissions: list[DocumentPermissionResponse] = []