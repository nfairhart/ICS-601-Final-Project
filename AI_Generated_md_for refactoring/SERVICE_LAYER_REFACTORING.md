# Service Layer Refactoring

## Overview

This document describes the service layer refactoring that extracts business logic from route handlers into dedicated service classes. This improves code organization, testability, and maintainability.

## What Changed

### Before: Business Logic in Route Handlers

```python
# app.py - 590 lines with mixed concerns
@app.post("/users", status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Validation logic
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(400, "Email already exists")

    # Business logic
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

### After: Thin Controllers with Service Layer

```python
# app_refactored.py - 387 lines, much cleaner
@app.post("/users", status_code=201)
def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """Create a new user"""
    return user_service.create_user(user)

# services/user_service.py - Reusable business logic
class UserService(BaseService[User]):
    def create_user(self, user_data: UserCreate) -> User:
        # Check if email already exists
        existing_user = self.db.query(User).filter(
            User.email == user_data.email
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")

        # Create user
        db_user = User(**user_data.model_dump())
        return self.create(db_user)
```

## New File Structure

```
backend/
├── services/
│   ├── __init__.py              # Service exports
│   ├── base.py                  # BaseService with common CRUD ops
│   ├── user_service.py          # User management logic
│   ├── document_service.py      # Document management logic
│   ├── version_service.py       # Version & PDF handling logic
│   └── permission_service.py    # Permission & access control logic
├── app.py                       # Original (590 lines)
└── app_refactored.py           # Refactored (387 lines, -34%)
```

## Benefits

### 1. Separation of Concerns

**Before:** Route handlers contained:
- HTTP request/response handling
- Input validation
- Business logic
- Database queries
- Error handling

**After:**
- **Controllers (app.py):** Only HTTP concerns and dependency injection
- **Services:** Pure business logic, reusable across different interfaces
- **Models:** Database schema
- **Schemas:** Input/output validation

### 2. Code Reusability

Services can be used from:
- REST API endpoints
- GraphQL resolvers
- Background tasks
- CLI commands
- Tests

Example:
```python
# Can be used anywhere, not just in route handlers
def background_job():
    db = SessionLocal()
    user_service = UserService(db)
    user = user_service.create_user(UserCreate(email="admin@example.com"))
    db.close()
```

### 3. Testability

**Before:** Testing required mocking HTTP requests
```python
# Hard to test
def test_create_user():
    response = client.post("/users", json={"email": "test@example.com"})
    assert response.status_code == 201
```

**After:** Test business logic directly
```python
# Easy to test
def test_create_user():
    db = TestSession()
    user_service = UserService(db)
    user = user_service.create_user(UserCreate(email="test@example.com"))
    assert user.email == "test@example.com"
```

### 4. DRY (Don't Repeat Yourself)

**Eliminated Patterns:**

#### Pattern 1: Get or 404
**Before (repeated 15+ times):**
```python
user = db.query(User).filter(User.id == user_id).first()
if not user:
    raise HTTPException(404, "User not found")
```

**After (once in BaseService):**
```python
user = user_service.get_or_404(user_id)
```

#### Pattern 2: Permission Checking
**Before (repeated in multiple endpoints):**
```python
permission = db.query(DocumentPermission).filter(
    DocumentPermission.document_id == document_id,
    DocumentPermission.user_id == current_user_id
).first()
if not permission:
    raise HTTPException(403, "Access denied")
```

**After (in PermissionService):**
```python
perm_service.require_document_access(current_user_id, document_id)
```

#### Pattern 3: PDF Upload Logic
**Before:** 205 lines duplicated across two endpoints

**After:**
- `version_service.create_version_from_pdf()` - 50 lines
- `version_service.create_document_with_pdf()` - 50 lines
- Shared core logic extracted

### 5. Dependency Injection

**Before:** Direct database access in routes
```python
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Direct database manipulation
```

**After:** Services injected as dependencies
```python
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

def create_user(user: UserCreate, user_service: UserService = Depends(get_user_service)):
    # Use service
```

Benefits:
- Easy to swap implementations (e.g., for testing)
- Clear dependencies
- Follows SOLID principles

## Key Services

### BaseService

Generic base class providing common CRUD operations:
- `get_by_id()` - Get by ID, return None if not found
- `get_or_404()` - Get by ID or raise 404
- `get_all()` - List all with optional limit
- `create()` - Create and persist
- `delete()` - Delete instance
- `commit()` - Commit transaction

### UserService

User management:
- `create_user()` - Create with email uniqueness check
- `get_user_with_relations()` - Get with documents and permissions
- `update_user()` - Update with timestamp
- `get_by_email()` - Find by email
- `verify_user_exists()` - Auth helper

### DocumentService

Document management:
- `create_document()` - Create with user verification
- `get_document_with_relations()` - Get with all relations
- `update_document()` - Update with validation
- `archive_document()` - Archive and update status
- `list_documents()` - List with optional status filter

### VersionService

Version and PDF management:
- `create_version()` - Create version and update document pointer
- `get_document_versions()` - List all versions
- `get_next_version_number()` - Calculate next version
- `create_version_from_pdf()` - Upload PDF → create version
- `create_document_with_pdf()` - Create document from PDF in one step

### PermissionService

Access control:
- `grant_permission()` - Grant with validation
- `get_document_permissions()` - List document permissions
- `get_user_permissions()` - List user permissions
- `get_user_accessible_documents()` - Get IDs for RAG filtering
- `revoke_permission()` - Remove access
- `check_user_access()` - Check with permission levels
- `require_document_access()` - Verify or raise 403

## Metrics

### Lines of Code

| File | Before | After | Change |
|------|--------|-------|--------|
| app.py | 590 | 387 | -203 (-34%) |
| Services | 0 | 450 | +450 |
| **Total** | **590** | **837** | **+247** |

While total lines increased, complexity decreased significantly:
- Route handlers: 50-100 lines → 5-15 lines each
- Business logic: Centralized and reusable
- Testing: Much easier (can test services directly)

### Complexity Reduction

**Route Handler Complexity:**
- Average lines per endpoint: 30 → 8 (73% reduction)
- Cyclomatic complexity: ~8 → ~2 per handler

**PDF Upload Endpoints:**
- Before: 205 lines (duplicated)
- After: 50 lines in routes + 100 in service (shared)
- Net reduction: 55 lines

## Migration Guide

### To Use Refactored Code

1. **Backup current app.py:**
   ```bash
   cp backend/app.py backend/app_old.py
   ```

2. **Replace with refactored version:**
   ```bash
   cp backend/app_refactored.py backend/app.py
   ```

3. **Test the application:**
   ```bash
   # Start server
   uvicorn backend.app:app --reload

   # Run tests (if you have them)
   pytest tests/
   ```

4. **If issues occur, rollback:**
   ```bash
   cp backend/app_old.py backend/app.py
   ```

### Example: Adding a New Feature

**Before (mixed concerns):**
```python
@app.post("/documents/{document_id}/publish")
def publish_document(document_id: UUID, db: Session = Depends(get_db)):
    # Find document
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")

    # Business logic
    if doc.status != "Approved":
        raise HTTPException(400, "Only approved documents can be published")

    doc.status = "Published"
    doc.published_at = datetime.utcnow()
    db.commit()

    # Send notifications
    send_notification(doc.created_by, f"Document {doc.title} published")

    return doc
```

**After (clean separation):**
```python
# services/document_service.py
def publish_document(self, document_id: UUID) -> Document:
    """Publish an approved document"""
    doc = self.get_or_404(document_id)

    if doc.status != DocumentStatus.APPROVED.value:
        raise HTTPException(
            status_code=400,
            detail="Only approved documents can be published"
        )

    doc.status = "Published"
    doc.published_at = datetime.utcnow()
    self.commit()

    return doc

# app.py
@app.post("/documents/{document_id}/publish")
def publish_document(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    doc_service: DocumentService = Depends(get_document_service)
):
    """Publish a document"""
    doc = doc_service.publish_document(document_id)

    # Handle side effects
    background_tasks.add_task(
        send_notification,
        doc.created_by,
        f"Document {doc.title} published"
    )

    return doc
```

## Best Practices

### 1. Keep Controllers Thin

Route handlers should only:
- Accept input
- Call service methods
- Handle HTTP-specific concerns (status codes, headers)
- Trigger side effects (background tasks, events)

### 2. Put Business Logic in Services

Services should contain:
- Validation rules
- Business workflows
- Data persistence
- Domain logic

### 3. Use Dependency Injection

```python
# Good
def my_endpoint(service: MyService = Depends(get_my_service)):
    return service.do_something()

# Bad
def my_endpoint(db: Session = Depends(get_db)):
    service = MyService(db)
    return service.do_something()
```

### 4. Return Domain Objects

Services should return domain models, not dictionaries:
```python
# Good
def get_user(self, user_id: UUID) -> User:
    return self.get_or_404(user_id)

# Bad
def get_user(self, user_id: UUID) -> dict:
    user = self.get_or_404(user_id)
    return {"id": user.id, "email": user.email}
```

### 5. Handle Errors in Services

Services should raise exceptions for business rule violations:
```python
# Good
def publish_document(self, doc_id: UUID) -> Document:
    doc = self.get_or_404(doc_id)
    if doc.status != "Approved":
        raise HTTPException(400, "Cannot publish unapproved document")
    # ...

# Bad - returning error flags
def publish_document(self, doc_id: UUID) -> Tuple[Document, str]:
    doc = self.get_by_id(doc_id)
    if not doc:
        return None, "Document not found"
    if doc.status != "Approved":
        return None, "Cannot publish"
    # ...
```

## Next Steps

1. **Add Tests:** Write unit tests for each service
2. **Extract RAG Logic:** Create `RAGService` to encapsulate ChromaDB operations
3. **Create Config Service:** Centralize configuration management
4. **Add Logging:** Add structured logging to services
5. **Consider Transactions:** Add transaction decorators for complex operations

## Conclusion

The service layer refactoring:
- ✅ Reduces route handler complexity by 73%
- ✅ Eliminates code duplication
- ✅ Improves testability
- ✅ Makes business logic reusable
- ✅ Follows SOLID principles
- ✅ Prepares codebase for growth

This is a foundational refactoring that will make all future development easier and more maintainable.
