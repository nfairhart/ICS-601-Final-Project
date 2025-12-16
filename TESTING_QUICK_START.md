# Testing Quick Start Guide

## Quick Commands

### 1. Clear and Test (Recommended for fresh start)

```bash
python test_backend.py --clear
```

This single command will:
- ✓ Clear all existing database records
- ✓ Delete all PDFs from storage bucket
- ✓ Run comprehensive tests
- ✓ Create 3 users with different roles
- ✓ Create 5 documents with 3 PDF versions each
- ✓ Test all API endpoints

### 2. Clear Only (Manual cleanup)

```bash
python clear_test_data.py
```

Use this to clean up without running tests. You'll be asked to confirm.

### 3. Test Only (Keep existing data)

```bash
python test_backend.py
```

⚠️ May fail if test users already exist due to duplicate email constraints.

## Prerequisites Checklist

Before running tests, ensure:

- [ ] FastAPI server is running
  ```bash
  uvicorn backend.app:app --reload
  ```

- [ ] Dependencies are installed
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Database is accessible (check `.env` file)

- [ ] Supabase credentials are configured (check `.env` file)

## What Gets Created

### Users (3)
| Email | Name | Role | Access Level |
|-------|------|------|--------------|
| admin@example.com | Admin User | admin | All 5 documents (admin) |
| editor@example.com | Editor User | editor | Documents 1-3 (write) |
| viewer@example.com | Viewer User | viewer | Documents 1-2 (read) |

### Documents (5)
1. **Project Requirements Document** - 3 versions
2. **Technical Architecture Spec** - 3 versions
3. **API Documentation** - 3 versions
4. **User Manual** - 3 versions
5. **Security Policy** - 3 versions

### Total Test Data
- **3 users** with varying permissions
- **5 documents** across different topics
- **15 PDF files** (3 versions per document)
- **8 permission grants** (various access levels)

## Expected Test Duration

- Cleanup: ~5-10 seconds
- Full test suite: ~3-5 minutes (includes PDF generation, uploads, and RAG indexing)

## Common Issues

### "Could not connect to API"
**Solution:** Start the FastAPI server:
```bash
uvicorn backend.app:app --reload
```

### "Email already exists"
**Solution:** Run with `--clear` flag to remove existing test users:
```bash
python test_backend.py --clear
```

### "Failed to upload PDF"
**Solution:** Check Supabase credentials in `.env` file

### "No search results found"
**Solution:** Wait longer for RAG indexing (script waits 5 seconds by default)

## Viewing Results

After tests complete, you can:

1. **Check the API docs:**
   - Visit http://localhost:8000/docs
   - Use the Swagger UI to explore data

2. **Query the database directly:**
   ```sql
   SELECT COUNT(*) FROM users;           -- Should be 3
   SELECT COUNT(*) FROM documents;       -- Should be 5
   SELECT COUNT(*) FROM document_versions; -- Should be 15
   ```

3. **Check Supabase storage:**
   - Log into your Supabase dashboard
   - Navigate to Storage → pdfs bucket
   - You should see 5 folders (one per document)

## Cleanup After Testing

When you're done testing and want to clean up:

```bash
python clear_test_data.py
```

This removes all test data from both database and storage.

## Help

For detailed information, see [TEST_README.md](TEST_README.md)

For test script options:
```bash
python test_backend.py --help
```
