# Document Management System with AI-Powered Document Assistant

## Application Overview

The Document Management System is a comprehensive web-based application that combines traditional document control features with advanced AI capabilities. The system manages documents, users, permissions, and document versions while leveraging AI to provide semantic search, document analysis, and intelligent question-answering capabilities.

The application addresses the challenge of managing and extracting insights from large document repositories by integrating retrieval-augmented generation (RAG) and structured LLM interactions. Users can not only store and organize documents but also interact with an AI agent to search, summarize, compare, and extract key information from their document collections.

## AI Techniques Used

### 1. Structured Output with Pydantic Models

The application uses **Pydantic AI agents** with strongly-typed schemas to ensure structured, validated responses from the LLM. This is implemented in [ai_agent.py](../backend/ai_agent.py) where:

- **Tool calling**: The AI agent has access to 10 specialized tools, each with defined Pydantic schemas that constrain inputs and outputs
- **Validation**: User queries and document operations are validated through Pydantic models defined in [schemas.py](../backend/schemas.py)
- **Type safety**: All database models in [models.py](../backend/models.py) use SQLAlchemy with type hints to ensure data integrity

Example tools with structured output:
- `search_documents()`: Returns formatted document results with relevance scores
- `get_document_info()`: Returns structured document metadata and version history
- `extract_key_points()`: Returns a structured list of document insights

### 2. Retrieval Augmented Generation (RAG)

The system implements a complete RAG pipeline using **ChromaDB** as a vector store (see [rag.py](../backend/rag.py)):

- **Document embeddings**: Uses OpenAI's `text-embedding-3-small` model to create semantic embeddings
- **Chunking strategy**: Implements intelligent markdown-aware chunking that preserves document structure and context
- **Semantic search**: Enables natural language queries like "find documents about project requirements"
- **Similarity matching**: Finds related documents based on content similarity
- **Permission-aware retrieval**: Filters search results based on user access permissions

**RAG Workflow:**
1. Documents are uploaded and stored in SQLite database
2. Content is chunked using markdown section boundaries (max 2000 chars/chunk)
3. Each chunk is embedded and stored in ChromaDB with metadata
4. User queries are embedded and matched against the vector store
5. Relevant chunks are retrieved and provided to the AI agent for response generation

### 3. AI Agent with Tool Calling

The Pydantic AI agent (OpenAI GPT-4o-mini) has access to 10 tools for document operations:

1. **search_documents**: Semantic search across accessible documents
2. **list_user_documents**: List documents with summaries
3. **get_document_info**: Retrieve metadata and version history
4. **get_full_document_content**: Access complete document text
5. **summarize_document**: Generate concise summaries
6. **find_related_documents**: Discover similar content
7. **compare_documents**: Side-by-side document comparison
8. **extract_key_points**: Identify main takeaways
9. **answer_from_document**: Targeted Q&A from specific documents
10. **get_document_content**: Retrieve full content for analysis

The agent autonomously selects appropriate tools based on user queries and maintains context about user permissions throughout the interaction.

## Key Features

### User Management
- Role-based user system (Admin, Editor, Viewer)
- User creation and profile management
- Email-based user identification

### Document Management
- Document upload with automatic versioning
- Full version history tracking with change summaries
- Document status tracking (draft, published, archived)
- Markdown content support

### Permission System
- Granular document-level permissions (view, edit, manage)
- Admin controls for granting/revoking access
- Permission-aware search and retrieval

### AI-Powered Features
- **Semantic Search**: Natural language document queries with relevance scoring
- **Document Summarization**: AI-generated summaries of document content
- **Key Point Extraction**: Automatic identification of main ideas
- **Document Comparison**: Side-by-side analysis of multiple documents
- **Related Document Discovery**: Similarity-based recommendations
- **Intelligent Q&A**: Ask questions about specific documents

### Technical Features
- RESTful API built with FastAPI
- FastHTML-based responsive frontend
- ChromaDB vector database with persistent storage
- SQLite relational database for structured data
- Environment-based configuration management

## Architecture Highlights

The application demonstrates proper separation of concerns:
- **Backend API** ([app.py](../backend/app.py)): FastAPI endpoints for all operations
- **Data Models** ([models.py](../backend/models.py)): SQLAlchemy ORM models
- **Schemas** ([schemas.py](../backend/schemas.py)): Pydantic validation models
- **RAG System** ([rag.py](../backend/rag.py)): Vector store operations
- **AI Agent** ([ai_agent.py](../backend/ai_agent.py)): Pydantic AI agent with tools
- **Frontend** ([frontend/](../frontend/)): FastHTML pages organized by feature
- **Utilities** ([utils.py](../backend/utils.py)): Helper functions for session management

This architecture ensures maintainability, testability, and clear boundaries between different system responsibilities.