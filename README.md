# Document Management System

A FastAPI-based document management system with RAG (Retrieval-Augmented Generation) and AI agent capabilities.

## Project Structure

```
├── backend/
│   ├── app.py              # Main FastAPI application
│   ├── models.py           # SQLAlchemy models
│   ├── rag.py              # ChromaDB RAG implementation
│   ├── setup.py            # Database setup script
│   ├── test_connection.py  # Database connection test
│   └── utils.py            # Utility functions
├── chroma_data/            # ChromaDB vector database storage
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Setup

1. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   
   Create a `.env` file in the root directory:
   ```bash
   # PostgreSQL/Supabase
   host=your-db-host
   port=5432
   dbname=your-db-name
   user=your-db-user
   password=your-db-password
   
   # OpenAI
   OPENAI_API_KEY=sk-your-key-here
   
   # ChromaDB
   CHROMA_PERSIST_DIR=./chroma_data
   
   # Supabase Storage (optional)
   BUCKET_NAME=pdfs
   ```

4. **Run database setup:**
   ```bash
   python -m backend.setup
   ```

5. **Start the API server:**
   ```bash
   uvicorn backend.app:app --reload
   ```

6. **Access the API documentation:**
   
   Open http://localhost:8000/docs in your browser

## Features

- **Document Management**: Create, read, update documents with version control
- **User Management**: User accounts with role-based permissions
- **Document Permissions**: Granular access control (read/write/admin)
- **RAG Integration**: Vector search using ChromaDB with OpenAI embeddings
- **AI Agent**: PydanticAI-powered agent with document search tools
- **Audit Trail**: All changes tracked with timestamps and user context

## API Endpoints

### Users
- `POST /users/` - Create user
- `GET /users/` - List users
- `GET /users/{user_id}` - Get user details
- `PATCH /users/{user_id}` - Update user

### Documents
- `POST /documents/` - Create document
- `GET /documents/` - List documents
- `GET /documents/{document_id}` - Get document details
- `PATCH /documents/{document_id}` - Update document metadata
- `PATCH /documents/{document_id}/archive` - Archive document

### RAG & Search
- `POST /documents/{document_id}/index-rag` - Index document for search
- `POST /search/documents` - Search documents using RAG
- `POST /agent/query` - Query AI agent about documents

### Versions
- `POST /versions/` - Create new document version
- `GET /documents/{document_id}/versions` - List document versions

### Permissions
- `POST /permissions/` - Grant document permission
- `GET /documents/{document_id}/permissions` - List permissions
- `PATCH /permissions/{permission_id}` - Update permission
- `PATCH /permissions/{permission_id}/revoke` - Revoke permission

## Development

Run tests:
```bash
python -m backend.test_connection
```

Check database structure:
```bash
cat erd.txt
```

## License

See LICENSE file for details.
