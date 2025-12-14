import os
from datetime import datetime
import uuid
from dotenv import load_dotenv

# SQLAlchemy imports
from sqlalchemy import (
    create_engine, Column, String, Integer, DateTime, Text, ForeignKey, text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.pool import NullPool

# 1. Load Environment Variables
load_dotenv()

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Construct the Connection String
DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

# 2. Define the SQLAlchemy Engine
# Using NullPool as per your request to disable client-side pooling for Supabase
engine = create_engine(DATABASE_URL, poolclass=NullPool)
Base = declarative_base()

# 3. Define the Models

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="creator", foreign_keys="[Document.created_by]")
    document_versions = relationship("DocumentVersion", back_populates="creator")
    permissions = relationship("DocumentPermission", back_populates="user")


class Document(Base):
    __tablename__ = 'documents'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    status = Column(String, default="Draft")  # e.g., Draft, Review, Published
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ForeignKey to the current version
    # use_alter=True handles the circular dependency
    current_version_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('document_versions.id', use_alter=True, name='fk_current_version'),
        nullable=True
    )

    # Relationships
    creator = relationship("User", back_populates="documents", foreign_keys=[created_by])
    versions = relationship("DocumentVersion", back_populates="document", foreign_keys="[DocumentVersion.document_id]")
    permissions = relationship("DocumentPermission", back_populates="document")


class DocumentVersion(Base):
    __tablename__ = 'document_versions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id'), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    version_number = Column(Integer, nullable=False)
    
    # The editable MD output from parser
    markdown_content = Column(Text, nullable=True)
    
    # URL/path to the PDF in Supabase Storage
    pdf_url = Column(String, nullable=True)
    
    # Summary of changes made in this version
    change_summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="versions", foreign_keys=[document_id])
    creator = relationship("User", back_populates="document_versions")


class DocumentPermission(Base):
    __tablename__ = 'document_permissions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    permission_type = Column(String, nullable=False)  # e.g., 'read', 'write', 'admin'
    granted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="permissions")
    user = relationship("User", back_populates="permissions")


# 4. Create Tables and Bucket
def setup_database():
    try:
        print("--- Starting Database Setup ---")
        
        # A. Create the Tables
        print("Creating relational tables...")
        Base.metadata.create_all(engine)
        print("Tables created successfully:")
        print("  - users")
        print("  - documents")
        print("  - document_versions")
        print("  - document_permissions")

        # B. Create the Storage Bucket
        bucket_name = "pdfs"
        
        print(f"\nCreating storage bucket: '{bucket_name}'...")
        with engine.connect() as connection:
            # SQL to insert bucket if it doesn't exist
            # Note: 'public' means files are accessible without signed URLs. Set 'false' for private.
            create_bucket_sql = text("""
                INSERT INTO storage.buckets (id, name, public)
                VALUES (:bucket_id, :bucket_name, true)
                ON CONFLICT (id) DO NOTHING;
            """)
            
            connection.execute(create_bucket_sql, {"bucket_id": bucket_name, "bucket_name": bucket_name})
            connection.commit()
            print(f"Bucket '{bucket_name}' ensured.")

        print("\n--- Setup Complete ---")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    setup_database()