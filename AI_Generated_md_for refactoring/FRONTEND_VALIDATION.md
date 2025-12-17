# Frontend Validation Updates

## Overview

The frontend has been updated to work with the new backend Pydantic validation schemas, including proper enum values, error handling, and user-friendly validation error messages.

## Changes Made

### 1. Document Management ([frontend/pages/documents.py](frontend/pages/documents.py))

#### Updated Status Enum Values
Added all valid document status options throughout the UI:

**Status Filter Dropdown:**
- Draft
- Review (NEW)
- Approved (NEW)
- Archived

**Document Edit Form:**
- All four status options now available when editing documents

#### Updated `update_document()` Function
**Before:**
```python
# Sent as query parameters
response = await client.patch(
    f"{API_BASE}/documents/{document_id}",
    params=params  # ❌ Query params
)
```

**After:**
```python
# Sends as JSON body with validation
response = await client.patch(
    f"{API_BASE}/documents/{document_id}",
    json=data  # ✅ JSON body
)
```

**New Features:**
- ✅ Strips whitespace from all string fields
- ✅ Converts empty strings to `None` for optional fields
- ✅ Parses and displays Pydantic validation errors
- ✅ Only sends fields that have values

**Example Validation Error Display:**
```
Validation errors: title: String should have at most 500 characters; status: Input should be 'Draft', 'Review', 'Approved' or 'Archived'
```

### 2. User Management ([frontend/pages/users.py](frontend/pages/users.py))

#### Added Role Dropdown
**Before:** Free-text input field
```python
Input(
    type="text",
    name="role",
    placeholder="e.g., editor, admin, viewer"  # ❌ No validation
)
```

**After:** Dropdown with valid enum values
```python
Select(
    Option("-- Select Role (Optional) --", value=""),
    Option("Viewer", value="viewer"),
    Option("Editor", value="editor"),
    Option("Admin", value="admin"),
    Option("Owner", value="owner"),
    name="role"
)
```

#### Updated User Functions
Both `create_user()` and `update_user()` now:
- ✅ Strip whitespace from all inputs
- ✅ Parse and display validation errors
- ✅ Handle empty string edge cases
- ✅ Provide clear error messages

**Example Error Handling:**
```python
try:
    error_data = e.response.json()
    if "detail" in error_data and isinstance(error_data["detail"], list):
        errors = [f"{err['loc'][-1]}: {err['msg']}" for err in error_data["detail"]]
        return None, "Validation errors: " + "; ".join(errors)
except:
    return None, f"Error: {e.response.text}"
```

### 3. Search & Agent Pages

These pages already send the X-User-ID header correctly and don't require changes for enum validation.

## Validation Rules Enforced

### Document Fields

| Field | Frontend Validation | Backend Validation |
|-------|-------------------|-------------------|
| Title | Required, trimmed | 1-500 chars, no whitespace-only |
| Description | Optional, trimmed | Max 5000 chars |
| Status | Dropdown (enum) | Must be valid DocumentStatus enum |

### User Fields

| Field | Frontend Validation | Backend Validation |
|-------|-------------------|-------------------|
| Email | Required, type="email" | Valid email format (EmailStr) |
| Full Name | Optional, trimmed | 1-200 chars, no whitespace-only |
| Role | Dropdown (enum) | Must be valid UserRole enum |

## User Experience Improvements

### 1. Clear Error Messages

**Before:**
```
Error: 422 Unprocessable Entity
```

**After:**
```
Validation errors: title: String should have at most 500 characters; status: Input should be 'Draft', 'Review', 'Approved' or 'Archived'
```

### 2. Dropdown Validation

Users can no longer enter invalid enum values because they select from predefined options.

**Status Options:**
- Draft
- Review
- Approved
- Archived

**Role Options:**
- Viewer
- Editor
- Admin
- Owner

### 3. Automatic Data Cleaning

- Whitespace is automatically trimmed
- Empty strings converted to `None` for optional fields
- Only non-empty fields are sent to the API

## Testing Frontend Changes

### Test Document Status

1. **Navigate to Documents**
2. **Click "Create New Document"**
3. **Create a document** (status will be "Draft" by default)
4. **Edit the document**
5. **Try all status options** from the dropdown:
   - Draft
   - Review
   - Approved
   - Archived
6. **Verify filter works** with all four options

### Test Document Validation

1. **Try to create a document with:**
   - Empty title → Should show error
   - Very long title (>500 chars) → Should show validation error
   - Valid data → Should succeed

### Test User Roles

1. **Navigate to Users**
2. **Click "Create New User"**
3. **Try each role from dropdown:**
   - Leave blank (optional)
   - Viewer
   - Editor
   - Admin
   - Owner
4. **Verify all roles save correctly**

### Test User Validation

1. **Try to create a user with:**
   - Invalid email format → Should show error
   - Whitespace-only full name → Converted to empty/None
   - Valid data → Should succeed

## Migration Notes

### Existing Data

If you have existing documents in the database with old status values, they may not match the new enums. Run this query to check:

```sql
SELECT DISTINCT status FROM documents;
```

If you find invalid statuses, update them:

```sql
UPDATE documents
SET status = 'Draft'
WHERE status NOT IN ('Draft', 'Review', 'Approved', 'Archived');
```

### Frontend Compatibility

The frontend now requires:
- Backend running with new schemas ([backend/schemas.py](backend/schemas.py))
- FastAPI with updated endpoints
- Pydantic v2 installed

## Common Validation Errors

### 1. Status Not Valid

**Error:**
```
status: Input should be 'Draft', 'Review', 'Approved' or 'Archived'
```

**Cause:** Trying to set an invalid status value

**Fix:** Use the dropdown to select a valid status

### 2. Email Invalid

**Error:**
```
email: value is not a valid email address
```

**Cause:** Email doesn't match standard format

**Fix:** Enter a valid email (e.g., user@example.com)

### 3. String Too Long

**Error:**
```
title: String should have at most 500 characters
```

**Cause:** Title exceeds maximum length

**Fix:** Shorten the title to 500 characters or less

### 4. Empty String

**Error:**
```
title: title cannot be empty or whitespace
```

**Cause:** Required field is empty or contains only spaces

**Fix:** Enter actual content in the field

## Future Enhancements

### 1. Client-Side Validation

Add JavaScript validation before submission:

```javascript
function validateForm() {
    const title = document.getElementById('title').value;
    if (title.length > 500) {
        alert('Title must be 500 characters or less');
        return false;
    }
    return true;
}
```

### 2. Real-Time Validation

Show validation errors as the user types:

```javascript
<Input
    type="text"
    name="title"
    oninput="validateTitle(this)"
    maxlength="500"
/>
```

### 3. Character Counter

Display remaining characters for length-limited fields:

```python
Div(
    Label("Title (500 chars max)"),
    Input(type="text", name="title", id="title", maxlength="500"),
    Span(id="char-count", style="font-size: 12px; color: #666;")
)
```

### 4. Better Error Styling

Style validation errors inline with fields:

```python
Div(
    Input(type="text", name="title", cls="is-invalid" if error else ""),
    error and Span(error, cls="field-error") or None
)
```

## Backwards Compatibility

### Breaking Changes

❌ **Query parameters replaced with JSON body** for PATCH requests
- Old: `PATCH /documents/{id}?title=New+Title`
- New: `PATCH /documents/{id}` with JSON `{"title": "New Title"}`

❌ **Status values must match enum** (capital first letter)
- Old: `"draft"`, `"archived"`
- New: `"Draft"`, `"Review"`, `"Approved"`, `"Archived"`

❌ **Role values must match enum** (lowercase)
- Old: Any string
- New: `"viewer"`, `"editor"`, `"admin"`, `"owner"`

### Migration Script

If you have external clients using the API, update them:

```python
# Old way
requests.patch(
    f"{API_BASE}/documents/{id}",
    params={"title": "New Title", "status": "draft"}  # ❌
)

# New way
requests.patch(
    f"{API_BASE}/documents/{id}",
    json={"title": "New Title", "status": "Draft"}  # ✅
)
```

## Summary

The frontend now:
- ✅ Sends data in the correct format (JSON body)
- ✅ Uses valid enum values for status and roles
- ✅ Handles validation errors gracefully
- ✅ Provides clear error messages to users
- ✅ Strips whitespace and cleans input data
- ✅ Uses dropdowns instead of free-text for enums

All user-facing forms now validate properly and provide helpful feedback when validation fails.
