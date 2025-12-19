# Document Management System with AI-Powered Document Assistant

A comprehensive document management application with AI-powered semantic search, document analysis, and intelligent question-answering capabilities.

Video Demo: https://drive.google.com/file/d/1kjKYqzkxe8LIjnw7gKaSUjRPENh5-ab9/view?usp=drive_link  

## Features

- **User Management**: Role-based access control (Admin, Editor, Viewer)
- **Document Management**: Upload, version control, and status tracking
- **Permission System**: Granular document-level permissions
- **AI-Powered Search**: Semantic search using RAG (Retrieval Augmented Generation)
- **Document Analysis**: AI agent with 10 specialized tools for document operations
- **Version History**: Full document version tracking with change summaries

## Tech Stack

- **Frontend**: FastHTML
- **Backend**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **Vector Store**: ChromaDB
- **AI**: Pydantic AI with OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small

## Prerequisites

- Python 3.9 or higher
- Supabase account and database
- OpenAI API key

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ICS-601-Final-Project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables:
   ```env
   # Supabase Database Configuration
   host=your-supabase-host
   port=5432
   dbname=postgres
   user=your-username
   password=your-password

   # OpenAI API Key
   OPENAI_API_KEY=your-openai-api-key

   # ChromaDB Configuration (optional, defaults to ./chroma_data)
   CHROMA_PERSIST_DIR=./chroma_data
   ```

4. Initialize the database:
   ```bash
   cd backend
   python3 setup.py
   cd ..
   ```

## Running the Application

You have two options for starting the application:

### Option 1: Single Terminal (Recommended)

This starts both servers in the background and monitors them:

```bash
./start.sh
```

Features:
- Starts both backend and frontend automatically
- Monitors both processes
- Logs output to `logs/backend.log` and `logs/frontend.log`
- Press `Ctrl+C` to stop both servers

### Option 2: Separate Terminal Windows

This opens each server in its own terminal window:

```bash
./start_separate.sh
```

Features:
- Backend opens in one terminal window
- Frontend opens in another terminal window
- Close each window individually to stop that server
- Useful for debugging or seeing live logs

### Manual Start

If you prefer to start each server manually:

**Backend (Terminal 1):**
```bash
cd backend
python3 app.py
```

**Frontend (Terminal 2):**
```bash
cd frontend
python3 main.py
```

## Accessing the Application

Once both servers are running:

- **Frontend UI**: http://localhost:5001
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)

## Project Structure

```
ICS-601-Final-Project/
├── backend/
│   ├── app.py                 # FastAPI application
│   ├── models.py              # SQLAlchemy ORM models
│   ├── schemas.py             # Pydantic validation models
│   ├── database.py            # Database configuration
│   ├── ai_agent.py            # Pydantic AI agent with tools
│   ├── rag.py                 # RAG system with ChromaDB
│   ├── utils.py               # Helper functions
│   └── setup.py               # Database initialization
├── frontend/
│   ├── main.py                # FastHTML application
│   ├── pages/                 # Page components
│   │   ├── users.py
│   │   ├── documents.py
│   │   ├── upload.py
│   │   ├── search.py
│   │   ├── permissions.py
│   │   └── agent.py
│   └── shared/
│       └── layout.py          # Shared UI components
├── documentation/             # Project documentation
│   ├── project_description.md
│   ├── class_diagram.uml
│   ├── sequence_diagram_1.uml
│   ├── sequence_diagram_2.uml
│   ├── code_organization_diagram.puml
│   └── README.md
├── chroma_data/              # ChromaDB persistent storage
├── logs/                     # Application logs
├── start.sh                  # Startup script (single terminal)
├── start_separate.sh         # Startup script (separate terminals)
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create this)
└── README.md                 # This file
```

## AI Features

### Pydantic AI Agent Tools

The AI agent has access to 10 specialized tools:

1. **search_documents** - Semantic search across accessible documents
2. **list_user_documents** - List documents with summaries
3. **get_document_info** - Retrieve metadata and version history
4. **get_full_document_content** - Access complete document text
5. **summarize_document** - Generate concise summaries
6. **find_related_documents** - Discover similar content
7. **compare_documents** - Side-by-side document comparison
8. **extract_key_points** - Identify main takeaways
9. **answer_from_document** - Targeted Q&A from specific documents
10. **get_document_content** - Retrieve full content for analysis

### RAG Pipeline

1. Documents are uploaded and stored in Supabase
2. Content is chunked using markdown section boundaries (max 2000 chars/chunk)
3. Each chunk is embedded and stored in ChromaDB with metadata
4. User queries are embedded and matched via cosine similarity
5. Relevant chunks are retrieved and filtered by user permissions
6. AI agent uses retrieved context to generate responses

## Development

### Code Organization

The application follows strict separation of concerns:

- **Backend API Layer**: FastAPI endpoints (`backend/app.py`)
- **Data Models**: SQLAlchemy ORM (`backend/models.py`)
- **Validation Schemas**: Pydantic models (`backend/schemas.py`)
- **AI/Agent Layer**: Pydantic AI agent (`backend/ai_agent.py`)
- **RAG System**: Vector operations (`backend/rag.py`)
- **Frontend Layer**: FastHTML pages organized by feature

### Database Schema

Main entities:
- **Users**: User accounts with roles
- **Documents**: Document metadata and status
- **DocumentVersions**: Version history with content
- **DocumentPermissions**: User access control

### API Endpoints

Key endpoints:
- `GET /api/users` - List users
- `POST /api/users` - Create user
- `GET /api/documents` - List documents
- `POST /api/documents` - Upload document
- `PUT /api/documents/{id}` - Update document
- `POST /api/search` - Semantic search
- `POST /api/agent/query` - AI agent query

See http://localhost:8000/docs for full API documentation.

## Documentation

Complete project documentation is available in the `documentation/` directory:

- [Project Description](documentation/project_description.md) - Comprehensive overview
- [Requirements Fulfillment](documentation/README.md) - Verification of all requirements
- [Class Diagram](documentation/class_diagram.uml) - UML class diagram
- [Sequence Diagrams](documentation/) - System interaction flows
- [Code Organization](documentation/code_organization_diagram.puml) - Architecture diagram

## License

This project was developed as part of the ICS-601 course at the University of Hawaii.

## Author

Nicholas Fairhart

## Statistics

- **Total Lines of Code**: 4,720 lines
- **Backend**: 1,921 lines
- **Frontend**: 2,799 lines
- **AI Agent**: 453 lines
- **RAG System**: 306 lines
