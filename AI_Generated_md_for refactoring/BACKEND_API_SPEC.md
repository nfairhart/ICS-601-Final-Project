# Backend API Specifications

## Base URL
```
http://localhost:8000
```

## Overview
This document management API provides endpoints for user management, document management with versioning, PDF upload/processing, permissions management, RAG-based search, and AI agent queries.

---

## Data Models

### User
```json
{
  "id": "uuid",
  "email": "string",
  "full_name": "string (optional)",
  "role": "string (optional)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Document
```json
{
  "id": "uuid",
  "created_by": "uuid",
  "current_version_id": "uuid (optional)",
  "title": "string",
  "status": "string (Draft/Archived)",
  "description": "string (optional)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### DocumentVersion
```json
{
  "id": "uuid",
  "document_id": "uuid",
  "created_by": "uuid (optional)",
  "version_number": "integer",
  "markdown_content": "string (optional)",
  "pdf_url": "string (optional)",
  "change_summary": "string (optional)",
  "created_at": "datetime"
}
```

### DocumentPermission
```json
{
  "id": "uuid",
  "document_id": "uuid",
  "user_id": "uuid",
  "permission_type": "string (read/write/admin)",
  "granted_at": "datetime"
}
```

---

## Endpoints

### Health Check

#### GET `/`
Check if the API is running.

**Response:**
```json
{
  "status": "ok"
}
```

---

## User Endpoints

### Create User
#### POST `/users`
Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe (optional)",
  "role": "editor (optional)"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "editor",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

**Error Responses:**
- `400 Bad Request` - Email already exists

---

### List All Users
#### GET `/users`
Retrieve all users.

**Response:**
```json
[
  {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "editor",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
]
```

---

### Get User by ID
#### GET `/users/{user_id}`
Retrieve a specific user with their documents and permissions.

**Parameters:**
- `user_id` (path, uuid) - User ID

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "editor",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "documents": [...],
  "permissions": [...]
}
```

**Error Responses:**
- `404 Not Found` - User not found

---

### Update User
#### PATCH `/users/{user_id}`
Update user information.

**Parameters:**
- `user_id` (path, uuid) - User ID

**Request Body:** (all fields optional)
```json
{
  "email": "newemail@example.com",
  "full_name": "Jane Doe",
  "role": "admin"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "newemail@example.com",
  "full_name": "Jane Doe",
  "role": "admin",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T12:45:00"
}
```

**Error Responses:**
- `404 Not Found` - User not found

---

## Document Endpoints

### Create Document
#### POST `/documents`
Create a new document.

**Request Body:**
```json
{
  "title": "Project Proposal",
  "description": "Q1 2024 Project Proposal (optional)",
  "created_by": "uuid"
}
```

**Response:**
```json
{
  "id": "uuid",
  "created_by": "uuid",
  "current_version_id": null,
  "title": "Project Proposal",
  "status": "Draft",
  "description": "Q1 2024 Project Proposal",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

**Error Responses:**
- `404 Not Found` - User not found

---

### List Documents
#### GET `/documents`
Retrieve all documents with optional status filtering.

**Query Parameters:**
- `status` (optional, string) - Filter by status (e.g., "Draft", "Archived")

**Example:** `GET /documents?status=Draft`

**Response:**
```json
[
  {
    "id": "uuid",
    "created_by": "uuid",
    "current_version_id": "uuid",
    "title": "Project Proposal",
    "status": "Draft",
    "description": "Q1 2024 Project Proposal",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
]
```

---

### Get Document by ID
#### GET `/documents/{document_id}`
Retrieve a specific document with creator, versions, and permissions.

**Parameters:**
- `document_id` (path, uuid) - Document ID

**Response:**
```json
{
  "id": "uuid",
  "created_by": "uuid",
  "current_version_id": "uuid",
  "title": "Project Proposal",
  "status": "Draft",
  "description": "Q1 2024 Project Proposal",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "creator": {...},
  "versions": [...],
  "permissions": [...]
}
```

**Error Responses:**
- `404 Not Found` - Document not found

---

### Update Document
#### PATCH `/documents/{document_id}`
Update document metadata.

**Parameters:**
- `document_id` (path, uuid) - Document ID

**Query Parameters:** (all optional)
- `title` (string) - New title
- `status` (string) - New status
- `description` (string) - New description

**Example:** `PATCH /documents/{id}?title=New Title&status=Archived`

**Response:**
```json
{
  "id": "uuid",
  "title": "New Title",
  "status": "Archived",
  "description": "Updated description",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T14:20:00"
}
```

**Error Responses:**
- `404 Not Found` - Document not found

---

### Archive Document
#### PATCH `/documents/{document_id}/archive`
Archive a document and remove it from RAG index.

**Parameters:**
- `document_id` (path, uuid) - Document ID

**Response:**
```json
{
  "id": "uuid",
  "status": "Archived",
  "updated_at": "2024-01-15T14:20:00"
}
```

**Error Responses:**
- `404 Not Found` - Document not found

---

## Version Endpoints

### Create Version
#### POST `/versions`
Create a new version of a document.

**Request Body:**
```json
{
  "document_id": "uuid",
  "version_number": 2,
  "markdown_content": "# Document Content (optional)",
  "pdf_url": "https://storage.url/file.pdf (optional)",
  "change_summary": "Updated introduction (optional)",
  "created_by": "uuid (optional)"
}
```

**Response:**
```json
{
  "id": "uuid",
  "document_id": "uuid",
  "created_by": "uuid",
  "version_number": 2,
  "markdown_content": "# Document Content",
  "pdf_url": "https://storage.url/file.pdf",
  "change_summary": "Updated introduction",
  "created_at": "2024-01-15T11:00:00"
}
```

**Notes:**
- Automatically updates the document's `current_version_id`
- If `markdown_content` is provided, it will be indexed in RAG in the background

**Error Responses:**
- `404 Not Found` - Document not found

---

### List Document Versions
#### GET `/documents/{document_id}/versions`
Get all versions for a document, ordered by version number (descending).

**Parameters:**
- `document_id` (path, uuid) - Document ID

**Response:**
```json
[
  {
    "id": "uuid",
    "document_id": "uuid",
    "version_number": 2,
    "markdown_content": "# Updated Content",
    "pdf_url": "https://storage.url/file-v2.pdf",
    "change_summary": "Updated introduction",
    "created_at": "2024-01-15T11:00:00"
  },
  {
    "id": "uuid",
    "document_id": "uuid",
    "version_number": 1,
    "markdown_content": "# Original Content",
    "pdf_url": "https://storage.url/file-v1.pdf",
    "change_summary": "Initial version",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

**Error Responses:**
- `404 Not Found` - Document not found

---

## PDF Upload Endpoints

### Upload PDF to Existing Document
#### POST `/documents/{document_id}/upload-pdf`
Upload a PDF, convert it to markdown, and create a new version.

**Parameters:**
- `document_id` (path, uuid) - Document ID

**Form Data:**
- `pdf_file` (file, required) - PDF file to upload
- `created_by` (uuid, required) - User ID
- `change_summary` (string, optional) - Description of changes

**Example using JavaScript:**
```javascript
const formData = new FormData();
formData.append('pdf_file', fileInput.files[0]);
formData.append('created_by', userId);
formData.append('change_summary', 'Version 2 updates');

fetch(`/documents/${documentId}/upload-pdf`, {
  method: 'POST',
  body: formData
});
```

**Response:**
```json
{
  "message": "PDF uploaded and processed successfully",
  "version": {
    "id": "uuid",
    "version_number": 2,
    "pdf_url": "https://storage.url/file.pdf",
    "created_at": "2024-01-15T11:30:00"
  }
}
```

**Notes:**
- Automatically converts PDF to markdown
- Uploads PDF to Supabase storage
- Creates new version with incremented version number
- Indexes content in RAG (background)
- Updates document's current_version_id

**Error Responses:**
- `404 Not Found` - Document or user not found

---

### Create Document from PDF
#### POST `/documents/create-from-pdf`
Create a new document directly from a PDF upload.

**Form Data:**
- `pdf_file` (file, required) - PDF file to upload
- `created_by` (uuid, required) - User ID
- `title` (string, optional) - Document title (defaults to filename)
- `description` (string, optional) - Document description

**Example using JavaScript:**
```javascript
const formData = new FormData();
formData.append('pdf_file', fileInput.files[0]);
formData.append('created_by', userId);
formData.append('title', 'My Document');
formData.append('description', 'Important document');

fetch('/documents/create-from-pdf', {
  method: 'POST',
  body: formData
});
```

**Response:**
```json
{
  "message": "Document created successfully from PDF",
  "document": {
    "id": "uuid",
    "title": "My Document",
    "created_at": "2024-01-15T11:00:00"
  },
  "version": {
    "id": "uuid",
    "version_number": 1,
    "pdf_url": "https://storage.url/file.pdf"
  }
}
```

**Notes:**
- Creates document and first version in one step
- Uses filename as title if not provided
- Automatically processes PDF and indexes content

**Error Responses:**
- `404 Not Found` - User not found
- `500 Internal Server Error` - PDF processing failed (document creation is rolled back)

---

## Permission Endpoints

### Grant Permission
#### POST `/permissions`
Grant a user permission to access a document.

**Request Body:**
```json
{
  "document_id": "uuid",
  "user_id": "uuid",
  "permission_type": "read"
}
```

**Permission Types:**
- `read` - Read-only access
- `write` - Read and write access
- `admin` - Full administrative access

**Response:**
```json
{
  "id": "uuid",
  "document_id": "uuid",
  "user_id": "uuid",
  "permission_type": "read",
  "granted_at": "2024-01-15T12:00:00"
}
```

**Error Responses:**
- `400 Bad Request` - Permission already exists
- `404 Not Found` - Document or user not found

---

### List Document Permissions
#### GET `/documents/{document_id}/permissions`
Get all permissions for a document.

**Parameters:**
- `document_id` (path, uuid) - Document ID

**Response:**
```json
[
  {
    "id": "uuid",
    "document_id": "uuid",
    "user_id": "uuid",
    "permission_type": "admin",
    "granted_at": "2024-01-15T10:30:00"
  },
  {
    "id": "uuid",
    "document_id": "uuid",
    "user_id": "uuid",
    "permission_type": "read",
    "granted_at": "2024-01-15T12:00:00"
  }
]
```

**Error Responses:**
- `404 Not Found` - Document not found

---

### Revoke Permission
#### DELETE `/permissions/{permission_id}`
Remove a user's permission from a document.

**Parameters:**
- `permission_id` (path, uuid) - Permission ID

**Response:**
```json
{
  "status": "revoked"
}
```

**Error Responses:**
- `404 Not Found` - Permission not found

---

## RAG/Search Endpoints

### Search Documents
#### POST `/search`
Search documents using RAG (Retrieval Augmented Generation).

**Request Body:**
```json
{
  "query": "What are the project deliverables?",
  "user_id": "uuid",
  "top_k": 5
}
```

**Response:**
```json
{
  "query": "What are the project deliverables?",
  "results": [
    {
      "document_id": "uuid",
      "version_id": "uuid",
      "title": "Project Proposal",
      "content": "Relevant text snippet...",
      "score": 0.85
    }
  ],
  "total": 5
}
```

**Notes:**
- Only searches documents the user has permission to access
- Results are ranked by relevance score
- `top_k` controls maximum number of results (default: 5)

---

### AI Agent Query
#### POST `/agent/query`
Query the AI agent about documents.

**Request Body:**
```json
{
  "query": "Summarize all project proposals from 2024",
  "user_id": "uuid"
}
```

**Response:**
```json
{
  "response": "Based on the documents you have access to, here are the 2024 project proposals..."
}
```

**Notes:**
- Agent uses RAG to search and analyze documents
- Only accesses documents the user has permission to view
- Provides natural language responses

**Error Responses:**
- `404 Not Found` - User not found
- `500 Internal Server Error` - Agent processing error

---

## Error Responses

All endpoints may return the following error formats:

### 400 Bad Request
```json
{
  "detail": "Error message describing the issue"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found message"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message with details"
}
```

---

## CORS Configuration

The API allows requests from all origins with credentials enabled. This is configured for development purposes.

---

## FastHTML Frontend Integration Tips

### 1. **Fetching Data**
```python
import httpx

async def get_documents():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/documents")
        return response.json()
```

### 2. **Creating Forms**
```python
from fasthtml.common import *

def document_form():
    return Form(
        Input(name="title", placeholder="Document Title"),
        Textarea(name="description", placeholder="Description"),
        Input(type="hidden", name="created_by", value=user_id),
        Button("Create Document"),
        hx_post="http://localhost:8000/documents",
        hx_target="#document-list"
    )
```

### 3. **File Upload**
```python
def pdf_upload_form(document_id):
    return Form(
        Input(type="file", name="pdf_file", accept=".pdf"),
        Input(type="hidden", name="created_by", value=user_id),
        Input(name="change_summary", placeholder="What changed?"),
        Button("Upload PDF"),
        enctype="multipart/form-data",
        hx_post=f"http://localhost:8000/documents/{document_id}/upload-pdf"
    )
```

### 4. **Displaying Documents**
```python
@app.get("/documents")
async def documents_page():
    docs = await get_documents()
    return Div(
        H1("Documents"),
        Ul(*[Li(A(doc["title"], href=f"/documents/{doc['id']}"))
             for doc in docs])
    )
```

### 5. **Search Interface**
```python
def search_form():
    return Form(
        Input(name="query", placeholder="Search documents..."),
        Input(type="hidden", name="user_id", value=user_id),
        Button("Search"),
        hx_post="http://localhost:8000/search",
        hx_target="#search-results"
    )
```

---

## Notes for Development

1. **UUIDs**: All IDs are UUIDs in string format
2. **Datetime Format**: ISO 8601 format (e.g., "2024-01-15T10:30:00")
3. **Background Tasks**: PDF processing and RAG indexing happen asynchronously
4. **File Storage**: PDFs are stored in Supabase storage
5. **Database**: PostgreSQL with SQLAlchemy ORM
6. **Authentication**: Currently no authentication implemented (user_id passed directly)

---

## Running the Backend

```bash
cd backend
uvicorn app:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI) will be available at `http://localhost:8000/docs`
