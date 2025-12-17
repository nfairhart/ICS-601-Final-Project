# Project Description

## Application Overview
The Document Control System is a web-based application designed to manage documents, users, and permissions. It incorporates AI techniques to enhance functionality, such as document search and validation.

## AI Techniques Used
1. **Structured Output**: Pydantic models are used to validate and constrain LLM responses for tasks like user creation, document updates, and permission management.
2. **Retrieval Augmented Generation (RAG)**: The application uses ChromaDB as a vector store to enable semantic search and similarity matching for documents.

## Key Features
- User management (create, update, list users)
- Document management (upload, update, archive documents)
- Permission management (grant/revoke permissions)
- Semantic document search
- AI-powered agent queries