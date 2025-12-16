import os
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base, engine

# Models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    role = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    documents = relationship("Document", back_populates="creator", foreign_keys="[Document.created_by]")
    versions = relationship("DocumentVersion", back_populates="creator")
    permissions = relationship("DocumentPermission", back_populates="user")


class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    current_version_id = Column(UUID(as_uuid=True), ForeignKey('document_versions.id', ondelete='CASCADE', use_alter=True, name='fk_current_version'))
    title = Column(String, nullable=False)
    status = Column(String, default="Draft")
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = relationship("User", back_populates="documents", foreign_keys=[created_by])
    versions = relationship("DocumentVersion", back_populates="document", foreign_keys="[DocumentVersion.document_id]")
    permissions = relationship("DocumentPermission", back_populates="document")


class DocumentVersion(Base):
    __tablename__ = 'document_versions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    version_number = Column(Integer, nullable=False)
    markdown_content = Column(Text)
    pdf_url = Column(String)
    change_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="versions", foreign_keys=[document_id])
    creator = relationship("User", back_populates="versions")


class DocumentPermission(Base):
    __tablename__ = 'document_permissions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    permission_type = Column(String, nullable=False)  # 'read', 'write', 'admin'
    granted_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="permissions")
    user = relationship("User", back_populates="permissions")


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(engine)
    print("✓ Database tables created")