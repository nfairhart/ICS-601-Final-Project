# Code Organization Diagram

## Components

### Backend
- **app.py**: FastAPI application setup and routing.
- **schemas.py**: Pydantic models for request/response validation.
- **services/**: Business logic for users, documents, permissions, etc.
- **database.py**: Database connection and session management.

### Frontend
- **main.py**: FastHTML application setup and routing.
- **pages/**: Individual page components for users, documents, search, etc.
- **shared/**: Shared components like layout and styles.

### AI/Agent
- **rag.py**: Retrieval Augmented Generation logic.
- **ai_agent.py**: Agent query handling.

### Data Storage
- **chroma.sqlite3**: Vector store for embeddings.
- **models.py**: SQLAlchemy models for database tables.