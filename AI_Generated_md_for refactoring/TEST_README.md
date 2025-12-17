# FastAPI Backend Testing Guide

This guide explains how to use the comprehensive test script to test your FastAPI backend.

## Overview

The test script (`test_backend.py`) automatically tests all backend functionality by:

1. Creating 3 users with different permission levels
2. Creating 5 documents
3. Uploading 3 PDF versions for each document (15 PDFs total)
4. Setting up role-based permissions
5. Testing all API endpoints
6. Testing RAG search functionality
7. Testing AI agent queries

## Prerequisites

### 1. Install Dependencies

Make sure you have all required packages installed:

```bash
pip install -r requirements.txt
```

The test script requires:
- `requests` - For making HTTP requests to the API
- `reportlab` - For generating test PDF files

### 2. Start the FastAPI Backend

In one terminal, start your FastAPI server:

```bash
uvicorn backend.app:app --reload
```

The server should be running at `http://localhost:8000`

### 3. Verify Database Connection

Make sure your database is properly configured in your `.env` file:

```
DATABASE_URL=postgresql://user:password@localhost/dbname
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
BUCKET_NAME=pdfs
OPENAI_API_KEY=your_openai_key
```

## Clearing Test Data

Before running tests, you may want to clear existing data to start fresh.

### Option 1: Clear Data First (Recommended)

Run the cleanup script, then run tests:

```bash
python clear_test_data.py
python test_backend.py
```

The cleanup script will:
- Ask for confirmation before deleting data
- Clear all database tables in the correct order
- Remove all files from the Supabase storage bucket
- Verify the cleanup was successful

### Option 2: Clear and Test in One Command

Run the test script with the `--clear` flag to automatically clear data first:

```bash
python test_backend.py --clear
```

This will automatically clean the database and bucket before running tests (no confirmation prompt).

### Option 3: Run Tests Without Clearing

Simply run the test script to add new test data to existing data:

```bash
python test_backend.py
```

⚠️ **Note**: Running tests without clearing may cause conflicts if test data already exists (e.g., duplicate emails).

## Running the Tests

### Basic Usage

Run the test script (optionally with `--clear` flag):

```bash
python test_backend.py --clear
```

### What the Script Does

#### Step 1: Create Users
Creates 3 users with different roles:
- **Admin User** (admin@example.com) - Role: admin
- **Editor User** (editor@example.com) - Role: editor
- **Viewer User** (viewer@example.com) - Role: viewer

#### Step 2: Create Documents
Creates 5 documents:
1. Project Requirements Document
2. Technical Architecture Spec
3. API Documentation
4. User Manual
5. Security Policy

#### Step 3: Upload PDF Versions
For each document, uploads 3 PDF versions:
- **Version 1**: Initial document with basic structure
- **Version 2**: Updated with additional details
- **Version 3**: Final revision with stakeholder feedback

Each PDF is generated dynamically with realistic content.

#### Step 4: Set Up Permissions
- **Admin**: Admin access to all 5 documents
- **Editor**: Write access to documents 1-3
- **Viewer**: Read access to documents 1-2

#### Step 5-10: Test Functionality
- Document retrieval and listing
- Document updates and status changes
- RAG search across document content
- AI agent queries
- Permission-based access control
- Document archival

## Expected Output

The script provides colorful, formatted output showing:

- ✓ Successful operations in green
- ✗ Failed operations in red
- ℹ Information messages in cyan
- ⚠ Warnings in yellow

Example output:
```
============================================================
Step 1: Creating 3 Users with Different Roles
============================================================

✓ Created user: Admin User (admin) - ID: 123e4567-e89b-12d3-a456-426614174000
✓ Created user: Editor User (editor) - ID: 234e5678-e89b-12d3-a456-426614174001
✓ Created user: Viewer User (viewer) - ID: 345e6789-e89b-12d3-a456-426614174002
```

## Test Coverage

The script tests the following API endpoints:

### User Endpoints
- `POST /users` - Create user
- `GET /users` - List all users
- `GET /users/{user_id}` - Get user details
- `PATCH /users/{user_id}` - Update user

### Document Endpoints
- `POST /documents` - Create document
- `GET /documents` - List documents
- `GET /documents/{document_id}` - Get document details
- `PATCH /documents/{document_id}` - Update document
- `PATCH /documents/{document_id}/archive` - Archive document

### PDF Upload Endpoints
- `POST /documents/{document_id}/upload-pdf` - Upload PDF version

### Version Endpoints
- `GET /documents/{document_id}/versions` - List document versions

### Permission Endpoints
- `POST /permissions` - Grant permission
- `GET /documents/{document_id}/permissions` - List permissions

### RAG/Search Endpoints
- `POST /search` - Search documents
- `POST /agent/query` - Query AI agent

## Test Data Summary

After successful execution, the script provides a summary:

```
Test Data Summary
============================================================

Users:
  1. Admin User (admin@example.com) - Role: admin
  2. Editor User (editor@example.com) - Role: editor
  3. Viewer User (viewer@example.com) - Role: viewer

Documents:
  1. Project Requirements Document - 3 versions
  2. Technical Architecture Spec - 3 versions
  3. API Documentation - 3 versions
  4. User Manual - 3 versions
  5. Security Policy - 3 versions

Permissions:
  Admin User: Admin access to all 5 documents
  Editor User: Write access to documents 1-3
  Viewer User: Read access to documents 1-2
```

## Troubleshooting

### Connection Error
If you see:
```
✗ Could not connect to API at http://localhost:8000
```

**Solution**: Make sure the FastAPI server is running:
```bash
uvicorn backend.app:app --reload
```

### PDF Upload Failures
If PDF uploads fail:
- Check Supabase credentials in `.env`
- Verify the storage bucket exists
- Check bucket permissions

### RAG Search Returns No Results
- Allow time for indexing (script waits 5 seconds)
- Check OpenAI API key is valid
- Verify ChromaDB is properly initialized

### Database Errors
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Run database migrations if needed

## Cleaning Up Test Data

To remove test data from your database and storage, use the cleanup script:

```bash
python clear_test_data.py
```

This will:
- Delete all records from database tables (respects foreign key constraints)
- Remove all PDF files from the Supabase storage bucket
- Verify cleanup was successful

**Alternative methods:**
1. Use your database client to manually delete test users (emails ending with @example.com)
2. Manually delete associated documents and permissions
3. Reset your entire database if this is a development environment

## Customization

You can modify the script to:

- Change the number of users, documents, or versions
- Add different permission combinations
- Test additional endpoints
- Customize PDF content
- Add more search queries or agent tests

## Next Steps

After running the tests:

1. Check the API responses for any errors
2. Verify data in your database
3. Check Supabase storage for uploaded PDFs
4. Review RAG search results for accuracy
5. Test the frontend with this data

## Support

If you encounter issues:
1. Check the FastAPI logs for error details
2. Verify all environment variables are set
3. Ensure all dependencies are installed
4. Check that your database and storage are accessible
