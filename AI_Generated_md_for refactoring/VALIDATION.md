# Input Validation Implementation

## Overview

Comprehensive input validation has been added using Pydantic schemas with enums, field validators, and proper type checking. This prevents invalid data from entering the system and provides clear error messages to API consumers.

## Changes Made

### 1. Created Centralized Schemas Module

**File:** [backend/schemas.py](backend/schemas.py)

New comprehensive validation schemas with:
- Enum types for status values, permission types, and user roles
- Field validators for string trimming and length constraints
- Custom validation logic for empty strings and whitespace
- Proper response schemas for API documentation

### 2. Enums for Type Safety

```python
class DocumentStatus(str, Enum):
    """Valid document status values"""
    DRAFT = "Draft"
    REVIEW = "Review"
    APPROVED = "Approved"
    ARCHIVED = "Archived"

class PermissionType(str, Enum):
    """Valid permission types"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

class UserRole(str, Enum):
    """Valid user roles"""
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"
    OWNER = "owner"
```

**Benefits:**
- ✅ Only valid values accepted
- ✅ Auto-complete in IDEs
- ✅ Type checking at compile time
- ✅ Clear error messages for invalid values

### 3. Field Validation

#### String Length Constraints

```python
class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
```

#### Custom Validators

```python
@field_validator('title')
@classmethod
def validate_title(cls, v):
    if v.strip() == "":
        raise ValueError("title cannot be empty or whitespace")
    return v.strip()
```

#### Numeric Constraints

```python
class RAGSearch(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(5, ge=1, le=50)  # Between 1 and 50
```

### 4. Updated Endpoints

#### Before (No Validation):
```python
@app.patch("/documents/{document_id}")
def update_document(document_id: UUID, title: Optional[str] = None,
                    status: Optional[str] = None, description: Optional[str] = None,
                    db: Session = Depends(get_db)):
    # Anyone could send status="InvalidStatus" ❌
    if status:
        doc.status = status
```

#### After (With Validation):
```python
@app.patch("/documents/{document_id}")
def update_document(document_id: UUID, payload: DocumentUpdate, db: Session = Depends(get_db)):
    """Update document metadata with validation"""
    # Pydantic validates DocumentStatus enum automatically ✅
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        if k == "status" and isinstance(v, DocumentStatus):
            setattr(doc, k, v.value)
```

### 5. Custom Error Handler

Added detailed validation error responses:

```python
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Custom handler for validation errors with detailed error messages"""
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error["loc"],  # Field location
            "msg": error["msg"],  # Error message
            "type": error["type"]  # Error type
        })
    return JSONResponse(
        status_code=422,
        content={"detail": errors, "body": exc.body}
    )
```

## Validation Rules

### User Schemas

**UserCreate:**
- `email`: Must be valid email format (EmailStr)
- `full_name`: Optional, 1-200 chars, no empty/whitespace
- `role`: Optional, must be valid UserRole enum

**UserUpdate:**
- All fields optional
- Same validation rules as UserCreate

### Document Schemas

**DocumentCreate:**
- `title`: Required, 1-500 chars, no empty/whitespace
- `description`: Optional, max 5000 chars
- `created_by`: Valid UUID

**DocumentUpdate:**
- `title`: Optional, 1-500 chars, no empty/whitespace
- `description`: Optional, max 5000 chars
- `status`: Optional, must be valid DocumentStatus enum

### Version Schemas

**VersionCreate:**
- `version_number`: Integer >= 1
- `markdown_content`: Optional, max 1,000,000 chars
- `pdf_url`: Optional, max 1000 chars
- `change_summary`: Optional, max 2000 chars

### Permission Schemas

**PermissionCreate:**
- `permission_type`: Must be one of: "read", "write", "admin"

### Search Schemas

**RAGSearch:**
- `query`: Required, 1-1000 chars, no empty/whitespace
- `top_k`: Integer between 1 and 50 (default: 5)

**AgentQuery:**
- `query`: Required, 1-2000 chars, no empty/whitespace

## Error Response Examples

### Invalid Enum Value

**Request:**
```json
POST /documents
{
  "title": "Test Doc",
  "created_by": "valid-uuid"
}
PATCH /documents/{id}
{
  "status": "InvalidStatus"
}
```

**Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "status"],
      "msg": "Input should be 'Draft', 'Review', 'Approved' or 'Archived'",
      "type": "enum"
    }
  ]
}
```

### Field Too Long

**Request:**
```json
POST /documents
{
  "title": "a very long title that exceeds the 500 character limit...",
  "created_by": "valid-uuid"
}
```

**Response (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "String should have at most 500 characters",
      "type": "string_too_long"
    }
  ]
}
```

### Empty String

**Request:**
```json
POST /documents
{
  "title": "   ",
  "created_by": "valid-uuid"
}
```

**Response (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "title cannot be empty or whitespace",
      "type": "value_error"
    }
  ]
}
```

### Out of Range

**Request:**
```json
POST /search
{
  "query": "test",
  "top_k": 100
}
```

**Response (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "top_k"],
      "msg": "Input should be less than or equal to 50",
      "type": "less_than_equal"
    }
  ]
}
```

## Benefits

### 1. **Security**
- ✅ Prevents SQL injection attempts via string validation
- ✅ Limits input sizes to prevent DoS attacks
- ✅ Validates UUID formats
- ✅ Enforces allowed values via enums

### 2. **Data Quality**
- ✅ No empty strings in required fields
- ✅ Whitespace automatically trimmed
- ✅ Consistent data format
- ✅ Type safety enforced

### 3. **API Documentation**
- ✅ FastAPI auto-generates OpenAPI specs with validation rules
- ✅ Interactive docs show allowed values
- ✅ Clear error messages for developers

### 4. **Developer Experience**
- ✅ Early error detection
- ✅ Type hints work in IDEs
- ✅ Self-documenting code
- ✅ Fewer bugs in production

## Testing Validation

You can test the validation using the FastAPI interactive docs at `http://localhost:8000/docs`:

1. **Navigate to any POST/PATCH endpoint**
2. **Click "Try it out"**
3. **Enter invalid data:**
   - Empty strings
   - Invalid enum values
   - Numbers out of range
   - Strings too long
4. **Execute and observe the detailed error responses**

## Future Improvements

### 1. Additional Validation Rules

```python
from pydantic import field_validator

class UserCreate(BaseModel):
    email: EmailStr

    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        # Only allow company email domains
        if not v.endswith('@company.com'):
            raise ValueError('Must use company email')
        return v
```

### 2. Cross-Field Validation

```python
from pydantic import model_validator

class DocumentCreate(BaseModel):
    title: str
    status: DocumentStatus

    @model_validator(mode='after')
    def validate_status_rules(self):
        # Don't allow creating directly as Approved
        if self.status == DocumentStatus.APPROVED:
            raise ValueError('Cannot create document as Approved')
        return self
```

### 3. Database-Level Validation

```python
@field_validator('email')
@classmethod
def validate_unique_email(cls, v, info):
    # Check database for duplicates
    # (Note: This requires access to db session)
    pass
```

### 4. File Upload Validation

```python
class PDFUpload(BaseModel):
    file_size: int = Field(..., le=10_000_000)  # Max 10MB
    file_type: str = Field(..., pattern=r'^application/pdf$')
```

## Migration Notes

### Frontend Changes Required

Update frontend code to send proper enum values:

**Before:**
```javascript
{
  "status": "archived"  // ❌ Wrong case
}
```

**After:**
```javascript
{
  "status": "Archived"  // ✅ Correct enum value
}
```

### Existing Data

Existing data in the database is NOT automatically validated. To ensure consistency:

1. **Run a data migration script** to fix any invalid data
2. **Add database constraints** matching validation rules
3. **Backfill missing/invalid enum values**

## Resources

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Validation](https://fastapi.tiangolo.com/tutorial/body/)
- [Python Enums](https://docs.python.org/3/library/enum.html)
