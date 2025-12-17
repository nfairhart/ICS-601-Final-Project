# Testing Troubleshooting Guide

This guide helps you fix common issues when running the test scripts.

## Current Issues and Solutions

### 1. PDF Upload Fails with 500 Internal Server Error

**Symptoms:**
```
✗ Failed to upload PDF: 500
Server error (500) - Check FastAPI server logs for details
```

**Common Causes:**

#### A. Missing or Invalid Supabase Credentials

Check your `.env` file has these variables:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key_here
BUCKET_NAME=pdfs
```

**How to verify:**
1. Run the environment check:
   ```bash
   python3 check_environment.py
   ```

2. Verify Supabase URL and key are correct in your Supabase dashboard

#### B. Storage Bucket Doesn't Exist

The `pdfs` bucket must exist in your Supabase storage.

**Solution:**
```bash
python3 -m backend.setup
```

This creates the storage bucket if it doesn't exist.

**Manual verification:**
1. Log into Supabase dashboard
2. Navigate to Storage
3. Check if `pdfs` bucket exists
4. If not, create it manually or run setup script

#### C. MarkItDown Library Issue

The PDF to markdown conversion may be failing.

**Solution:**
```bash
pip3 install --upgrade markitdown
```

**Test manually:**
```python
from markitdown import MarkItDown
md = MarkItDown()
# Should not raise an error
```

### 2. RAG Search Fails with OpenAI Authentication Error

**Symptoms:**
```
openai.AuthenticationError: Error code: 401 - {'error': {'message': 'Incorrect API key provided...
```

**Cause:** Invalid or missing OpenAI API key

**Solution:**

1. **Get a valid API key:**
   - Go to https://platform.openai.com/api-keys
   - Create a new API key
   - Make sure you have credits/billing enabled

2. **Update your `.env` file:**
   ```bash
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```

3. **Restart your FastAPI server:**
   ```bash
   # Stop the current server (Ctrl+C)
   # Start it again
   uvicorn backend.app:app --reload
   ```

**Note:** The test script will now gracefully skip RAG search and AI agent tests if OpenAI key is invalid.

### 3. Database Connection Errors

**Symptoms:**
```
Could not connect to database
sqlalchemy.exc.OperationalError
```

**Solutions:**

1. **Check PostgreSQL is running:**
   ```bash
   # On macOS with Homebrew
   brew services list | grep postgres

   # Start if not running
   brew services start postgresql
   ```

2. **Verify database credentials in `.env`:**
   ```bash
   user=your_db_user
   password=your_db_password
   host=localhost
   port=5432
   dbname=your_database_name
   ```

3. **Test database connection:**
   ```bash
   psql -h localhost -U your_db_user -d your_database_name
   ```

4. **Check database exists:**
   ```sql
   \l  -- List all databases
   ```

### 4. Module Not Found Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'requests'
ModuleNotFoundError: No module named 'reportlab'
```

**Solution:**
```bash
pip3 install -r requirements.txt
```

**If using a virtual environment:**
```bash
# Activate your virtual environment first
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Then install
pip install -r requirements.txt
```

## Step-by-Step Diagnostic Process

### Step 1: Check Environment Configuration

```bash
python3 check_environment.py
```

This will show you:
- ✓ Which environment variables are set
- ✗ Which are missing
- ✓ Which Python modules are installed
- ✗ Which need to be installed

### Step 2: Fix Missing Configuration

Based on the output from Step 1:

1. **If database vars are missing:** Update `.env` with database credentials
2. **If Supabase vars are missing:** Update `.env` with Supabase credentials
3. **If OpenAI key is missing:** Update `.env` with OpenAI API key
4. **If modules are missing:** Run `pip3 install -r requirements.txt`

### Step 3: Initialize Database and Storage

```bash
python3 -m backend.setup
```

This creates:
- Database tables
- Supabase storage bucket

### Step 4: Start FastAPI Server

```bash
uvicorn backend.app:app --reload
```

Keep this running in a separate terminal.

### Step 5: Run Tests

```bash
# Clear existing data and run full test suite
python3 test_backend.py --clear
```

## Partial Testing (When Some Features Don't Work)

The test script is now designed to skip tests for features that aren't working:

### Test Without PDF Upload
If Supabase is not configured, you can still test:
- ✓ User CRUD operations
- ✓ Document CRUD operations
- ✓ Permission management
- ✗ PDF uploads (will fail but continue)
- ✗ RAG search (requires PDFs)
- ✗ AI agent (requires RAG)

### Test Without OpenAI
If OpenAI API key is invalid, you can still test:
- ✓ User operations
- ✓ Document operations
- ✓ PDF uploads (if Supabase is configured)
- ✗ RAG search (will fail gracefully)
- ✗ AI agent (will be skipped)

## Understanding Error Messages

### From Test Script

| Message | Meaning | Action |
|---------|---------|--------|
| `✗ Failed to upload PDF: 500` | Server error during PDF processing | Check FastAPI logs, verify Supabase config |
| `⚠ Server error (500) - Check FastAPI server logs` | Generic server error | Look at terminal running uvicorn |
| `✗ Search failed: 401` | Invalid OpenAI API key | Update OPENAI_API_KEY in .env |
| `✗ Could not connect to API` | FastAPI server not running | Start with `uvicorn backend.app:app --reload` |
| `✗ Email already exists` | Test users from previous run | Use `--clear` flag or run `clear_test_data.py` |

### From FastAPI Server Logs

| Error | Cause | Solution |
|-------|-------|----------|
| `ValueError: Missing SUPABASE_URL` | .env missing Supabase config | Add SUPABASE_URL to .env |
| `requests.exceptions.HTTPError: 401` | Invalid Supabase key | Verify SUPABASE_KEY in .env |
| `openai.AuthenticationError` | Invalid OpenAI key | Update OPENAI_API_KEY |
| `sqlalchemy.exc.OperationalError` | Database connection issue | Check database is running and credentials |
| `Failed to convert PDF to markdown` | MarkItDown issue | Reinstall: `pip3 install --upgrade markitdown` |

## Getting More Information

### Enable Verbose Logging in FastAPI

Edit `backend/app.py` and add logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check What's Working

Run the simple diagnostic:
```bash
python3 test_pdf_upload.py
```

This performs a minimal test with detailed output at each step.

## Quick Fixes Summary

```bash
# Fix 1: Install dependencies
pip3 install -r requirements.txt

# Fix 2: Setup database and storage
python3 -m backend.setup

# Fix 3: Check environment
python3 check_environment.py

# Fix 4: Update .env file with valid credentials
# Edit .env manually

# Fix 5: Clear old test data
python3 clear_test_data.py

# Fix 6: Run tests
python3 test_backend.py --clear
```

## Still Having Issues?

1. **Check the FastAPI server terminal** - The actual error is always shown there
2. **Share the full error traceback** - Copy the entire error from the terminal
3. **Verify each service separately:**
   - Database: Can you connect with `psql`?
   - Supabase: Can you access the dashboard?
   - OpenAI: Does your API key work on platform.openai.com?

## Success Criteria

When everything is working, you should see:

```
✓ API is running!
✓ Created user: Admin User (admin)
✓ Created document: Project Requirements Document
✓ Uploaded PDF version 1 for document...
✓ Granted admin permission to user...
✓ Search completed: found 3 results
✓ Agent query completed
```

If you see these checkmarks, your backend is fully functional!
