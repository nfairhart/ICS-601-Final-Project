# Security Documentation

## Overview

This document describes the security measures implemented in the Document Control System and provides guidance for further security improvements.

## Current Security Implementation

### 1. CORS (Cross-Origin Resource Sharing)

**Location:** [backend/app.py:22-32](backend/app.py#L22-L32)

**Implementation:**
- Replaced wildcard `allow_origins=["*"]` with environment-configurable origins
- Only allows specific domains listed in `ALLOWED_ORIGINS` environment variable
- Restricts allowed HTTP methods to: GET, POST, PUT, PATCH, DELETE, OPTIONS
- Limits allowed headers to: Content-Type, Authorization, Accept, X-User-ID

**Configuration:**
```bash
# .env file
ALLOWED_ORIGINS=http://localhost:5001,http://127.0.0.1:5001
```

**Production Deployment:**
When deploying to production, update `ALLOWED_ORIGINS` to include only your production domain:
```bash
ALLOWED_ORIGINS=https://yourdomain.com
```

### 2. User Authentication (Header-Based)

**Location:** [backend/app.py:34-72](backend/app.py#L34-L72)

**Implementation:**
- Search and Agent endpoints now require `X-User-ID` header
- User ID is validated from the header, not from request body
- Prevents users from impersonating other users
- Verifies user exists in database before processing requests

**How it Works:**
1. Client sends `X-User-ID` header with user's UUID
2. Backend validates the UUID format
3. Backend verifies the user exists in the database
4. Backend uses the authenticated user ID for permission checks

**Example Request:**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 123e4567-e89b-12d3-a456-426614174000" \
  -d '{"query": "project proposal", "top_k": 5}'
```

### 3. Permission Validation

**Location:** [backend/app.py:522-559](backend/app.py#L522-L559)

**Implementation:**
- Search endpoint only returns documents the authenticated user has permission to access
- Document permissions are checked against the authenticated user ID from header
- Users cannot search documents they don't have access to

**Affected Endpoints:**
- `POST /search` - RAG document search
- `POST /agent/query` - AI agent queries

## Security Vulnerabilities Still Present

### ⚠️ WARNING: Development-Only Authentication

The current header-based authentication (`X-User-ID`) is **NOT SECURE** for production use.

**Why it's insecure:**
- Headers can be easily manipulated by any client
- No cryptographic verification of user identity
- No session management or token expiration
- No protection against replay attacks

**This is acceptable for:**
- Local development
- Internal testing
- Proof-of-concept demonstrations

**This is NOT acceptable for:**
- Production deployments
- Public internet access
- Any environment with untrusted users

## Recommended Production Security Improvements

### 1. Implement JWT Authentication (High Priority)

Replace header-based auth with JWT tokens:

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta

security = HTTPBearer()

def create_access_token(user_id: UUID) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "sub": str(user_id),
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Validate JWT token and return user"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id = UUID(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(401, "Invalid user")
        return user
    except JWTError:
        raise HTTPException(401, "Invalid token")
```

**Required packages:**
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

### 2. Add Password Authentication

Implement user login with password hashing:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@app.post("/auth/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login endpoint - returns JWT token"""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    access_token = create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}
```

### 3. Add HTTPS in Production

**Never deploy without HTTPS:**
- Prevents man-in-the-middle attacks
- Protects credentials in transit
- Required for secure cookie handling

**Deployment options:**
- Use a reverse proxy (nginx, Caddy) with Let's Encrypt
- Deploy behind a cloud provider's load balancer (AWS ALB, Google Cloud Load Balancer)
- Use a platform with built-in HTTPS (Heroku, Railway, Render)

### 4. Environment Variable Security

**Current risk:** `.env` file contains sensitive credentials in plain text

**Improvements:**
- Never commit `.env` to git (already in `.gitignore`)
- Use secret management services in production:
  - AWS Secrets Manager
  - Google Cloud Secret Manager
  - Azure Key Vault
  - HashiCorp Vault
- Rotate credentials regularly
- Use different credentials for each environment (dev, staging, prod)

### 5. Rate Limiting

Add rate limiting to prevent abuse:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/search")
@limiter.limit("10/minute")
def search_documents(...):
    ...
```

### 6. Input Validation & Sanitization

Add comprehensive validation:
- Validate all user inputs with Pydantic
- Sanitize file uploads
- Validate document permissions on every operation
- Add SQL injection protection (already handled by SQLAlchemy ORM)
- Validate file types and sizes for PDF uploads

### 7. Audit Logging

Log all security-relevant events:
- Authentication attempts (success and failure)
- Permission changes
- Document access
- Administrative actions

## Security Checklist for Production

- [ ] Replace header-based auth with JWT tokens
- [ ] Implement user registration and login with password hashing
- [ ] Enable HTTPS/TLS
- [ ] Move secrets to secure secret management service
- [ ] Add rate limiting
- [ ] Enable database connection encryption
- [ ] Set up audit logging
- [ ] Implement session management
- [ ] Add CSRF protection for state-changing operations
- [ ] Configure proper CORS for production domain only
- [ ] Set up security headers (HSTS, CSP, X-Frame-Options)
- [ ] Regular security updates for dependencies
- [ ] Implement monitoring and alerting

## Reporting Security Issues

If you discover a security vulnerability, please:
1. Do NOT open a public issue
2. Email the maintainer directly
3. Provide detailed information about the vulnerability
4. Allow reasonable time for a fix before public disclosure

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
