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

   Copy the example file and configure your settings:
   ```bash
   cp .env.example .env
   ```

   Then edit `.env` with your actual values:
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

   # Supabase Storage
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-supabase-anon-key
   BUCKET_NAME=pdfs

   # CORS Configuration
   # Development: include both localhost and 127.0.0.1
   # Production: only include your production domain(s)
   ALLOWED_ORIGINS=http://localhost:5001,http://127.0.0.1:5001
   ```

   **Security Note:** The `ALLOWED_ORIGINS` setting controls which domains can access your API.
   Never use `*` in production. Update this value before deploying.

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
- **Input Validation**: Comprehensive Pydantic validation with enums and field validators
- **CORS Security**: Configurable origins (no wildcard in production)

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

### Code Organization

The project follows a modular structure with shared components:

**Backend:** `/backend`
- `app.py` - FastAPI application with REST endpoints
- `models.py` - SQLAlchemy database models
- `database.py` - Database configuration
- `rag.py` - RAG (Retrieval-Augmented Generation) with ChromaDB
- `ai_agent.py` - PydanticAI agent with document tools
- `utils.py` - Utility functions for PDF processing

**Frontend:** `/frontend`
- `main.py` - FastHTML application entry point
- `shared/` - Shared styles and layout components (eliminates CSS duplication)
  - `styles.py` - Centralized CSS styles (~675 lines)
  - `layout.py` - Reusable page layout function
- `pages/` - Individual page modules (documents, users, search, agent, etc.)

**Additional Documentation:**
- [REFACTORING.md](REFACTORING.md) - CSS refactoring details (~1,000 lines eliminated)
- [VALIDATION.md](VALIDATION.md) - Backend Pydantic validation with enums
- [FRONTEND_VALIDATION.md](FRONTEND_VALIDATION.md) - Frontend validation updates

### Running Tests

Run tests:
```bash
python -m backend.test_connection
```

Check database structure:
```bash
cat erd.txt
```

## Security

This application implements basic authentication for development purposes. **The current authentication is NOT suitable for production.**

See [SECURITY.md](SECURITY.md) for:
- Current security implementation details
- Known security limitations
- Production security recommendations
- Security checklist before deployment

**Important:** Never deploy to production with the current header-based authentication. Implement JWT tokens or OAuth2 first.

## License

See LICENSE file for details.
