"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


# === ENUMS FOR VALIDATION ===

class DocumentStatus(str, Enum):
    """Valid document status values"""
    DRAFT = "Draft"
    REVIEW = "Review"
    APPROVED = "Approved"
    ARCHIVED = "Archived"


class PermissionType(str, Enum):
    """Valid permission types"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class UserRole(str, Enum):
    """Valid user roles"""
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"
    OWNER = "owner"


# === USER SCHEMAS ===

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    role: Optional[UserRole] = None

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("full_name cannot be empty or whitespace")
        return v.strip() if v else v


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    role: Optional[UserRole] = None

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("full_name cannot be empty or whitespace")
        return v.strip() if v else v


class UserResponse(BaseModel):
    """Schema for user responses"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: Optional[str] = None
    role: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# === DOCUMENT SCHEMAS ===

class DocumentCreate(BaseModel):
    """Schema for creating a new document"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    created_by: UUID

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v.strip() == "":
            raise ValueError("title cannot be empty or whitespace")
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is not None and v.strip() == "":
            return None
        return v.strip() if v else v


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[DocumentStatus] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("title cannot be empty or whitespace")
        return v.strip() if v else v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is not None and v.strip() == "":
            return None
        return v.strip() if v else v


class DocumentResponse(BaseModel):
    """Schema for document responses"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: Optional[str] = None
    status: str
    created_by: UUID
    current_version_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


# === VERSION SCHEMAS ===

class VersionCreate(BaseModel):
    """Schema for creating a document version"""
    document_id: UUID
    version_number: int = Field(..., ge=1)
    markdown_content: Optional[str] = Field(None, max_length=1_000_000)
    pdf_url: Optional[str] = Field(None, max_length=1000)
    change_summary: Optional[str] = Field(None, max_length=2000)
    created_by: Optional[UUID] = None

    @field_validator('version_number')
    @classmethod
    def validate_version_number(cls, v):
        if v < 1:
            raise ValueError("version_number must be at least 1")
        return v

    @field_validator('change_summary')
    @classmethod
    def validate_change_summary(cls, v):
        if v is not None and v.strip() == "":
            return None
        return v.strip() if v else v


class VersionResponse(BaseModel):
    """Schema for version responses"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    version_number: int
    markdown_content: Optional[str] = None
    pdf_url: Optional[str] = None
    change_summary: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime


# === PERMISSION SCHEMAS ===

class PermissionCreate(BaseModel):
    """Schema for granting a permission"""
    document_id: UUID
    user_id: UUID
    permission_type: PermissionType


class PermissionUpdate(BaseModel):
    """Schema for updating a permission"""
    permission_type: PermissionType


class PermissionResponse(BaseModel):
    """Schema for permission responses"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    user_id: UUID
    permission_type: str
    granted_at: datetime


# === SEARCH SCHEMAS ===

class RAGSearch(BaseModel):
    """Schema for RAG search requests"""
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(5, ge=1, le=50)

    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        if v.strip() == "":
            raise ValueError("query cannot be empty or whitespace")
        return v.strip()


class SearchResult(BaseModel):
    """Schema for a single search result"""
    document_id: str
    version_id: str
    title: str
    content: str
    score: float = Field(..., ge=0.0, le=1.0)


class SearchResponse(BaseModel):
    """Schema for search response"""
    query: str
    results: list[SearchResult]
    total: int
    user_email: Optional[str] = None
    message: Optional[str] = None


# === AGENT SCHEMAS ===

class AgentQuery(BaseModel):
    """Schema for AI agent queries"""
    query: str = Field(..., min_length=1, max_length=2000)

    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        if v.strip() == "":
            raise ValueError("query cannot be empty or whitespace")
        return v.strip()


class AgentResponse(BaseModel):
    """Schema for agent responses"""
    response: str
    user_email: Optional[str] = None


# === PDF UPLOAD SCHEMAS ===

class PDFUploadResponse(BaseModel):
    """Schema for PDF upload response"""
    message: str
    version: dict
    document: Optional[dict] = None


# === ERROR SCHEMAS ===

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationErrorDetail(BaseModel):
    """Schema for validation error details"""
    loc: list[str]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses"""
    detail: list[ValidationErrorDetail]
